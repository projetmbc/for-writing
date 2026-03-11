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

from natsort import (
    natsorted,
    ns
)


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent


REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

SUBPALS_JSON = REPORT_DIR / 'AUDIT-SUBPALETTES.json'

with SUBPALS_JSON.open('r') as f:
    SUBPALS_DATA = json_load(f)


TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"

SUBPALS_TEX_FILE = TRANSLATE_DIR / "report" /  "subpalettes.latex"

SUBPALS_TEX_FILE.touch()


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

TAB_1 = " "*4
TAB_2 = TAB_1*2


TEX_SUBPALSS_TABLE_HEADER = r"""
%
\begin{longtblr}[caption = \palsunkept]{
    colspec     = {@{} r | r@{\ }c@{\ }l},
    baseline    = T,
    column{1-4} = {cmd = \tdoccodein{text}},
}
""".strip()


TEX_TABLE_FOOTER = r"\end{longtblr}"


TEX_TMPL_START_CODE = f'{TAB_2}& pal_to_use &=& {{name}}'
TEX_TMPL_CODE_LINE  = rf'{TAB_1}\\  & {{var}} &=& {{val}}'


# ----------- #
# -- TOOLS -- #
# ----------- #

def indices_2_str(vals):
    return ', '.join(map(str, vals))


def range_2_str(vals):
    params = f'from {vals[0]} to {vals[1]}'

    if vals[2] != 1:
        params += f' with step {vals[2]}'

    return params


TRANSFORMER = {
    'indices': indices_2_str,
    'range'  : range_2_str,
}

# ----------------- #
# -- SUBPALETTES -- #
# ----------------- #

logging.info("(TeX) Build 'subpalette infos'")

_texcode = [
    TEX_NO_EDIT,
    TEX_SUBPALSS_TABLE_HEADER
]

for subname in natsorted(
    SUBPALS_DATA,
    alg = ns.IGNORECASE
):
    data   = SUBPALS_DATA[subname]
    name   = data['palette']

    _texcode += [
        f'{TAB_1}{subname}',
        TEX_TMPL_START_CODE.format(name = name),
    ]

    for method, _params in data['extract']:
        params = TRANSFORMER[method](_params)

        _texcode += [
            TEX_TMPL_CODE_LINE.format(
                var = method,
                val = params
            ),
            rf'{TAB_1}\\\hline',
        ]

_texcode.pop(-1)
_texcode.append(TEX_TABLE_FOOTER)

texcode = '\n'.join(_texcode)

SUBPALS_TEX_FILE.write_text(texcode)
