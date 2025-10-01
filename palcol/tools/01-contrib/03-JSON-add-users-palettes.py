#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent
CONTRIB_DIR = PROJECT_DIR / "contrib" / "palettes"
DATA_DIR    = THIS_DIR.parent.parent / "data"

PALETTES_JSON_FILE = DATA_DIR / "palettes.json"


# ----------- #
# -- TOOLS -- #
# ----------- #

PATTERN_COLOR_DEF = re.compile(
    r"--PALETTE-\d+\s*:([^;\n]+)[;\n]"
)

PATTERN_RGB_VARS = re.compile(
    r"rgb\(([^,]+)\s*,\s*([^,]+)\s*,\s*([^,]+)\s*\)"
)

def extract_from_css(pathfile):
    code = pathfile.read_text()

    matches = PATTERN_COLOR_DEF.findall(code)

    if not matches:
        BUG_1

    for onecol in matches:
        onecol = onecol.strip()

# HTML hexadecimal coding.
        if onecol[0] == '#':
            TODO

# RGB coding with %, or without.
        elif onecol[:3] == 'rgb':
            match = PATTERN_RGB_VARS.search(onecol)

            if not match:
                BUG_2

            if len(match.groups()) != 3:
                BUG_2_bis

            r, g, b = normalize_rgb(match.groups())

            print(f"[{r}][{g}][{b}]")

# Unsupported color coding.
        else:
            BUG_3


    exit()

    return r, g, b


def normalize_rgb(vals):
    return map(normalize_one_css_rgb, vals)


def normalize_one_css_rgb(one_rgb_val):
    return f"<{one_rgb_val}>"


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

with PALETTES_JSON_FILE.open(mode = "r") as f:
    all_palettes = json_load(f)

for folder, contribs in get_accepted_paths(PROJECT_DIR).items():
    ctxt = folder.parent.name

    logging.info(f"Working on '{ctxt}'.")

    for one_contrib in contribs:
        contrib_file = folder / one_contrib

        this_palette = extract_from_css(contrib_file)
