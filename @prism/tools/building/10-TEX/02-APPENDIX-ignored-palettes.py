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

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR     = BUILD_TOOLS_DIR / TAG_AUDIT
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate" / "common"
USED_BY_TOOLS_DIR = TRANSLATE_DIR.parent / "en" / TAG_USED_BY_TOOLS


for p in [
    REBUILDABLE_PALS_TEX_FILE:= TRANSLATE_DIR / "report" /  "rebuildable-palettes.latex",
    EXCLUDED_PALS_TEX_FILE   := USED_BY_TOOLS_DIR / "report" /  "excluded-palettes.latex",
]:
    p.parent.mkdir(
        parents = True,
        exist_ok = True
    )

    if p.is_file():
        p.unlink()

    p.touch()


SQLITE_DB_FILE = AUDIT_DIR / 'palettes.db'


IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'


EXCLUDED_PALS_BY_TECHNO    = defaultdict(list)
PALS_REBUILDABLE_BY_TECHNO = defaultdict(list)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

TAB_1 = " "*4
TAB_2 = TAB_1*2


TEX_CMDS = {
    PAL_STATUS.EQUAL_TO  : "=",
    PAL_STATUS.REVERSE_OF: r"\rightleftharpoons",
    PAL_STATUS.SUBSET_OF : r"\prec",
    PAL_STATUS.SHIFT_OF  : r"\ll",
}


STATUS = {
    '='  : PAL_STATUS.EQUAL_TO,
    '<'  : PAL_STATUS.SUBSET_OF,
    '<<<': PAL_STATUS.SHIFT_OF,
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


TEX_REBUILDABLE_TABLE_HEADER = r"""
%
\begin{center}
    \begin{longtblr}[caption = {Rebuildable palettes}]{
      colspec     = {@{}l | r Q[c,$] l},
      baseline    = T,
      column{2,4} = {cmd = \tdoccodein{text}},
    }
""".strip()


TEX_EXCLUDED_TABLE_HEADER = r"""
%
\begin{center}
    \begin{longtblr}[caption = {Excluded palettes}]{
      colspec   = {@{}l | r l},
      baseline  = T,
      column{2} = {cmd = \tdoccodein{text}},
    }
""".strip()


TEX_TABLE_FOOTER = TAB_1 + r"""
    \end{longtblr}
\end{center}
""".strip()


TEX_TMPL_SRC   = TAB_2 + r"{src}"
TEX_TMPL_ROW   = TAB_2 + r"  & {row} \\"
TEX_TMPL_HRULE = TAB_2 + r"\hline"


# ----------------------------- #
# -- YAML - IGNORED PALETTES -- #
# ----------------------------- #

logging.info("Get 'all final names'")

ALL_NAMES = set()

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    query = """
SELECT
    COALESCE(a.alias, h.name)
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
    """

    cursor.execute(query)

    for name, in cursor.fetchall():
        ALL_NAMES.add(name)


# ----------------------------- #
# -- YAML - IGNORED PALETTES -- #
# ----------------------------- #

logging.info("Extract 'ignored palettes' by human or design")

with IGNORED_YAML.open('r') as f:
    for src, pals in safe_load(f).items():
# Same source for 1st and 2nd palettes.
        for name, data in pals.items():
# Unkown name.
            if not name in ALL_NAMES:
                log_raise_error(
                    context   = "Looking for ignored palette",
                    desc      = f"Unknown '{name}' to ignore",
                    exception = ValueError,
                )

# Excluded by desing (too big, fully black...).
            if not TAG_REL in data:
                EXCLUDED_PALS_BY_TECHNO[src].append((
                    name,
                    data[TAG_WHY],
                ))

                continue

# Rebuildable palette.
            status = STATUS[data[TAG_REL]]

# Unkown name.
            if not data[TAG_PAL] in ALL_NAMES:
                log_raise_error(
                    context   = "Looking for ignored palette",
                    desc      = f"Unknown '{name}' kept",
                    exception = ValueError,
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

with sqlite3.connect(SQLITE_DB_FILE) as conn:
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

    for name_1, alias_1, name_2, alias_2, src in rows:
        name_1 = alias_1 if alias_1 else name_1
        name_2 = alias_2 if alias_2 else name_2


        PALS_REBUILDABLE_BY_TECHNO[src].append((
            name_2,
            TEX_CMDS[PAL_STATUS.REVERSE_OF],
            name_1
        ))


# ------------------------------------------------- #
# -- REBUILDABLE PALETTES /  EXCLUDED BY DESIGN  -- #
# ------------------------------------------------- #

for ctxt, data, texfile, comment, tbl_header in [
    (
        "rebuildable palettes",
        PALS_REBUILDABLE_BY_TECHNO,
        REBUILDABLE_PALS_TEX_FILE,
        TEX_NO_EDIT,
        TEX_REBUILDABLE_TABLE_HEADER
    ),
    (
        "excluded by design palettes",
        EXCLUDED_PALS_BY_TECHNO,
        EXCLUDED_PALS_TEX_FILE,
        TEX_TRANSLATE_LAST_COL,
        TEX_EXCLUDED_TABLE_HEADER
    )
]:
    if not data:
        logging.info(f"No '{ctxt}'")

        continue

    logging.info(f"Build '{ctxt}' TeX file")

    _texcode = [comment, tbl_header]

    for src in sorted(data):
        src_name = YAML_CONFIGS[TAG_RESRC][src]['name']

        _texcode.append(
            TEX_TMPL_SRC.format(src = src_name),
        )

        for row in data[src]:
            row = ' & '.join(row)

            _texcode.append(
                TEX_TMPL_ROW.format(row = row)
            )

        _texcode.append(TEX_TMPL_HRULE)

    _texcode.pop(-1)
    _texcode.append(TEX_TABLE_FOOTER)

    texcode = '\n'.join(_texcode)

    texfile.write_text(texcode)
