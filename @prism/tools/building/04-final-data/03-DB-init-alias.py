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

SQL_TABLE_CREATE = '''
DROP TABLE IF EXISTS alias;
CREATE TABLE alias (
--
    pal_id   INTEGER NOT NULL PRIMARY KEY,
    alias    VARCHAR(30) NOT NULL,
--
    FOREIGN KEY (pal_id) REFERENCES hash (pal_id)
)
'''

SQL_TABLE_INSERT = '''
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
            SQL_TABLE_INSERT.format(
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


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info("Alias DB - 'Init table'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.executescript(SQL_TABLE_CREATE)


if not RENAMED:
    logging.info("Alias DB - No alias")

    exit(0)


# ----------- #
# -- ALIAS -- #
# ----------- #

logging.info("Alias DB - 'Populate'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for nsn, alias in get_pal_alias(RENAMED).items():
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
