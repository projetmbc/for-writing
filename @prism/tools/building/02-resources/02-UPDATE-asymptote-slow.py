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

THIS_RESRC = TAG_ASYMPTOTE


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


THIS_RESRC_DIR = PROJ_DIR / "EXTRA-RESOURCES" / stdname(THIS_RESRC)


UPDATES_NEEDED_JSON =  THIS_DIR.parent / "REPORT" / "UPDATES_NEEDED.json"

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

THIS_RESRC_DIR /= "asymptote-master"

for p in THIS_RESRC_DIR.glob("*"):
    if p.is_dir():
        if p.name != "base":
            rmtree(p)

    elif not p.name in [
        "LICENSE",
    ]:
        p.unlink()

    else:
        p.rename(p.parent.parent / p.name)


THIS_RESRC_DIR /= "base"

for p in THIS_RESRC_DIR.glob("*"):
    if p.is_dir():
        rmtree(p)

    elif not p.name in [
        "colormap.asy",
    ]:
        p.unlink()

    else:
        p.rename(p.parent.parent.parent / p.name)


rmtree(THIS_RESRC_DIR.parent)
