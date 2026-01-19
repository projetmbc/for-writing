#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
# -- DEBUG - OFF -- #

from typing import Iterator


# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# -------------------- #
# -- SQL QUERIES #1 -- #
# -------------------- #

SQL_SAME_HASH = '''
SELECT
    GROUP_CONCAT(
        h.pal_id                  || ',' ||
        p.priority                || ',' ||
        COALESCE(a.alias, h.name) || ',' ||
        h.source,
        ';'
    )
FROM hash h
JOIN priority p ON h.source = p.source
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1
GROUP BY h.hash_normal
HAVING COUNT(*) > 1;
'''

SQL_UPDATE_EQUAL_TO = '''
UPDATE hash
SET equal_to = ?,
    is_kept  = 0
WHERE pal_id = ?;
'''

SQL_UPDATE_IGNORED = '''
UPDATE hash
SET is_kept = 0
WHERE pal_id = ?;
'''


# -------------------- #
# -- SQL QUERIES #1 -- #
# -------------------- #

SQL_MIRROR_HASH = '''
SELECT
    p1.pal_id,
    prio1.priority,
    COALESCE(a1.alias, p1.name),
    p2.pal_id,
    prio2.priority,
    COALESCE(a2.alias, p2.name)
FROM hash p1
LEFT JOIN alias a1 ON p1.pal_id = a1.pal_id
JOIN priority prio1 ON p1.source = prio1.source
JOIN hash p2 ON p1.hash_normal = p2.hash_reverse
LEFT JOIN alias a2 ON p2.pal_id = a2.pal_id
JOIN priority prio2 ON p2.source = prio2.source
WHERE p1.is_kept = 1
  AND p2.is_kept = 1
  AND p1.pal_id < p2.pal_id;
'''

SQL_TABLE_INSERT_MIRROR = '''
INSERT INTO mirror (
    cand_pal_id_1,
    cand_pal_id_2
) VALUES (?, ?)
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'


# -------------- #
# -- TOOLS #1 -- #
# -------------- #

def iter_semi_colon_coma(text: str) -> Iterator[str]:
    for sc_parts in text.split(';'):
        yield sc_parts.split(',')


# -------------- #
# -- TOOLS #2 -- #
# -------------- #

def dp_update_full_equal_pals(
    conn,
    id_2_meta
):
# Looking for the "higher" palette.
    higher_srcs = set()
    higher_val  = float('-inf')
    kept_id     = None

    for pal_id, (priority, _ , src) in id_2_meta.items():
        if (
            not higher_srcs
            or
            higher_val < priority
        ):
            higher_srcs = set([src])
            higher_val = priority
            kept_id    = pal_id

        elif higher_val == priority:
            higher_srcs.add(src)

# Do we have a same priority conflicts?
    if len(higher_srcs) != 1:
        tab = "\n  + "

        higher_srcs = list(higher_srcs)
        higher_srcs.sort()

        log_raise_error(
            context   = "Conflicts need NOAI resolution",
            desc      = "Equal project priorities found.",
            exception = Exception,
            xtra      = f"See:{tab}{tab.join(higher_srcs)}"
        )

# Let's store the infos.
    for one_id in id_2_meta:
        if one_id != kept_id:
            cursor.execute(
                SQL_UPDATE_EQUAL_TO,
                (kept_id, one_id)
            )


def report_or_not_difname_samepal(same_pal_diff_names):
    if not same_pal_diff_names:
        return None

    _xtra_what = []

    tab_1 = "  + "
    tab_2 = "    - "

    for i, equal_pals in enumerate(same_pal_diff_names, 1):
        _xtra_what.append(f"{tab_1}Group #{i}")

        equal_pals.sort(
            key     = lambda x: int(x[0]),
            reverse = True,
        )

        equal_pals = [
            (
                f"Prio[{x[0]}] "
                f"{reverse_build_name_n_srcname(*x[1:])}"
            )
            for x in equal_pals
        ]

        for w in equal_pals:
            _xtra_what.append(f"{tab_2}{w}")

    xtra_what = '\n'.join(_xtra_what)

    log_raise_error(
        context   = "Conflicts need NOAI resolution",
        desc      = "Identical palettes but different names",
        exception = Exception,
        xtra      = (
            f"See:\n{xtra_what}\n"
            f"Open '{IGNORED_YAML}'."
        )
    )


# -------------- #
# -- TOOLS #3 -- #
# -------------- #

def dp_update_mirror_pals(conn):
    cursor = conn.cursor()
    cursor.execute(SQL_MIRROR_HASH)

    for data in cursor.fetchall():
        pal_ids = data[::3]
        scores  = [
            (- prio, alias)
            for prio, alias in zip(
                data[1::3],
                data[2::3]
            )
        ]

# Same score for two palettes implies a name conflict (same name
# in two different projects of same priority).
# Another script will handle this immediately afterwards.
        if scores[0] == scores[1]:
            return None

# Palette #2 takes precedence.
        if scores[1] < scores[0]:
            pal_ids = pal_ids[::-1]

# Palette #1 has strict greater score, so we ignore palette #2.
        cursor.execute(
            SQL_UPDATE_IGNORED,
            (pal_ids[1],)
        )

# We keep the info about the mirror relation.
        cursor.execute(
            SQL_TABLE_INSERT_MIRROR,
            tuple(pal_ids)
        )


# ----------------------------- #
# -- STRICTLY EQUAL PALETTES -- #
# ----------------------------- #

logging.info("Analyze data - 'Look for equal hash'")

# -- Same name / Same palette -- #

same_pal_diff_names = list()

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_SAME_HASH)

    for _equal_pals in cursor.fetchall():
# Pythonic data.
        id_2_meta = dict()

        for pal_id, *oppoprio_name in iter_semi_colon_coma(_equal_pals[0]):
            id_2_meta[pal_id] = oppoprio_name

# Identical palettes but different names.
#
# We store the values to indicate ALL conflicts to resolve.
        if 1 != len(
            set(d[1] for d in id_2_meta.values())
        ):
            same_pal_diff_names.append(
                list(id_2_meta.values())
            )

            continue

# Identical palettes and same name.
        else:
            dp_update_full_equal_pals(conn, id_2_meta)


# -- Different names / Same palette -- #

report_or_not_difname_samepal(same_pal_diff_names)


# --------------------- #
# -- MIRROR PALETTES -- #
# --------------------- #

logging.info("Analyze data - 'Look for mirror palettes'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    dp_update_mirror_pals(conn)
