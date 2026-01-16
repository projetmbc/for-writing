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

from yaml import (
    safe_load,
    dump as yaml_dump
)


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

SQL_GET_NO_KIND = '''
SELECT
    name, source
FROM palettes
WHERE kind = ''
  AND is_kept = 1
'''

SQL_RESOLVE_EMPTY_KIND = '''
SELECT
    p1.name,
    (
        SELECT GROUP_CONCAT(p2.kind, ',')
        FROM palettes p2
        WHERE p2.kind != ''
          AND (p2.equal_to = p1.id
            OR p2.mirror_of = p1.id)
    ) AS all_kinds
FROM palettes p1
WHERE p1.kind = ''
  AND p1.is_kept = 1
'''


SQL_UPDATE_KIND = '''
UPDATE palettes
SET kind = CASE
    WHEN kind = '' THEN
        '{kind}'
    ELSE kind || ', ' || '{kind}'
END
WHERE is_kept = 1
  AND name = '{name}'
'''


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT
AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT


SQLITE_DB_FILE  = AUDIT_DIR / "palettes.db"


HUMAN_KIND_YAML = AUDIT_DIR / 'HUMAN-KIND.yaml'

if HUMAN_KIND_YAML.is_file():
    with HUMAN_KIND_YAML.open('r') as f:
        HUMAN_KIND = safe_load(f)

    if HUMAN_KIND is None:
        HUMAN_KIND = dict()

else:
    HUMAN_KIND_YAML.touch()

    HUMAN_KIND = dict()


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

MISSING_KIND_JSON = REPORT_DIR / "AUDIT-MISSING-KIND.json"


def get_std_kind(kind):
    _kind = [
        k.strip()
        for k in kind.split(',')
        if k.strip()
    ]

    return ','.join(_kind)


# --------------------- #
# -- HUMAN KINDS :-) -- #
# --------------------- #

logging.info(f"KINDS - 'Add human kinds'. :-)")


with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for name, kind in HUMAN_KIND.items():
        query = SQL_UPDATE_KIND.format(
            name = name,
            kind = get_std_kind(kind),
        )

        cursor.execute(query)


# -------------- #
# -- DB KINDS -- #
# -------------- #

logging.info(f"KINDS - 'DB missing kind resolution'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_RESOLVE_EMPTY_KIND)

    for name, kind in cursor.fetchall():
        if kind is None:
            continue

        query = SQL_UPDATE_KIND.format(
            name = name,
            kind = get_std_kind(kind),
        )

        cursor.execute(query)


# ------------------- #
# -- MISSING KINDS -- #
# ------------------- #

logging.info(f"KINDS - 'Unresolved missing kinds'?")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_GET_NO_KIND)

    for name, source in cursor.fetchall():
        print(name, source)


exit()




# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(
    f"KINDS - Update '{MISSING_KIND_JSON.relative_to(PROJ_DIR)}'."
)

MISSING_KIND_JSON.write_text(
    json_dumps(MISSING_KINDS)
)


# ------------------------- #
# -- MISSING KINDS FOUND -- #
# ------------------------- #

if MISSING_KINDS:
    nb = len(MISSING_KINDS)

    plurial = '' if nb == 1 else 's'

    reslover = PROJ_DIR / "tools" / "lab" / "resolve" / "missing-kinds.py"

    log_raise_error(
        context   = f"{nb} missing kind{plurial} need NOAI resolution",
        desc      = "Palettes need to have at least one kind.",
        exception = ValueError,
        xtra      = (
            f'Use:\n---\nstreamlit run "{reslover}"\n---')
    )
