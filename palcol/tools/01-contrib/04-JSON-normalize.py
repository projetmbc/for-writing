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

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent.parent / "data"

PALETTES_JSON_FILE = DATA_DIR / "palettes.json"


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

sorted_palettes = dict()

with PALETTES_JSON_FILE.open(mode = "r") as f:
    palettes = json_load(f)

for n in sorted(palettes.keys()):
    sorted_palettes[n] = palettes[n]


# --------------------- #
# -- JSON NORMALIZED -- #
# --------------------- #

logging.info("JSON file normalized.")

PALETTES_JSON_FILE.write_text(json_dumps(sorted_palettes))
