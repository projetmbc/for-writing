#!/usr/bin/env python3

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(TOOLS_DIR))

from cbutils.core import *
from cbutils      import *


# --------------- #
# -- CONSTANTS -- #
# --------------- #

CTXT = TAG_COLORBREWER

PROJ_DIR         = TOOLS_DIR.parent
PRODS_DIR        = PROJ_DIR / "products"
ORIGINAL_SRC_DIR = PROJ_DIR / "resources" / "Colorbrewer"
REPORT_DIR       = THIS_DIR.parent / "REPORT"


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


PAL_COLORBREWER_FILE = ORIGINAL_SRC_DIR / "colorbrewer.json"

with PAL_COLORBREWER_FILE.open(mode = "r") as f:
    PAL_COLORBREWER = json_load(f)


# --------------------------------- #
# -- EXTRACT MAPS FROM JSON FILE -- #
# --------------------------------- #

def extract_palette(pal_def: dict) -> list[ [float, float, float] ]:
    max_size = 0

    for s in pal_def:
        if s == "type":
            continue

        max_size = max(int(s), max_size)

    pal_def = pal_def[str(max_size)]
    pal_def = pal255_to_pal01([
        eval(c.replace("rgb", ""))
        for c in pal_def
    ])

    return pal_def


# ------------------------------------- #
# -- BUILD FROM COLORBREWER PALETTES -- #
# ------------------------------------- #

logging.info(f"Work with the '{CTXT}' source code.")

nb_new_pals = len(ALL_PALETTES)

for pal_name, pal_def in PAL_COLORBREWER.items():
    std_name = stdname(pal_name)
    pal_def  = extract_palette(pal_def)

    aprism_name, ALL_PALETTES, PAL_REPORT = update_palettes(
        context   = CTXT,
        name      = std_name,
        candidate = pal_def,
        palettes  = ALL_PALETTES,
        ignored   = PAL_REPORT,
        logcom    = logging
    )

    ORIGINAL_NAMES[aprism_name] = pal_name
    PAL_CREDITS[aprism_name]    = CTXT


nb_new_pals = resume_pal_build(
    context     = CTXT,
    nb_new_pals = nb_new_pals,
    palettes    = ALL_PALETTES,
    logcom      = logging,
)


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

update_jsons(
    nb_new_pals = nb_new_pals,
    names       = ORIGINAL_NAMES,
    jsnames     = NAMES_FILE,
    credits     = PAL_CREDITS,
    jscredits   = PAL_CREDITS_FILE,
    reports     = PAL_REPORT,
    jsreports   = PAL_REPORT_FILE,
    palettes    = ALL_PALETTES,
    jspalettes  = PAL_JSON_FILE,
    logcom      = logging,
)
