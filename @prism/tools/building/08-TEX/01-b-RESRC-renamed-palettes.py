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

TAB = " "*8


TEX_NO_EDIT = f"""
% ------------------------------------------- %
% -- AUTOMATICALLY GENERATED - DO NOT EDIT -- %
% ------------------------------------------- %
""".strip()


TEX_ITEM_HEADER = TAB + r"""
\item The following palettes have been renamed: \boxed{{\Rightarrow}\vphantom{pM}} indicates a name modification, with the \thisproj\ name displayed on the right.

    \begin{center}
        \begin{tblr}{
          colspec     = {@{}l | r Q[c,$] l},
          baseline    = T,
          column{2,4} = {cmd=\tdoccodein{text}},
        }
""".strip()


TEX_TMPL_TABLE_FOOTER = TAB + r"""
\end{tblr}
    \end{center}
""".strip()


TEX_TMPL_KIND  = TAB*2 + r"{ctxt}"
TEX_TMPL_ROW   = TAB*2 + r"  & {row} \\"
TEX_TMPL_HRULE = TAB*2 + r"\hline"


TEX_EQUIV_CMD = r"\Rightarrow"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR     = BUILD_TOOLS_DIR / TAG_AUDIT
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"


PALS_RENAMED_BY_TECHNO = defaultdict(dict)


TEX_FILE = TRANSLATE_DIR / "report" / "renamed-palettes.latex"


# -------------------------- #
# -- DB - PALETTE ALIASES -- #
# -------------------------- #

with sqlite3.connect(AUDIT_DIR / 'palettes.db') as conn:
    cursor = conn.cursor()

    query = """
SELECT
    h.name, a.alias, h.source
FROM hash h
JOIN alias a ON h.pal_id = a.pal_id
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    for name, alias, resrc in rows:
        resrc = RESRC_ALIAS[resrc.lower()]

        if not resrc in PALS_RENAMED_BY_TECHNO:
            PALS_RENAMED_BY_TECHNO[resrc] = []

        PALS_RENAMED_BY_TECHNO[resrc].append((
            name,
            TEX_EQUIV_CMD,
            alias
        ))


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Build 'renamed palette list' in TeX file.")

texcode = []

if PALS_RENAMED_BY_TECHNO:
    texcode = [
        TEX_NO_EDIT,
        '',
        TEX_ITEM_HEADER,
    ]

    for ctxt in sorted(PALS_RENAMED_BY_TECHNO):
        texcode += [
            TEX_TMPL_KIND.format(ctxt = ctxt),
        ]

        for row in PALS_RENAMED_BY_TECHNO[ctxt]:
            row = ' & '.join(row)

            texcode.append(
                TEX_TMPL_ROW.format(row = row)
            )

        texcode.append(TEX_TMPL_HRULE)

    texcode.pop(-1)
    texcode.append(TEX_TMPL_TABLE_FOOTER)

texcode = '\n'.join(texcode)

TEX_FILE.write_text(texcode)
