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

from json import load as json_load


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PATTERN_MAX_SEM_SIZE = re.compile(
    r'(\\newcommand\\palSemMaxSize\{)\d+(\})'
)

PATTERN_NB_OF_PALS = re.compile(
    r'(\\newcommand\\nbOfPals\{)\d+(\})'
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


MANUAL_DIR = PROJ_DIR / "contrib" / "translate" / "en" / 'manual'
PREAMBLE_TEX = MANUAL_DIR / "preamble.cfg.sty"
PREAMBLE_CODE = PREAMBLE_TEX.read_text()


JSON_PROD_DIR = PROJ_DIR / "products" / "json"
HF_PALS_JSON  = JSON_PROD_DIR / "palettes-hf.json"

with HF_PALS_JSON.open() as f:
    NB_OF_PALS = len(json_load(f))


MAX_SEM_SIZE = YAML_CONFIGS['SEMANTIC']['MAX_SEM_SIZE']


# --------------------------------- #
# -- NB OF PALS / MAX. SEM. SIZE -- #
# --------------------------------- #

for ctxt, pat, val in [
    (
        'max semantic size',
        PATTERN_MAX_SEM_SIZE,
        MAX_SEM_SIZE
    ),
    (
        'nb of palettes',
        PATTERN_NB_OF_PALS,
        NB_OF_PALS
    )
]:
    logging.info(f"DYNA VAR UPDATE - 'ctxt'")

    PREAMBLE_CODE = pat.sub(
        r"\g<1>" + str(val) + r"\g<2>",
        PREAMBLE_CODE
    )

    PREAMBLE_TEX.write_text(PREAMBLE_CODE)
