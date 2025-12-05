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


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

JSON_PALETTE_URL = (
    "https://raw.githubusercontent.com/"
    "projetmbc/for-writing/main/@prism/"
    "products/json/palettes.json"
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

DATA_DIR = THIS_DIR / "data"

DATA_DIR.mkdir(
    parents  = True,
    exist_ok = True
)

LAST_PALETTES_JSON = DATA_DIR / f"LAST_PALETTES.json"


# --------------------- #
# -- "LAST" PALETTES -- #
# --------------------- #

if LAST_PALETTES_JSON.is_file():
    logging.info("Nothing to do.")

else:
    logging.info("Try to get last 'MAIN palettes'.")

    try:
        resp               = requests.get(JSON_PALETTE_URL)
        last_main_palettes = resp.json()

    except requests.ConnectionError as e:
        logging.warning(
            f"No connection - We can't initialize de the data folder!"
        )

        exit(1)

    logging.info("Initiliaze data folder with 'last MAIN palettes'.")

    LAST_PALETTES_JSON.write_text(
        json_dumps(last_main_palettes)
    )
