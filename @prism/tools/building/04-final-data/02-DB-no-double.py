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

SQL_EQUAL = '''
SELECT
    GROUP_CONCAT(
        id || ',' || name || ',' || source,
        ';'
    )
FROM palettes
GROUP BY hash_normal
HAVING COUNT(*) > 1
'''

SQL_UPDATE_EQUAL_TO = """
UPDATE palettes
SET equal_to = ?
WHERE id = ?;
"""


SQL_MIRROR = '''
SELECT
    p1.id, p1.name, p1.source,
    p2.id, p2.name, p2.source
FROM palettes p1, palettes p2
WHERE p1.hash_normal = p2.hash_reverse
AND p1.id < p2.id
'''


SQL_NAME_CONFLICT = """
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


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

SQLITE_DB_FILE  = AUDIT_DIR / "palettes.db"


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
            PALS_IGNORED.add(get_uid(src, n))


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

EQUAL_JSON         = REPORT_DIR / "AUDIT-EQUAL.json"
MIRROR_JSON        = REPORT_DIR / "AUDIT-MIRROR.json"
NAME_CONFLICT_JSON = REPORT_DIR / "AUDIT-NAME-CONFLICT.json"

NAME_CONFLICTS = defaultdict(set)


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

    for lastid, (_ , src) in id_2_nsn.items():
        if (
            not higher_srcs
            or
            higher_val < PRIORITY[src]
        ):
            higher_srcs = set([src])
            higher_val = PRIORITY[src]

        elif higher_val == PRIORITY[src]:
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
    if same_pal_diff_names:
        _xtra_what = []

        tab_1 = "  + "
        tab_2 = "    - "

        for i, equal_pals in enumerate(same_pal_diff_names, 1):
            _xtra_what.append(f"{tab_1}Group #{i}")

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


# -------------------- #
# -- EQUAL PALETTES -- #
# -------------------- #

logging.info("Analyze data - 'Looking for equal palettes'.")

same_pal_diff_names = list()

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_EQUAL)

    for _equal_pals in cursor.fetchall():
# Pythonic data.
        id_2_nsn = dict()

        for idnsn in _equal_pals[0].split(';'):
            _id , name, src = idnsn.split(',')

            uid = get_uid(src, name)

            if not uid in PALS_IGNORED:
                id_2_nsn[_id] = (name, src)

# No equality (some palettes ignored).
        if len(id_2_nsn) == 1:
            continue

# Identical palettes but different names.
#
# We store the values to indicate ALL conflicts to resolve.
        if 1 != len(
            set(n for n, _ in id_2_nsn.values())
        ):
            same_pal_diff_names.append(
                list(id_2_nsn.values())
            )

            continue

# Identical palettes and same name.
        else:
            dp_update_full_equal_pals(conn, id_2_nsn)

# -- PB! Different names / Same palette -- #
report_or_not_difname_samepal(same_pal_diff_names)


# --------------------- #
# -- MIRROR PALETTES -- #
# --------------------- #

logging.info("Analyze data - 'Looking for mirror palettes'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_MIRROR)

    for x in cursor.fetchall():
        print(x)


exit(1)


# ------------------- #
# -- WHAT IS KEPT? -- #
# ------------------- #


# --  PALETTES -- #

for mirror_pals in PALS_SAME[TAG_MIRROR]:
    pal_1, pal_2 = [
        extract_name_n_srcname(uid)
        for uid in mirror_pals
    ]

    pal_alias_1 = EQUALS.get(pal_1, pal_1)
    pal_alias_2 = EQUALS.get(pal_2, pal_2)

# Palette #1 takes precedence.
    if (
        (-PRIORITY[pal_alias_1[1]], pal_alias_1[0])
        <
        (-PRIORITY[pal_alias_2[1]], pal_alias_2[0])
    ):
        MIRRORS[pal_alias_2] = pal_alias_1

# Palette #2 takes precedence.
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

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_NAME_CONFLICT)

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
    cursor.execute(SQL_CREATE_FINAL_DB)


# ----------------- #
# -- POPULATE DB -- #
# ----------------- #

logging.info(f"DATA cleaning - Final SQLite DB - 'Populate table'.")

already_kept = set()


with (
    sqlite3.connect(SQLITE_DB_FILE) as full_conn,
    sqlite3.connect(FINAL_SQLITE_DB_FILE) as final_conn,
):
    full_cursor  = full_conn.cursor()
    final_cursor = final_conn.cursor()

    full_cursor.execute(SQL_EXTRACT_FOR_FINAL)

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
            SQL_INSERT_IN_FINAL,
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
