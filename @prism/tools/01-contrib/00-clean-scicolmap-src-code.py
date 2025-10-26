#!/usr/bin/env python3

from pathlib import Path
from shutil  import rmtree

# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR          = Path(__file__).parent
PROJECT_DIR       = THIS_DIR.parent.parent
SCICOLMAP_SRC_DIR = PROJECT_DIR / "x-ScientificColourMaps8-x"


# --------------------------------- #
# -- CLEANING SOURCE CODE FOLDER -- #
# --------------------------------- #

if not SCICOLMAP_SRC_DIR.is_dir():
    exit(0)

for p in SCICOLMAP_SRC_DIR.glob("*"):
    if p.name.startswith('+') and p.is_dir():
        rmtree(p)


for p in SCICOLMAP_SRC_DIR.glob("*"):
    if p.is_file():
        p.unlink()
        continue

    for sp in p.glob("*"):
        if sp.is_dir():
            rmtree(sp)

        elif sp.suffix != '.py':
            sp.unlink()
