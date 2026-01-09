#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
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


# ----------- #
# -- TOOLS -- #
# ----------- #

def extract_name_n_srcname(name_srcname: str) -> (str, str):
    return tuple(name_srcname.split('::'))


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

SPECIAL_QUERIES = {
    TAG_EQUAL: """
SELECT
    COUNT(*) as nb,
    GROUP_CONCAT(name || '::' || source, ',')
FROM palettes
GROUP BY hash_normal
HAVING nb > 1
    """,
    TAG_MIRROR: """
SELECT
    GROUP_CONCAT(p1.name || '::' || p1.source),
    GROUP_CONCAT(p2.name || '::' || p2.source)
FROM palettes p1, palettes p2
WHERE p1.hash_normal = p2.hash_reverse
AND p1.id < p2.id
    """,
}


QUERY_PALS_NAME_CONFLICT = """
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

AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


FULL_SQLITE_DB_FILE  = REPORT_DIR / "full-palettes.db"
FINAL_SQLITE_DB_FILE = AUDIT_DIR / "final-palettes.db"


with (AUDIT_DIR / 'PRIORITY.yaml').open(mode = 'r') as stream:
    PRIORITY_CONFIG = yaml.safe_load(stream)


with (AUDIT_DIR / 'IGNORED.yaml').open(mode = 'r') as stream:
    IGNORED_CONFIG = yaml.safe_load(stream)

PALS_IGNORED = set()

if not IGNORED_CONFIG is None:
    for src, names in IGNORED_CONFIG.items():
        for n in names:
            PALS_IGNORED.add((n, src))


with (AUDIT_DIR / 'RENAMED.yaml').open(mode = 'r') as stream:
    RENAMED_CONFIG = yaml.safe_load(stream)

if RENAMED_CONFIG is None:
    PALS_RENAMED = dict()

else:
    PALS_RENAMED = RENAMED_CONFIG


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

EQUAL_JSON         = REPORT_DIR / "AUDIT-EQUAL.json"
MIRROR_JSON        = REPORT_DIR / "AUDIT-MIRROR.json"
NAME_CONFLICT_JSON = REPORT_DIR / "AUDIT-NAME-CONFLICT.json"


PALS_SAME = {
    TAG_EQUAL : [],
    TAG_MIRROR: [],
}


PALS_EQUALS             = dict()
PALS_MIRRORS            = dict()
PALS_PALS_NAME_CONFLICT = defaultdict(set)


# ----------------------------- #
# -- EQUAL / MIRROR PALETTES -- #
# ----------------------------- #

# -- DB EXTRACTION -- #

logging.info(f"DATA cleaning - 'Equal or mirror'.")


with sqlite3.connect(FULL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for tag, query in SPECIAL_QUERIES.items():
        cursor.execute(query)

        PALS_SAME[tag] = list(cursor.fetchall())


# -- IDENTICAL PALETTES -- #

for _ , _equal_pals in PALS_SAME[TAG_EQUAL]:
    equal_pals = set(
        extract_name_n_srcname(nsn)
        for nsn in _equal_pals.split(',')
    )

    equal_pals -= PALS_IGNORED

# No equality (some palettes ignored).
    if len(equal_pals) == 1:
        continue

# Identical palettes but different names
    if 1 != len(set(n for n, _ in equal_pals)):
        tab = "\n  + "

        equal_pals = [
            reverse_build_name_n_srcname(*nsn)
            for nsn in equal_pals
        ]
        equal_pals.sort()

        log_raise_error(
            context   = "Conflicts need NOAI resolution",
            desc      = "Identical palettes but different names",
            exception = Exception,
            xtra      = f"See:{tab}{tab.join(equal_pals)}"
        )

# Looking for the "higher" palette.
    higher_projs = set()
    higher_val   = 0

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

# Do we have a same priority conflicts?
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

# No problem! Let's record our choices.
    pal_kept = (name, list(higher_projs)[0])

    for p in equal_pals:
        if p == pal_kept:
            continue

        PALS_EQUALS[p] = pal_kept


# -- MIRROR PALETTES -- #

for mirror_pals in PALS_SAME[TAG_MIRROR]:
    pal_1, pal_2 = [
        extract_name_n_srcname(nsn)
        for nsn in mirror_pals
    ]

    pal_alias_1 = PALS_EQUALS.get(pal_1, pal_1)
    pal_alias_2 = PALS_EQUALS.get(pal_2, pal_2)

    if PRIORITY_CONFIG[pal_alias_1[1]] > PRIORITY_CONFIG[pal_alias_2[1]]:
        PALS_MIRRORS[pal_alias_2] = pal_alias_1

    elif PRIORITY_CONFIG[pal_alias_1[1]] < PRIORITY_CONFIG[pal_alias_2[1]]:
        PALS_MIRRORS[pal_alias_1] = pal_alias_2

    elif pal_alias_1[0] < pal_alias_2[0]:
        PALS_MIRRORS[pal_alias_2] = pal_alias_1

    else:
        PALS_MIRRORS[pal_alias_1] = pal_alias_2


# --------------------- #
# -- NAME CONFLICTS? -- #
# --------------------- #

logging.info(f"DATA cleaning - 'Same name / Different palettes'.")

PALS_NAME_CONFLICT = defaultdict(set)

# -- DB EXTRACTION -- #

with sqlite3.connect(FULL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(QUERY_PALS_NAME_CONFLICT)

    for name, *sources in cursor.fetchall():
        for s in sources:
            pal = (name, s)
            pal = PALS_EQUALS.get(pal, pal)

            if not pal in PALS_IGNORED:
                PALS_NAME_CONFLICT[name].add(pal[1])

# Error will be indicated after updating the JSON file.


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(f"DATA cleaning - 'Update JSON audit files'.")

jsonify_dict = lambda d: {
    build_name_n_srcname(*nsn_1): build_name_n_srcname(*nsn_2)
    for nsn_1, nsn_2 in d.items()
}


EQUAL_JSON.write_text(
    json_dumps(jsonify_dict(PALS_EQUALS))
)

MIRROR_JSON.write_text(
    json_dumps(jsonify_dict(PALS_MIRRORS))
)


_PALS_NAME_CONFLICT = {
    k: list(v)
    for k, v in PALS_NAME_CONFLICT.items()
}

NAME_CONFLICT_JSON.write_text(
    json_dumps(_PALS_NAME_CONFLICT)
)


# -------------------------------------- #
# -- NAME CONFLICTS MUST BE RESOLVED! -- #
# -------------------------------------- #

if PALS_NAME_CONFLICT:
    reslover = PROJ_DIR / "tools" / "lab" / "resolve" /"name-conflicts.py"

    log_raise_error(
        context   = "Conflicts need NOAI resolution",
        desc      = "Same name for different and not mirror palettes.",
        exception = ValueError,
        xtra      = f"Open\n{reslover}"
    )


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info(f"SQLite DB - 'FINAL table creation'.")

with sqlite3.connect(FINAL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS palettes;')
    cursor.execute('''
CREATE TABLE palettes (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT NOT NULL,
    source TEXT NOT NULL,
    kind   TEXT NOT NULL,
)
    ''')
