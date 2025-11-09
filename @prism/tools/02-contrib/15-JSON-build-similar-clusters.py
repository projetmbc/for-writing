#!/usr/bin/env python3

from pathlib import Path
import              sys

TOOLS_DIR = Path(__file__).parent.parent
sys.path.append(str(TOOLS_DIR))

from cbutils.core import *

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

IMAX = 3

THIS_DIR          = Path(__file__).parent
PROJ_DIR          = THIS_DIR.parent.parent
PRODS_DIR         = PROJ_DIR / "products"
HUMAN_CHOICES_DIR = PROJ_DIR / "tools-lab" / "human-choices" / "similar"


PAL_SIMILAR_JSON_FILE = PROJ_DIR / "tools" / "report" / "PAL-SIMILAR.json"
PAL_SIMILAR_JSON_FILE.touch()


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


# ------------- #
# -- EXTRACT -- #
# ------------- #

def extract_real_clusters(file: Path) -> [[str]]:
    blocks = [
        l.strip()
        for l in file.read_text().splitlines()
        if l.strip() and l.strip()[0] != "#"
    ]

    blocks = "\n".join(blocks)
    blocks = blocks.split('---')

    clusters = []

    for b in blocks:
        if not b:
            continue

        b = [
            p.strip()
            for p in b.split(',')
            if p.strip()
        ]

        for n in b:
            if not n in ALL_PALETTES:
                raise ValueError(
                    f"unknown palette '{n}'. See file:\n{file}"
                )

        if len(b) > 1:
            clusters.append(set(b))

    return sorted(clusters)


def update_clusters(
    all_clusters: [[str]],
    new_clusters: [[str]],
) -> [[str]]:
    for new_c in new_clusters:
        added = False

        for i, c in enumerate(all_clusters):
            if new_c & c:
                c |= new_c

                all_clusters[i] = c

                added = True
                break

        if not added:
            all_clusters.append(new_c)

    return all_clusters


# ------------------ #
# -- "CLUSTERIZE" -- #
# ------------------ #

logging.info("JSON file of similar palettes.")


all_clusters = []


# -- STEP 1 -- #

for file in HUMAN_CHOICES_DIR.rglob("01-*/new.txt"):
    clusters =  extract_real_clusters(file)

    if clusters:
        all_clusters += [set(c) for c in clusters]


# -- STEPS 2... -- #

for i in range(2, IMAX + 1):
    new_clusters = []

    for file in HUMAN_CHOICES_DIR.rglob(f"{i:02d}-*/new.txt"):
        new_clusters += extract_real_clusters(file)

    all_clusters = update_clusters(all_clusters, new_clusters)


# -- NOTHING LEFT TO DO -- #

all_clusters = sorted([
    sorted(list(c))
    for c in all_clusters
])

PAL_SIMILAR_JSON_FILE.write_text(
    json_dumps(all_clusters)
)
