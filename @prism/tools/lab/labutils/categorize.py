#!/usr/bin/env python3

from typing import TypeAlias

from collections import Counter

import numpy as np

from scipy.spatial.distance import euclidean, cosine
from sklearn.cluster        import KMeans


# ------------ #
# -- TYPING -- #
# ------------ #

RGBCols    :TypeAlias = [float, float, float]
PaletteCols:TypeAlias = list[RGBCols]


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

MAX_COL_SIZE = 4


# --------------------- #
# -- "AI" - CATEGORY -- #
# --------------------- #

def classify_palette_colors(
    colors    : PaletteCols,
    n_clusters: int
) -> float:
    colors = np.array(colors)

    kmeans = KMeans(
        n_clusters   = n_clusters,
        random_state = 42,
        n_init       = 10
    )

    labels = kmeans.fit_predict(colors)

    return kmeans.inertia_


def has_colsize_n(
    colors   : PaletteCols,
    size     : int,
    threshold: float = 0.08,
) -> bool:
    result = classify_palette_colors(
        colors,
        n_clusters = size
    )

    normalized_inertia = result / len(colors)

    return normalized_inertia < threshold


HAS_COLSIZE_FUNCS = [
    lambda c, t = 0.05: has_colsize_n(
        colors    = c,
        size      = n,
        threshold = t,
    )
    for n in range(1, MAX_COL_SIZE + 1)
]


# -------------------- #
# -- "AI" - SIMILAR -- #
# -------------------- #

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
