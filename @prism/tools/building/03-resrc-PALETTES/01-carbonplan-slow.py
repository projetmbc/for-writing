#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

import ast


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

TAG_DARK  = 'dark'
TAG_LIGHT = 'light'


PATTERN_GET_KINDS = re.compile(r"\[.*\]", re.DOTALL)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[1]
THIS_RESRC = THIS_RESRC.upper()
THIS_RESRC = globals()[f"TAG_{THIS_RESRC}"]

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


_RESRC_PALS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_PALS_JSON  = REPORT_DIR / f"{_RESRC_PALS_JSON}.json"


# ---------------------- #
# -- FROM COLORBREWER -- #
# ---------------------- #

logging.info(f"Analyze '{THIS_RESRC}' source code")

# -- Original palette defs -- #

with (RESRC_DIR / "colormaps.json").open(mode = "r") as f:
    original_pals = json_load(f)

names_treated = set()
final_names   = set()

for name in original_pals:
    if name in names_treated:
        continue

    main_name, suffix = name.split('-')

    if suffix == TAG_DARK:
        print(f'{name = }')
        BUG

    dark_name = f'{main_name}-{TAG_DARK}'

    if original_pals[name] == original_pals[dark_name]:
        names_treated |= set([name, dark_name])

        final_names.add(main_name)


# -- Get palette kinds -- #

pycode = (RESRC_DIR / "colormaps.mjs").read_text()

match = PATTERN_GET_KINDS.search(pycode)

pycode = match.group(0)
pycode = re.sub(r'(\w+):', r'"\1":', pycode)

pal_kinds = ast.literal_eval(pycode)

name_2_kind = {
    data['name']: data['type']
    for data in pal_kinds
}

# -- @prism palette defs -- #

pals = dict()

for palname in sorted(final_names):
    palkind = name_2_kind[palname]

    stdname = get_stdname(palname)

    suffix  = '' if '-' in palname else f'-{TAG_LIGHT}'
    palname = f"{palname}{suffix}"

    paldef = original_pals[palname]

    pals[stdname] = resrc_std_palette(
        palname   = palname,
        palkind   = palkind,
        paldef    = paldef,
        precision = PAL_PRECISION + 2,
    )


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info(f"Update '{RESRC_PALS_JSON.relative_to(PROJ_DIR)}'")

pals = get_sorted_dict(pals)

RESRC_PALS_JSON.write_text(
    json_dumps(pals)
)
