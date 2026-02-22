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

from eralchemy2 import render_er



# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

DB_INIT_PY_FILE = THIS_DIR / '02-a-DB-init-tables.py'


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

AUDIT_DB_VIEW_TXT = AUDIT_DIR / "DB-VIEW.txt"
AUDIT_DB_VIEW_PNG = AUDIT_DIR / "DB-VIEW.png"


# -------------------------------- #
# -- GATHER SQL TABLE CREATIONS -- #
# -------------------------------- #

logging.info("DB diagram - 'Get creation code'")

code = DB_INIT_PY_FILE.read_text()

_ , _ , code = code.partition("SQL_TABLE_CREATE = '''")
code, _ , _  = code.partition("'''")

code = code.strip() + '\n'


# -------------- #
# -- TXT FILE -- #
# -------------- #

logging.info(f"Update '{AUDIT_DB_VIEW_TXT.relative_to(PROJ_DIR)}'")

AUDIT_DB_VIEW_TXT.write_text(code)


# ---------------- #
# -- DB DIAGRAM -- #
# ---------------- #

logging.info("Update 'PNG file'")

render_er(
    f"sqlite:///{SQLITE_DB_FILE}",
    str(AUDIT_DB_VIEW_PNG)
)
