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

THIS_DIR          = Path(__file__).parent
PROJ_DIR          = THIS_DIR.parent.parent
SCICOLMAP_SRC_DIR = PROJ_DIR / "x-ScientificColourMaps8-x"


# --------------------------------- #
# -- CLEANING SOURCE CODE FOLDER -- #
# --------------------------------- #

logging.info("Cleaning 'Scientific Colour Maps' source folder.")

if not SCICOLMAP_SRC_DIR.is_dir():
    logging.warning("Empty 'Scientific Colour Maps' source folder.")

    exit(0)

for p in SCICOLMAP_SRC_DIR.glob("*"):
    if p.name.startswith('+') and p.is_dir():
        rmtree(p)


for p in SCICOLMAP_SRC_DIR.glob("*"):
    if p.is_file():
        p.unlink()
        continue

    for sp in p.glob("*"):
        if sp.is_dir():
            rmtree(sp)

        elif sp.suffix != '.py':
            sp.unlink()
