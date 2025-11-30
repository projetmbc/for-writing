#!/usr/bin/env python3

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(TOOLS_DIR))

from cbutils.core    import *
from cbutils.version import VERSION


from json import (
    dumps as json_dumps,
    load  as json_load,
)

import shutil


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR         = TOOLS_DIR.parent
PRODS_DIR        = PROJ_DIR / "products"
CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_JSON_CREDITS_FILE = PROD_JSON_DIR / "CREDITS.md"


CREDITS_TXT_FILE = THIS_DIR.parent / "CREDITS.txt"

CREDITS = CREDITS_TXT_FILE.read_text().strip()
CREDITS = CREDITS.format(VERSION = VERSION)


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

PAL_JSON_CREDITS_FILE.touch()
PAL_JSON_CREDITS_FILE.write_text(md_credtits)


# ------------------------------ #
# -- CONTRIB. IMPLEMENTATIONS -- #
# ------------------------------ #

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
    logging.info(f"'{ctxt}': copy structure.")

    fake_dir  = impl_folder / "fake-prod"
    final_dir = PRODS_DIR / ctxt

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
