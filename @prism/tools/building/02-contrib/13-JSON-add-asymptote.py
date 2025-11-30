#!/usr/bin/env python3

# Asymptote source code.
#     + https://github.com/vectorgraphics/asymptote/blob/master/base/palette.asy
#
#     + https://github.com/vectorgraphics/asymptote/blob/master/base/colormap.asy

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from collections import defaultdict

import requests


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

ASY_COLORMAP_RAW_URL = (
    "https://raw.githubusercontent.com/vectorgraphics/"
    "asymptote/master/base/colormap.asy"
)


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


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

CTXT = TAG_ASY


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR  = PROJ_DIR / "products"
REPORT_DIR = BUILD_TOOLS_DIR / "REPORT"


CTXT_FILE_NAME = CTXT.replace(' ', '-').upper()
NAMES_FILE     = REPORT_DIR / f"NAMES-{CTXT_FILE_NAME}.json"
ORIGINAL_NAMES = dict()


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)


PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"

with PAL_CREDITS_FILE.open(mode = "r") as f:
    PAL_CREDITS = json_load(f)


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


# ------------------------------- #
# -- FROM ASYMPTOTE COLOR MAPS -- #
# ------------------------------- #

logging.info(f"Work on the '{CTXT}' color maps.")


nb_new_pals = len(ALL_PALETTES)


for name, body in PATTERN_ASY_COLORMAP.findall(asy_code):
    std_name = stdname(name)

    if(
        std_name in ALL_PALETTES
        or
        std_name in PAL_REPORT[TAG_NAMES_IGNORED]
    ):
        continue

    pal_def = minimize_palette([
        [
            round(float(r), 4),
            round(float(g), 4),
            round(float(b), 4)
        ]
        for r, g, b in PATTERN_ASY_RGB.findall(body)
    ])

    aprism_name, ALL_PALETTES, PAL_REPORT = update_palettes(
        context   = CTXT,
        name      = std_name,
        candidate = pal_def,
        palettes  = ALL_PALETTES,
        ignored   = PAL_REPORT,
        logcom    = logging
    )

    ORIGINAL_NAMES[aprism_name] = name
    PAL_CREDITS[aprism_name]    = CTXT


nb_new_pals = resume_nbpals_build(
    context     = f"'{CTXT}' list of pens.",
    nb_new_pals = nb_new_pals,
    palettes    = ALL_PALETTES,
    logcom      = logging,
)


# --------------------------------------- #
# -- FROM ASYMPTOTE SEGMENTED PALETTES -- #
# --------------------------------------- #

# TODO_SEG_PALETTES

# logging.info(f"Work on the '{CTXT}' segmented palettes.")

# nb_asy_segpal = len(ALL_PALETTES)

# for name, body in PATTERN_ASY_SEGPAL.findall(asy_code):
#     std_name = stdname(name)

#     if std_name in STD_NAMES_IGNORED:
#         continue

#     logging.info(f"New palette from '{name}' segmented palette.")


# nb_asy_segpal = resume_nbpals_build(
#     context     = f"'{CTXT}' segmented palettes.",
#     nb_new_pals = nb_asy_segpal,
#     palettes    = ALL_PALETTES,
#     logcom      = logging,
# )


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

update_jsons(
    nb_new_pals = nb_new_pals,
    names       = ORIGINAL_NAMES,
    jsnames     = NAMES_FILE,
    credits     = PAL_CREDITS,
    jscredits   = PAL_CREDITS_FILE,
    reports     = PAL_REPORT,
    jsreports   = PAL_REPORT_FILE,
    palettes    = ALL_PALETTES,
    jspalettes  = PAL_JSON_FILE,
    logcom      = logging,
)
