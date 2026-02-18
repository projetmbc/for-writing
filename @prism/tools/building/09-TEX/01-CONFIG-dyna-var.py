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

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


MANUAL_DIR = PROJ_DIR / "contrib" / "translate" / "en" / 'manual'
PREAMBLE_TEX = MANUAL_DIR / "preamble.cfg.sty"
PREAMBLE_CODE = PREAMBLE_TEX.read_text()


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

DATA = dict()


JSON_PALS_HF_DIR = PROJ_DIR / "products" / 'json' / 'palettes-hf'

DATA['NB_OF_PALS'] = len(
    list(JSON_PALS_HF_DIR.glob('*.json'))
)


REPORT_DIR      = PROJ_DIR / "tools" / "building" / TAG_REPORT

DATA['NB_NEW_PALS'] = (
    REPORT_DIR / "AUDIT-LOCMAIN-NAMES-NEW-NB.txt"
).read_text().strip()


DATA.update(YAML_CONFIGS['SEMANTIC'])


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
