#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from shutil import rmtree


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_RESRC = TAG_PALETTABLE


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


THIS_RESRC_DIR = PROJ_DIR / TAG_XTRA_RESRC / stdname(THIS_RESRC)


UPDATES_NEEDED_JSON =  THIS_DIR.parent /  "UPDATES" / "NEEDED.json"

with UPDATES_NEEDED_JSON.open(mode = "r") as f:
    UPDATES_NEEDED = json_load(f)


# ---------------------- #
# -- SOMETHING TO DO? -- #
# ---------------------- #

if not UPDATES_NEEDED[THIS_RESRC]:
    logging.info(f"'{THIS_RESRC}' - No update.")

    exit(0)


# ----------------------- #
# -- EMPTY SOURCE CODE -- #
# ----------------------- #

logging.info(f"Empty '{THIS_RESRC}' folder.")

if THIS_RESRC_DIR.is_dir():
    rmtree(THIS_RESRC_DIR)

THIS_RESRC_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


# -------------------------- #
# -- DOWNLOAD SOURCE CODE -- #
# -------------------------- #

logging.info(f"Downloading '{THIS_RESRC}' source code.")

download_and_unzip(
    log_raise_error = log_raise_error,
    url             = SRC_URLS[THIS_RESRC],
    extract_to      = THIS_RESRC_DIR,
)


# ----------------------- #
# -- CLEAN SOURCE CODE -- #
# ----------------------- #

logging.info(f"Cleaning '{THIS_RESRC}' folder.")


for p in THIS_RESRC_DIR.glob("*/license.txt"):
    p.rename(THIS_RESRC_DIR / p.name)


clean_src_dirs(
    local_src_dir = THIS_RESRC_DIR / "palettable-master",
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


for p in THIS_RESRC_DIR.glob("*/__init__.py"):
    p.unlink()
