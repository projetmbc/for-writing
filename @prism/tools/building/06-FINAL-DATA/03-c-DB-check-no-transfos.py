#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
# -- DEBUG - OFF -- #

from typing import Iterator


# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

SQL_GET_PAL_IDS = """
SELECT
    COALESCE(a.alias, h.name),
    h.name,
    h.source
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1;
"""



exit(1)





# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

from collections import defaultdict
from pathlib     import Path

from copy import deepcopy
from json import load as json_load


THIS_DIR = Path(__file__).parent

PROJ_DIR = THIS_DIR.parent

while(PROJ_DIR.name != '@prism'):
    PROJ_DIR = PROJ_DIR.parent


SEM_SIZE = 40


# ------------------ #
# -- TERM - TOOLS -- #
# ------------------ #

ITEM_TAGS = '+->'

def printlev(text, level = 0):
    tab  = ' '*4*level
    item = ITEM_TAGS[level]

    print(f'{tab}{item} {text}')


# ------------------- #
# -- AUDIT - TOOLS -- #
# ------------------- #

def isublistof(pal_1, pal_2):
    cols_1 = deepcopy(pal_1)
    cols_2 = deepcopy(pal_2)

    positions = []
    pos       = -1

    while cols_1:
        c = cols_1.pop(0)

        if not c in cols_2:
            return False, []

        cursor = cols_2.index(c)
        pos   += cursor + 1

        positions.append(pos)

        cols_2 = cols_2[cursor + 1:]

    return True, positions


def isshiftof(pal_1, pal_2):
    if len(pal_1) != len(pal_2):
        return False, -1

    i = pal_2.index(pal_1[0])

    pal_shifted = pal_2[i:] + pal_2[:i]

    if pal_1 != pal_shifted:
        return False, -1

    return True, i + 1


def isreversedshiftof(pal_1, pal_2):
    return isshiftof(pal_1[::-1], pal_2)



# ---------------------- #
# -- GET PALETTE DATA -- #
# ---------------------- #

PAL_COLOR_LISTS = dict()
PAL_COLOR_SETS  = dict()

for paljson in (
    PROJ_DIR / 'products' / 'json' / 'palettes-hf'
).glob('*.json'):
    with paljson.open('r') as f:
        colors = json_load(f)

        PAL_COLOR_LISTS[paljson.stem] = colors

        PAL_COLOR_SETS[paljson.stem] = set(
            tuple(rgb)
            for rgb in colors
        )

PAL_NAMES = list(PAL_COLOR_SETS)


CANDIDATES            = dict()
SUBLIST_PALS          = dict()
SHIFTED_PALS          = dict()
REVERSED_SHIFTED_PALS = dict()


# ---------------- #
# -- CANDIDATES -- #
# ---------------- #

printlev("Looking for candidate palettes")

for name in PAL_NAMES:
    matches   = list()
    small_matches = list()

    for subname in PAL_NAMES:
        if subname == name:
            continue

        if PAL_COLOR_SETS[name] <=  PAL_COLOR_SETS[subname]:
            matches.append(subname)

    if matches:
        CANDIDATES[name] = matches


nb_candidates = len(CANDIDATES)

if nb_candidates == 0:
    printlev('No candidate')
    exit(0)

else:
    printlev(f'Nb of candidates = {nb_candidates}')


# ---------------------- #
# -- TRANSFO PALETTES -- #
# ---------------------- #

for ctxt, validator, memodict in [
    ('sublist', isublistof, SUBLIST_PALS),
    ('shifted', isshiftof, SHIFTED_PALS),
    ('reversed and shifted', isreversedshiftof, REVERSED_SHIFTED_PALS),
]:
    printlev(f"Looking for '{ctxt} palettes'")

    for name_1, candidates in CANDIDATES.items():
        for name_2 in candidates:
            test, data = validator(
                pal_1 = PAL_COLOR_LISTS[name_1],
                pal_2 = PAL_COLOR_LISTS[name_2],
            )

            if not test:
                continue

            if name_2 in memodict:
                continue

            memodict[name_1] = (name_2, data)

    if memodict:
        printlev(f"'{len(memodict)} {ctxt}' palettes found")

    else:
        printlev(f"'No {ctxt} palettes' found")


print(REVERSED_SHIFTED_PALS)
