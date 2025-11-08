#!/usr/bin/env python3

from pathlib import Path

from json import dumps as json_dumps


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR          = Path(__file__).parent
PROJ_DIR          = THIS_DIR.parent
HUMAN_CHOICES_DIR = THIS_DIR / "human-choices"

PAL_CATEGO_JSON_FILE = PROJ_DIR / "tools" / "report" / "PAL-CATEGO.json"
PAL_CATEGO_JSON_FILE.touch()


# ------------- #
# -- EXTRACT -- #
# ------------- #

def extract_real_clusters(file: Path) -> [[str]]:
    blocks = file.read_text()
    blocks = blocks.split('---')

    clusters = []

    for b in blocks:
        b = b.strip()
        b = [
            p.strip()
            for p in b.split(',')
            if p.strip()
        ]

        if len(b) > 1:
            clusters.append(sorted(b))

    return sorted(clusters)



# ------------------ #
# -- "CLUSTERIZE" -- #
# ------------------ #

all_clusters = []


# -- STEP 1 -- #

for file in HUMAN_CHOICES_DIR.rglob("01-*/*.txt"):
    clusters =  extract_real_clusters(file)

    if clusters:
        all_clusters += clusters


# -- STEP 2 -- #

new_clusters = []

for file in HUMAN_CHOICES_DIR.rglob("02-*/*.txt"):
    clusters = extract_real_clusters(file)

    for c in clusters:
        for i, allc in enumerate(all_clusters):
            set_allc = set(allc)
            set_c    = set(c)

            if set_allc.intersection(set_c) or set_c.intersection(set_allc):
                set_allc |= set_c
                all_clusters[i] = list(set_allc)
                break

            elif not c in new_clusters:
                new_clusters.append(c)
                break

all_clusters += new_clusters


# -- NOTHING LEFT TO DO -- #

all_clusters = sorted([
    sorted(c)
    for c in all_clusters
])

PAL_CATEGO_JSON_FILE.write_text(
    json_dumps(
        obj       = all_clusters,
        indent    = 2,
        sort_keys = True,
    )
)
