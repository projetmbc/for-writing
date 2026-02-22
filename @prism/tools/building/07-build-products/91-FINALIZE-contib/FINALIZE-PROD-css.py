#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from json import load  as json_load

from natsort import (
    natsorted,
    ns
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR    = PROJ_DIR / "products"
PAL_JSON_DIR = PRODS_DIR / "json" / "palettes-hf"


JS_PAL_SIZES_FILE = PRODS_DIR / "css" / "showcase" / "core" / "palsizes.js"


# ------------------- #
# -- PALETTE SPECS -- #
# ------------------- #

logging.info(f"Finalize 'css' product")

palsizes = dict()

for paljson in natsorted(
    PAL_JSON_DIR.glob('*.json'),
    alg = ns.IGNORECASE
):
    with paljson.open(mode = "r") as f:
        palsize = len(json_load(f))

    palsizes[paljson.stem] = palsize


js_code = f"const palsize = {repr(palsizes)};"

for old, new in [
    ("'", '"'),
    (', ', ',\n  '),
    ('{"', '{\n  "'),
    ("};", '\n};\n'),
]:
    js_code = js_code.replace(old, new)

# Alphabet comments
_js_code    = []
last_letter = ''

for line in js_code.splitlines():
    if line.startswith('  "'):
        letter = line[3]

        if letter != last_letter:
            _js_code.append(f'// -- {letter} -- //')

            last_letter = letter

    _js_code.append(line)

js_code = '\n'.join(_js_code)

JS_PAL_SIZES_FILE.write_text(js_code)
