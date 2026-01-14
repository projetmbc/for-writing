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

# Full DB.

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
    CONCAT(p1.name || '::' || p1.source),
    CONCAT(p2.name || '::' || p2.source)
FROM palettes p1, palettes p2
WHERE p1.hash_normal = p2.hash_reverse
AND p1.id < p2.id
    """,
}

QUERY_NAME_CONFLICT = """
SELECT
    p1.name,
    p1.source,
    p2.name,
    p2.source
FROM palettes p1
JOIN palettes p2 ON LOWER(p1.name) = LOWER(p2.name)
WHERE p1.id < p2.id
  AND p1.hash_normal != p2.hash_normal
  AND p1.hash_normal != p2.hash_reverse;
"""

QUERY_EXTRACT_FOR_FINAL = """
SELECT
    p.name,
    p.source,
    p.kind
FROM palettes p;
"""

# Final DB.

QUERY_CREATE_FINAL_DB = '''
CREATE TABLE palettes (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    uid    TEXT NOT NULL,
    name   TEXT NOT NULL,
    kind   TEXT NOT NULL
)
'''

QUERY_INSERT_IN_FINAL = """
INSERT INTO palettes (
    uid,
    name,
    kind
) VALUES (?, ?, ?)
"""


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR     = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR    = BUILD_TOOLS_DIR / TAG_REPORT

FULL_SQLITE_DB_FILE  = REPORT_DIR / "full-palettes.db"
FINAL_SQLITE_DB_FILE = AUDIT_DIR / "final-palettes.db"


PRIORITY = YAML_CONFIGS['PRIORITY']


RENAMED_YAML = AUDIT_DIR / 'RENAMED.yaml'
RENAMED_YAML.touch()


IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'

with IGNORED_YAML.open(mode = 'r') as f:
    IGNORED = yaml.safe_load(f)

PALS_IGNORED = set()

if not IGNORED is None:
    for src, names in IGNORED.items():
        for n in names:
            PALS_IGNORED.add((n, src))


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


EQUALS         = dict()
MIRRORS        = dict()
NAME_CONFLICTS = defaultdict(set)


# ----------------------------- #
# -- EQUAL / MIRROR PALETTES -- #
# ----------------------------- #

# WARNING! We don't apply any renaming because this ones resolve
# conflict names (same lower names for different palettes).

# -- DB EXTRACTION -- #

logging.info(
    f"DATA cleaning - 'Equal or mirror' (no renaming here)."
)


with sqlite3.connect(FULL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for tag, query in SPECIAL_QUERIES.items():
        cursor.execute(query)

        PALS_SAME[tag] = list(cursor.fetchall())


# -- SAME NAME / SAME PALETTE / DIFFERNT TECHNO. -- #

grps_equal_pals = list()

for _ , _equal_pals in PALS_SAME[TAG_EQUAL]:
    equal_pals = set(
        extract_name_n_srcname(uid)
        for uid in _equal_pals.split(',')
    )

    equal_pals -= PALS_IGNORED

# No equality (some palettes ignored).
    if len(equal_pals) == 1:
        continue

# Identical palettes but different names.
    if 1 != len(set(n for n, _ in equal_pals)):
        grps_equal_pals.append(equal_pals)

        continue

# Looking for the "higher" palette.
    higher_projs = set()
    higher_val   = 0

    for name, src in equal_pals:
        if (
            not higher_projs
            or
            higher_val < PRIORITY[src]
        ):
            higher_projs = set([src])
            higher_val = PRIORITY[src]

        elif higher_val == PRIORITY[src]:
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

        EQUALS[p] = pal_kept


# -- DIFFERENT NAMES / SAME PALETTE -- #

if grps_equal_pals:
    _xtra_what = []

    tab_1 = "  + "
    tab_2 = "    - "

    for i, equal_pals in enumerate(grps_equal_pals, 1):
        _xtra_what.append(f"{tab_1}Group #{i}")

        equal_pals = list(equal_pals)

        equal_pals.sort(
            key     = lambda uid: int(PRIORITY[uid[1]]),
            reverse = True,
        )

        equal_pals = [
            (
                f"Prio[{PRIORITY[uid[1]]}] "
                f"{reverse_build_name_n_srcname(*uid)}"
            )
            for uid in equal_pals
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


# -- MIRROR PALETTES -- #

for mirror_pals in PALS_SAME[TAG_MIRROR]:
    pal_1, pal_2 = [
        extract_name_n_srcname(uid)
        for uid in mirror_pals
    ]

    pal_alias_1 = EQUALS.get(pal_1, pal_1)
    pal_alias_2 = EQUALS.get(pal_2, pal_2)

    if PRIORITY[pal_alias_1[1]] > PRIORITY[pal_alias_2[1]]:
        MIRRORS[pal_alias_2] = pal_alias_1

    elif PRIORITY[pal_alias_1[1]] < PRIORITY[pal_alias_2[1]]:
        MIRRORS[pal_alias_1] = pal_alias_2

    elif pal_alias_1[0] < pal_alias_2[0]:
        MIRRORS[pal_alias_2] = pal_alias_1

    else:
        MIRRORS[pal_alias_1] = pal_alias_2


# ----------- #
# -- ALIAS -- #
# ----------- #

logging.info(f"DATA cleaning - 'Building alias'.")

with RENAMED_YAML.open(mode = 'r') as f:
    _RENAMED = yaml.safe_load(f)

RENAMED = (
    dict()
    if _RENAMED is None else
    builde_new_palnames(_RENAMED)
)

assert len(list(RENAMED.values())) == len(set(RENAMED.values()))

# NEWNAME_2_UID = {
#     v: k
#     for k, v in RENAMED.items()
# }


# --------------------- #
# -- NAME CONFLICTS? -- #
# --------------------- #

logging.info(f"DATA cleaning - 'Same lower name / Different palettes'.")

# -- DB EXTRACTION -- #

name_conflicts = defaultdict(set)

with sqlite3.connect(FULL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(QUERY_NAME_CONFLICT)

    for data in cursor.fetchall():
        for pal in zip(data[::2], data[1::2]):
            if build_name_n_srcname(*pal) in RENAMED:
                continue

            pal = EQUALS.get(pal, pal)

            if not pal in PALS_IGNORED:
                name_conflicts[pal[0].lower()].add(pal)

PALS_NAME_CONFLICT = []

for name, sources in name_conflicts.items():
    if len(sources) > 1:
        PALS_NAME_CONFLICT.append(list(sources))

PALS_NAME_CONFLICT.sort()

# NOTE. Error will be indicated after updating the JSON file.


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(f"DATA cleaning - 'Update JSON audit files'.")

jsonify_dict = lambda d: get_sorted_dict({
    build_name_n_srcname(*uid_1): build_name_n_srcname(*uid_2)
    for uid_1, uid_2 in d.items()
})


_EQUALS  = jsonify_dict(EQUALS)
_MIRRORS = jsonify_dict(MIRRORS)


EQUAL_JSON.write_text(
    json_dumps(_EQUALS)
)

MIRROR_JSON.write_text(
    json_dumps(_MIRRORS)
)

NAME_CONFLICT_JSON.write_text(
    json_dumps(PALS_NAME_CONFLICT)
)


# -------------------------------------- #
# -- NAME CONFLICTS MUST BE RESOLVED! -- #
# -------------------------------------- #

if PALS_NAME_CONFLICT:
    reslover = PROJ_DIR / "tools" / "lab" / "resolve" / "name-conflicts.py"

    log_raise_error(
        context   = "Conflicts need NOAI resolution",
        desc      = "Same name for different and not mirror palettes.",
        exception = ValueError,
        xtra      = f'Use:\n---\nstreamlit run "{reslover}"\n---'
    )


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info(f"DATA cleaning - Final SQLite DB - 'Init table'.")

with sqlite3.connect(FINAL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS palettes;')
    cursor.execute(QUERY_CREATE_FINAL_DB)


# ----------------- #
# -- POPULATE DB -- #
# ----------------- #

logging.info(f"DATA cleaning - Final SQLite DB - 'Populate table'.")

already_kept = set()


with (
    sqlite3.connect(FULL_SQLITE_DB_FILE) as full_conn,
    sqlite3.connect(FINAL_SQLITE_DB_FILE) as final_conn,
):
    full_cursor  = full_conn.cursor()
    final_cursor = final_conn.cursor()

    full_cursor.execute(QUERY_EXTRACT_FOR_FINAL)

    for name, src, kind in full_cursor.fetchall():
        name_src = build_name_n_srcname(name, src)

        for tokeep in [
            _EQUALS,
            _MIRRORS,
        ]:
            if name_src in tokeep:
                name_src = tokeep[name_src]

                break

        aprism_name_src = RENAMED.get(name_src, name_src)

        if aprism_name_src in already_kept:
            continue

        already_kept.add(aprism_name_src)

        aprism_name, _ = extract_name_n_srcname(aprism_name_src)

        final_cursor.execute(
            QUERY_INSERT_IN_FINAL,
            [name_src.lower(), aprism_name, kind]
        )


# ------------------------ #
# -- NOTHING LEFT TO DO -- #
# ------------------------ #

logging.info(
     "DATA cleaning - Final SQLite DB - File "
    f"'{FINAL_SQLITE_DB_FILE.relative_to(PROJ_DIR)}' "
     "build."
)
