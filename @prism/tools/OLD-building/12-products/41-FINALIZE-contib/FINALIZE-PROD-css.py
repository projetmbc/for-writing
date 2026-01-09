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

from json import load  as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR = PROJ_DIR / "products"


PAL_SPECS_JS_FILE = PRODS_DIR / "css" / "showcase" / "core" / "palettes.js"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


# ------------------- #
# -- PALETTE SPECS -- #
# ------------------- #

logging.info(f"Finalize 'css' product.")

pal_specs = {
    n: len(c)
    for n, c in ALL_PALETTES.items()
}

js_code = f"const palsize = {repr(pal_specs)};"

for old, new in [
    ("'", '"'),
    (', ', ',\n  '),
    ('{"', '{\n  "'),
    ("};", '\n};\n'),
]:
    js_code = js_code.replace(old, new)

PAL_SPECS_JS_FILE.write_text(js_code)
