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

PATTERN_SQL_CREATE_TABLE = re.compile(
    r"CREATE TABLE.*?\);",
    re.DOTALL | re.IGNORECASE
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE    = AUDIT_DIR / "palettes.db"
AUDIT_DB_VIEW_TXT = AUDIT_DIR / "DB-VIEW.txt"
AUDIT_DB_VIEW_DOT = AUDIT_DIR / "DB-VIEW.dot"
AUDIT_DB_VIEW_PNG = AUDIT_DIR / "DB-VIEW.png"


# -------------------------------- #
# -- GATHER SQL TABLE CREATIONS -- #
# -------------------------------- #

logging.info("DB diagram - 'Gather table creation codes'")

_sql_full_code = []

for pyfile in BUILD_TOOLS_DIR.glob("*-final-data/*DB-init*.py"):
    logging.info(
        f"Analyze '{pyfile.relative_to(PROJ_DIR)}'"
    )

    pycode = pyfile.read_text()

    _sql_full_code += PATTERN_SQL_CREATE_TABLE.findall(pycode)


sql_full_code = ''

for i, block in enumerate(_sql_full_code, start = 1):
    title = f"TABLE #{i}"
    deco  = '-'*(len(title) + 6)

    sql_full_code += f"\n\n\n{deco}\n-- {title} --\n{deco}\n\n{block}"

sql_full_code = sql_full_code.strip() + '\n'


# -------------- #
# -- TXT FILE -- #
# -------------- #

logging.info(f"Update '{AUDIT_DB_VIEW_TXT.relative_to(PROJ_DIR)}'")

AUDIT_DB_VIEW_TXT.write_text(sql_full_code)


# ---------------- #
# -- DB DIAGRAM -- #
# ---------------- #

logging.info("Update 'PNG file'")

render_er(
    f"sqlite:///{SQLITE_DB_FILE}",
    str(AUDIT_DB_VIEW_PNG)
)
