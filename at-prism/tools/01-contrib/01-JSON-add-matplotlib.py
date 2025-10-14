#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from collections import defaultdict

from json import dumps as json_dumps

from matplotlib import colormaps


# --------------- #
# -- CONSTANTS -- #
# --------------- #

SAMPLING_SIZE = 8
PRECISION     = 10**5

THIS_DIR     = Path(__file__).parent
PRODUCTS_DIR = THIS_DIR.parent.parent / "products"

PAL_JSON_FILE   = PRODUCTS_DIR / "palettes.json"
MP_NAMES_FILE   = THIS_DIR / "mp-names.json"
PAL_REPORT_FILE = THIS_DIR / "pal-report.json"

PAL_JSON_FILE.parent.mkdir(
    parents  = True,
    exist_ok = True
)


# -------------------------------------- #
# -- BUILD FROM MATPLOTLIB COLOR MAPS -- #
# -------------------------------------- #

logging.info("Work on the 'Matplotlib' color maps.")

allnames = sorted(colormaps, key = lambda x: x.lower())

palettes = {}
ignored  = {
    STATUS_TAG[PAL_STATUS.EQUAL_TO]  : defaultdict(list),
    STATUS_TAG[PAL_STATUS.REVERSE_OF]: defaultdict(list),
}

scale_factor = SAMPLING_SIZE - 1

for cmap_name in allnames:
    if cmap_name[-2:] == "_r":
        logging.warning(
            f"'{stdname(cmap_name)}' ignored."
        )

        continue

    cmap      = colormaps[cmap_name]
    cmap_name = stdname(cmap_name)

    candidate = minimize_palette([
        [
            stdfloat(x, PRECISION)
            for x in cmap(i / scale_factor)[:-1]  # No alpha chanel.
        ]
        for i in range(SAMPLING_SIZE)
    ])

    palettes, ignored = update_palettes(
        cmap_name,
        candidate,
        palettes,
        ignored,
        logging
    )


logging.info(
    f"{len(palettes)} palettes build from 'Matplotlib' color maps."
)



# ------------------- #
# -- JSON CREATION -- #
# ------------------- #

MP_NAMES_FILE.write_text(
    json_dumps({
        stdname(n): n for n in allnames
    })
)

PAL_REPORT_FILE.write_text(json_dumps(ignored))


logging.info("Create the initial palette JSON file.")

PAL_JSON_FILE.write_text(json_dumps(palettes))
