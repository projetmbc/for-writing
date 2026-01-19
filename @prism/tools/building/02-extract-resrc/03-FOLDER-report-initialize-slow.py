#!/usr/bin/env python3

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

from shutil  import rmtree


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = Path(__file__).parent

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


# ----------------------------- #
# -- EMPTY THE REPORT FOLDER -- #
# ----------------------------- #

logging.info(f"Empty 'REPORT' folder")

if REPORT_DIR.is_dir():
    rmtree(REPORT_DIR)

REPORT_DIR.mkdir(
    parents  = True,
    exist_ok = True
)
