#!/usr/bin/env python3

FORCING_ALL = True
FORCING_ALL = False

from pathlib import Path
import              sys


_utils_dir_ = Path(__file__).parent

while _utils_dir_.name != "tools-lab":
    _utils_dir_ = _utils_dir_.parent

sys.path.append(str(_utils_dir_))

from labutils import *


from shutil  import rmtree

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
CLUSTERS_DIR = THIS_DIR.parent / "clusters"


PROJ_DIR = THIS_DIR

while PROJ_DIR.name != "@prism":
    PROJ_DIR = PROJ_DIR.parent


PAL_JSON_FILE   = PROJ_DIR / "products" / "json" / "palettes.json"

with PAL_JSON_FILE.open('r') as f:
    ALL_PALETTES = json_load(f)


PAL_SIMILAR_FILE = PROJ_DIR / "tools" / "report" / "PAL-SIMILAR.json"

with PAL_SIMILAR_FILE.open('r') as f:
    ALL_CLUSTERS = json_load(f)


LAST_HUMAN_CHOICES_FILE = (
    PROJ_DIR / "tools-lab" / "human-choices"
             / "similar" / "last.txt"
)

if not LAST_HUMAN_CHOICES_FILE.is_file():
    LAST_HUMAN_CHOICES_FILE.touch()


CLUSTER_METHODS = [
    'euclidean',
    'cosine'
]

for meth in CLUSTER_METHODS:
    folder = CLUSTERS_DIR / meth

    if not folder.is_dir():
        folder.mkdir(parents = True)

    else:
        for p in folder.glob("*"):
            p.unlink() if p.is_file() else rmtree(p)


# ---------------------------- #
# -- UNCLUSTERIZED PALETTES -- #
# ---------------------------- #

print("+ Looking for unclusterized palettes.")

if FORCING_ALL:
    print("+ Forcing all palettes.")
    newpals = list(ALL_PALETTES)

else:
    newpals = set()

# Clusterized.
    ignored_names = sum(ALL_CLUSTERS, [])

# False positives.
    false_pos = LAST_HUMAN_CHOICES_FILE.read_text()
    false_pos = sum(
        [
            l[2:].split(',')
            for l in false_pos.splitlines()
            if l[:2] == "#:"
        ],
        []
    )

    for fp in false_pos:
        fp = fp.strip()

        if fp:
            ignored_names.append(fp)

# Needed names.
    ignored_names = set(ignored_names)

    for n in ALL_PALETTES:
        if not n in ignored_names:
            newpals.add(n)

    if not newpals:
        print("+ No new palette.")

        exit()

    nb_pals = len(newpals)

    plurial = "" if nb_pals == 1 else "s"

    print(f"+ {nb_pals} palette{plurial} to analyze.")


# ---------------- #
# -- CLUSTERING -- #
# ---------------- #

print("+ Clustering the palettes.")

newpals = list(newpals)
newpals.sort(key = lambda n: n.lower())

# DEBUG
# [print(name) for name in newpals];exit()
# print(", ".join(name for name in newpals));exit()


for meth in CLUSTER_METHODS:
    print(f"+ Using '{meth}' method...")

    for name in newpals:
        print(f"    - [{meth}] Working on '{name}'.")

        similar_names = find_similar_palettes(
            target_name  = name,
            palettes     = ALL_PALETTES,
            cluster_size = 29,
            method       = meth
        )

        similar_names = [name] + [name for name, _ in similar_names]

        create_palette_grid(
            palnames = similar_names,
            palettes = ALL_PALETTES,
            title    = f"'{name}' family.",
            file_    = CLUSTERS_DIR / meth / f'{name}.png'
        )

print(f"+ Full list.")
print(', '.join(newpals))
