#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

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

import numpy as np
from scipy.interpolate import interp1d


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

TOLERANCE = 10**(-2)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != '@prism'):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR = PROJ_DIR / "products"


REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

REPORT_SAME_NAMED_PALS_JSON = REPORT_DIR / "AUDIT-SAME-NAMED-PALETTES.json"

REPORT_SAME_NAMED_PALS_JSON.touch()



# ----------- #
# -- TOOLS -- #
# ----------- #

def get_palette_compatibility(palette_a, palette_b):
    """
    Retourne un booléen 'match' et un 'score' de 0 à 100.
    100 = Identique, 0 = Totalement différent.
    """
    p1 = np.array(palette_a)
    p1 = np.round(p1, 6)

    p2 = np.array(palette_b)

    # Détermination de la taille cible (la plus petite)
    if len(p1) != len(p2):
        small_p = p1 if len(p1) < len(p2) else p2
        large_p = p2 if len(p1) < len(p2) else p1

        # Interpolation
        old_indices = np.linspace(0, 1, len(large_p))
        new_indices = np.linspace(0, 1, len(small_p))
        interp_func = interp1d(old_indices, large_p, axis=0, kind='linear')
        p_ref = small_p
        p_test = interp_func(new_indices)
    else:
        p_ref, p_test = p1, p2

    # Calcul de l'erreur maximale et moyenne
    distances = np.linalg.norm(p_test - p_ref, axis=1)
    max_err = np.max(distances)
    mean_err = np.mean(distances)

    # Calcul du score (0 à 100)
    # On utilise l'erreur moyenne pour le score global
    # Un écart de 0.5 (sur 1.0 en RGB) est considéré comme une opposition totale (0/100)
    score = max(0, 100 * (1 - (mean_err / 0.5)))

    # Le match est validé si TOUTES les couleurs respectent la tolérance
    match = bool(max_err <= TOLERANCE)

    return match, round(score, 2)


# ------------------- #
# -- LOCAL VERSION -- #
# ------------------- #

logging.info("MAIN/LOCAL - Get 'last local' version")

JSON_PROD_FILE = PROJ_DIR / "products" / "json" / "palettes.json"

with JSON_PROD_FILE.open(mode = "r") as f:
    LOCAL_PALS = json_load(f)


# ------------------------ #
# -- MAIN LOCAL VERSION -- #
# ------------------------ #

logging.info("MAIN/LOCAL - Get 'main local' version")

REPORT_LAST_MAIN_JSON = REPORT_DIR / f"AUDIT-LAST-MAIN.json"

with REPORT_LAST_MAIN_JSON.open(mode = "r") as f:
    MAIN_PALS = json_load(f)


# ------------------------- #
# -- PALETTE COMPARISONS -- #
# ------------------------- #

logging.info("Analyze - 'Vals of same named palettes'")

same_named_pals_results = dict()

for name, pal_1 in LOCAL_PALS.items():
    if not name in MAIN_PALS:
        continue

    pal_2 = MAIN_PALS[name]

    same_named_pals_results[name] = get_palette_compatibility(
        pal_1,
        pal_2
    )


# ------------------------- #
# -- PALETTE COMPARISONS -- #
# ------------------------- #

logging.info(
    f"Update '{REPORT_SAME_NAMED_PALS_JSON.relative_to(PROJ_DIR)}'"
)

REPORT_SAME_NAMED_PALS_JSON.write_text(
    json_dumps(same_named_pals_results)
)
