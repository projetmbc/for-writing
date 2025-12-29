#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent.parent

sys.path.append(str(BUILD_TOOLS_DIR))


from cbutils.core import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from shutil import rmtree


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

GLOB_BY_DIRS = {
    'dev': [
        "*/*.pdf",
        "*/*.lua",
        "*/*.sty",
    ],
    'fake-prod/showcase': [
        "*/*.pdf",
    ],
}


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PROD_DIR = (
    PROJ_DIR / "contrib" / "products" / "lua"
)


# ------------------------------- #
# -- CLEAN CONTRIB PROD FOLDER -- #
# ------------------------------- #

relpath = CONTRIB_PROD_DIR.relative_to(PROJ_DIR)

logging.info(f"Clean '{relpath}' folder.")

for subdir, patterns in GLOB_BY_DIRS.items():
    subpath = CONTRIB_PROD_DIR

    for p in subdir.split('/'):
        subpath /= p

        for g in patterns:
            for f in subpath.glob(g):
                f.unlink()
