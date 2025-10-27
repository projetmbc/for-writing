#!/usr/bin/env python3

# Source code.
#     + https://www.fabiocrameri.ch/colourmaps

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

CTXT = "Scientific Colour Maps"

THIS_DIR          = Path(__file__).parent
PROJECT_DIR       = THIS_DIR.parent.parent
PRODUCTS_DIR      = PROJECT_DIR / "products"
SCICOLMAP_SRC_DIR = PROJECT_DIR / "x-ScientificColourMaps8-x"
REPORT_DIR        = THIS_DIR.parent / "report"


PAL_JSON_FILE   = PRODUCTS_DIR / "palettes.json"
MP_NAMES_FILE   = THIS_DIR / "mp-names.json"
PAL_REPORT_FILE = THIS_DIR / "pal-report.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)

with MP_NAMES_FILE.open(mode = "r") as f:
    ALL_MP_NAMES = json_load(f)

with PAL_REPORT_FILE.open(mode = "r") as f:
    IGNORED = json_load(f)


if not REPORT_DIR.is_dir():
    REPORT_DIR.mkdir(
        parents  = True,
        exist_ok = True
    )


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


# ------------------------------------- #
# -- BUILD FROM ASYMPTOTE COLOR MAPS -- #
# ------------------------------------- #

logging.info("Work with the 'Scientific Coulour Maps 8' source code.")

nb_scicolmaps = len(ALL_PALETTES)

for pyfile in sorted(SCICOLMAP_SRC_DIR.glob("*/*.py")):
    palette_name = pyfile.stem
    palette_name = stdname(palette_name)
    palette_def  = exract_palette(pyfile)


    ALL_PALETTES, IGNORED = update_palettes(
        context   = CTXT,
        name      = palette_name,
        candidate = palette_def,
        palettes  = ALL_PALETTES,
        ignored   = IGNORED,
        logcom    = logging
    )


nb_scicolmaps = len(ALL_PALETTES) - nb_scicolmaps

if nb_scicolmaps == 0:
    logging.info("Nothing new found.")

else:
    plurial = "" if nb_scicolmaps == 1 else "s"

    logging.info(f"{nb_scicolmaps} palette{plurial} added.")


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

PAL_REPORT_FILE.write_text(json_dumps(IGNORED))

logging.info("Update palette JSON file.")

PAL_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
