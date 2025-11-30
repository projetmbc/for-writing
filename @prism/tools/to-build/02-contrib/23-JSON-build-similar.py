#!/usr/bin/env python3

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

IMAX = 3


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR         = PROJ_DIR / "products"
HUMAN_CHOICES_DIR = PROJ_DIR / "tools" / "lab" / "human-choices" / "similar"


LAST_FILE = HUMAN_CHOICES_DIR / "last.txt"


PAL_SIMILAR_JSON_FILE = BUILD_TOOLS_DIR / "REPORT" / "PAL-SIMILAR.json"
PAL_SIMILAR_JSON_FILE.touch()


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


# ----------- #
# -- TOOLS -- #
# ----------- #

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


# def update_clusters(
#     all_clusters: [[str]],
#     new_clusters: [[str]],
# ) -> [[str]]:
#     for new_c in new_clusters:
#         added = False

#         for i, c in enumerate(all_clusters):
#             if new_c & c:
#                 c |= new_c

#                 all_clusters[i] = c

#                 added = True
#                 break

#         if not added:
#             all_clusters.append(new_c)

#     return all_clusters


# ------------------ #
# -- "CLUSTERIZE" -- #
# ------------------ #

logging.info("JSON file of similar palettes.")

if not LAST_FILE.is_file():
    logging.info(
        f"No '{LAST_FILE.name}' found."
    )

    all_clusters = []

else:
    logging.info(
        f"Work on '{LAST_FILE.name}'."
    )

    all_clusters = extract_real_clusters(LAST_FILE)
    all_clusters = sorted([
        sorted(list(c), key = lambda n: n.lower())
        for c in all_clusters
    ])

    if not all_clusters:
        message = "No cluster"

    else:
        nb_clusters = len(all_clusters)

        plurial = "" if nb_clusters == 1 else "s"
        message = f"{nb_clusters} cluster{plurial}"

    logging.info(
        f"'{message}' found."
    )


PAL_SIMILAR_JSON_FILE.write_text(
    json_dumps(all_clusters)
)
