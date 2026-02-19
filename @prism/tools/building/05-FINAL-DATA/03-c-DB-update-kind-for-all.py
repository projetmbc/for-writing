#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

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

from yaml import (
    safe_load,
    dump as yaml_dump
)


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

# WARNING! Since name conflicts are resolved by the previous script,
# we can work with palette names and sources directly.

SQL_UPDATE_KIND = '''
UPDATE hash
SET kind = CASE WHEN kind = ''
    THEN '{kind}'
    ELSE kind || ', ' || '{kind}'
END
WHERE name = '{name}' AND source = '{source}'
'''


SQL_GET_NO_KIND = '''
SELECT
    h.name,
    h.source
FROM hash h
WHERE h.kind = ''
  AND h.is_kept = 1;
'''


SQL_RESOLVE_EMPTY_KIND = '''
SELECT
    p1.name,
    p1.source,
    (
        SELECT GROUP_CONCAT(p2.kind, ',')
        FROM hash p2
        WHERE p2.kind != ''
          AND (
              p2.equal_to = p1.pal_id
              OR
              EXISTS (
                  SELECT 1 FROM mirror m
                  WHERE (
                      m.cand_pal_id_1 = p1.pal_id
                      AND
                      m.cand_pal_id_2 = p2.pal_id
                  ) OR (
                      m.cand_pal_id_1 = p2.pal_id
                      AND
                      m.cand_pal_id_2 = p1.pal_id
                  )
              )
          )
    ) AS all_kinds
FROM hash p1
WHERE p1.kind = ''
  AND p1.is_kept = 1;
'''


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

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

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

MISSING_KIND_JSON = REPORT_DIR / "AUDIT-MISSING-KIND.json"

MISSING_KINDS = []


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_std_kind(kind):
    _kind = sorted(
        list(
            set(
                k.strip()
                for k in kind.split(',')
                if k.strip()
            )
        )
    )

    return ','.join(_kind)


# --------------------- #
# -- HUMAN KINDS :-) -- #
# --------------------- #

logging.info("DB - Kinding ;-) 'Add human kinds' :-)")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for src, namekinds in HUMAN_KIND.items():
        for name, kind in namekinds.items():
            query = SQL_UPDATE_KIND.format(
                name   = name,
                kind   = get_std_kind(kind),
                source = src
            )

            cursor.execute(query)


# -------------- #
# -- DB KINDS -- #
# -------------- #

logging.info("DB - Kinding ;-) 'DB missing kind resolution'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_RESOLVE_EMPTY_KIND)

    for name, src, kind in cursor.fetchall():
# No matches found.
        if kind is None:
            continue

# At least one match found.
        kind = get_std_kind(kind)

        logging.info(f"'{name}' [{src}] is '{kind}'")

        query = SQL_UPDATE_KIND.format(
            name  = name,
            kind  = kind,
            source = src
        )

        cursor.execute(query)


# ------------------- #
# -- MISSING KINDS -- #
# ------------------- #

logging.info("DB - Kinding ;-) 'Unresolved missing kinds'?")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_GET_NO_KIND)

    MISSING_KINDS.extend([
        list(x) for x in cursor.fetchall()
    ])


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(
    f"DB - Kinding ;-) Update '{MISSING_KIND_JSON.relative_to(PROJ_DIR)}'"
)

MISSING_KIND_JSON.write_text(
    json_dumps(MISSING_KINDS)
)


# ------------------------- #
# -- MISSING KINDS FOUND -- #
# ------------------------- #

if not MISSING_KINDS:
    logging.info(
    f"DB - Kinding ;-) No problem!"
)

else:
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
