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

from collections import defaultdict

import numpy as np


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PATTERN_CMP_LIST = re.compile(
    r'cm_data\s*=\s*(\[\[.*?\]\])',
    re.DOTALL
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

CTXT = TAG_SCICOLMAP


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR        = PROJ_DIR / "products"
ORIGINAL_SRC_DIR = PROJ_DIR / "resources" / "ScientificColourMaps" / "ScientificColourMaps8"
REPORT_DIR       = BUILD_TOOLS_DIR / "REPORT"


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


# ----------- #
# -- TOOLS -- #
# ----------- #

def exract_palette(file: Path) -> list[ [float, float, float] ]:
    content = file.read_text()

    match = PATTERN_CMP_LIST.search(content)

    if not match:
        BUG_KO

    palette = eval(match.group(1))

    return palette


# -------------------------- #
# -- FROM SCI. COLOR MAPS -- #
# -------------------------- #

logging.info(f"Work with the '{CTXT}' source code.")

nb_new_pals = len(ALL_PALETTES)

for pyfile in sorted(ORIGINAL_SRC_DIR.glob("*/*.py"), key = lambda x: str(x).lower()):
    pal_name = pyfile.stem
    std_name = stdname(pal_name)
    pal_def  = exract_palette(pyfile)

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
