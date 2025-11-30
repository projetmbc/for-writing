#!/usr/bin/env python3

# DEBUG - START
# from rich import print
# DEBUG - END

from typing import TypeAlias

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
PROJ_DIR  = THIS_DIR.parent
TOOLS_DIR = PROJ_DIR / "tools"

sys.path.append(str(TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

from shutil import rmtree

from datetime import datetime

import hashlib
import requests


# ------------ #
# -- TYPING -- #
# ------------ #

PaletteCols:TypeAlias = list[ [float, float, float] ]


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

JSON_PALETTE_URL = "https://raw.githubusercontent.com/projetmbc/for-writing/main/%40prism/products/json/palettes.json"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #
