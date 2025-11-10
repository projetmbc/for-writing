#!/usr/bin/env python3

from pathlib import Path
import              sys

TOOLS_DIR = Path(__file__).parent.parent
sys.path.append(str(TOOLS_DIR))

from cbutils.core import *

from shutil import rmtree


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR  = Path(__file__).parent
PROJ_DIR  = THIS_DIR.parent.parent
PRODS_DIR = PROJ_DIR / "products"


# --------------------------------- #
# -- EMPTY PRODUCTS FOLDER EMPTY -- #
# --------------------------------- #

logging.info("Empty 'product' folder.")

if not PRODS_DIR.is_dir():
    PRODS_DIR.mkdir()

else:
    for p in PRODS_DIR.glob("*"):
        p.unlink() if p.is_file() else rmtree(p)
