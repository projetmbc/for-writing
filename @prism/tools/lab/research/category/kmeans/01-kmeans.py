#!/usr/bin/env python3

REBUILD = False
REBUILD = True

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

from pathlib import Path
import              sys


LAB_DIR = Path(__file__).parent

while LAB_DIR.name != "lab":
    LAB_DIR = LAB_DIR.parent

sys.path.append(str(LAB_DIR))

from labutils import *


from shutil  import rmtree

from json import load as json_load


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

THIS_DIR = Path(__file__).parent


PROJ_DIR = THIS_DIR

while PROJ_DIR.name != "@prism":
    PROJ_DIR = PROJ_DIR.parent


# We want an empty cluster directory.
CLUSTERS_DIR = THIS_DIR.parent / "clusters"

if not CLUSTERS_DIR.is_dir():
    CLUSTERS_DIR.mkdir()

else:
    for p in CLUSTERS_DIR.glob("*"):
        p.unlink() if p.is_file() else rmtree(p)


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


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

ALL_CATEGO_DIRNAMES = []
CLUSTERING_FUNCS    = []


for n in range(1, MAX_COL_SIZE + 1):
    varname = f"COLSIZE_{n}_DIRNAME"

    globals()[varname] = f"col-size-{n}"

    ALL_CATEGO_DIRNAMES.append(globals()[varname])

ALL_CATEGO_DIRNAMES += [
    RAINBOW_DIRNAME     := "rainbow",
    SEMANTIC_DIRNAME    := "semantic",
    UNCLASSIFIED_DIRNAME:= '__UNCLASSIFIED__'
]


no_implementation = lambda x: False
do_not_classify   = lambda x: True

CLUSTERING_FUNCS  = HAS_COLSIZE_FUNCS[:]
CLUSTERING_FUNCS += [
    no_implementation,
    no_implementation,
    do_not_classify
]

# Just add our category folders.
for catego_name in ALL_CATEGO_DIRNAMES:
    (CLUSTERS_DIR / catego_name).mkdir(exist_ok = True)


# ---------------------------- #
# -- CATEGORY NAME CHECKING -- #
# ---------------------------- #

project_categos = set(ALL_CATEGOS)
current_categos = set(
    n
    for n in ALL_CATEGO_DIRNAMES
    if n != UNCLASSIFIED_DIRNAME
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

print("+ Clustering the palettes.")

newpals = sorted(
    newpals,
    key = lambda n: n.lower()
)

for name in newpals:
    colors = ALL_PALETTES[name]

    for n, catego_name in enumerate(ALL_CATEGO_DIRNAMES):
        clusterfunc = CLUSTERING_FUNCS[n]

        if clusterfunc(colors):
            print(f"    - Adding '{name}' in '{catego_name}'.")

            create_palette_img(
                name   = name,
                colors = colors,
                folder = CLUSTERS_DIR / catego_name
            )

            break


# ---------------------- #
# -- FINAL CLUSTERING -- #
# ---------------------- #

print("+ Human selection needed.")

whatsnext = f"""
Place PNG images in folders other than'__UNCLASSIFIED__'.

Then, just invoke the Python file '02-human-version.py'
to obtain files 'new.txt' as a satrting point to finalize
the selection.
"""

whatsnext = whatsnext.strip().splitlines()

maxlen = max(len(l) for l in whatsnext)

rule = '-'*(maxlen + 4)

print(f"    {rule}")

for l in whatsnext:
    print(f"    | {l:<{maxlen}} |")

print(f"    {rule}")
