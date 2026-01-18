exit(1)


#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

SQL_SAME_HASH = '''
SELECT
    GROUP_CONCAT(
        id   || ',' ||
        name || ',' || source || ',' ||
        priority,
        ';'
    )
FROM palettes
WHERE is_kept = 1
GROUP BY hash_normal
HAVING COUNT(*) > 1
'''

SQL_UPDATE_EQUAL_TO = """
UPDATE palettes
SET equal_to = ?,
    is_kept = 0
WHERE id = ?;
"""

SQL_UPDATE_IGNORED = """
UPDATE palettes
SET is_kept = 0
WHERE id = ?;
"""


SQL_MIRROR_HASH = '''
SELECT
    p1.equal_to, p1.priority,
    p2.equal_to, p2.priority
FROM palettes p1, palettes p2
WHERE p1.hash_normal = p2.hash_reverse
  AND p1.id < p2.id
'''

SQL_UPDATE_MIRROR_TO = """
UPDATE palettes
SET mirror_of = ?
WHERE id = ?;
"""


SQL_GET_ALIAS = """
SELECT
    p.name
FROM palettes p
WHERE p.id = ?
"""


SQL_GET_NAME_SRC = """
SELECT
    p.name, p.source
FROM palettes p
WHERE p.id = ?
"""


SQL_NAME_CONFLICT = """
SELECT
    p1.id, p2.id
FROM palettes p1
JOIN palettes p2 ON LOWER(p1.name) = LOWER(p2.name)
WHERE p1.is_kept = 1
  AND p2.is_kept = 1
  AND p1.hash_normal != p2.hash_normal
  AND p1.hash_normal != p2.hash_reverse
  AND p1.id < p2.id
"""


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

SQLITE_DB_FILE  = AUDIT_DIR / "palettes.db"


IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

NAME_CONFLICT_JSON =  REPORT_DIR / f"AUDIT-NAME-CONFLICT.json"

NAME_CONFLICT_IDS   = set()
AUDIT_NAME_CONFLICT = defaultdict(list)


# ----------- #
# -- TOOLS -- #
# ----------- #

def dp_update_full_equal_pals(
    conn,
    id_2_nsn
):
# Looking for the "higher" palette.
    higher_srcs = set()
    higher_val   = 0

    for lastid, (_ , src, priority) in id_2_nsn.items():
        if (
            not higher_srcs
            or
            higher_val < priority
        ):
            higher_srcs = set([src])
            higher_val = priority

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
    for oneid in id_2_nsn:
        if oneid == lastid:
            continue

        cursor.execute(
            SQL_UPDATE_EQUAL_TO,
            (lastid, oneid)
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
            key     = lambda x: int(x[-1]),
            reverse = True,
        )

        equal_pals = [
            (
                f"Prio[{x[-1]}] "
                f"{reverse_build_name_n_srcname(*x[:-1])}"
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


def get_alias(conn, pal_id):
    cursor = conn.cursor()
    cursor.execute(
        SQL_GET_ALIAS,
        (pal_id, )
    )

    return list(cursor.fetchall())[0][0]


def dp_update_mirror_pals(conn):
    cursor = conn.cursor()
    cursor.execute(SQL_MIRROR_HASH)

    for data in cursor.fetchall():
        pals_equ_tos = data[::2]
        pals_prios   = data[1::2]

        pals_alias = [
            get_alias(conn, final_id)
            for final_id in pals_equ_tos
        ]

        scores = [
            (- prio, alias)
            for prio, alias in zip(pals_prios, pals_alias)
        ]

# Same score for two palettes implies a name conflict (same name
# in two different projects of same priority).
        if scores[0] == scores[1]:
            NAME_CONFLICT_IDS.add((pals_equ_tos[0], pals_equ_tos[1]))

            return None

# Palette #2 takes precedence.
        if scores[1] < scores[0]:
            pals_equ_tos = pals_equ_tos[::-1]

# Palette #1 has strict greater score, so we ignore palette #2.
        cursor.execute(
            SQL_UPDATE_IGNORED,
            (pals_equ_tos[0],)
        )

# We keep the info about the mirror relation.
        cursor.execute(
            SQL_UPDATE_MIRROR_TO,
            tuple(pals_equ_tos)
        )


# -------------------- #
# -- EQUAL PALETTES -- #
# -------------------- #

logging.info("Analyze data - 'Equal palettes'.")

same_pal_diff_names = list()

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_SAME_HASH)

    for _equal_pals in cursor.fetchall():
# Pythonic data.
        id_2_nsn = dict()

        for idnsn in _equal_pals[0].split(';'):
            _id, *nsn = idnsn.split(',')

            id_2_nsn[_id] = nsn

# No equality (some palettes ignored).
        if len(id_2_nsn) == 1:
            continue

# Identical palettes but different names.
#
# We store the values to indicate ALL conflicts to resolve.
        if 1 != len(
            set(n for n, *_ in id_2_nsn.values())
        ):
            same_pal_diff_names.append(
                list(id_2_nsn.values())
            )

            continue

# Identical palettes and same name.
        else:
            dp_update_full_equal_pals(conn, id_2_nsn)

# -- Different names / Same palette ? -- #
report_or_not_difname_samepal(same_pal_diff_names)


# --------------------- #
# -- MIRROR PALETTES -- #
# --------------------- #

logging.info("Analyze data - 'Mirror palettes'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    dp_update_mirror_pals(conn)


# --------------------- #
# -- NAME CONFLICTS? -- #
# --------------------- #

logging.info(f"DATA cleaning - 'Different palettes / Same lower case name ?'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_NAME_CONFLICT)

    NAME_CONFLICT_IDS |= set(cursor.fetchall())


    AUDIT_NAME_CONFLICT

    for two_ids in NAME_CONFLICT_IDS:
        for pal_id in two_ids:
            cursor.execute(
                SQL_GET_NAME_SRC,
                (pal_id, )
            )

            name, src = list(cursor.fetchall())[0]

            AUDIT_NAME_CONFLICT[name.lower()].append((name, src))


# NOTE. Error will be indicated after updating the JSON file.


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(f"DATA cleaning - 'Update name conflict JSON audit file'.")

NAME_CONFLICT_JSON.write_text(
    json_dumps(AUDIT_NAME_CONFLICT)
)


# -------------------------------------- #
# -- NAME CONFLICTS MUST BE RESOLVED! -- #
# -------------------------------------- #

if AUDIT_NAME_CONFLICT:
    reslover = PROJ_DIR / "tools" / "lab" / "resolve" / "name-conflicts.py"

    log_raise_error(
        context   = "Conflicts need NOAI resolution",
        desc      = "Same name for different and not mirror palettes.",
        exception = ValueError,
        xtra      = f'Use:\n---\nstreamlit run "{reslover}"\n---'
    )


# ------------------------ #
# -- NOTHING LEFT TO DO -- #
# ------------------------ #

logging.info(
     "DATA cleaning - "
    f"'{SQLITE_DB_FILE.relative_to(PROJ_DIR)}' "
     "build."
)
