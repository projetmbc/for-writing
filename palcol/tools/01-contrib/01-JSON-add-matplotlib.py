#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json import dumps as json_dumps
from math import          floor

from matplotlib import colormaps


# --------------- #
# -- CONSTANTS -- #
# --------------- #

SAMPLING_SIZE = 8
PRECISION     = 10**5

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent.parent / "data"

PALETTES_JSON_FILE = DATA_DIR / "palettes.json"

PALETTES_JSON_FILE.parent.mkdir(
    parents  = True,
    exist_ok = True
)


# --------------- #
# -- FORMATTER -- #
# --------------- #

def stdfloat(x):
    return floor(x * PRECISION) / PRECISION


def minimize_palette(p):
    if len(set(tuple(c) for c in p)) == len(p):
        return p

    new_p = []

    for c in p:
        if (not new_p or c != new_p[-1]):
            new_p.append(c)

    return new_p


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

palettes = {}

logging.info("Working on the Matplotlib color maps.")

allnames = sorted(
    [cm for cm in colormaps if cm[-2:] != "_r"],
    key = lambda x: x.lower()
)

scale_factor = SAMPLING_SIZE - 1

for cmap_name in allnames:
    cmap      = colormaps[cmap_name]
    cmap_name = cmap_name[0].upper() + cmap_name[1:]

    palettes[cmap_name] = minimize_palette([
        [
            stdfloat(x)
            for x in cmap(i / scale_factor)[:-1]  # No alpha canal.
        ]
        for i in range(SAMPLING_SIZE)
    ])

    logging.info(f"New palette from '{cmap_name}' color map.")

    # break

logging.info(f"{len(allnames)} palettes build from Matplotlib color maps.")


# ------------------ #
# -- JSON VERSION -- #
# ------------------ #

logging.info("Create the initial palette JSON file.")

PALETTES_JSON_FILE.write_text(json_dumps(palettes))
