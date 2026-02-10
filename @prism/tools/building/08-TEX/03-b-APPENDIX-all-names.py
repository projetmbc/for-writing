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

from natsort import natsorted


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

LETTERS_COL_BREAK = ''
LETTERS_COL_BREAK = 'DT'


TAB_1 = ' '*4
TAB_2 = TAB_1*2


TEX_HEADER_TMPL = r"""
% !TEX TS-program = lualatex

% ------------------------------------------- %
% -- AUTOMATICALLY GENERATED - DO NOT EDIT -- %
% ------------------------------------------- %

\documentclass{tutodoc}

\usepackage{../preamble.cfg}

\begin{document}

\phantomsection
\section*{\hfill Appendix 1 -- All palette names \hfill\null} \label{palette-all-names}
\addcontentsline{toc}{section}{Appendix 1 -- All palette names}


\begin{tdocwarn}
    The palette names in this appendix are standard, but some \thisproj\ implementations add a specific prefix.
\end{tdocwarn}


\begin{multicols*}{3}
%    \setlength{\columnseprule}{0.5pt}
%    \renewcommand{\columnseprulecolor}{\color{LightGrey}}
""".strip()+ '\n'


TEX_FOOTER_TMPL = r"""
\end{multicols*}

\end{document}""".strip()


TEX_LETTER_TMPL = TAB_1 + r"""
    \medskip
    \hspace{{3pt}}%
    \fbox{{\textbf{{\Large\texttt{{{letter}}}}}}}
    \smallskip
""".strip() + '\n'


TEX_PALETTE_TMPL = TAB_1 + r"""
    \smallskip
    \hspace{{1em}}{name}
""".strip() + '\n'


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


# -------------------- #
# -- DB - ALL NAMES -- #
# -------------------- #

logging.info("Build 'all names' TeX file")

_texcode = [TEX_HEADER_TMPL]

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

    for name, in natsorted(rows):
        letter = name[0].upper()

        if letter != last_letter:
            if letter in LETTERS_COL_BREAK:
                _texcode.append(r"\columnbreak")

            _texcode.append(
                TEX_LETTER_TMPL.format(letter = letter)
            )

            last_letter = letter

        _texcode.append(
            TEX_PALETTE_TMPL.format(name = name)
        )

_texcode[-1] = _texcode[-1].rstrip()

_texcode.append(TEX_FOOTER_TMPL)

texcode = '\n'.join(_texcode)

APPENDIX_TEX_FILE.touch()
APPENDIX_TEX_FILE.write_text(texcode)
