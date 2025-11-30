#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from shutil import rmtree


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR = PROJ_DIR / "products"


# --------------------------- #
# -- EMPTY PRODUCTS FOLDER -- #
# --------------------------- #

logging.info("Empty 'product' folder.")

if not PRODS_DIR.is_dir():
    PRODS_DIR.mkdir()

else:
    for p in PRODS_DIR.glob("*"):
        p.unlink() if p.is_file() else rmtree(p)
