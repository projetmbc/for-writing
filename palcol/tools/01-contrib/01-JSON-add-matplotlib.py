#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json   import dumps as json_dumps
from math   import          floor
from string import          ascii_letters, digits

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

CHARS_ALLOWED = set(ascii_letters + digits)


# --------------- #
# -- FORMATTER -- #
# --------------- #

def _capitalize(n):
    return n[0].upper() + n[1:]

def stdname(n):
    letters = set(n)

    if not letters <= CHARS_ALLOWED:
        for c in letters - CHARS_ALLOWED:
            n = ''.join([
                _capitalize(p)
                for p in n.split(c)
            ])

    else:
        n = _capitalize(n)

    return n

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


# -------------------------------------- #
# -- BUILD FROM MATPLOTLIB COLOR MAPS -- #
# -------------------------------------- #

palettes = {}

logging.info("Work on the 'Matplotlib' color maps.")

allnames = sorted(
    [cm for cm in colormaps if cm[-2:] != "_r"],
    key = lambda x: x.lower()
)

scale_factor = SAMPLING_SIZE - 1

for cmap_name in allnames:
    cmap      = colormaps[cmap_name]
    cmap_name = stdname(cmap_name)

    palettes[cmap_name] = minimize_palette([
        [
            stdfloat(x)
            for x in cmap(i / scale_factor)[:-1]  # No alpha canal.
        ]
        for i in range(SAMPLING_SIZE)
    ])

    logging.info(f"New palette from '{cmap_name}' color map.")

    # break

logging.info(f"{len(allnames)} palettes build from 'Matplotlib' color maps.")


# ------------------- #
# -- JSON CREATION -- #
# ------------------- #

logging.info("Create the initial palette JSON file.")

PALETTES_JSON_FILE.write_text(json_dumps(palettes))
