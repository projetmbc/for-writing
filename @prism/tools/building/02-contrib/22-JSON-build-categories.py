#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from collections import defaultdict

from json import (
    dumps as json_dumps,
    load  as json_load,
)

from natsort import natsorted


# --------------- #
# -- CONSTANTS -- #
# --------------- #

LAST_FILE_NAME      =  "last.txt"
TAG_UNCLASSIFIED    = "__UNCLASSIFIED__"
TAG_DEFICIENT_BLIND = "deficient-blind"


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR         = PROJ_DIR / "products"
HUMAN_CHOICES_DIR = PROJ_DIR / "tools" / "lab" / "human-choices" / "category"


PAL_CATEGO_JSON_FILE = BUILD_TOOLS_DIR / "REPORT" / "PAL-CATEGORY.json"
PAL_CATEGO_JSON_FILE.touch()


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


SCICOLMAP_NAMES_FILE = BUILD_TOOLS_DIR / "REPORT" / "NAMES-SCIENTIFIC-COLOUR-MAPS.json"

with SCICOLMAP_NAMES_FILE.open(mode = "r") as f:
    ALL_SCICOLMAP_NAMES = json_load(f)


# ----------- #
# -- TOOLS -- #
# ----------- #

def extract_names(file: Path) -> [str]:
    names = [
        l.strip()
        for l in file.read_text().splitlines()
        if l.strip() and l.strip()[0] != "#"
    ]

    for n in names:
        if not n in ALL_PALETTES:
            raise ValueError(
                f"unknown palette '{n}'. See file:\n{file}"
            )

    return sorted(names)


# -------------------- #
# -- HUMAN CLUSTERS -- #
# -------------------- #

logging.info("JSON file of palette categories.")


# -- HUMAN CHOICES -- #

all_categories  = defaultdict(list)
all_categorized = []

for file in sorted(HUMAN_CHOICES_DIR.rglob("*/last.txt")):
    catego = file.parent.name

    logging.info(f"Work on '{catego}/{file.name}'.")

    names = extract_names(file)

    all_categorized += names

    if names:
        all_categories[catego] = names


# -- NOT CLASSIFIED BY HUMAN -- #

nocatego = []

for n in ALL_PALETTES:
    if not n in all_categorized:
        nocatego.append(n)

if nocatego:
    nocatego.sort(key = lambda x: x.lower())

    all_categories[TAG_UNCLASSIFIED] = nocatego


# -- COLOUR-VISION DEFICIENT / COLOUR-BLIND PEOPLE -- #

logging.info(f"Work on 'Scientific Colour Maps'.")

for n in ALL_SCICOLMAP_NAMES:
    all_categories[TAG_DEFICIENT_BLIND].append(n)


# -- NOTHING LEFT TO DO -- #

PAL_CATEGO_JSON_FILE.write_text(
    json_dumps(all_categories)
)


# --------------------------------------------- #
# --  SOME UNCLASSIFIED ==> STOP THE PROCESS -- #
# --------------------------------------------- #

if all_categories[TAG_UNCLASSIFIED]:
    unclassified = all_categories[TAG_UNCLASSIFIED]

    plurial = "" if len(unclassified) == 1 else "s"

    unclassified = '\n    > '.join(
        n
        for n in unclassified
    )

    xtra = f"\nHere are the palette{plurial} to classify.\n    > {unclassified}"

    log_raise_error(
        context   = "Palette categories",
        desc      = "all palettes must be classified.",
        exception = ValueError,
        xtra      = xtra,
    )

del all_categories[TAG_UNCLASSIFIED]
del all_categories[TAG_DEFICIENT_BLIND]


# ---------------------------------------- #
# --  STD VERSION OF LAST HUMAN CHOICES -- #
# ---------------------------------------- #

logging.info(f"Standard version of 'last.txt' human choices (see 'tools/lab').")

TMPL_HEAD = """
# -------------------------- #
# -- Last Human Selection -- #
# -------------------------- #

# CATEGORY = '{catego}'
""".strip()

for catego, names in all_categories.items():
    last_file = HUMAN_CHOICES_DIR / catego / LAST_FILE_NAME

    content = [
        TMPL_HEAD.format(catego = catego),
        ''
    ]

    last_initial = ''

    for n in natsorted(names):
        if n[0] != last_initial:
            last_initial = n[0]

            content += [
                '',
                f"# -- {last_initial} -- #",
                '',
            ]

        content.append(n)

    content = '\n'.join(content)

    last_file.write_text(content)
