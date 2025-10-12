#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *


from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
PRODUCTS_DIR = PROJECT_DIR / "products"

PALETTES_JSON_FILE = PRODUCTS_DIR / "palettes.json"


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

    logging.info(f"Add '{ctxt}' implementation.")

    extend = import_from_path(
        module_name = "extend",
        file_path   = folder.parent / "extend.py"
    )

    code = []

    for name, data in palettes.items():
        code.append(extend.build_code(name, data))

    code = "\n".join(code)

    final_file = PRODUCTS_DIR / ctxt / extend.PALETTES_FILE_NAME

    final_file.parent.mkdir(
        parents  = True,
        exist_ok = True
    )

    final_file.write_text(code)


plurial = "" if nb_impl == 1 else "s"

logging.info(f"{nb_impl} implementation{plurial} added.")
