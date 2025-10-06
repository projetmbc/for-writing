#!/usr/bin/env python3

# Asymptote sourc code.
#     + https://github.com/vectorgraphics/asymptote/blob/master/base/palette.asy
#     + https://github.com/vectorgraphics/asymptote/blob/master/base/colormap.asy

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json import (
    dumps as json_dumps,
    load  as json_load,
)

from string import ascii_letters, digits

import requests

import numpy as np


# --------------- #
# -- CONSTANTS -- #
# --------------- #

ASY_COLORMAP_RAW_URL = (
    "https://raw.githubusercontent.com/vectorgraphics/"
    "asymptote/master/base/colormap.asy"
)

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent
CONTRIB_DIR = PROJECT_DIR / "contrib" / "palettes"
DATA_DIR    = THIS_DIR.parent.parent / "data"

PALETTES_JSON_FILE = DATA_DIR / "palettes.json"

with PALETTES_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


CHARS_ALLOWED = set(ascii_letters + digits)


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


# --------------- #
# -- FORMATTER -- #
# --------------- #

def _capitalize(n):
    return n[0].upper() + n[1:]

def stdname(n):
    letters = set(n)

    if not letters <= CHARS_ALLOWED:
        for c in letters - CHARS_ALLOWED:
            n = ''.join([
                _capitalize(p)
                for p in n.split(c)
            ])

    else:
        n = _capitalize(n)

    return n


# --------------------- #
# -- GET SOURCE CODE -- #
# --------------------- #

logging.info("Get piece of 'Asymptote' source code (web connection needed).")

resp     = requests.get(ASY_COLORMAP_RAW_URL)
asy_code = resp.text


# ------------------------------------- #
# -- BUILD FROM ASYMPTOTE COLOR MAPS -- #
# ------------------------------------- #

logging.info("Work on the 'Asymptote' color maps.")

nb_asy_cmps = 0

for name, body in PATTERN_ASY_COLORMAP.findall(asy_code):
    name = stdname(name)

    if name in ALL_PALETTES:
        continue

    nb_asy_cmps += 1

    rgb_values = PATTERN_ASY_RGB.findall(body)

    ALL_PALETTES[name] = [
        [round(float(r), 4), round(float(g), 4), round(float(b), 4)]
        for r, g, b in rgb_values
    ]

    logging.info(f"New palette from '{name}' color map.")


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

nb_asy_segpal = 0

for name, body in PATTERN_ASY_SEGPAL.findall(asy_code):
    name = stdname(name)

    if name in ALL_PALETTES:
        continue

    nb_asy_segpal += 1

    TODO

    logging.info(f"New palette from '{name}' segmented palette.")


if nb_asy_segpal == 0:
    logging.info("Nothing new found.")


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

if nb_asy_cmps + nb_asy_segpal != 0:
    logging.info("Update palette JSON file.")

    PALETTES_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
