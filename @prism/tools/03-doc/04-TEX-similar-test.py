#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR   = Path(__file__).parent
PROJ_DIR   = THIS_DIR.parent.parent
REPORT_DIR = PROJ_DIR / "tools" / "report"
TEST_DIR   = PROJ_DIR / "tests" / "similar"


TEST_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


PAL_CLUSTERS_FILE = REPORT_DIR / "PAL-SIMILAR.json"

with PAL_CLUSTERS_FILE.open(mode = "r") as f:
    ALL_CLUSTERS = json_load(f)


TEX_FILE_KINDS = [
    (STD := 'std'),
    (DARK:= 'dark')
]


ALL_TEST_SIMILAR_TEX_FILES = {
    k: TEST_DIR / f"main-similar-{k}.tex"
    for k in TEX_FILE_KINDS
}


HEADER_TEX_CODES = {
    STD : "",
    DARK: "[theme = dark]",
}

HEADER_TEX_CODES = {
    k: rf"\documentclass{opt}{{tutodoc}}"
    for k, opt in HEADER_TEX_CODES.items()
}


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
    {{[{cluster_id}] {palname}}},
    lab-pal-{palname}
  }}%
]{{../../pre-doc/showcase/single/main-{palname}-{kind}.pdf}}
""".strip()


# ------------------- #
# -- TESTING FILES -- #
# ------------------- #

logging.info("Build the similar test files.")

similar_palnames = sum(ALL_CLUSTERS, [])

cluster_id = dict()

for palname in similar_palnames:
    for id, cluster in enumerate(ALL_CLUSTERS, 1):
        if palname in cluster:
            cluster_id[palname] = id

for kind, showfile in ALL_TEST_SIMILAR_TEX_FILES.items():
    tex_code = [
        HEADER_TEX_CODES[kind],
        START_FINAL_TEX_CODE,
    ]

    for palname in similar_palnames:
        tex_code.append(
            TMPL_TEX_INCLUDE_PDF.format(
                cluster_id = cluster_id[palname],
                palname    = palname,
                kind       = kind,
            )
        )

    tex_code.append(r"\end{document}")

    tex_code = '\n\n'.join(tex_code) + '\n'

    showfile.write_text(tex_code)
