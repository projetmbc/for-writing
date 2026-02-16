#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR.parent

while PROJ_DIR.name != "@prism":
    PROJ_DIR = PROJ_DIR.parent

TOOLS_DIR = PROJ_DIR / "tools" / "building"

sys.path.append(str(TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from datetime import datetime

from natsort import natsorted, ns


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

DATA_DIR = THIS_DIR / "data"

LAST_UPDATES_JSON = DATA_DIR / f"LAST_UPDATES.json"

with LAST_UPDATES_JSON.open() as f:
    LAST_UPDATES = json_load(f)

if not LAST_UPDATES:
    logging.info("Nothing to do")

    exit()


HUMAN_CHECK_DIR        = THIS_DIR / "human"
HUMAN_CHECK_SINGLE_DIR = HUMAN_CHECK_DIR / "single"
HUMAN_CHECK_BCKUP_DIR  = HUMAN_CHECK_DIR / "check"


HUMAN_CHECK_BCKUP_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

START_FINAL_TEX_CODE = r"""
\geometry{
  landscape,
  margin = 1.75cm
}

\usepackage{hyperref}
\usepackage{pdfpages}
\usepackage{multicol}

\def\thesection{\arabic{section}}

\title{\raisebox{-.20ex}{@}prism palettes -- Version """.lstrip() + VERSION + r"""}
\date{}

\begin{document}

\maketitle{}

{
  \setlength{\columnsep}{2cm}
  \setlength{\columnseprule}{0.4pt}

  \begin{multicols}{2}
    \tableofcontents
  \end{multicols}
}

\newpage
""".strip()


TMPL_TEX_INCLUDE_PDF = r"""
\includepdf[%
  pagecommand = {{\thispagestyle{{plain}}}},%
  pages       = 1,%
  addtotoc    = {{%
    1,%
    section,%
    1,
    {palname},
    lab-pal-{palname}
  }}%
]{{../../single/{kind}-{palname}-{src}.pdf}}
""".strip()


HEADER_TEX_CODES = {
    "std" : "",
    "dark": "[theme = dark]",
}

HEADER_TEX_CODES = {
    k: rf"\documentclass{opt}{{tutodoc}}"
    for k, opt in HEADER_TEX_CODES.items()
}


# ------------------- #
# -- FULL SHOWCASE -- #
# ------------------- #

now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


all_singles = dict()

for kind in ['dark', 'std']:
    all_singles[kind] = natsorted(
        HUMAN_CHECK_SINGLE_DIR.glob(f"{kind}-*.tex"),
        alg = ns.IGNORECASE
    )

if not all_singles['dark']:
    logging.info(f"'No TeX files' build")

    exit()


logging.info(f"Building '{now} TeX files'")

for kind in ['dark', 'std']:
    showfile = HUMAN_CHECK_BCKUP_DIR / f"{now}" / f"{kind}.tex"

    showfile.parent.mkdir(
        parents  = True,
        exist_ok = True
    )

    tex_code = [
        "% !TEX TS-program = lualatex",
        HEADER_TEX_CODES[kind],
        START_FINAL_TEX_CODE,
    ]

    for texfile in all_singles[kind]:
        _ , palname, src = texfile.stem.split('-')

        tex_code.append(
            TMPL_TEX_INCLUDE_PDF.format(
                kind    = kind,
                src     = src,
                palname = palname,
            )
        )

    tex_code.append(r"\end{document}")
    tex_code = '\n\n'.join(tex_code) + '\n'

    showfile.write_text(tex_code)
