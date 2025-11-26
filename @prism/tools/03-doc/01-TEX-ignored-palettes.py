#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core     import *
from cbutils.cleanpal import *

from collections import defaultdict
from json        import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR      = Path(__file__).parent
PROJ_DIR      = THIS_DIR.parent.parent
REPORT_DIR    = PROJ_DIR / "tools" / "report"
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"


IGNORE_TEX_FILE = TRANSLATE_DIR / "ignored-palettes.latex"


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    IGNORED = json_load(f)


PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"

with PAL_CREDITS_FILE.open(mode = "r") as f:
    PAL_CREDITS = json_load(f)


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


TEX_CMDS = {
    PAL_STATUS.EQUAL_TO  : "=",
    PAL_STATUS.REVERSE_OF: r"\rightleftharpoons",
}


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Build 'ignored palette list' in TeX file.")


bytechno = defaultdict(list)

for name, infos in IGNORED.items():
    ctxt = infos[TAG_CTXT]
    ctxt = PAL_CREDITS[name]

    if STATUS_TAG[PAL_STATUS.EQUAL_TO] in infos:
        status = PAL_STATUS.EQUAL_TO

    else:
        status = PAL_STATUS.REVERSE_OF

    bytechno[ctxt].append((
        name,
        TEX_CMDS[status],
        infos[STATUS_TAG[status]]
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
                ctxt    = TEX_CMDS.get(ctxt, ctxt),
                nblines = len(listof)
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

IGNORE_TEX_FILE.write_text(texcode)
