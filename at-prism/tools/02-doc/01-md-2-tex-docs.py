#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core    import *
from cbutils.mdutils import *

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
PRODUCTS_DIR = PROJECT_DIR / "products"
CONTRIB_DIR  = PROJECT_DIR / "contrib"

CONTRIB_PRODUCTS   = CONTRIB_DIR / "products"
CONTRIB_EN_DOC_DIR = (
    CONTRIB_DIR / "translate" / "en"
                / "doc" / "manual" / "products"
)

PAL_JSON_FILE = PRODUCTS_DIR / "palettes.json"


with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)






converter = MdToLatexConverter()
