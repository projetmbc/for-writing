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


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_LUADRAW_DIR = (
    PROJ_DIR / "contrib" / "products" / "lua" / "dev" / "luadraw"
)


# ------------------------------- #
# -- EMPTY CONTRIB PROD FOLDER -- #
# ------------------------------- #

relpath = CONTRIB_LUADRAW_DIR.relative_to(PROJ_DIR)

logging.info(f"Clean '{relpath}' folder.")

for p in CONTRIB_LUADRAW_DIR.glob("*.pdf"):
    p.unlink()

for p in CONTRIB_LUADRAW_DIR.glob("*.lua"):
    p.unlink()
