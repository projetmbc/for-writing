#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #


from pathlib import Path

import requests

from json import (
    dumps as json_dumps,
    load  as json_load,
)

import matplotlib.colors as mcolors
import numpy             as np


# ------------------------- #
# -- MAIN ONLINE VERSION -- #
# ------------------------- #

url = (
    "https://raw.githubusercontent.com/"
    "projetmbc/for-writing/main/"
    "%40prism/products/json/palettes.json"
)

response = requests.get(url)
response.raise_for_status()

MAIN_PALS = response.json()


# ------------------- #
# -- LOCAL VERSION -- #
# ------------------- #

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != '@prism'):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR   = PROJ_DIR / "products"
PROD_JSON_DIR = PRODS_DIR / "json"

PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"


with PAL_JSON_FILE.open(mode = "r") as f:
    LOCAL_PALS = json_load(f)


# ----------- #
# -- TOOLS -- #
# ----------- #

def lower_names_kept(
    main_set: set[str],
    alt_set : set[str]
) -> list[str]:
    lower_2_std = {
        x.lower(): x
        for x in main_set
    }

    _main_set = set(x.lower() for x in main_set)
    _alt_set  = set(x.lower() for x in alt_set)

    return sorted(
        lower_2_std[x]
        for x in _main_set - _alt_set
    )



def compare_rgb_palettes(small_pal, large_pal, tolerance=0.01):
    n = len(small_pal)
    M = len(large_pal)

    # Calcul des indices cibles dans la grande palette
    # On échantillonne de façon régulière du premier au dernier index
    indices = np.linspace(0, M - 1, n).round().astype(int)

    print(f"Comparaison de la structure ({n} vs {M} couleurs)")
    print("-" * 50)

    for i, idx in enumerate(indices):
        rgb_small = np.array(small_pal[i])
        rgb_sampled = np.array(large_pal[idx])

        # Calcul de la distance Euclidienne entre les deux vecteurs RGB
        distance = np.linalg.norm(rgb_small - rgb_sampled)

        status = "✅ MATCH" if distance < tolerance else f"❌ DIFF (dist: {distance:.3f})"

        print(f"Small[{i}] vs Large[{idx}]: {status}")
        print(f"   S: {rgb_small} | L: {rgb_sampled}")




# --------------------- #
# -- KEY COMPARISONS -- #
# --------------------- #

ITEM = '  + '

print("""
--------
NEW NAME  (case ignored)
--------
""".lstrip())

for n in lower_names_kept(LOCAL_PALS, MAIN_PALS):
    print(f"{ITEM}{n}")


print("""
------------
REMOVED NAME  (case ignored)
------------
""")

for n in lower_names_kept(MAIN_PALS, LOCAL_PALS):
    print(f"{ITEM}{n}")


# ----------------------- #
# -- COLOR COMPARISONS -- #
# ----------------------- #


print("""
-------
COMPARE
-------
""")

TODO
