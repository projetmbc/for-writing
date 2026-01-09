#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# --------------- #
# -- CONSTANTS -- #
# --------------- #

CTXT = TAG_COLORBREWER

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR        = PROJ_DIR / "products"
ORIGINAL_SRC_DIR = PROJ_DIR / TAG_XTRA_RESRC / "Colorbrewer"
REPORT_DIR       = THIS_DIR.parent / TAG_REPORT


CTXT_FILE_NAME = CTXT.replace(' ', '-').upper()
NAMES_FILE     = REPORT_DIR / f"NAMES-{CTXT_FILE_NAME}.json"
ORIGINAL_NAMES = dict()


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

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


# ----------- #
# -- TOOLS -- #
# ----------- #

def extract_palette(paldef: dict) -> list[ [float, float, float] ]:
    max_size = 0

    for s in paldef:
        if s == "type":
            continue

        max_size = max(int(s), max_size)

    paldef = paldef[str(max_size)]
    paldef = pal255_to_pal01([
        eval(c.replace("rgb", ""))
        for c in paldef
    ])

    return paldef


# ---------------------- #
# -- FROM COLORBREWER -- #
# ---------------------- #

logging.info(f"Work with the '{CTXT}' source code.")

nb_new_pals = len(ALL_PALETTES)

for palname, paldef in PAL_COLORBREWER.items():
    stdname = get_stdname(palname)
    paldef  = extract_palette(paldef)

    aprism_name, ALL_PALETTES, PAL_REPORT = update_palettes(
        context   = CTXT,
        name      = stdname,
        candidate = paldef,
        palettes  = ALL_PALETTES,
        ignored   = PAL_REPORT,
        logcom    = logging
    )

    ORIGINAL_NAMES[aprism_name] = palname
    PAL_CREDITS[aprism_name]    = CTXT


nb_new_pals = resume_nbpals_build(
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
