#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PATTERN_JSON_LIST = re.compile(r'\[\s*\n\s*([-\d.,\s]+)\s*\n\s*\]')


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR  = PROJ_DIR / "products"
REPORT_DIR = THIS_DIR.parent / "REPORT"


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"


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

logging.info("Normalize all reporting JSON codes.")

for jsonfile in REPORT_DIR.glob("*.json"):
    with jsonfile.open(mode = "r") as f:
        code = json_load(f)

    json_code = json_dumps(
        obj       = code,
        indent    = 2,
        sort_keys = True,
    )

    jsonfile.write_text(json_code)


logging.info("Normalize JSON product code.")

with PAL_JSON_FILE.open(mode = "r") as f:
    palettes = json_load(f)

json_code = json_dumps(
    obj       = palettes,
    indent    = 2,
    sort_keys = True,
)

json_code = compact_nblists(json_code)


logging.info("Update palette JSON file.")

PAL_JSON_FILE.write_text(json_code)
