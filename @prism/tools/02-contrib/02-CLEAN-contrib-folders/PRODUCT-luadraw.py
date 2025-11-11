#!/usr/bin/env python3

from pathlib import Path
import              sys

TOOLS_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(TOOLS_DIR))

from cbutils.core import *

from shutil import rmtree


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR.parent.parent.parent

CONTRIB_LUADRAW_DIR = (
    PROJ_DIR / "contrib" / "products" / "luadraw" / "dev"
)


# --------------------------------- #
# -- EMPTY CONTRIB PRODUCT FOLDER -- #
# --------------------------------- #

relpath = CONTRIB_LUADRAW_DIR.relative_to(PROJ_DIR)

logging.info(f"Clean '{relpath}' folder.")

for p in CONTRIB_LUADRAW_DIR.glob("*.pdf"):
    p.unlink()

for p in CONTRIB_LUADRAW_DIR.glob("*.lua"):
    p.unlink()
