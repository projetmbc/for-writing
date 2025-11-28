#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from shutil import rmtree

from json import (
    dumps as json_dumps,
    load  as json_load,
)

from matplotlib import colormaps


# --------------- #
# -- CONSTANTS -- #
# --------------- #

CTXT = TAG_MPL

THIS_DIR   = Path(__file__).parent
PRODS_DIR  = THIS_DIR.parent.parent / "products"
REPORT_DIR = THIS_DIR.parent / "report"


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"


CTXT_FILE_NAME   = CTXT.replace(' ', '-').upper()
NAMES_FILE       = REPORT_DIR / f"NAMES-{CTXT_FILE_NAME}.json"
PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)


PROD_JSON_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


# -------------------------------------- #
# -- BUILD FROM MATPLOTLIB COLOR MAPS -- #
# -------------------------------------- #

logging.info("Work on the 'Matplotlib' color maps.")

allnames = sorted(colormaps, key = lambda x: x.lower())

PAL_CREDITS    = dict()
ALL_PALETTES   = dict()
ORIGINAL_NAMES = dict()

scale_factor = PALSIZE - 1

for cmap_name in allnames:
    if cmap_name[-2:] == "_r":
        logging.warning(f"'{cmap_name}' ignored by design.")

        continue

    cmap     = colormaps[cmap_name]
    std_name = stdname(cmap_name)

    candidate = minimize_palette([
        [
            stdfloat(x, PRECISION)
            for x in cmap(i / scale_factor)[:-1]  # No alpha chanel.
        ]
        for i in range(PALSIZE)
    ])

    aprism_name, ALL_PALETTES, PAL_REPORT = update_palettes(
        context   = CTXT,
        name      = std_name,
        candidate = candidate,
        palettes  = ALL_PALETTES,
        ignored   = PAL_REPORT,
        logcom    = logging
    )

    ORIGINAL_NAMES[aprism_name] = cmap_name
    PAL_CREDITS[aprism_name]    = CTXT


logging.info(
    f"{len(ALL_PALETTES)} palettes build using 'Matplotlib' color maps."
)


# ------------------- #
# -- JSON CREATION -- #
# ------------------- #

NAMES_FILE.write_text(
    json_dumps(ORIGINAL_NAMES)
)

PAL_CREDITS_FILE.write_text(
    json_dumps(PAL_CREDITS)
)

PAL_REPORT_FILE.write_text(
    json_dumps(PAL_REPORT)
)


logging.info("Create the initial palette JSON file.")

PAL_JSON_FILE.write_text(
    json_dumps(ALL_PALETTES)
)
