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

TAB = " "*4


TEX_NO_TRANSLATION = f"""
% --------------------------------- %
% -- NO TRANSLATION NEEDED HERE! -- %
% --------------------------------- %
""".strip()


TEX_TMPL_TABLE_HEADER = TAB + r"""
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

TAG_SAME_NAME = STATUS_TAG[PAL_STATUS.SAME_NAME]


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR    = BUILD_TOOLS_DIR / "REPORT"
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"


TEX_FILE = TRANSLATE_DIR / "renamed-palettes.latex"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PAL_JSON_FILE = PROJ_DIR / "products" / "json" / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)

PAL_REPORT = PAL_REPORT[TAG_NEW_NAMES]


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Build 'renamed palette list' in TeX file.")

bytechno = defaultdict(list)

for name_n_ctxt, projname in PAL_REPORT.items():
    name, ctxt = extract_namectxt(name_n_ctxt)

    bytechno[ctxt].append((
        name,
        TEX_EQUIV_CMD,
        projname
    ))


texcode = []

if bytechno:
    texcode = [
        TEX_NO_TRANSLATION,
        '',
        TEX_TMPL_TABLE_HEADER,
    ]

    for ctxt in sorted(bytechno):
        listof = bytechno[ctxt]

        texcode += [
            TEX_TMPL_KIND.format(
                ctxt = ctxt,
            ),
        ]

        for row in listof:
            row = ' & '.join(row)

            texcode.append(
                TEX_TMPL_ROW.format(row = row)
            )

        texcode.append(TEX_TMPL_HRULE)

    texcode.pop(-1)
    texcode.append(TEX_TMPL_TABLE_FOOTER)

texcode = '\n'.join(texcode)

TEX_FILE.write_text(texcode)
