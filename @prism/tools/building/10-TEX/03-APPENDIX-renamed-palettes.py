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

from collections import defaultdict


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR     = BUILD_TOOLS_DIR / TAG_AUDIT
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"


SQLITE_DB_FILE = AUDIT_DIR / 'palettes.db'


TRANS_REPORT_DIR = TRANSLATE_DIR / "report"


RENAMED_PALS_TEX_FILE = TRANS_REPORT_DIR / "renamed-palettes.latex"

if RENAMED_PALS_TEX_FILE.is_file():
    RENAMED_PALS_TEX_FILE.unlink()

RENAMED_PALS_TEX_FILE.touch()


RENAMING_SUFFIXES_TEX_FILE = TRANS_REPORT_DIR / "suffixes-used.latex"

if RENAMING_SUFFIXES_TEX_FILE.is_file():
    RENAMED_PALS_TEX_FILE.unlink()

RENAMED_PALS_TEX_FILE.touch()


PALS_RENAMED_BY_TECHNO = defaultdict(list)
SUFFIXES_USED          = dict()


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

TAB_1 = " "*4
TAB_2 = TAB_1*2


TEX_RENAME_TABLE_HEADER = r"""
%
\begin{longtblr}[caption = \palsrenamed]{
    colspec     = {@{}l | r Q[c,$] l},
    baseline    = T,
    column{2,4} = {cmd = \tdoccodein{text}},
}
""".strip()


TEX_LONGTABLE_FOOTER = r"\end{longtblr}"


TEX_RENAME_TMPL_SRC   = TAB_1 + r"{src}"
TEX_RENAME_TMPL_ROW   = TAB_1 + r"  & {row} \\"
TEX_RENAME_TMPL_HRULE = TAB_1 + r"\hline"


TEX_EQUIV_CMD = r"\Rightarrow"


TEX_SUFFIX_TABLE_HEADER = r"""
%
\begin{longtblr}[caption = \suffixesused]{
    colspec     = {r @{\,}l | r @{\,}l},
    baseline    = T,
    column{2,4} = {cmd = \tdoccodein{text}},
}
""".strip()


TEX_SUFFIX_TMPL_SRC = r"\{src}: & {suffix}"


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

SQL_GET_SUFFIX = """
SELECT
    source, suffix
FROM suffix s
ORDER BY source ASC;
"""


SQL_GET_ALIAS = """
SELECT
    h.name, a.alias, h.source
FROM hash h
JOIN alias a ON h.pal_id = a.pal_id
"""


# -------------------------- #
# -- DB - PALETTE ALIASES -- #
# -------------------------- #

logging.info("DB - Get 'alias'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    cursor.execute(SQL_GET_ALIAS)

    rows = cursor.fetchall()

    for name, alias, src in rows:
        PALS_RENAMED_BY_TECHNO[src].append((
            name,
            TEX_EQUIV_CMD,
            alias
        ))


if not PALS_RENAMED_BY_TECHNO:
    logging.info("No 'renamed palettes'")

    exit(0)


# -------------------------- #
# -- DB - PALETTE ALIASES -- #
# -------------------------- #

logging.info("DB - Get 'suffixes used'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    cursor.execute(SQL_GET_SUFFIX)

    rows = cursor.fetchall()

    for src, suffix in rows:
        SUFFIXES_USED[src] = suffix


# ------------------- #
# -- SUFFIXES USED -- #
# ------------------- #

logging.info("TeX - Build 'suffixes used'")

nb_suffixes  = len(SUFFIXES_USED)
tex_suffixes = [None]*nb_suffixes

# Trick needed to ease the incoming calculus.
if nb_suffixes % 2 == 0:
    nb_suffixes -=1

for i, (s, sf) in enumerate(SUFFIXES_USED.items()):
    j = 2*i

    if j > nb_suffixes:
        j -= nb_suffixes

    tex_suffixes[j] = (s, sf)

_texcode = [
    TEX_NO_EDIT,
    TEX_SUFFIX_TABLE_HEADER
]

_row = []


for i, (src, suffix) in enumerate(
    tex_suffixes,
    start = 1
):
    _row.append(
        TEX_SUFFIX_TMPL_SRC.format(
            src    = src.lower(),
            suffix = suffix
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

_texcode.append(TEX_LONGTABLE_FOOTER)

texcode = '\n'.join(_texcode)

RENAMING_SUFFIXES_TEX_FILE.write_text(texcode)


# ---------------------- #
# -- RENAMED PALETTES -- #
# ---------------------- #

logging.info("TeX - Build 'renamed palettes'")

_texcode = [
    TEX_NO_EDIT,
    TEX_RENAME_TABLE_HEADER
]

for src in sorted(PALS_RENAMED_BY_TECHNO):
    src_name = YAML_CONFIGS[TAG_RESRC][src]['name']

    _texcode.append(
        TEX_RENAME_TMPL_SRC.format(src = src_name),
    )

    for _row in PALS_RENAMED_BY_TECHNO[src]:
        row = ' & '.join(_row)

        _texcode.append(
            TEX_RENAME_TMPL_ROW.format(row = row)
        )

    _texcode.append(TEX_RENAME_TMPL_HRULE)

_texcode.pop(-1)
_texcode.append(TEX_LONGTABLE_FOOTER)

texcode = '\n'.join(_texcode)

RENAMED_PALS_TEX_FILE.write_text(texcode)
