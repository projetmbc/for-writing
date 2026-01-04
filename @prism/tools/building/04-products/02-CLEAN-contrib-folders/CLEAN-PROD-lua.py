#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from shutil import rmtree


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

COMMON_EXTS = [
    "pdf",
] + LATEX_TEMP_EXT

FILE_GLOB_BY_DIRS = {
    'dev': [
        f"*/*.{ext}"
        for ext in [
            "lua",
            "sty",
        ] + COMMON_EXTS
    ],
    'fake-prod/showcase': [
        f"*/*.{ext}"
        for ext in COMMON_EXTS
    ],
}


COMMON_FOLDER = [
    "_*",
]

FOLDER_GLOB_BY_DIRS = {
    'dev': [
        f"*/{g}"
        for g in COMMON_FOLDER
    ],
    'fake-prod/showcase': [
        f"*/{g}"
        for g in COMMON_FOLDER
    ],
}


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PROD_DIR = (
    PROJ_DIR / "contrib" / "products" / "lua"
)


# ------------------------------- #
# -- CLEAN CONTRIB PROD FOLDER -- #
# ------------------------------- #

relpath = CONTRIB_PROD_DIR.relative_to(PROJ_DIR)


logging.info(f"Clean 'files in {relpath}' folder.")

for subdir, patterns in FILE_GLOB_BY_DIRS.items():
    subpath = CONTRIB_PROD_DIR

    for p in subdir.split('/'):
        subpath /= p

    for g in patterns:
        for f in subpath.glob(g):
            if f.is_file():
                f.unlink()


logging.info(f"Clean 'dirs in {relpath}' folder.")

for subdir, patterns in FOLDER_GLOB_BY_DIRS.items():
    subpath = CONTRIB_PROD_DIR

    for p in subdir.split('/'):
        subpath /= p

    for g in patterns:
        for d in subpath.glob(g):
            if d.is_dir():
                rmtree(d)
