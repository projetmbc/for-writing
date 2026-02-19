#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = Path(__file__).parent

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT


# ----------------------------- #
# -- EMPTY THE REPORT FOLDER -- #
# ----------------------------- #

logging.info(
    f"Dynamic files - Clean '{AUDIT_DIR.relative_to(PROJ_DIR)}'"
)

AUDIT_DIR.mkdir(
    parents  = True,
    exist_ok = True
)

for dynafile in AUDIT_DIR.glob("AUDIT-*"):
    logging.warning(
        f"Remove '{dynafile.relative_to(PROJ_DIR)}'"
    )

    dynafile.unlink()
