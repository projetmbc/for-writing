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

from natsort import (
    natsorted,
    ns
)


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

LETTERS_COL_BREAK = 'J'


TAB_1 = ' '*4
TAB_2 = TAB_1*2


TAG_LIST_OF_NAMES = r"LIST OF NAMES"

TAG_LIST_OF_NAMES_START = rf"% -- {TAG_LIST_OF_NAMES} - AUTO - START -- %"
TAG_LIST_OF_NAMES_END   = rf"% -- {TAG_LIST_OF_NAMES} - AUTO - END -- %"


TEX_HEADER_TMPL = r"\begin{multicols*}{3}"
TEX_FOOTER_TMPL = r"\end{multicols*}"

TEX_LETTER_TMPL = TAB_1 + r"""
    \medskip
    \hspace{{3pt}}%
    \fbox{{\textbf{{\Large\texttt{{{letter}}}}}}}
    \smallskip
""".strip() + '\n'


TEX_PALETTE_TMPL = TAB_1 + r"\smallskip\hspace{{1em}}{name}"


TEX_NEW_PALETTE_TMPL =(
      TEX_PALETTE_TMPL
    + r' ${{}}^{{\text{{{{\tiny\bfseries\faStar}}}}}}$'
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


AUDIT_DIR     = BUILD_TOOLS_DIR / TAG_AUDIT
TRANSLATE_DIR = PROJ_DIR / "contrib" / "translate"
MANUAL_DIR    = TRANSLATE_DIR / "en" / "manual"


APPENDIX_TEX_FILE = MANUAL_DIR / "appendixes" / "all-names.tex"


# ---------------------- #
# -- JSON - NEW NAMES -- #
# ---------------------- #

NEW_NAMES_JSON = BUILD_TOOLS_DIR / TAG_REPORT / "AUDIT-LOCMAIN-NAMES-NEW.json"

with NEW_NAMES_JSON.open(mode = "r") as f:
    NEW_NAMES = set(json_load(f))


# -------------------- #
# -- DB - ALL NAMES -- #
# -------------------- #

logging.info("Build 'all names' TeX file")

_namescode = [TEX_HEADER_TMPL]

last_letter = ''

with sqlite3.connect(AUDIT_DIR / 'palettes.db') as conn:
    cursor = conn.cursor()

    query = """
SELECT
    COALESCE(a.alias, h.name)
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1
    """

    cursor.execute(query)

    rows = cursor.fetchall()

# Funny comma... :-)
    for name, in natsorted(
        rows,
        alg = ns.IGNORECASE
    ):
        letter = name[0].upper()

        if letter != last_letter:
            if letter in LETTERS_COL_BREAK:
                _namescode += [
                    r"\columnbreak",
                    ''
                ]

            _namescode.append(
                TEX_LETTER_TMPL.format(letter = letter)
            )

            last_letter = letter

        tmpl = (
            TEX_NEW_PALETTE_TMPL
            if name in NEW_NAMES else
            TEX_PALETTE_TMPL
        )

        _namescode += [
            tmpl.format(name = name),
            '',
        ]


_namescode[-1] = _namescode[-1].rstrip()

_namescode.append(TEX_FOOTER_TMPL)

namescode = '\n'.join(_namescode)


content = APPENDIX_TEX_FILE.read_text()

before, _ , after = content.partition(f"\n{TAG_LIST_OF_NAMES_START}")

_ , _ , after = after.partition(f"{TAG_LIST_OF_NAMES_END}\n")

content = f"""
{before}
{TAG_LIST_OF_NAMES_START}
{namescode}
{TAG_LIST_OF_NAMES_END}
{after}
""".strip() + '\n'

APPENDIX_TEX_FILE.touch()
APPENDIX_TEX_FILE.write_text(content)
