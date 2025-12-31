#!/usr/bin/env python3

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

from json import load  as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR        = PROJ_DIR / "products"
CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_JSON_CREDITS_FILE = PROD_JSON_DIR / "CREDITS.md"


CREDITS_TXT_FILE = THIS_DIR.parent / "CREDITS.txt"

CREDITS = CREDITS_TXT_FILE.read_text().strip()
CREDITS = CREDITS.format(VERSION = VERSION)


# ---------------- #
# -- LET'S WORK -- #
# ---------------- #

logging.info("Update 'contrib palette files'.")

contribs_accepted = get_accepted_paths(PROJ_DIR)

impl_accepted = contribs_accepted.get(
    CONTRIB_PROD_DIR,
    []
)

for ctxt in sorted(impl_accepted, key = lambda x: x.lower()):
    logging.info(f"'{ctxt}' implementation.")

    impl_folder = CONTRIB_PROD_DIR / ctxt

# Import extend.py.
    logging.info(f"'{ctxt}': import 'extend.py'.")

    extend = import_from_path(
        module_name = "extend",
        file_path   = impl_folder / "extend.py"
    )

# Fake prod to real prod.
    logging.info(f"'{ctxt}': update '{extend.PALETTES_FILE_NAME}'.")

    code = extend.build_code(
        credits  = CREDITS,
        palettes = ALL_PALETTES
    )

    contrib_file = CONTRIB_PROD_DIR / ctxt / extend.PALETTES_FILE_NAME

    contrib_file.parent.mkdir(
        parents  = True,
        exist_ok = True
    )

    contrib_file.write_text(code)
