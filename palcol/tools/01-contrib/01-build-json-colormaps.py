#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json import dumps as json_dumps
from math import          floor

import matplotlib.pyplot as plt
import matplotlib.cm     as cm


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PALETTE_SIZE = 10
PRECISION    = 10**5

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent.parent / "data"

JSON_PALETTES = DATA_DIR / "palcol.json"


# --------------- #
# -- FORMATTER -- #
# --------------- #

def stdfloat(x):
    return floor(x * PRECISION) / PRECISION


# ------------------------- #
# -- MATPLOTLIB PALETTES -- #
# ------------------------- #

palettes = {}

logging.info("Working on the Matplotlib color maps.")

allnames = sorted(
    [cm for cm in plt.colormaps() if cm[-2:] != "_r"],
    key = lambda x: x.lower()
)

scale_factor = PALETTE_SIZE - 1

for cmap_name in allnames:
    cmap      = cm.get_cmap(cmap_name)
    cmap_name = cmap_name[0].upper() + cmap_name[1:]

    palettes[cmap_name] = [
        [
            stdfloat(x)
            for x in cmap(i / scale_factor)[:-1]  # No alpha canal.
        ]
        for i in range(PALETTE_SIZE)
    ]

    logging.info(f"Extracted color map '{cmap_name}'.")

    # break

logging.info(f"{len(allnames)} Matplotlib color maps extracted.")


# ------------------ #
# -- JSON VERSION -- #
# ------------------ #

logging.info("Update/create the JSON file of palettes.")

JSON_PALETTES.write_text(json_dumps(palettes))
