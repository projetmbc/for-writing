#!/usr/bin/env python3

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(TOOLS_DIR))

from cbutils.core import *
from cbutils      import *


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = TOOLS_DIR.parent

CODE_NAME = "Colorbrewer"
SRC_JSON  = PROJ_DIR / "resources" / CODE_NAME / f"{CODE_NAME.lower()}.json"


# ----------------------- #
# -- CLEAN SOURCE CODE -- #
# ----------------------- #

logging.info(f"Resource - Cleaning '{CODE_NAME}' JSON file.")

with SRC_JSON.open(mode = "r") as f:
    palettes = json_load(f)

json_code = json_dumps(
    obj       = palettes,
    indent    = 2,
    sort_keys = True,
)

SRC_JSON.write_text(json_code)
