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


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

SQL_TABLE_CREATE = '''
DROP TABLE IF EXISTS mirror;
CREATE TABLE mirror (
--
    cand_pal_id_1 INTEGER NOT NULL,
    cand_pal_id_2 INTEGER NOT NULL,
--
    PRIMARY KEY (cand_pal_id_1, cand_pal_id_2),
    CHECK (cand_pal_id_1 < cand_pal_id_2),
--
    FOREIGN KEY (cand_pal_id_1) REFERENCES hash (pal_id),
    FOREIGN KEY (cand_pal_id_2) REFERENCES hash (pal_id)
)
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info("Mirror DB - 'Init table' (nothing else done here)")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.executescript(SQL_TABLE_CREATE)
