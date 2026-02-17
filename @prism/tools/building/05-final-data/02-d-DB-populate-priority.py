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


# --------------------- #
# -- PRIORITY SOURCE -- #
# --------------------- #

logging.info("DB - Priority - 'Populate'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    for resrc_json in sorted(REPORT_DIR.glob("*.json")):
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
