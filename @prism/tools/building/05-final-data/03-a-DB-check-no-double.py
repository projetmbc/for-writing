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

from collections import defaultdict


# -------------------- #
# -- SQL QUERIES #1 -- #
# -------------------- #

SQL_SAME_HASH = '''
SELECT
    GROUP_CONCAT(
        h.name     || ',' ||
        h.source   || ',' ||
        h.is_kept  || ',' ||
        p.priority || ',' ||
        h.pal_id,
        ';'
    )
FROM hash h
JOIN priority p
  ON h.source = p.source
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
# -- SQL QUERIES #2 -- #
# -------------------- #

SQL_MIRROR_HASH = '''
SELECT
    h1.pal_id, p1.priority, h1.name,
    h2.pal_id, p2.priority, h2.name
FROM hash h1
---
JOIN priority p1
  ON h1.source = p1.source
---
JOIN hash h2
  ON h1.hash_normal = h2.hash_reverse
---
JOIN priority p2
  ON h2.source = p2.source
---
WHERE h1.is_kept = 1
  AND h2.is_kept = 1
  AND h1.pal_id < h2.pal_id;
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
IGNORED_YAML   = AUDIT_DIR / 'IGNORED.yaml'


# -------------- #
# -- TOOLS #1 -- #
# -------------- #

def iter_semi_colon_coma(text: str) -> Iterator[str]:
    for sc_parts in text.split(';'):
        yield sc_parts.split(',')


# -------------- #
# -- TOOLS #2 -- #
# -------------- #

def get_unkept_ids(data: list[str]) -> list[str]:
    maxprio = str(
        max(int(d[2]) for d in data)
    )

# We can't have several sources with maximal priority.
    if 1 != len([
        None
        for d in data
        if d[2] == maxprio
    ]):
        data = [
            d
            for d in data
            if d[2] == maxprio
        ]

        log_raise_error(
            context = "Unkept palettes",
            desc    = (
                 "Max priority for several sources, "
                f"see palette '{name}' for sources "
                f"{', '.join(f"'{n}'" for n, *_ in data)}"
            ),
            exception = Exception,
            xtra      = f"Update:\n{IGNORED_YAML}"
        )

# Let's gives the IDs to ignore.

    return set(
        d[-1]
        for d in data
        if d[2] != maxprio
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


# ----------------------------- #
# -- STRICTLY EQUAL PALETTES -- #
# ----------------------------- #

logging.info("DB - Analyze - 'Equal hash'")

# -- Same name / Same palette -- #

same_pal_diff_names = list()

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_SAME_HASH)

    for _equal_pals, in cursor.fetchall():
        name2data = defaultdict(list)

# Data to analyze.
        for name, *data in iter_semi_colon_coma(_equal_pals):
            name2data[name].append(data)

        namesrc_kept = []

# Get nb. of unkept by design palettes.
        for name, data in name2data.items():
            nb_pals_managed = len(data)

            nb_unkept = len(
                set(
                    s
                    for s, k, *_ in data
                    if k == '0'
                )
            )

# All palettes removed.
            if nb_unkept == nb_pals_managed:
                continue

# One removed palette by human
# =>
# All full equal palettes removed
            if nb_unkept == 1:
                subpals_ignored = []

                for _ , is_kept, _ , palid in data:
                    if is_kept == '0':
                        mainpal_ignored = palid

                    else:
                        subpals_ignored.append(palid)


                for palid in subpals_ignored:
                    cursor.execute(
                        SQL_UPDATE_EQUAL_TO,
                        (mainpal_ignored, palid)
                    )

                continue

# Too much removed palettes by human
            if nb_unkept != 0:
                log_raise_error(
                    context = "Unkept palettes",
                    desc    = (
                         "Too much removed palettes by human, "
                        f"palette '{name}' for sources "
                        f"{', '.join(f"'{n}'" for n, *_ in data)}"
                    ),
                    exception = Exception,
                    xtra      = f"Update:\n{IGNORED_YAML}"
                )

# Auto removed palettes.
            unkept_ids = get_unkept_ids(data)

            for src , _ , prio, palid in data:
                if not palid in unkept_ids:
                    palkept = palid

                    namesrc_kept.append([prio, name, src])

                    break

            for palid in unkept_ids:
                cursor.execute(
                    SQL_UPDATE_EQUAL_TO,
                    (palkept, palid)
                )

# Identical palettes but different names.
#
# We store the values to indicate ALL conflicts to resolve.
        if len(namesrc_kept) > 1:
            same_pal_diff_names.append(namesrc_kept)


# -- Different names / Same palette -- #

report_or_not_difname_samepal(same_pal_diff_names)


# --------------------- #
# -- MIRROR PALETTES -- #
# --------------------- #

logging.info("DB - Analyze - 'Mirror palettes'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
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
            continue

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
