#!/usr/bin/env python3

# Source code.
#     + https://www.fabiocrameri.ch/colourmaps

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR   = Path(__file__).parent
PROJ_DIR   = THIS_DIR.parent.parent
PRODS_DIR  = PROJ_DIR / "products"
RESRC_DIR  = PROJ_DIR / "resources" / "Colorbrewer"
REPORT_DIR = THIS_DIR.parent / "report"


NAMES_FILE     = REPORT_DIR / "COLORBREWER-NAMES.json"
ORIGINAL_NAMES = {}


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"

with PAL_CREDITS_FILE.open(mode = "r") as f:
    PAL_CREDITS = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)


PAL_COLORBREWER_FILE = RESRC_DIR / "colorbrewer.json"

with PAL_COLORBREWER_FILE.open(mode = "r") as f:
    PAL_COLORBREWER = json_load(f)


PATTERN_CMP_LIST = re.compile(
    r'cm_data\s*=\s*(\[\[.*?\]\])',
    re.DOTALL
)


# ------------------------------------- #
# -- BUILD FROM ASYMPTOTE COLOR MAPS -- #
# ------------------------------------- #

logging.info("Work with the 'Colorbrewer' source code.")

nb_colorbrewer   = len(ALL_PALETTES)
names_to_ignores = list(PAL_REPORT) + list(ALL_PALETTES)

for pal_name in PAL_COLORBREWER:
    std_name = stdname(pal_name)

    if not std_name in names_to_ignores:
        print(pal_name)
        TODO

    if not std_name in PAL_REPORT:
        PAL_CREDITS[std_name] = "Colorbrewer"


nb_colorbrewer = len(ALL_PALETTES) - nb_colorbrewer

if nb_colorbrewer == 0:
    logging.info("Nothing new found.")

else:
    TODO


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

NAMES_FILE.write_text(
    json_dumps(ORIGINAL_NAMES)
)

PAL_CREDITS_FILE.write_text(
    json_dumps(PAL_CREDITS)
)

if nb_colorbrewer != 0:
    PAL_REPORT_FILE.write_text(
        json_dumps(PAL_REPORT)
    )

    logging.info("Update palette JSON file.")

    PAL_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
