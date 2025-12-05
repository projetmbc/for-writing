#!/usr/bin/env python3

REBUILD = False
# REBUILD = True


from pathlib import Path
import              sys


# ----------------------------- #
# -- IMPORT LABUTILS - START -- #

LAB_DIR = Path(__file__).parent

while LAB_DIR.name != "lab":
    LAB_DIR = LAB_DIR.parent

sys.path.append(str(LAB_DIR))

from labutils import *

# -- IMPORT LABUTILS - END -- #
# --------------------------- #


from shutil  import rmtree

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = Path(__file__).parent


PROJ_DIR = THIS_DIR

while PROJ_DIR.name != "@prism":
    PROJ_DIR = PROJ_DIR.parent


# We want an empty cluster directory.
CLUSTERS_DIR = THIS_DIR / "clusters"

if not CLUSTERS_DIR.is_dir():
    CLUSTERS_DIR.mkdir()

else:
    for p in CLUSTERS_DIR.glob("*"):
        p.unlink() if p.is_file() else rmtree(p)


AUTOBUILD_DIR = CLUSTERS_DIR / '__AUTOBUILD__'
AUTOBUILD_DIR.mkdir(exist_ok = True)


# Just add our category folders.
for catego_name in ALL_CATEGO_TAGS:
    (CLUSTERS_DIR / catego_name).mkdir(exist_ok = True)
    (AUTOBUILD_DIR / catego_name).mkdir(exist_ok = True)


PAL_JSON_FILE = PROJ_DIR / "products" / "json" / "palettes.json"

with PAL_JSON_FILE.open('r') as f:
    ALL_PALETTES = json_load(f)


if REBUILD:
    ALL_CATEGOS = dict()

else:
    PAL_CATEGO_FILE = (
        PROJ_DIR / "tools" / "building" / "REPORT"
                 / "PAL-CATEGORY.json"
    )

    with PAL_CATEGO_FILE.open('r') as f:
        ALL_CATEGOS = json_load(f)

    if 'deficient-blind' in ALL_CATEGOS:
        del ALL_CATEGOS['deficient-blind']


# ---------------------------- #
# -- CATEGORY NAME CHECKING -- #
# ---------------------------- #

project_categos = set(ALL_CATEGOS)
current_categos = set(
    n
    for n in ALL_CATEGO_TAGS
    if n != TAG_CATEGO_NO_CATEGO_FOUND
)

xtra_categos = project_categos - current_categos

if xtra_categos:
    xtra_categos    = sorted(xtra_categos)
    nb_xtra_categos = len(xtra_categos)

    plurials = "" if xtra_categos == 1 else "s"

    raise ValueError(
        f"{nb_xtra_categos} extra catego{plurials} found in the project:"
        f"{'\n  + '.join([''] + xtra_categos)}"
           "\n"
           "\n    ----------------------------------------"
           "\n    | Use 'REBUILD = True' in this script. |"
           "\n    ----------------------------------------"
    )


# ------------------ #
# -- NEW PALETTES -- #
# ------------------ #

print("+ Looking for new palettes.")

newpals = set()

categorized_names = sum(list(ALL_CATEGOS.values()), [])

for n in ALL_PALETTES:
    if not n in categorized_names:
        newpals.add(n)

if not newpals:
    print("+ No new palette.")

    exit()


nb_pals = len(newpals)
plurial = "" if nb_pals == 1 else "s"

print(f"+ {nb_pals} palette{plurial} to analyze.")


# ------------------- #
# -- PRECLUSTERING -- #
# ------------------- #

print("+ Pre-clustering the palettes.")

newpals = sorted(
    newpals,
    key = lambda n: n.lower()
)

pals_to_classify = {
    name: ALL_PALETTES[name]
    for name in newpals
    if name in newpals
}

categos = classify_palettes(pals_to_classify)


for catego, names in categos.items():
    if not names:
        continue

    nb_pals = len(names)
    plurial = "" if nb_pals == 1 else "s"

    print(f"    - '{catego}' with {nb_pals} palette{plurial}.")

    categodir = AUTOBUILD_DIR / catego

    for n in names:
        create_palette_img(
            name   = n,
            colors = ALL_PALETTES[n],
            folder = categodir
        )


# ---------------------- #
# -- FINAL CLUSTERING -- #
# ---------------------- #

print("+ Human selection needed.")

whatsnext = f"""
Move PNG images from '{AUTOBUILD_DIR.name}' folders outside into
the good category folder.

Then, just invoke the Python file '02-human-version.py'
such as to obtain files 'human-choices/category/new.txt'
as a satrting point to finalize the selection.
"""

whatsnext = whatsnext.strip().splitlines()

maxlen = max(len(l) for l in whatsnext)

rule = '-'*(maxlen + 4)

print(f"    {rule}")

for l in whatsnext:
    print(f"    | {l:<{maxlen}} |")

print(f"    {rule}")
