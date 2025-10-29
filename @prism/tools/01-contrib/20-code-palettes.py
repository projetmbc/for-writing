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

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
PRODUCTS_DIR = PROJECT_DIR / "products"

PALETTES_JSON_FILE         = PRODUCTS_DIR / "palettes.json"
PALETTES_JSON_CREDITS_FILE = PRODUCTS_DIR / "palettes.json.CREDITS.md"

VERSION = "1.2.0"

CREDITS = f"""
File created by the ''@prism'' project, version {VERSION}

''@prism'', that will be available soon on PyPI, is developed at
https://github.com/projetmbc/for-writing/tree/main/@prism .
""".strip()


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

with PALETTES_JSON_FILE.open(mode = "r") as f:
    palettes = json_load(f)

contribs_accepted = get_accepted_paths(PROJECT_DIR)

nb_impl = 0

for folder in sorted(contribs_accepted):
    nb_impl += 1

    ctxt = folder.parent.name

    logging.info(f"'{ctxt}' implementation.")

# Import extend.py.
    logging.info(f"'{ctxt}': import 'extend.py'.")

    extend = import_from_path(
        module_name = "extend",
        file_path   = folder.parent / "extend.py"
    )

# Fake prod to real prod.
    logging.info(f"'{ctxt}': copy structure.")

    fake_dir  = folder.parent / "fake-prod"
    final_dir = PRODUCTS_DIR / ctxt

    shutil.copytree(
        src = fake_dir,
        dst = final_dir,
    )

# The file of palettes.
    logging.info(f"'{ctxt}': add file of palettes.")

    extend = import_from_path(
        module_name = "extend",
        file_path   = folder.parent / "extend.py"
    )

    code = extend.build_code(
        credits  = CREDITS,
        palettes = palettes
    )

    final_file = final_dir / extend.PALETTES_FILE_NAME

    final_file.parent.mkdir(
        parents  = True,
        exist_ok = True
    )

    final_file.write_text(code)


plurial = "" if nb_impl == 1 else "s"

logging.info(f"{nb_impl} implementation{plurial} added.")
