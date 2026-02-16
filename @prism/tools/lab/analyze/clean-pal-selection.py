#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ----------------------------- #
# -- IMPORT LABUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR = Path(__file__).parent
LAB_DIR  = THIS_DIR.parent

sys.path.append(str(LAB_DIR))

from labutils import *

# -- IMPORT LABUTILS - END -- #
# --------------------------- #

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR = PROJ_DIR / "products"


JSON_PALS_HF_DIR = PRODS_DIR / 'json' / 'palettes-hf'

ALL_PALS = dict()

for jsonfile in JSON_PALS_HF_DIR.glob('*.json'):
    with jsonfile.open() as f:
        ALL_PALS[jsonfile.stem] = json_load(f)

ALL_PAL_NAMES = sorted(
    list(ALL_PALS),
    key = lambda p: len(
        set(
            tuple(rgb)
            for rgb in ALL_PALS[p]
        )
    )
)


# ---------------------- #
# -- LOOK FOR SIMILAR -- #
# ---------------------- #

SAME_COLORS = dict()
SUB_COLORS  = dict()

for i, palname_1 in enumerate(ALL_PAL_NAMES):
    print(palname_1)
    print(len(ALL_PALS[palname_1]))
    print('---')
    for palname_2 in ALL_PAL_NAMES[i+1:]:
        ...
