#!/usr/bin/env python3

import numpy as np
from scipy.interpolate import interp1d
from skimage import color
import json

from pathlib import Path

THIS_DIR = Path(__file__).parent

PROJ_DIR = THIS_DIR.parent

while(PROJ_DIR.name != '@prism'):
    PROJ_DIR = PROJ_DIR.parent

JSON_HF_PALS_DIR  = PROJ_DIR / 'products' / 'json' / 'palettes-hf'


def normalize_and_convert_lab(palette, samples=50):
    palette = np.array(palette)

    x_old = np.linspace(0, 1, len(palette))
    x_new = np.linspace(0, 1, samples)

    f = interp1d(x_old, palette, axis=0, kind='linear')

    resampled = f(x_new)

    return color.rgb2lab(resampled.reshape(1, -1, 3))


def get_top_10_matches(target_name, all_palettes):
    target_lab = normalize_and_convert_lab(all_palettes[target_name])

    scores = []

    for name, colors in all_palettes.items():
        if name == target_name: continue

        comparison_lab = normalize_and_convert_lab(colors)

        dist = np.mean(np.sqrt(np.sum((target_lab - comparison_lab)**2, axis=2)))

        scores.append({"name": name, "score": float(dist)})


    return sorted(scores, key=lambda x: x['score'])[:20]


ALL_PALS = dict()

for jsfile in JSON_HF_PALS_DIR.glob('*.json'):
    with jsfile.open() as f:
        pal = json.load(f)


    ALL_PALS[jsfile.stem] = pal

with open(THIS_DIR / 'all-pals.json', 'w') as f:
    json.dump(ALL_PALS, f, indent=4)

results = {}

for name in ALL_PALS.keys():
    results[name] = get_top_10_matches(name, ALL_PALS)

with open(THIS_DIR / 'similar-pals.json', 'w') as f:
    json.dump(results, f, indent=4)

print("Calcul terminé ! Fichier 'similarities.json' prêt.")
