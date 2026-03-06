#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
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


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

SQL_INSERT_ALIAS = '''
INSERT INTO alias (
    pal_id,
    alias
) VALUES ({placeholders})
'''

SQL_GET_PAL_ID = """
SELECT
    pal_id
FROM hash
WHERE name = ?
  AND source = ?
"""


SQL_INSERT_SUFFIX = '''
INSERT INTO suffix (
    source,
    suffix
) VALUES (?, ?)
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

RENAMED_YAML = AUDIT_DIR / 'RENAMED.yaml'
RENAMED_YAML.touch()

with RENAMED_YAML.open(mode = 'r') as f:
    RENAMED = yaml.safe_load(f)


if '_SUFFIXES_' in RENAMED:
    SUFFIXES = RENAMED['_SUFFIXES_']

    del RENAMED['_SUFFIXES_']

else:
    SUFFIXES = dict()


# ----------- #
# -- TOOLS -- #
# ----------- #

def dbadd_aliaspals(
    conn,
    pal_id: int,
    alias : str
) -> None:
    placeholders = ['?']*(len(locals()) - 1)
    placeholders = ','.join(placeholders)

    try:
        cursor = conn.cursor()

        cursor.execute(
            SQL_INSERT_ALIAS.format(
                placeholders = placeholders
            ),
            (
                pal_id,
                alias
            )
        )

        conn.commit()

    except Exception:
        conn.close()

        log_raise_error(
            context   = "Alias DB.",
            desc      = f"Insertion fails for '{alias}'.",
            exception = Exception,
        )


# ----------- #
# -- ALIAS -- #
# ----------- #

if not RENAMED:
    logging.info("DB - Alias - No alias")

    exit(0)


logging.info("DB - Alias - 'Populate'")

suffixes_used = set()

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for nsn, (alias, suffix) in get_pal_alias(
        SUFFIXES,
        RENAMED
    ).items():
        if suffix:
            suffixes_used.add(suffix)

        cursor.execute(
            SQL_GET_PAL_ID,
            (*nsn,)
        )

        pal_id = cursor.fetchall()[0][0]

        dbadd_aliaspals(
            conn   = conn,
            pal_id = pal_id,
            alias  = alias,
        )


# -------------- #
# -- SUFFIXES -- #
# -------------- #

if suffixes_used:
    logging.info("DB - Suffixes used - 'Populate'")

    with sqlite3.connect(SQLITE_DB_FILE) as conn:
        cursor = conn.cursor()

        for src, suffix in SUFFIXES.items():
            if suffix in suffixes_used:
                cursor.execute(
                    SQL_INSERT_SUFFIX,
                    (src, suffix)
                )
