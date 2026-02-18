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

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR     = BUILD_TOOLS_DIR / TAG_AUDIT
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"


SQLITE_DB_FILE = AUDIT_DIR / 'palettes.db'


PALS_RENAMED_BY_TECHNO = defaultdict(list)


RENAMED_PALS_TEX_FILE = TRANSLATE_DIR / "report" / "renamed-palettes.latex"

if RENAMED_PALS_TEX_FILE.is_file():
    RENAMED_PALS_TEX_FILE.unlink()

RENAMED_PALS_TEX_FILE.touch()


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

TAB_1 = " "*4
TAB_2 = TAB_1*2


TEX_NO_EDIT = f"""
% ------------------------------------------- %
% -- AUTOMATICALLY GENERATED - DO NOT EDIT -- %
% ------------------------------------------- %
""".strip()


TEX_TABLE_HEADER = r"""
%
\begin{center}
    \begin{longtblr}[caption = {Renamed palettes}]{
      colspec     = {@{}l | r Q[c,$] l},
      baseline    = T,
      column{2,4} = {cmd=\tdoccodein{text}},
    }
""".strip()


TEX_TABLE_FOOTER = TAB_1 + r"""
    \end{longtblr}
\end{center}
""".strip()


TEX_TMPL_SRC   = TAB_2 + r"{src}"
TEX_TMPL_ROW   = TAB_2 + r"  & {row} \\"
TEX_TMPL_HRULE = TAB_2 + r"\hline"


TEX_EQUIV_CMD = r"\Rightarrow"


# -------------------------- #
# -- DB - PALETTE ALIASES -- #
# -------------------------- #

logging.info("Get 'alias'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    query = """
SELECT
    h.name, a.alias, h.source
FROM hash h
JOIN alias a ON h.pal_id = a.pal_id
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    for name, alias, src in rows:
        PALS_RENAMED_BY_TECHNO[src].append((
            name,
            TEX_EQUIV_CMD,
            alias
        ))


# ---------------------- #
# -- RENAMED PALETTES -- #
# ---------------------- #

if not PALS_RENAMED_BY_TECHNO:
    logging.info("No 'renamed palettes'")

    exit(0)


logging.info("Build 'renamed palettes' TeX file")

_texcode = [
    TEX_NO_EDIT,
    TEX_TABLE_HEADER
]

for src in sorted(PALS_RENAMED_BY_TECHNO):
    src_name = YAML_CONFIGS[TAG_RESRC][src]['name']

    _texcode.append(
        TEX_TMPL_SRC.format(src = src_name),
    )

    for row in PALS_RENAMED_BY_TECHNO[src]:
        row = ' & '.join(row)

        _texcode.append(
            TEX_TMPL_ROW.format(row = row)
        )

    _texcode.append(TEX_TMPL_HRULE)

_texcode.pop(-1)
_texcode.append(TEX_TABLE_FOOTER)

texcode = '\n'.join(_texcode)

RENAMED_PALS_TEX_FILE.write_text(texcode)
