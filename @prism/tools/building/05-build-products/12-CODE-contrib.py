exit(1)



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

from json import (
    dumps as json_dumps,
    load  as json_load,
)

from shutil import copytree, rmtree


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

VERSION = (BUILD_TOOLS_DIR / 'VERSION.txt').read_text()

CREDITS = (BUILD_TOOLS_DIR / 'CREDITS.txt').read_text()
CREDITS = CREDITS.strip()
CREDITS = CREDITS.format(VERSION = VERSION)


AUTO_QUAL_CATEGO_SIZE = YAML_CONFIGS['SEMANTIC']['AUTO_QUAL_CATEGO_SIZE']


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"

PRODS_DIR     = PROJ_DIR / "products"
PROD_JSON_DIR = PRODS_DIR / "json"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

CONTRIBS_ACCEPTED = get_accepted_paths(PROJ_DIR)

IMPL_ACCEPTED = CONTRIBS_ACCEPTED.get(
    CONTRIB_PROD_DIR,
    []
)


# ------------------ #
# -- GET PAL DICT -- #
# ------------------ #

logging.info(f"Get 'JSON palette defs'")


HIGH_PAL_JSON_FILE = PROD_JSON_DIR / "palettes-hf.json"

with HIGH_PAL_JSON_FILE.open(mode = "r") as f:
    HIGH_PALETTES = json_load(f)


NORM_PAL_JSON_FILE = PROD_JSON_DIR / f"palettes-s{AUTO_QUAL_CATEGO_SIZE}.json"

with NORM_PAL_JSON_FILE.open(mode = "r") as f:
    NORM_PALETTES = json_load(f)


# ----------------------------------- #
# -- MONOLITHIC & MODULAR VERSIONS -- #
# ----------------------------------- #

# -- DEBUG - ON -- #
rmtree(PRODS_DIR / 'css')
# -- DEBUG - OFF -- #

for ctxt in sorted(
    IMPL_ACCEPTED,
    key = lambda x: x.lower()
):
    logging.info(f"Implement '{ctxt}'")

    impl_folder = CONTRIB_PROD_DIR / ctxt

# Import extend.py.
    logging.info(f"({ctxt}) Import 'extend.py'")

    extend = import_from_path(
        module_name = "extend",
        file_path   = impl_folder / "extend.py"
    )

# Fake prod to real prod.
    logging.info(f"({ctxt}) Copy structure")

    fake_dir  = impl_folder / "fake-prod"
    final_dir = PRODS_DIR / ctxt

    copytree(
        src = fake_dir,
        dst = final_dir,
    )

# The file of palettes.




# -- DEBUG - ON -- #
    exit()
# -- DEBUG - OFF -- #





nb_impl = len(IMPL_ACCEPTED)

plurial = "" if nb_impl == 1 else "s"

logging.info(f"'{nb_impl} implementation{plurial} added'")













exit(1)









# ------------------------------ #
# -- CONTRIB. IMPLEMENTATIONS -- #
# ------------------------------ #

contribs_accepted = get_accepted_paths(PROJ_DIR)

impl_accepted = contribs_accepted.get(
    CONTRIB_PROD_DIR,
    []
)

for ctxt in sorted(impl_accepted, key = lambda x: x.lower()):

# The file of palettes.
    logging.info(f"'{ctxt}': add file of palettes")

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
