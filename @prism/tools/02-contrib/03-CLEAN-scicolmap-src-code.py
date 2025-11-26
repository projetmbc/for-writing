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

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR.parent.parent

CODE_NAME = "Scientific Colour Maps"
SRC_DIR   = PROJ_DIR / "resources" / CODE_NAME.replace(' ', '') / "ScientificColourMaps8"


# ----------------------- #
# -- CLEAN SOURCE CODE -- #
# ----------------------- #

logging.info(f"Cleaning '{CODE_NAME}' source folder.")


if not SRC_DIR.is_dir():
    logging.warning(f"Empty '{CODE_NAME}' source folder.")

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
