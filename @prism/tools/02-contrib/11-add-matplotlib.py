#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from shutil import rmtree
from json   import dumps as json_dumps

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

PAL_SRC_FILE    = REPORT_DIR / "PAL-SRC.json"
MP_NAMES_FILE   = REPORT_DIR / "MP-NAMES.json"
PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"


PROD_JSON_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


# ----------------------------- #
# -- EMPTY THE REPORT FOLDER -- #
# ----------------------------- #

REPORT_DIR  = THIS_DIR.parent / "report"

if REPORT_DIR.is_dir():
    rmtree(REPORT_DIR)

REPORT_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


# -------------------------------------- #
# -- BUILD FROM MATPLOTLIB COLOR MAPS -- #
# -------------------------------------- #

logging.info("Work on the 'Matplotlib' color maps.")

allnames = sorted(colormaps, key = lambda x: x.lower())

PAL_SRC      = dict()
ALL_PALETTES = dict()
PAL_REPORT      = dict()

scale_factor = PALSIZE - 1

reverse_status = STATUS_TAG[PAL_STATUS.REVERSE_OF]

for cmap_name in allnames:
    if cmap_name[-2:] == "_r":
        PAL_REPORT[stdname(cmap_name)] = {
            reverse_status: stdname(cmap_name[:-2]),
            TAG_CTXT      : CTXT
        }

        logging.warning(f"'{cmap_name}' PAL_REPORT.")

        continue

    cmap      = colormaps[cmap_name]
    cmap_name = stdname(cmap_name)

    candidate = minimize_palette([
        [
            stdfloat(x, PRECISION)
            for x in cmap(i / scale_factor)[:-1]  # No alpha chanel.
        ]
        for i in range(PALSIZE)
    ])

    ALL_PALETTES, PAL_REPORT = update_palettes(
        context   = CTXT,
        name      = cmap_name,
        candidate = candidate,
        palettes  = ALL_PALETTES,
        ignored   = PAL_REPORT,
        logcom    = logging
    )

    if not cmap_name in PAL_REPORT:
        PAL_SRC[cmap_name] = CTXT


logging.info(
    f"{len(ALL_PALETTES)} palettes build from 'Matplotlib' color maps."
)


# ------------------- #
# -- JSON CREATION -- #
# ------------------- #

MP_NAMES_FILE.write_text(
    json_dumps({
        stdname(n): n for n in allnames
    })
)

PAL_SRC_FILE.write_text(
    json_dumps(PAL_SRC)
)

PAL_REPORT_FILE.write_text(
    json_dumps(PAL_REPORT)
)


logging.info("Create the initial palette JSON file.")

PAL_JSON_FILE.write_text(
    json_dumps(ALL_PALETTES)
)
