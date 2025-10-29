#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *


from json import (
    dumps as json_dumps,
    load  as json_load,
)

import shutil


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR         = Path(__file__).parent
PROJECT_DIR      = THIS_DIR.parent.parent
PRODUCTS_DIR     = PROJECT_DIR / "products"
CONTRIB_PROD_DIR = PROJECT_DIR / "contrib" / "products"


PALETTES_JSON_FILE = PRODUCTS_DIR / "palettes.json"

with PALETTES_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PALETTES_JSON_CREDITS_FILE = PRODUCTS_DIR / "palettes.json.CREDITS.md"


CREDITS_TXT_FILE = THIS_DIR / "credits.txt"

CREDITS = CREDITS_TXT_FILE.read_text().strip()
CREDITS = CREDITS.format(VERSION = "1.2.0")


# ---------------------------------- #
# -- MD CREDITS FOR THE JSON FILE -- #
# ---------------------------------- #

# warning::
#     Credits in the JSON file via an extra key just complicates
#     its future used (this is a bad practice).

md_credtits = CREDITS  + '\n'
md_credtits = md_credtits.replace("''", "`")
md_credtits = re.sub(
    r'(https?://[^\s]+)',
    r'[\1](\1)',
    md_credtits
)

PALETTES_JSON_CREDITS_FILE.touch()
PALETTES_JSON_CREDITS_FILE.write_text(md_credtits)


# ------------------------------ #
# -- CONTRIB. IMPLEMENTATIONS -- #
# ------------------------------ #

contribs_accepted = get_accepted_paths(PROJECT_DIR)

impl_accepted = contribs_accepted.get(
    CONTRIB_PROD_DIR,
    []
)

for ctxt in sorted(impl_accepted):
    logging.info(f"'{ctxt}' implementation.")

    impl_folder = CONTRIB_PROD_DIR / ctxt

# Import extend.py.
    logging.info(f"'{ctxt}': import 'extend.py'.")

    extend = import_from_path(
        module_name = "extend",
        file_path   = impl_folder / "extend.py"
    )

# Fake prod to real prod.
    logging.info(f"'{ctxt}': copy structure.")

    fake_dir  = impl_folder / "fake-prod"
    final_dir = PRODUCTS_DIR / ctxt

    shutil.copytree(
        src = fake_dir,
        dst = final_dir,
    )

# The file of palettes.
    logging.info(f"'{ctxt}': add file of palettes.")

    code = extend.build_code(
        credits  = CREDITS,
        palettes = ALL_PALETTES
    )

    final_file = final_dir / extend.PALETTES_FILE_NAME

    final_file.parent.mkdir(
        parents  = True,
        exist_ok = True
    )

    final_file.write_text(code)


nb_impl = len(impl_accepted)

plurial = "" if nb_impl == 1 else "s"

logging.info(f"{nb_impl} implementation{plurial} added.")
