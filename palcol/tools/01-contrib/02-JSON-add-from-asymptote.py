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

import requests


# --------------- #
# -- CONSTANTS -- #
# --------------- #

ASY_COLORMAP_RAW_URL = "https://raw.githubusercontent.com/vectorgraphics/asymptote/master/base/colormap.asy"

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent
CONTRIB_DIR = PROJECT_DIR / "contrib" / "palettes"
DATA_DIR    = THIS_DIR.parent.parent / "data"

PALETTES_JSON_FILE = DATA_DIR / "palettes.json"


PATTERN_ASY_COLORMAP = re.compile(
    r"list_data\s+([A-Za-z0-9_]+)\s*=.*\{([^}]+)\}",
    re.MULTILINE
)


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

palettes = {}

logging.info("Working on the Asymptote color maps (web connection needed).")

resp     = requests.get(ASY_COLORMAP_RAW_URL)
asy_code = resp.text

with PALETTES_JSON_FILE.open(mode = "r") as f:
    all_palettes = json_load(f)

all_names = [n.lower() for n in all_palettes]

matches = PATTERN_ASY_COLORMAP.findall(asy_code)

for name, body in matches:
    if name.lower() in all_names:
        continue

    TODO
    print(name)


if not palettes:
    logging.info("Nothing new found.")

else:
    TODO
