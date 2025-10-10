#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
PRODUCTS_DIR = THIS_DIR.parent.parent / "products"

PALETTES_JSON_FILE = PRODUCTS_DIR / "palettes.json"


# ------------------ #
# -- NAME SORTING -- #
# ------------------ #

logging.info("Normalize palette dict.")

sorted_palettes = dict()

with PALETTES_JSON_FILE.open(mode = "r") as f:
    palettes = json_load(f)

for n in sorted(palettes.keys()):
    sorted_palettes[n] = palettes[n]


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info("Update palette JSON file.")

PALETTES_JSON_FILE.write_text(json_dumps(sorted_palettes))
