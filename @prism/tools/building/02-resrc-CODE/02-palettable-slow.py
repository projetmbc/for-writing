#!/usr/bin/env python3

# --------------------------- #
# -- UPDATE NEEDED - START -- #

from json    import load as json_load
from pathlib import Path

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[1]
THIS_RESRC = THIS_RESRC.upper()

UPDATES_NEEDED_JSON = BUILD_TOOLS_DIR /  "UPDATES" / "NEEDED.json"

with UPDATES_NEEDED_JSON.open(mode = "r") as f:
    UPDATES_NEEDED = json_load(f)


if not UPDATES_NEEDED[THIS_RESRC]:
    exit(0)

# -- UPDATE NEEDED - END -- #
# ------------------------- #


# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

import sys

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from shutil import rmtree


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent


RESRC_DIR = PROJ_DIR / TAG_RESOURCES / THIS_RESRC
RESRC_DIR.mkdir(
    parents  = True,
    exist_ok = True,
)


# ----------------------- #
# -- EMPTY SOURCE CODE -- #
# ----------------------- #

logging.info(f"Folder - Empty '{THIS_RESRC}'")

if RESRC_DIR.is_dir():
    rmtree(RESRC_DIR)

RESRC_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


# -------------------------- #
# -- DOWNLOAD SOURCE CODE -- #
# -------------------------- #

logging.info(
    f"Source - Download '{RESRC_ALIAS[THIS_RESRC]}'"
)

download_and_unzip(
    log_raise_error = log_raise_error,
    url             = SRC_URLS[THIS_RESRC],
    extract_to      = RESRC_DIR,
)


# ----------------------- #
# -- CLEAN SOURCE CODE -- #
# ----------------------- #

logging.info(f"Folder - Clean '{THIS_RESRC}'")

for p in RESRC_DIR.glob("*/license.txt"):
    p.rename(RESRC_DIR / p.name)

clean_src_dirs(
    local_src_dir = RESRC_DIR / "palettable-master",
    globs_kept    = [
        f"palettable/{n}/*.py"
        for n in [
            "tableau",
            "wesanderson",
            "plotly",
            "mycarta",
            "lightbartlein",
            "cubehelix",
            "cmocean",
        ]
    ],
)


for p in RESRC_DIR.glob("*/__init__.py"):
    p.unlink()
