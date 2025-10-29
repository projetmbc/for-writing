#!/usr/bin/env python3

# Asymptote source code.
#     + https://github.com/vectorgraphics/asymptote/blob/master/base/palette.asy
#     + https://github.com/vectorgraphics/asymptote/blob/master/base/colormap.asy

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from collections import defaultdict

from json import (
    dumps as json_dumps,
    load  as json_load,
)

import requests


# --------------- #
# -- CONSTANTS -- #
# --------------- #

ASY_COLORMAP_RAW_URL = (
    "https://raw.githubusercontent.com/vectorgraphics/"
    "asymptote/master/base/colormap.asy"
)

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
PRODUCTS_DIR = PROJECT_DIR / "products"

PAL_JSON_FILE   = PRODUCTS_DIR / "palettes.json"
MP_NAMES_FILE   = THIS_DIR / "mp-names.json"
PAL_REPORT_FILE = THIS_DIR / "pal-report.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)

with MP_NAMES_FILE.open(mode = "r") as f:
    ALL_MP_NAMES = json_load(f)

with PAL_REPORT_FILE.open(mode = "r") as f:
    IGNORED = json_load(f)


PATTERN_ASY_COLORMAP = re.compile(
    r"list_data\s+([A-Za-z0-9_]+)\s*=.*\{([^}]+)\}",
    re.MULTILINE
)

PATTERN_ASY_RGB = re.compile(
    r"rgb\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)"
)

PATTERN_ASY_SEGPAL = re.compile(
    r"seg_data\s+(\w+)\s*=\s*seg_data\s*\((.*?)\);",
    re.S
)

PATTERN_ASY_TRIPLE = re.compile(
    r"new triple\[\]\s*{(.*?)}",
    re.S
)

PATTERN_ASY_CHANNEL = re.compile(
    r"\(([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\)"
)


# --------------------- #
# -- GET SOURCE CODE -- #
# --------------------- #

logging.info(
    "Get piece of 'Asymptote' source code (web connection needed)."
)

resp     = requests.get(ASY_COLORMAP_RAW_URL)
asy_code = resp.text


# ------------------------------------- #
# -- BUILD FROM ASYMPTOTE COLOR MAPS -- #
# ------------------------------------- #

logging.info("Work on the 'Asymptote' color maps.")


nb_asy_cmps = len(ALL_PALETTES)

for name, body in PATTERN_ASY_COLORMAP.findall(asy_code):
    name = stdname(name)

    if name in ALL_MP_NAMES:
        continue

    rgb_values = PATTERN_ASY_RGB.findall(body)

    candidate = minimize_palette([
        [round(float(r), 4), round(float(g), 4), round(float(b), 4)]
        for r, g, b in rgb_values
    ])

    ALL_PALETTES, IGNORED = update_palettes(
        name,
        candidate,
        ALL_PALETTES,
        IGNORED,
        logging
    )

nb_asy_cmps = len(ALL_PALETTES) - nb_asy_cmps

if nb_asy_cmps == 0:
    logging.info("Nothing new found.")

else:
    plurial = "" if nb_asy_cmps == 1 else "s"

    logging.info(
        f"{nb_asy_cmps} palette{plurial} build from 'Asymptote' list of pens."
    )


# --------------------------------------------- #
# -- BUILD FROM ASYMPTOTE SEGMENTED PALETTES -- #
# --------------------------------------------- #

logging.info("Work on the 'Asymptote' segmented palettes.")

nb_asy_segpal = len(ALL_PALETTES)

for name, body in PATTERN_ASY_SEGPAL.findall(asy_code):
    name = stdname(name)

    if name in ALL_MP_NAMES:
        continue

    TODO_SEG_PALETTES

    logging.info(f"New palette from '{name}' segmented palette.")


nb_asy_segpal = len(ALL_PALETTES) - nb_asy_segpal

if nb_asy_segpal == 0:
    logging.info("Nothing new found.")


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

PAL_REPORT_FILE.write_text(json_dumps(IGNORED))

if nb_asy_cmps + nb_asy_segpal != 0:
    logging.info("Update palette JSON file.")

    PAL_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
