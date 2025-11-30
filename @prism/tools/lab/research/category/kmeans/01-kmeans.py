#!/usr/bin/env python3

from pathlib import Path
import              sys


LAB_DIR = Path(__file__).parent

while LAB_DIR.name != "lab":
    LAB_DIR = LAB_DIR.parent

sys.path.append(str(LAB_DIR))

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


PAL_CATEGO_FILE = (
    PROJ_DIR / "tools" / "building" / "REPORT"
             / "PAL-CATEGORY.json"
)

with PAL_CATEGO_FILE.open('r') as f:
    ALL_CATEGOS = json_load(f)


if not CLUSTERS_DIR.is_dir():
    CLUSTERS_DIR.mkdir()

else:
    for p in CLUSTERS_DIR.glob("*"):
        p.unlink() if p.is_file() else rmtree(p)


ALL_CATEGO_DIRS = [
# Automated process starts with ''_''.
    MONOCHROME_DIR := CLUSTERS_DIR / "_monochrome",
    BICHROME_DIR   := CLUSTERS_DIR / "bicolor",
    TRICHROME_DIR  := CLUSTERS_DIR / "tricolor",
    MULTICHROME_DIR:= CLUSTERS_DIR / "_multicolor",
    RAINBOW_DIR    := CLUSTERS_DIR / "rainbow",
    BIF_VAR_DIR    := CLUSTERS_DIR / "big-var",
]

for dir in ALL_CATEGO_DIRS:
    dir.mkdir(exist_ok=True)


FOLDERS = {
    p.name: p
    for p in [
        MONOCHROME_DIR,
        BICHROME_DIR,
        TRICHROME_DIR,
        MULTICHROME_DIR,
    ]
}


CLUSTERING_FUNC = {
    MONOCHROME_DIR.name : is_monochrome,
    BICHROME_DIR.name   : is_bicolor,
    TRICHROME_DIR.name  : is_tricolor,
    MULTICHROME_DIR.name: lambda x: True
}


# ------------------ #
# -- NEW PALETTES -- #
# ------------------ #

print("+ Looking for new palettes.")

newpals = set()

categorized_names = sum(
    [
        names
        for catego, names in ALL_CATEGOS.items()
        if catego != '__UNCLASSIFIED__'
    ],
    []
)

for n in ALL_PALETTES:
    if not n in categorized_names:
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

for name in newpals:
    colors = ALL_PALETTES[name]

    for catego, clusterfunc in CLUSTERING_FUNC.items():
        if clusterfunc(colors):
            print(f"    - Adding '{name}' in '{catego}'.")

            create_palette_img(
                name   = name,
                colors = colors,
                folder = FOLDERS[catego]
            )

            break


print("+ Human selection needed.")

whatsnext = f"""
Place PNG images only in folders whose names do not
begin with an underscore.

Then, just invoke the Python file '02-human-version.py'
to obtain files 'new.txt' as a satrting point to
finalize the selection.
"""

whatsnext = whatsnext.strip().splitlines()

maxlen = max(len(l) for l in whatsnext)

rule = '-'*(maxlen + 4)

print(f"    {rule}")

for l in whatsnext:
    print(f"    | {l:<{maxlen}} |")

print(f"    {rule}")
