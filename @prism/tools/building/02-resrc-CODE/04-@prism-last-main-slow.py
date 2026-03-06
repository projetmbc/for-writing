#!/usr/bin/env python3

# --------------------------- #
# -- UPDATE NEEDED - START -- #

from json    import load as json_load
from pathlib import Path

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

THIS_RESRC = 'aprism'.upper()

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


RESRC_DIR = PROJ_DIR / TAG_RESOURCES / TAG_APRISM_LAST_MAIN
RESRC_DIR.mkdir(
    parents  = True,
    exist_ok = True,
)


# ----------------------- #
# -- EMPTY SOURCE CODE -- #
# ----------------------- #

logging.info(f"Empty '{THIS_RESRC}' folder")

if RESRC_DIR.is_dir():
    rmtree(RESRC_DIR)

RESRC_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


# -------------------------- #
# -- DOWNLOAD SOURCE CODE -- #
# -------------------------- #

logging.info(f"Download '{THIS_RESRC}' source code")

download_and_unzip(
    log_raise_error = log_raise_error,
    url             = SRC_URLS[THIS_RESRC],
    extract_to      = RESRC_DIR / "temp",
)


# ----------------------- #
# -- CLEAN SOURCE CODE -- #
# ----------------------- #

logging.info(f"Clean '{THIS_RESRC}' folder")

clean_src_files(
    local_src_dir = RESRC_DIR / "temp",
    globs_kept    = [
        "**/products/json/palettes-hf/*.json",
    ],
)
