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
from yaml        import safe_load


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

TAB = " "*8


TEX_CMDS = {
    PAL_STATUS.EQUAL_TO  : "=",
    PAL_STATUS.REVERSE_OF: r"\rightleftharpoons",
}


TEX_NO_EDIT = f"""
% ------------------------------------------- %
% -- AUTOMATICALLY GENERATED - DO NOT EDIT -- %
% ------------------------------------------- %
""".strip()


TEX_ITEM_HEADER = r"""
\item The following palettes are excluded because they duplicate \thisproj\ palettes either directly or in reversed order, except that exact duplicates (same name and colors) are omitted: we use \boxed{{=}\vphantom{pM}} for equality, and \boxed{{\rightleftharpoons}\vphantom{pM}} for reversal, and the rightmost palettes are the ones retained in \thisproj.

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


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR     = BUILD_TOOLS_DIR / TAG_AUDIT
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"


PALS_IGNORED_BY_TECHNO = defaultdict(dict)


TEX_FILE = TRANSLATE_DIR / "report" /  "ignored-palettes.latex"


# ------------------------------ #
# -- HUMAN - IGNORED PALETTES -- #
# ------------------------------ #

IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'

with IGNORED_YAML.open('r') as f:
    for resrc, data in safe_load(f).items():
        resrc = RESRC_ALIAS[resrc.lower()]

        if not resrc in PALS_IGNORED_BY_TECHNO:
            PALS_IGNORED_BY_TECHNO[resrc] = []

        PALS_IGNORED_BY_TECHNO[resrc] += [
            (
                old,
                TEX_CMDS[PAL_STATUS.EQUAL_TO],
                new
            )
            for old, new in data.items()
        ]


# -------------------------- #
# -- DB - MIRROR PALETTES -- #
# -------------------------- #

with sqlite3.connect(AUDIT_DIR / 'palettes.db') as conn:
    cursor = conn.cursor()

    query = """
SELECT
    h1.name, a1.alias,
    h2.name, a2.alias, h2.source
FROM mirror m
JOIN hash h1 ON m.cand_pal_id_1 = h1.pal_id
JOIN hash h2 ON m.cand_pal_id_2 = h2.pal_id
LEFT JOIN alias a1 ON h1.pal_id = a1.pal_id
LEFT JOIN alias a2 ON h2.pal_id = a2.pal_id
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    for name_1, alias_1, name_2, alias_2, resrc in rows:
        name_1 = alias_1 if alias_1 else name_1
        name_2 = alias_2 if alias_2 else name_2

        resrc = RESRC_ALIAS[resrc.lower()]

        if not resrc in PALS_IGNORED_BY_TECHNO:
            PALS_IGNORED_BY_TECHNO[resrc] = []

        PALS_IGNORED_BY_TECHNO[resrc].append((
            name_2,
            TEX_CMDS[PAL_STATUS.REVERSE_OF],
            name_1
        ))


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Build 'ignored palette list' in TeX file.")

texcode = []

if PALS_IGNORED_BY_TECHNO:
    texcode = [
        TEX_NO_EDIT,
        '',
        TEX_ITEM_HEADER,
    ]

    for ctxt in sorted(PALS_IGNORED_BY_TECHNO):
        texcode += [
            TEX_TMPL_KIND.format(
                ctxt = TEX_CMDS.get(ctxt, ctxt),
            ),
        ]

        for row in PALS_IGNORED_BY_TECHNO[ctxt]:
            row = ' & '.join(row)

            texcode.append(
                TEX_TMPL_ROW.format(row = row)
            )

        texcode.append(TEX_TMPL_HRULE)

    texcode.pop(-1)
    texcode.append(TEX_TMPL_TABLE_FOOTER)

texcode = '\n'.join(texcode)

TEX_FILE.write_text(texcode)
