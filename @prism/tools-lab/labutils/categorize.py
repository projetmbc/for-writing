#!/usr/bin/env python3

import numpy as np
from sklearn.cluster import KMeans
from collections import Counter


# --------------------- #
# -- "AI" CLUSTERING -- #
# --------------------- #

def classify_palette_colors(
    colors    : [[float, float, float]],
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


def is_monochrome(
    colors   : [[float, float, float]],
    threshold: float = 0.08
) -> bool:
    result = classify_palette_colors(
        colors,
        n_clusters = 1
    )

    normalized_inertia = result / len(colors)

    return normalized_inertia < threshold


def is_bicolor(
    colors   : [[float, float, float]],
    threshold: float = 0.15
) -> bool:
    result = classify_palette_colors(
        colors,
        n_clusters = 2
    )

    normalized_inertia = result / len(colors)

    return normalized_inertia < threshold


def is_tricolor(
    colors   : [[float, float, float]],
    threshold: float = 0.15
) -> bool:
    result = classify_palette_colors(
        colors,
        n_clusters = 3
    )

    normalized_inertia = result / len(colors)

    return normalized_inertia < threshold
