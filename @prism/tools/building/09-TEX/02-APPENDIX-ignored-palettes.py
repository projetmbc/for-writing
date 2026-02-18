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

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR     = BUILD_TOOLS_DIR / TAG_AUDIT
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"
USED_BY_TOOLS_DIR = TRANSLATE_DIR.parent / "en" / TAG_USED_BY_TOOLS


REBUILDABLE_PALS_TEX = TRANSLATE_DIR / "report" /  "rebuildable-palettes.latex"


PALS_REBUILDABLE_BY_TECHNO = defaultdict(dict)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

TAB_1 = " "*4
TAB_2 = TAB_1*2
TAB_4 = TAB_2*2


TEX_CMDS = {
    PAL_STATUS.EQUAL_TO  : "=",
    PAL_STATUS.REVERSE_OF: r"\rightleftharpoons",
    PAL_STATUS.SUBSET_OF: r"\prec",
}


TEX_NO_EDIT = f"""
% ------------------------------------------- %
% -- AUTOMATICALLY GENERATED - DO NOT EDIT -- %
% ------------------------------------------- %
""".strip()


TEX_TRANSLATE_LAST_COL = f"""
% ------------------------------------------ %
% -- JUST TRANSLATE THE LAST COLMUN TEXTS -- %
% ------------------------------------------ %
""".strip()


TEX_ITEM_HEADER = TAB_1 + r"""
    %
    \begin{center}
        \begin{longtblr}[caption = {Ignored palettes}]{
          colspec     = {@{}l | r Q[c,$] l},
          baseline    = T,
          column{2,4} = {cmd=\tdoccodein{text}},
        }
""".strip()


TEX_TMPL_TABLE_FOOTER = TAB_2 + r"""
        \end{longtblr}
    \end{center}
""".strip()


TEX_TMPL_KIND  = TAB_4 + r"{ctxt}"
TEX_TMPL_ROW   = TAB_4 + r"  & {row} \\"
TEX_TMPL_HRULE = TAB_4 + r"\hline"


# ----------------------------- #
# -- YAML - IGNORED PALETTES -- #
# ----------------------------- #

logging.info("Extract 'ignored palettes' by human or design")

IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'

PALS_EXCLUDED_BY_TECHNO    = defaultdict(list)
PALS_REBUILDABLE_BY_TECHNO = defaultdict(list)

with IGNORED_YAML.open('r') as f:
    for src, pals in safe_load(f).items():
# Same source for 1st and 2nd palettes.
        for name, data in pals.items():
# Excluded by desing (too big, fully black...).
            if not TAG_REL in data:
                PALS_EXCLUDED_BY_TECHNO[src].append((
                    name,
                    data[TAG_WHY],
                ))

                continue

# Rebuildable palette.
            status = (
                PAL_STATUS.EQUAL_TO
                if data[TAG_REL] == '=' else
                PAL_STATUS.SUBSET_OF
            )

# Nothing left to do here.
            PALS_REBUILDABLE_BY_TECHNO[src].append((
                name,
                TEX_CMDS[status],
                data[TAG_PAL]
            ))


# -------------------------- #
# -- DB - MIRROR PALETTES -- #
# -------------------------- #

logging.info("Extract 'mirror palettes'")

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


        PALS_REBUILDABLE_BY_TECHNO[src].append((
            name_2,
            TEX_CMDS[PAL_STATUS.REVERSE_OF],
            name_1
        ))


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Build 'ignored palette' TeX files")



print(PALS_REBUILDABLE_BY_TECHNO)


exit(1)



src_name = YAML_CONFIGS[TAG_RESRC][src]['name']













# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Build 'ignored palette list' in TeX file")

texcode = []

if PALS_REBUILDABLE_BY_TECHNO:
    texcode = [
        TEX_NO_EDIT,
        '',
        TEX_ITEM_HEADER,
    ]

    for ctxt in sorted(PALS_REBUILDABLE_BY_TECHNO):
        texcode += [
            TEX_TMPL_KIND.format(
                ctxt = TEX_CMDS.get(ctxt, ctxt),
            ),
        ]

        for row in PALS_REBUILDABLE_BY_TECHNO[ctxt]:
            row = ' & '.join(row)

            texcode.append(
                TEX_TMPL_ROW.format(row = row)
            )

        texcode.append(TEX_TMPL_HRULE)

    texcode.pop(-1)
    texcode.append(TEX_TMPL_TABLE_FOOTER)

texcode = '\n'.join(texcode)

TEX_FILE.write_text(texcode)
