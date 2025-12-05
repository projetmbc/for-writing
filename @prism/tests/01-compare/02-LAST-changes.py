#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR.parent

while PROJ_DIR.name != "@prism":
    PROJ_DIR = PROJ_DIR.parent

TOOLS_DIR = PROJ_DIR / "tools" / "building"

sys.path.append(str(TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

import requests

from natsort import natsorted


# --------------- #
# -- CONSTANTS -- #
# --------------- #

JSON_PROD_DIR = PROJ_DIR / "products" / "json"
DATA_DIR      = THIS_DIR / "data"


LAST_UPDATES_JSON = DATA_DIR / f"LAST_UPDATES.json"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

LAST_PALETTES_JSON = DATA_DIR / f"LAST_PALETTES.json"

with LAST_PALETTES_JSON.open() as f:
    LAST_PALETTES = json_load(f)


DEV_PALETTES_JSON = JSON_PROD_DIR / f"palettes.json"

with DEV_PALETTES_JSON.open() as f:
    DEV_PALETTES = json_load(f)


# --------------------------- #
# -- TRACKING ONLY UPDATES -- #
# --------------------------- #

logging.info(
    "Looking for 'updated palettes' (no new / no removed)."
)

report = []

for palname, paldef in LAST_PALETTES.items():
    if (
        palname in DEV_PALETTES
        and
        paldef != DEV_PALETTES[palname]
    ):
        report.append(palname)

if report:
    report     = natsorted(report)
    nb_updates = len(report)

    plurial = "" if nb_updates == 1 else "s"

    logging.info(
        f"'{nb_updates} updated palette{plurial}' found."
    )

else:

    logging.info(
        "'No updated palette' found."
    )


logging.info("Build JSON report file.")

LAST_UPDATES_JSON.write_text(
    json_dumps(report)
)
