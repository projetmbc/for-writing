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


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent


MANUAL_DIR    = PROJ_DIR / "contrib" / "translate" / "en" / 'manual'
PREAMBLE_TEX  = MANUAL_DIR / "preamble.cfg.sty"
PREAMBLE_CODE = PREAMBLE_TEX.read_text()

REPORT_DIR  = BUILD_TOOLS_DIR / TAG_REPORT
APRISM_JSON = REPORT_DIR / "APRISM.json"

# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

logging.info(f"Dyna Var Update - 'Data extraction'")

# Config. values.
DATA = {
    k: v
    for k, v in YAML_CONFIGS['SEMANTIC'].items()
    if type(v) == int
}

# General nb of pals.
JSON_PALS_HF_DIR = PROJ_DIR / "products" / 'json' / 'palettes-hf'

DATA['NB_OF_PALS'] = len(
    list(JSON_PALS_HF_DIR.glob('*.json'))
)


REPORT_DIR = PROJ_DIR / "tools" / "building" / TAG_REPORT

DATA['NB_NEW_PALS'] = int(
    (
        REPORT_DIR / "AUDIT-LOCMAIN-NAMES-NEW-NB.txt"
    ).read_text().strip()
)

# @prism vs resource nbs of pals.

with APRISM_JSON.open('r') as f:
    DATA['NB_APRISM_PALS'] = len(json_load(f))

DATA['NB_RESRC_PALS'] = DATA['NB_OF_PALS'] - DATA['NB_APRISM_PALS']

DATA['PERCENT_APRISM_PALS'] = round(
    100 * DATA['NB_APRISM_PALS'] / DATA['NB_OF_PALS']
)


# -------------------- #
# -- DYNA TEXT VALS -- #
# -------------------- #

for ctxt, uppername, prefix in [
    (
        'nb of palettes',
        'NB_OF_PALS',
        '',
    ),
    (
        'nb of new palettes',
        'NB_NEW_PALS',
        '',
    ),
    (
        'nb of resource palettes',
        'NB_RESRC_PALS',
        '',
    ),
    (
        'nb of @prism palettes',
        'NB_APRISM_PALS',
        '',
    ),
    (
        '% of @prism palettes',
        'PERCENT_APRISM_PALS',
        '',
    ),
    (
        'max size',
        'MAX_SIZE',
        'pal',
    ),
    (
        'max semantic size',
        'MAX_SEM_SIZE',
        'pal',
    ),
    (
        'sub semantic group size',
        'SUB_SEM_SIZE',
        'pal',
    ),
    (
        'nb of sub semantic groups',
        'NB_SEM_GRPS',
        'pal',
    ),
]:
    logging.info(f"Dyna Var Update - '{ctxt.capitalize()}'")

    camelname = uppername.title()
    camelname = camelname.replace('_', '')
    camelname = (
        prefix + camelname
        if prefix else
        camelname[0].lower() + camelname[1:]
    )

    val = DATA[uppername]

    PREAMBLE_CODE = (
        re.compile(
              r'(\\newcommand\\'
            + camelname
            + r'\{)\d+(\})'
        )
    ).sub(
        r"\g<1>" + str(val) + r"\g<2>",
        PREAMBLE_CODE
    )

PREAMBLE_TEX.write_text(PREAMBLE_CODE)
