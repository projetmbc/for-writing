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

CODE_NAME = "Scientific Colour Maps"
SRC_DIR   = PROJ_DIR / "resources" / CODE_NAME.replace(' ', '') / "ScientificColourMaps8"


# ----------------------- #
# -- CLEAN SOURCE CODE -- #
# ----------------------- #

logging.info(f"Resource - Cleaning '{CODE_NAME}' folder.")


if not SRC_DIR.is_dir():
    logging.warning(f"Empty '{CODE_NAME}' folder.")

    exit(0)


for p in SRC_DIR.glob("*"):
    if p.is_file():
        p.unlink()

    elif p.name.startswith('+'):
        rmtree(p)

    else:
        for sp in p.glob("*"):
            if sp.is_dir():
                rmtree(sp)

            elif sp.suffix != '.py':
                sp.unlink()
