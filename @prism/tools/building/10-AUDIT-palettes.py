#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR

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

TAB_1 = ' '*4
TAB_2 = TAB_1*2


NB_MAX_COL_PER_CATEGO = 4


TEX_HEADER_TMPL = r"""
\documentclass{tutodoc}

\usepackage{amssymb}
\usepackage{array}

\begin{document}

\section*{\hfill AUDIT -- Last new palettes \hfill\null}

\renewcommand{\arraystretch}{1.5}
""".strip()+ '\n'


TEX_FOOTER_TMPL = r"\end{document}"


TEX_TABLE_HEADER_TMPL = (
     r"\begin{tabular}{p{3.25cm}*"
    rf"{{{NB_MAX_COL_PER_CATEGO}}}"
     r"{p{2.25cm}}}"
)
TEX_TABLE_FOOTER_TMPL = r"\end{tabular}"


TEX_CMD_CHECK_OR_NOT = {
    False: r"$\square$",
    True : r"$\boxtimes$",
}


TEX_CENTER_HEADER_TMPL = r"\begin{center}"
TEX_CENTER_FOOTER_TMPL = r"""
\end{center}

\noindent\hrulefill
"""


TEX_INCLUDEGRAPH_TMPL = (
    TAB_1
    +
    r"\includegraphics[scale=1.25]{{../../../contrib/translate/common/showcase/{name}-{format}.pdf}}"
)

TEX_GRAPHSEP_TMPL = TAB_1 + r'\smallskip'



# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE    = AUDIT_DIR / "palettes.db"
TEX_NEW_PALS_FILE = AUDIT_DIR / "NEW-PALS.tex"


CONTRIB_SHOWCASE_DIR = PROJ_DIR / "contrib" / "translate" / "common" / "showcase"


ALL_CATEGOS = sorted(
    YAML_CONFIGS['METADATA']['CATEGORY']
)


# ------------------ #
# -- GET LAST NEW -- #
# ------------------ #

logging.warning("LAST NEW PALS NOT YET IMPLEMENTED!")


# --------------- #
# -- AUDIT PDF -- #
# --------------- #

logging.info("Last new pals - Build 'audit PDF'")

query = '''
SELECT
    COALESCE(a.alias, h.name),
    h.kind
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1
'''

_texcode = [TEX_HEADER_TMPL]

nbpals = 0

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(query)

    for name, kinds in natsorted(
        cursor.fetchall(),
        alg = ns.IGNORECASE
    ):
        nbpals += 1

        _kinds = set(
            k.strip()
            for k in kinds.split(',')
        )

# We have to build the folowing LaTeX code.
#
#     \textbf{name}
#        & $\square$ colorblind & $\square$ cyclic & $\square$ dark & $\square$ divergent \\
#        & $\boxtimes$ qualitative & $\square$ semantic & $\square$ sequential
        _tablecode = [
            TAB_1 + rf"\textbf{{{name}}}",
            TAB_2
        ]

        cursor = 1

        for i, k in enumerate(ALL_CATEGOS):
            texcmd = TEX_CMD_CHECK_OR_NOT[k in _kinds]

            if i == NB_MAX_COL_PER_CATEGO:
                _tablecode[cursor] += r'\\'

                _tablecode.append(TAB_2)
                cursor += 1

            _tablecode[cursor] += f"& {texcmd} {k} "

        _tablecode[cursor] = _tablecode[cursor].rstrip()

        tablecode = '\n'.join(_tablecode)

        _texcode += [
            TEX_TABLE_HEADER_TMPL,
            tablecode,
            TEX_TABLE_FOOTER_TMPL,
        ]

# We have graphics.
        _texcode += [
            '',
            TEX_CENTER_HEADER_TMPL,
            TEX_INCLUDEGRAPH_TMPL.format(
                name  = name,
                format = 'spectrum'
            )
        ]

        if (
            CONTRIB_SHOWCASE_DIR / f"{name}-palette.pdf"
        ).is_file():
            _texcode += [
                '',
                TEX_GRAPHSEP_TMPL,
                TEX_INCLUDEGRAPH_TMPL.format(
                    name   = name,
                    format = 'palette'
                )
            ]

        _texcode.append(TEX_CENTER_FOOTER_TMPL)

_texcode.append(
    rf"\centering\bfseries\Large {nbpals} palettes found."
)
_texcode.append(TEX_FOOTER_TMPL)

texcode = '\n'.join(_texcode)

TEX_NEW_PALS_FILE.touch()
TEX_NEW_PALS_FILE.write_text(texcode)
