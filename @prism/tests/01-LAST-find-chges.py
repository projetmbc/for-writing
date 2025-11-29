#!/usr/bin/env python3

# DEBUG - START
from rich import print
# DEBUG - END


from typing import Any, Optional, TypeAlias

from pathlib import Path
import              sys

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR.parent

sys.path.append(str(PROJ_DIR / "tools"))

from cbutils.core import *
from cbutils      import *

from shutil import rmtree

import requests
import hashlib


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PaletteCols:TypeAlias = list[[float, float, float]]


JSON_PALETTE_URL = "https://raw.githubusercontent.com/projetmbc/for-writing/main/%40prism/products/json/palettes.json"


REPORT_DIR    = THIS_DIR  / "report"
PROD_JSON_DIR = PROJ_DIR / "products" / "json"


PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    DEV_PALETTES = json_load(f)


if REPORT_DIR.is_dir():
    rmtree(str(REPORT_DIR))

REPORT_DIR.mkdir(
    parents  = True,
    exist_ok = True,
)


ADDITIONS = {
    (TAG_REMOVED:= 'removed'): None,
    (TAG_UPDATED:= 'updated'): None,
    (TAG_NEW    := 'new')    : None,
}

FILE_NAMES = {
    t: f"{t.upper()}.json"
    for t in ADDITIONS
}


# ----------- #
# -- TOOLS -- #
# ----------- #

def compute_palette_hash(palette: PaletteCols) -> str:
    palette_json = json_dumps(
        palette,
        sort_keys    = True,
        ensure_ascii = False
    )

    return hashlib.sha256(
        palette_json.encode('utf-8')
    ).hexdigest()


# ------------------- #
# -- HASH BUILDING -- #
# ------------------- #

logging.info("Building online 'hashes of last main'.")

response = requests.get(JSON_PALETTE_URL)
response.raise_for_status()

MAIN_PALETTES = response.json()

main_hashes = {
    n: compute_palette_hash(p)
    for n, p in MAIN_PALETTES.items()
}


logging.info("Building local 'hashes of dev version'.")

dev_hashes = {
    n: compute_palette_hash(p)
    for n, p in DEV_PALETTES.items()
}


# ---------------------- #
# -- GET REAL CHANGES -- #
# ---------------------- #

logging.info("Looking for 'dev additions'.")

ADDITIONS[TAG_REMOVED] = sorted(set(main_hashes) - set(dev_hashes))
ADDITIONS[TAG_NEW]     = sorted(set(dev_hashes) - set(main_hashes))
ADDITIONS[TAG_UPDATED] = sorted(
    n
    for n in main_hashes
    if (
        not n in ADDITIONS[TAG_REMOVED]
        and
        dev_hashes[n] != main_hashes[n]
    )
)


# ---------------- #
# -- REPORT ALL -- #
# ---------------- #

logging.info("Report 'dev additions' in JSON files.")

for tag, filename in FILE_NAMES.items():
    (REPORT_DIR / filename).write_text(
        json_dumps(ADDITIONS[tag])
    )

(REPORT_DIR / "MAIN-PALS.json").write_text(
    json_dumps(MAIN_PALETTES)
)

(REPORT_DIR / "DEV-PALS.json").write_text(
    json_dumps(DEV_PALETTES)
)
