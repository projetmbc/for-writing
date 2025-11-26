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

CTXT = TAG_ASY


ASY_COLORMAP_RAW_URL = (
    "https://raw.githubusercontent.com/vectorgraphics/"
    "asymptote/master/base/colormap.asy"
)


THIS_DIR   = Path(__file__).parent
PROJ_DIR   = THIS_DIR.parent.parent
PRODS_DIR  = PROJ_DIR / "products"
REPORT_DIR = THIS_DIR.parent / "report"


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)


STD_NAMES_IGNORED = list(ALL_PALETTES) + list(PAL_REPORT)


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
    f"Get piece of '{CTXT}' source code (web connection needed)."
)

try:
    resp     = requests.get(ASY_COLORMAP_RAW_URL)
    asy_code = resp.text

except requests.ConnectionError as e:
    logging.warning(
        f"No connection - Ignoring '{CTXT}' color maps."
    )

    exit()


# ------------------------------------- #
# -- BUILD FROM ASYMPTOTE COLOR MAPS -- #
# ------------------------------------- #

logging.info(f"Work on the '{CTXT}' color maps.")


nb_new_pals = len(ALL_PALETTES)

for name, body in PATTERN_ASY_COLORMAP.findall(asy_code):
    std_name = stdname(name)

    if std_name in STD_NAMES_IGNORED:
        continue

    rgb_values = PATTERN_ASY_RGB.findall(body)

    pal_def = minimize_palette([
        [round(float(r), 4), round(float(g), 4), round(float(b), 4)]
        for r, g, b in rgb_values
    ])

    ALL_PALETTES, PAL_REPORT = update_palettes(
        context   = CTXT,
        name      = std_name,
        candidate = pal_def,
        palettes  = ALL_PALETTES,
        ignored   = PAL_REPORT,
        logcom    = logging
    )

    PAL_CREDITS[std_name] = CTXT


nb_new_pals = len(ALL_PALETTES) - nb_new_pals

if nb_new_pals == 0:
    logging.info("Nothing new found.")

else:
    plurial = "" if nb_new_pals == 1 else "s"

    logging.info(
        f"{nb_new_pals} palette{plurial} build from '{CTXT}' list of pens."
    )


# --------------------------------------------- #
# -- BUILD FROM ASYMPTOTE SEGMENTED PALETTES -- #
# --------------------------------------------- #

logging.info(f"Work on the '{CTXT}' segmented palettes.")

nb_asy_segpal = len(ALL_PALETTES)

for name, body in PATTERN_ASY_SEGPAL.findall(asy_code):
    std_name = stdname(name)

    if std_name in STD_NAMES_IGNORED:
        continue

    TODO_SEG_PALETTES

    logging.info(f"New palette from '{name}' segmented palette.")


nb_asy_segpal = len(ALL_PALETTES) - nb_asy_segpal

if nb_asy_segpal == 0:
    logging.info("Nothing new found.")


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

PAL_REPORT_FILE.write_text(json_dumps(PAL_REPORT))

if nb_new_pals + nb_asy_segpal != 0:
    logging.info("Update palette JSON file.")

    PAL_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
