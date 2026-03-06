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


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

UPDATES_DIR   = BUILD_TOOLS_DIR / 'UPDATES'
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"


RESRC_LAST_TEX_FILE = TRANSLATE_DIR / "rescr" / "last-versions.latex"

if RESRC_LAST_TEX_FILE.is_file():
    RESRC_LAST_TEX_FILE.unlink()

RESRC_LAST_TEX_FILE.touch()


BACKUP_JSON_FILE = UPDATES_DIR / 'BACKUP.json'

with BACKUP_JSON_FILE.open('r') as f:
    LAST_CHGES = {
        s: d[0].split('T')[0]
        for s, d in json_load(f).items()
    }


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

SRC_IGNORED = [
    'APRISM',
    'NCLCOLTABLES',
]

TAB_1 = " "*4
TAB_2 = TAB_1*2


VERSION_TABE_NB_COLS       = 2
TEX_VERSIONS_TABLE_HEADER = r"""
%
\begin{tblr}{
    colspec  = {r@{\,}lQ[5pt]|Q[5pt]r@{\,}l},
    baseline = T
}
""".strip()

TEX_TABLE_FOOTER = r"\end{tblr}"


TEX_VERSIONS_TMPL_SRC = r"\{src}: & {version} &&"


# ------------------- #
# -- VERSIONS USED -- #
# ------------------- #

logging.info("TeX - Build 'versions used'")

_texcode = [
    TEX_NO_EDIT,
    TEX_VERSIONS_TABLE_HEADER
]

_row = []


i = 0

for src, version in LAST_CHGES.items():
    if src in SRC_IGNORED:
        continue

    i += 1

    _row.append(
        TEX_VERSIONS_TMPL_SRC.format(
            src     = src.lower(),
            version = version
        )
    )

    if i % VERSION_TABE_NB_COLS == 0:
        _texcode += [
            TAB_1 + ' & '.join(_row)[:-3].strip(),
            TAB_1 + r'\\'
        ]

        _row = []

if _row:
    _texcode.append(
        TAB_1 + ' & '.join(_row)[:-3].strip()
    )

_texcode.append(TEX_TABLE_FOOTER)

texcode = '\n'.join(_texcode)

RESRC_LAST_TEX_FILE.write_text(texcode)
