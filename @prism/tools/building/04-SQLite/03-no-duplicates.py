#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

_THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = _THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

import yaml


# ----------- #
# -- TOOLS -- #
# ----------- #

def extract_name_n_srcname(name_srcname: str) -> (str, str):
    return name_srcname.split('::')


def build_name_n_srcname(
    name: str,
    srcname: str,
) -> str:
    return '::'.join([name, srcname])


def reverse_build_name_n_srcname(
    name: str,
    srcname: str,
) -> str:
    return build_name_n_srcname(srcname, name)


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

QUERY_SAME_HASH = """
SELECT
    COUNT(*) as nb,
    GROUP_CONCAT(
       name || '::' || source,
       ','
    )
FROM palettes
GROUP BY hash_normal
HAVING nb > 1
"""

QUERY_MIRROR_HASH = """
SELECT
    p1.name, p1.source,
    p2.name, p2.source
FROM palettes p1, palettes p2
WHERE p1.hash_normal = p2.hash_reverse
AND p1.id < p2.id
"""

QUERY_NAME_CONFLICT = """
SELECT
    p1.name,
    p1.source,
    p2.source
FROM palettes p1
JOIN palettes p2 ON p1.name = p2.name
WHERE p1.id < p2.id
  AND p1.hash_normal != p2.hash_normal
  AND p1.hash_normal != p2.hash_reverse;
"""


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


FULL_SQLITE_DB_FILE     = REPORT_DIR / "full-palettes.db"
FINAL_SQLITE_DB_FILE    = REPORT_DIR / "final-palettes.db"
CONFLICT_SQLITE_DB_FILE = REPORT_DIR / "conflict-palettes.db"


with (_THIS_DIR / 'PRIORITY.yaml').open(mode = 'r') as stream:
    PRIORITY_CONFIG = yaml.safe_load(stream)


with (_THIS_DIR / 'IGNORED.yaml').open(mode = 'r') as stream:
    IGNORED_CONFIG = yaml.safe_load(stream)

PALS_IGNORED = set()

if not IGNORED_CONFIG is None:
    for src, names in IGNORED_CONFIG.items():
        for n in names:
            PALS_IGNORED.add((n, src))


with (_THIS_DIR / 'RENAMED.yaml').open(mode = 'r') as stream:
    RENAMED_CONFIG = yaml.safe_load(stream)

if RENAMED_CONFIG is None:
    PALS_RENAMED = dict()

else:
    PALS_RENAMED = RENAMED_CONFIG


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

PALS_IDENTICAL_JSON = REPORT_DIR / f"SAME-PALS-IDENTICAL.json"
PALS_MIRROR_JSON    = REPORT_DIR / f"SAME-PALS-MIRROR.json"


PALS_SAME = {
    TAG_IDENTICAL: [],
    TAG_MIRROR   : [],
    TAG_KEPT     : [],
}


# ------------------------ #
# -- DB INITIALIZATIONS -- #
# ------------------------ #

logging.info(f"SQLite DB - 'FINAL table creation'.")

with sqlite3.connect(FINAL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS palettes;')
    cursor.execute('''
CREATE TABLE palettes (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT NOT NULL,
    source TEXT NOT NULL,
    size   INTEGER NOT NULL,
    kind   TEXT NOT NULL
)
    ''')


logging.info(f"SQLite DB - 'CONFLICT table creation'.")

with sqlite3.connect(CONFLICT_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS palettes;')
    cursor.execute('''
CREATE TABLE palettes (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name_1   TEXT NOT NULL,
    source_1 TEXT NOT NULL,
    name_2   TEXT NOT NULL,
    source_2 TEXT NOT NULL
)
    ''')


# ----------------------- #
# -- REMOVE DUPLICATES -- #
# ----------------------- #

# Extraction for DB.
with sqlite3.connect(FULL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for tag, query in [
        (TAG_IDENTICAL, QUERY_SAME_HASH  ),
        (TAG_MIRROR   , QUERY_MIRROR_HASH),
    ]:
        cursor.execute(query)

        PALS_SAME[tag] = list(cursor.fetchall())

# Identical palettes.
for _ , _equal_pals in PALS_SAME[TAG_IDENTICAL]:
    equal_pals = set(
        tuple(extract_name_n_srcname(nsn))
        for nsn in _equal_pals.split(',')
    )

    equal_pals -= PALS_IGNORED

    if len(equal_pals) == 1:
        continue

    if len(
        set(n for n, _ in equal_pals)
    ) != 1:
        tab = "\n  + "

        equal_pals = [
            revers_build_name_n_srcname(*nsn)
            for nsn in equal_pals
        ]
        equal_pals.sort()

        log_raise_error(
            context   = "Conflicts need NOAI resolution",
            desc      = "Identical palettes with different names",
            exception = Exception,
            xtra      = f"See:{tab}{tab.join(equal_pals)}"
        )

    higher_projs = set()
    higher_val  = 0

    for name, src in equal_pals:
        if (
            not higher_projs
            or
            higher_val < PRIORITY_CONFIG[src]
        ):
            higher_projs = set([src])
            higher_val = PRIORITY_CONFIG[src]

        elif higher_val == PRIORITY_CONFIG[src]:
            higher_projs.add(src)

    if len(higher_projs) != 1:
        tab = "\n  + "

        higher_projs = list(higher_projs)
        higher_projs.sort()

        log_raise_error(
            context   = "Conflicts need NOAI resolution",
            desc      = "No priority found for the following projects.",
            exception = Exception,
            xtra      = f"See:{tab}{tab.join(higher_projs)}"
        )

    pal_kept = (name, list(higher_projs)[0])

    PALS_SAME[TAG_KEPT].append(pal_kept)

    PALS_IGNORED |= equal_pals - set([pal_kept])

# Mirror palettes.
for name_1, src_1, name_2, src_2 in PALS_SAME[TAG_MIRROR]:
    if (
        (name_2, src_2) in PALS_IGNORED
        or
        PRIORITY_CONFIG[src_1] > PRIORITY_CONFIG[src_2]
    ):
        pal_kept = (name_1, src_1)

    elif (
        (name_1, src_1) in PALS_IGNORED
        or
        PRIORITY_CONFIG[src_1] < PRIORITY_CONFIG[src_2]
    ):
        pal_kept = (name_2, src_2)

    elif name_1 < name_2:
        pal_kept = (name_1, src_1)

    else:
        pal_kept = (name_2, src_2)

    PALS_SAME[TAG_KEPT].append(pal_kept)

    # PALS_IGNORED |= set([
    #     (name_1, src_1),
    #     (name_2, src_2)
    # ]) - set([pal_kept])


# --------------- #
# -- HOMONYMS? -- #
# --------------- #

name_conflict = defaultdict(set)

# Extraction for DB.
with sqlite3.connect(FULL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(QUERY_NAME_CONFLICT)

    for name, *sources in cursor.fetchall():
        for s in sources:
            if not (name, s) in PALS_IGNORED:
                name_conflict[name].add(s)



print(name_conflict)
