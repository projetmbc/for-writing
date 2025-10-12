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

PATTERN_JSON_LIST = re.compile(r'\[\s*\n\s*([-\d.,\s]+)\s*\n\s*\]')


# ----------- #
# -- TOOLS -- #
# ----------- #

def compact_nblists(json_code: str) -> str:
    def myreplace(match: re.Match) -> str:
        content = match.group(1)
        numbers = re.findall(r'[-\d.]+', content)

        return f"[{', '.join(numbers)}]"

    return PATTERN_JSON_LIST.sub(myreplace, json_code)


# ------------------------ #
# -- JSON NORMALIZATION -- #
# ------------------------ #

logging.info("Normalize palette dict JSON code.")

sorted_palettes = dict()

with PALETTES_JSON_FILE.open(mode = "r") as f:
    palettes = json_load(f)

json_code = json_dumps(
    obj       = palettes,
    indent    = 2,
    sort_keys = True,
)

json_code = compact_nblists(json_code)


logging.info("Update palette JSON file.")

PALETTES_JSON_FILE.write_text(json_code)
