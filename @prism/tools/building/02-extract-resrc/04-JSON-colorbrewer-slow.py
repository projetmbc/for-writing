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


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

THIS_RESRC = TAG_COLORBREWER

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_XTRA_RESRC / get_stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


RESRC_PALS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_PALS_JSON = REPORT_DIR / f"{RESRC_PALS_JSON}.json"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PRECISION = YAML_CONFIG['PRECISION']


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

ORIGINAL_RESRC_PALS_JSON = RESRC_DIR / f"{THIS_RESRC.lower()}.json"

with ORIGINAL_RESRC_PALS_JSON.open(mode = "r") as f:
    ORIGINAL_RESRC_PALS = json_load(f)


# ----------- #
# -- TOOLS -- #
# ----------- #

def extract_palette(pal_data: dict) -> [str, PaletteCols]:
    kind = pal_data["type"]

    max_size = max(
        int(k)
        for k in pal_data
        if k != "type"
    )

    max_size = str(max_size)

    paldef = pal_data[str(max_size)]
    paldef = pal255_to_pal01([
        eval(c.replace("rgb", ""))
        for c in paldef
    ])

    return kind, paldef


# ---------------------- #
# -- FROM COLORBREWER -- #
# ---------------------- #

logging.info(f"Analyzing '{THIS_RESRC}' source code.")

pals = dict()

for palname, pal_data in ORIGINAL_RESRC_PALS.items():
    stdname = get_stdname(palname)

    pal_kind, paldef = extract_palette(pal_data)

    pals[stdname] = resrc_std_palette(
        palname   = palname,
        pal_kind  = pal_kind,
        paldef    = paldef,
        precision = PRECISION + 2,
    )


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info(f"'{RESRC_PALS_JSON.relative_to(PROJ_DIR)}' update.")

RESRC_PALS_JSON.write_text(
    json_dumps(pals)
)
