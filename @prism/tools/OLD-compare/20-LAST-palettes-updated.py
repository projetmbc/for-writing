#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR.parent

while PROJ_DIR.name != "@prism":
    PROJ_DIR = PROJ_DIR.parent

TOOLS_DIR = PROJ_DIR / "tools" / "building"

sys.path.append(str(TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# --------------- #
# -- CONSTANTS -- #
# --------------- #

JSON_PROD_DIR = PROJ_DIR / "products" / "json"
DATA_DIR      = THIS_DIR / "data"

LAST_PALETTES_JSON = DATA_DIR / f"LAST_PALETTES.json"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

DEV_PALETTES_JSON = JSON_PROD_DIR / f"palettes.json"

with DEV_PALETTES_JSON.open() as f:
    DEV_PALETTES = json_load(f)


# ------------------------------------ #
# -- UPDATE LAST PALETTES JSON FILE -- #
# ------------------------------------ #

logging.info("Build new 'last palettes'.")

LAST_PALETTES_JSON.write_text(
    json_dumps(DEV_PALETTES)
)
