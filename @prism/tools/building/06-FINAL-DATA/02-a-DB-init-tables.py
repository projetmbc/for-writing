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
----------------
-- MAIN TABLE --
----------------

DROP TABLE IF EXISTS hash;
CREATE TABLE hash (
--
    pal_id INTEGER PRIMARY KEY,
    name   VARCHAR(30) NOT NULL,
    source VARCHAR(30) NOT NULL,
--
    is_kept  INTEGER DEFAULT 1,
    equal_to INTEGER REFERENCES hash(pal_id),
    catego   TEXT DEFAULT '',
--
    hash_normal  TEXT NOT NULL,
    hash_reverse TEXT NOT NULL
);


----------------
-- SUB TABLES --
----------------

DROP TABLE IF EXISTS alias;
CREATE TABLE alias (
--
    pal_id INTEGER NOT NULL PRIMARY KEY,
    alias  VARCHAR(30) NOT NULL,
--
    FOREIGN KEY (pal_id) REFERENCES hash (pal_id)
);


DROP TABLE IF EXISTS priority;
CREATE TABLE priority (
--
    source   VARCHAR(30) NOT NULL PRIMARY KEY,
    priority INTEGER NOT NULL,
--
    FOREIGN KEY (source) REFERENCES hash (source)
);


DROP TABLE IF EXISTS mirror;
CREATE TABLE mirror (
--
    pal_id_1 INTEGER NOT NULL,
    pal_id_2 INTEGER NOT NULL,
--
    PRIMARY KEY (pal_id_1, pal_id_2),
    CHECK (pal_id_1 < pal_id_2),
--
    FOREIGN KEY (pal_id_1) REFERENCES hash (pal_id),
    FOREIGN KEY (pal_id_2) REFERENCES hash (pal_id)
);

DROP TABLE IF EXISTS suffix;
CREATE TABLE suffix (
--
    source VARCHAR(30) NOT NULL PRIMARY KEY,
    suffix VARCHAR(30),
--
    FOREIGN KEY (source) REFERENCES hash (source)
);
'''

# --------------- #
# -- CONSTANTS -- #
# --------------- #

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

if SQLITE_DB_FILE.is_file():
    SQLITE_DB_FILE.unlink()


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info("DB - 'Init all tables'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.executescript(SQL_TABLE_CREATE)
