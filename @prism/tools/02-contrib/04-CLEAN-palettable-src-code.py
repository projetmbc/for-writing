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

CODE_NAME = "Palettable"
SRC_DIR   = PROJ_DIR / "resources" / CODE_NAME / "palettable-master"


# ----------------------- #
# -- CLEAN SOURCE CODE -- #
# ----------------------- #

logging.info(f"Cleaning '{CODE_NAME}' source folder.")


if not SRC_DIR.is_dir():
    logging.warning(f"Empty '{CODE_NAME}' source folder.")

    exit(0)


for p in SRC_DIR.glob("*"):
    if p.is_dir():
        if p.name != "palettable":
            rmtree(p)

    else:
        p.unlink()


to_ignore = [
    "colorbrewer",
    "matplotlib",
    "scientific",   # Scientific Colour Maps
    "test",
]

for p in SRC_DIR.glob("*/*"):
    if p.is_dir():
        if p.name in to_ignore:
            rmtree(p)

    else:
        p.unlink()


for p in SRC_DIR.glob("*/*/*"):
    if p.is_dir() and p.name == "test":
        rmtree(p)

    elif p.name == "__init__.py":
        p.unlink()


for p in SRC_DIR.glob("*/*/*"):
    if p.is_dir():
        print(p.name)
