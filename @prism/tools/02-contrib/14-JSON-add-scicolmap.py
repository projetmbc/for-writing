#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from collections import defaultdict

from json import (
    dumps as json_dumps,
    load  as json_load,
)

import numpy as np


# --------------- #
# -- CONSTANTS -- #
# --------------- #

CTXT = TAG_SCICOLMAP

THIS_DIR         = Path(__file__).parent
PROJ_DIR         = THIS_DIR.parent.parent
PRODS_DIR        = PROJ_DIR / "products"
ORIGINAL_SRC_DIR = PROJ_DIR / "resources" / "ScientificColourMaps" / "ScientificColourMaps8"
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


PATTERN_CMP_LIST = re.compile(
    r'cm_data\s*=\s*(\[\[.*?\]\])',
    re.DOTALL
)


# ------------------------------- #
# -- EXTRACT MAPS FROM PY FILE -- #
# ------------------------------- #

def exract_palette(file: Path) -> list[ [float, float, float] ]:
    content = file.read_text()

    match = PATTERN_CMP_LIST.search(content)

    if not match:
        BUG_KO

    palette = eval(match.group(1))

    return palette


# -------------------------------- #
# -- BUILD FROM SCI. COLOR MAPS -- #
# -------------------------------- #

logging.info(f"Work with the '{CTXT}' source code.")

nb_new_pals = len(ALL_PALETTES)

# We force the integration of Scicolor Maps !

for pyfile in sorted(ORIGINAL_SRC_DIR.glob("*/*.py"), key = lambda x: str(x).lower()):
    pal_name = pyfile.stem
    std_name = stdname(pal_name)
    pal_def  = exract_palette(pyfile)

    ORIGINAL_NAMES[std_name] = pal_name

    ALL_PALETTES, PAL_REPORT = update_palettes(
        context   = CTXT,
        name      = std_name,
        candidate = pal_def,
        palettes  = ALL_PALETTES,
        ignored   = PAL_REPORT,
        logcom    = logging
    )

    PAL_CREDITS[std_name] = CTXT


nb_new_pals = len(ALL_PALETTES) - nb_new_pals

if nb_new_pals == 0:
    logging.info("Nothing new found.")

else:
    plurial = "" if nb_new_pals == 1 else "s"

    logging.info(f"{nb_new_pals} palette{plurial} added.")


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
