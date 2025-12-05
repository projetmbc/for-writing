#!/usr/bin/env python3

from typing import TypeAlias

from collections import defaultdict

import numpy as np


# ------------ #
# -- TYPING -- #
# ------------ #

RGBCols    :TypeAlias = [float, float, float]
PaletteCols:TypeAlias = list[RGBCols]


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

MIN_COL_SIZE = 2
MAX_COL_SIZE = 4


ALL_CATEGO_TAGS = []

for n in range(MIN_COL_SIZE, MAX_COL_SIZE + 1):
    varname = f"TAG_CATEGO_SIZE_{n}"

    globals()[varname] = f"col-size-{n}"

    ALL_CATEGO_TAGS.append(globals()[varname])

ALL_CATEGO_TAGS += [
    TAG_CATEGO_SMOOTH         := "smooth",
    TAG_CATEGO_SEMANTIC       := "semantic",
    TAG_CATEGO_NO_CATEGO_FOUND:= "no-catego-found",
]


# -------------- #
# -- CATEGORY -- #
# -------------- #

def classify_palettes(
    palettes: dict[str, PaletteCols]
):
    categories = {
        TAG_CATEGO_NO_CATEGO_FOUND: list(palettes),
    }

    return categories


# ------------- #
# -- SIMILAR -- #
# ------------- #

def create_palette_spectrum(colors: PaletteCols) -> None:
    spectrum = np.zeros(30)

    for r, g, b in colors:
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff    = max_val - min_val

        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360

        # Saturation
        s = 0 if max_val == 0 else diff / max_val

        # Value
        v = max_val

        # Ajouter aux bins du spectre
        h_bin = min(int(h / 36), 9)  # 10 bins pour hue (0-360)
        s_bin = min(int(s * 10), 9)   # 10 bins pour saturation (0-1)
        v_bin = min(int(v * 10), 9)   # 10 bins pour value (0-1)

        spectrum[h_bin] += 1
        spectrum[10 + s_bin] += 1
        spectrum[20 + v_bin] += 1

    # Normaliser
    return spectrum / np.linalg.norm(spectrum)


def find_similar_palettes(
    target_name : str,
    palettes    : dict[str, PaletteCols],
    cluster_size: int = 10,
    method      : str = 'euclidean'
) -> list[tuple[str, float]]:
    assert method in ['euclidean', 'cosine']

    target_spectrum = create_palette_spectrum(palettes[target_name])

    similarities = []

    for name, colors in palettes.items():
        if name == target_name:
            continue

        spectrum = create_palette_spectrum(colors)

        if method == 'euclidean':
            distance = euclidean(
                target_spectrum,
                spectrum
            )

        else:  # cosine
            distance = cosine(
                target_spectrum,
                spectrum
            )

        similarities.append((name, distance))

    # Trier par similarité (distance la plus faible)
    similarities.sort(key=lambda x: x[1])

    return similarities[:cluster_size]
