#!/usr/bin/env python3

from pathlib import Path
from shutil  import rmtree


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent
PRODUCT_DIR = PROJECT_DIR / "products"


# --------------------------------- #
# -- EMPTY PRODUCTS FOLDER EMPTY -- #
# --------------------------------- #

if not PRODUCT_DIR.is_dir():
    PRODUCT_DIR.mkdir()

else:
    for p in PRODUCT_DIR.glob("*"):
        p.unlink() if p.is_file() else rmtree(p)
