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
DROP TABLE IF EXISTS priority;
CREATE TABLE priority (
--
    source   VARCHAR(30) NOT NULL PRIMARY KEY,
    priority INTEGER NOT NULL,
--
    FOREIGN KEY (source) REFERENCES hash (source)
)
'''

SQL_TABLE_INSERT = '''
INSERT INTO priority (
    source,
    priority
) VALUES ({placeholders})
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PRIORITY  = YAML_CONFIGS['PRIORITY']


# -------------- #
# -- TOOLS #2 -- #
# -------------- #

def dbadd_hashpals(
    conn,
    source      : str,
    priority    : str,
) -> None:
    placeholders = ['?']*(len(locals()) - 1)
    placeholders = ','.join(placeholders)

    try:
        cursor = conn.cursor()

        cursor.execute(
            SQL_TABLE_INSERT.format(
                placeholders = placeholders
            ),
            (source, priority)
        )

        conn.commit()

    except Exception:
        conn.close()

        log_raise_error(
            context   = "Priority DB.",
            desc      = f"Insertion fails for '[{source}] {name}'.",
            exception = Exception,
        )


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info("Priority DB - 'Init table'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.executescript(SQL_TABLE_CREATE)


# --------------------- #
# -- PRIORITY SOURCE -- #
# --------------------- #

logging.info("Priority DB - 'Populate'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    for resrc_json in REPORT_DIR.glob("*.json"):
        src = resrc_json.stem

        if (
            src.startswith('KIND-')
            or
            src.startswith('AUDIT-')
        ):
            continue

        logging.info(f"Add '{resrc_json.relative_to(REPORT_DIR).stem}'")

        dbadd_hashpals(
            conn     = conn,
            priority = PRIORITY[src],
            source   = src,
        )
