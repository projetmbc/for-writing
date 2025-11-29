#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from collections import defaultdict


# --------------- #
# -- CONSTANTS -- #
# --------------- #

TAG_SAME_NAME = STATUS_TAG[PAL_STATUS.SAME_NAME]


THIS_DIR      = Path(__file__).parent
PROJ_DIR      = THIS_DIR.parent.parent
REPORT_DIR    = PROJ_DIR / "tools" / "REPORT"
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"


TEX_FILE = TRANSLATE_DIR / "ignored-palettes.latex"


PAL_JSON_FILE = PROJ_DIR / "products" / "json" / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)

for k in [
    TAG_SAME_NAME,
    TAG_NAMES_IGNORED,
    TAG_NEW_NAMES,
]:
    del PAL_REPORT[k]


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

for name_n_ctxt, infos in PAL_REPORT.items():
    name, ctxt = extract_namectxt(name_n_ctxt)

    for st, tag_st in STATUS_TAG.items():
        if tag_st in infos:
            projname = infos[tag_st]
            break

    if (
        st == PAL_STATUS.EQUAL_TO
        and
        name == projname
    ):
        continue

    bytechno[ctxt].append((
        name,
        TEX_CMDS[st],
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
                ctxt = TEX_CMDS.get(ctxt, ctxt),
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
