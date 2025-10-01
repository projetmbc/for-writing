#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json import load as json_load

# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent.parent / "data"

JSON_PALETTES = DATA_DIR / "palcol.json"


# ----------------------- #
# -- CONTRIBS ACCEPTED -- #
# ----------------------- #
