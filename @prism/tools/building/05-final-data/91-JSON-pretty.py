#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

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

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent


REPORT_DIR = THIS_DIR.parent / TAG_REPORT


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

logging.info(f"Human friendly JSON files")

for p in sorted(REPORT_DIR.glob('*.json')):
    tokeep = False

    for prefix in [
        'AUDIT',
        'KIND',
    ]:
        if p.name.startswith(f'{prefix}-'):
            tokeep = True

            break

    if not tokeep:
        continue

    logging.info(f"Pretty '{p.relative_to(PROJ_DIR)}'")

    with p.open(mode = "r") as f:
        code = json_load(f)

    json_code = json_dumps(
        obj       = code,
        indent    = 2,
        sort_keys = True,
    )

    json_code += '\n'

    p.write_text(json_code)
