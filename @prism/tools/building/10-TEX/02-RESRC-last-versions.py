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

SRC_IGNORED = [
    'APRISM',
    'COLORMAPS',
    'NCLCOLTABLES',
]


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
        if not s in SRC_IGNORED
    }


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

TAB_1 = " "*4
TAB_2 = TAB_1*2


TEX_VERSIONS_TABLE_HEADER = r"""
%
\begin{tblr}{
    colspec  = {r@{\,}l|r@{\,}l},
    baseline = T
}
""".strip()

TEX_TABLE_FOOTER = r"\end{tblr}"


TEX_VERSIONS_TMPL_SRC = r"\{src}: & {version}"


# ------------------- #
# -- VERSIONS USED -- #
# ------------------- #

logging.info("TeX - Build 'versions used'")

nb_last_changes = len(LAST_CHGES)
tex_last_chges  = [None]*nb_last_changes

# Trick needed to ease the incoming calculus.
if nb_last_changes % 2 == 0:
    nb_last_changes -=1

for i, (s, v) in enumerate(LAST_CHGES.items()):
    j = 2*i

    if j > nb_last_changes:
        j -= nb_last_changes

    tex_last_chges[j] = (s, v)


_texcode = [
    TEX_NO_EDIT,
    TEX_VERSIONS_TABLE_HEADER
]

_row = []


for i, (src, version) in enumerate(
    tex_last_chges,
    start = 1
):
    _row.append(
        TEX_VERSIONS_TMPL_SRC.format(
            src     = src.lower(),
            version = version
        )
    )

    if i % 2 == 0:
        _texcode += [
            TAB_1 + ' & '.join(_row).strip(),
            TAB_1 + r'\\'
        ]

        _row = []

if _row:
    _texcode.append(
        TAB_1 + ' & '.join(_row).strip()
    )

_texcode.append(TEX_TABLE_FOOTER)

texcode = '\n'.join(_texcode)

RESRC_LAST_TEX_FILE.write_text(texcode)
