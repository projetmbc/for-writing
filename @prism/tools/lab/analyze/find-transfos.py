#!/usr/bin/env python3

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

    positions = [0]
    pos       = 0

    while cols_1:
        c = cols_1.pop(0)

        if not c in cols_2:
            return False, []

        cursor = cols_2.index(c)
        pos   += cursor + 1

        positions.append(pos)

        cols_2 = cols_2[cursor + 1:]



    return True, positions






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

SUBLIST_PALS = dict()


# ---------------- #
# -- CANDIDATES -- #
# ---------------- #

printlev("Looking for candidate palettes")

BIG_CANDIDATES   = dict()
SMALL_CANDIDATES = dict()

for name in PAL_NAMES:
    big_matches   = list()
    small_matches = list()

    for subname in PAL_NAMES:
        if subname == name:
            continue

        if PAL_COLOR_SETS[name] <=  PAL_COLOR_SETS[subname]:
            big_matches.append(subname)

            if len(PAL_COLOR_LISTS[subname]) <= SEM_SIZE:
                small_matches.append(subname)

    for m, c in [
        (big_matches  , BIG_CANDIDATES),
        (small_matches, SMALL_CANDIDATES),
    ]:
        if m:
            c[name] = m


for what, candidates in [
    ('big'  , BIG_CANDIDATES),
    ('small', SMALL_CANDIDATES),
]:
    nb_candidates = len(candidates)

    if nb_candidates == 0:
        printlev(f'No {what} candidate', 1)
        exit(0)

    else:
        printlev(f'Nb of {what} candidates = {nb_candidates}', 1)

# ---------------------- #
# -- SUBLIST PALETTES -- #
# ---------------------- #

if SMALL_CANDIDATES:
    printlev("Looking for sublist 'small' palettes")

    for name_1, candidates in SMALL_CANDIDATES.items():
        for name_2 in candidates:
            test, positions = isublistof(
                pal_1 = PAL_COLOR_LISTS[name_1],
                pal_2 = PAL_COLOR_LISTS[name_2],
            )

            if not test:
                continue

            print(f'{name_1} <  {name_2}')
            print(f'{positions = }')


exit()
for name in PAL_NAMES:
    matches = list()

    for subname in PAL_NAMES:
        if (
            subname == name
            or
            len(PAL_COLOR_LISTS[paljson.stem]) > SEM_SIZE
        ):
            continue

        if PAL_COLOR_SETS[name] <=  PAL_COLOR_SETS[subname]:
            matches.append(subname)

    if matches:
        CANDIDATES[name] = matches


if len(CANDIDATES) == 0:
    printlev(f'No candidate', 1)

else:
    printlev(f'Nb of CANDIDATES = {len(CANDIDATES)}', 1)

    TODO


# ---------------------- #
# -- SHIFTED PALETTES -- #
# ---------------------- #

printlev("Looking for shifted palettes...")

CANDIDATES = dict()
