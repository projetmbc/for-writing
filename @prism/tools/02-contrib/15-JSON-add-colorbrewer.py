#!/usr/bin/env python3

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

CTXT = TAG_COLORBREWER

THIS_DIR         = Path(__file__).parent
PROJ_DIR         = THIS_DIR.parent.parent
PRODS_DIR        = PROJ_DIR / "products"
ORIGINAL_SRC_DIR = PROJ_DIR / "resources" / "Colorbrewer"
REPORT_DIR       = THIS_DIR.parent / "report"


CTXT_FILE_NAME = CTXT.replace(' ', '-').upper()
NAMES_FILE     = REPORT_DIR / f"NAMES-{CTXT_FILE_NAME}.json"
ORIGINAL_NAMES = dict()


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)


PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"

with PAL_CREDITS_FILE.open(mode = "r") as f:
    PAL_CREDITS = json_load(f)


STD_NAMES_IGNORED = list(ALL_PALETTES) + list(PAL_REPORT)


PAL_COLORBREWER_FILE = ORIGINAL_SRC_DIR / "colorbrewer.json"

with PAL_COLORBREWER_FILE.open(mode = "r") as f:
    PAL_COLORBREWER = json_load(f)


# ------------------------------------- #
# -- BUILD FROM COLORBREWER PALETTES -- #
# ------------------------------------- #

logging.info(f"Work with the '{CTXT}' source code.")

nb_new_pals = len(ALL_PALETTES)

for pal_name in PAL_COLORBREWER:
    std_name = stdname(pal_name)

    ORIGINAL_NAMES[std_name] = pal_name
    PAL_CREDITS[std_name]    = CTXT

    if not std_name in STD_NAMES_IGNORED:
        print(pal_name)
        TODO


nb_new_pals = len(ALL_PALETTES) - nb_new_pals

if nb_new_pals == 0:
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

if nb_new_pals != 0:
    PAL_REPORT_FILE.write_text(
        json_dumps(PAL_REPORT)
    )

    logging.info("Update palette JSON file.")

    PAL_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
