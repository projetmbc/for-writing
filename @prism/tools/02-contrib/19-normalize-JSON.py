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

THIS_DIR  = Path(__file__).parent
PRODS_DIR = THIS_DIR.parent.parent / "products"


PAL_REPORT_FILE = THIS_DIR / "PAL-REPORT.json"

PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"


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

logging.info("Normalize palette dict JSON codes.")


with PAL_REPORT_FILE.open(mode = "r") as f:
    report = json_load(f)

json_code = json_dumps(
    obj       = report,
    indent    = 2,
    sort_keys = True,
)

PAL_REPORT_FILE.write_text(json_code)

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
