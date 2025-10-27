#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
PRODUCTS_DIR = PROJECT_DIR / "products"
PREDOC_DIR   = PROJECT_DIR / "pre-doc" / "showcase"
SHOWCASE_DIR = PREDOC_DIR / "single"

PAL_JSON_FILE = PRODUCTS_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


SHOWCASE_DIR.mkdir(exist_ok = True)

TEX_FILE_KINDS = [
    (STD := 'std'),
    (DARK:= 'dark')
]

# We don't use the 'main' prefix since each showcase PDF needs
# to be compiled separately beforehand. A Bash script will handle
# this accordingly.
ALL_SHOWCASE_TEX_FILES = dict()

TMPL_TEX_FILES = {
    k: PREDOC_DIR / "templates" / f"single-palette-{k}.tex"
    for k in TEX_FILE_KINDS
}

TMPL_SINGLE_SHOWCASE_TEX_CODES = {
    k: TMPL_TEX_FILES[k].read_text()
    for k in TEX_FILE_KINDS
}


ALL_SHOWCASE_TEX_FILES = {
    k: PREDOC_DIR / f"showcase-en-{k}.tex"
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


PATTERN_CHGE_PAL_NAME = re.compile(r"\\newcommand\{\\PALETTE\}\{(.*)\}")


START_FINAL_TEX_CODE = r"""
\geometry{
  landscape,
  margin = 1.5cm
}

\usepackage{hyperref}
\usepackage{pdfpages}
\usepackage{multicol}

\def\thesection{\arabic{section}}

\title{Palettes in Action -- Version 1.2.0}
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
]{{single/main-{palname}-{kind}.pdf}}
""".strip()


TEX_EXT_N_FRIENDS = [
    "aux",
    "dvi",
    "fdb_latexmk",
    "fls",
    "log",
    "pdf",
    "tex",
]


# ----------- #
# -- TOOLS -- #
# ----------- #

def build_name(name):
    return f"main-{name}"

def extract_palname(filename):
    return filename.split('-')[1]


# ------------------------------------------ #
# -- REMOVED OLD SINGLE PALETTE SHOWCASES -- #
# ------------------------------------------ #

for tex_file in sorted([f for f in SHOWCASE_DIR.glob("main-*.tex")]):
    palname = extract_palname(tex_file.stem)

    if not palname in ALL_PALETTES:
        logging.warning(f"Removing '{palname}.tex' and its friends.")

        for ext in TEX_EXT_N_FRIENDS:
            remove_me = tex_file.parent / f"{build_name(palname)}.{ext}"

            remove_me.unlink(missing_ok = True)


# ------------------------------ #
# -- SINGLE PALETTE SHOWCASES -- #
# ------------------------------ #

logging.info("Add single palette showcase TeX files.")

for palname in ALL_PALETTES:
    for kind, tmp_file in TMPL_SINGLE_SHOWCASE_TEX_CODES.items():
        palfile = SHOWCASE_DIR / f"{build_name(palname)}-{kind}.tex"

        texcode = PATTERN_CHGE_PAL_NAME.sub(
            lambda m: m.group(0).replace(
                m.group(1),
                palname
            ),
            tmp_file
        )

        palfile.write_text(texcode)


# ------------------- #
# -- FULL SHOWCASE -- #
# ------------------- #

logging.info("Building full palette showcase TeX files.")

for kind, showfile in ALL_SHOWCASE_TEX_FILES.items():
    tex_code = [
        HEADER_TEX_CODES[kind],
        START_FINAL_TEX_CODE,
    ]

# Compilation will be done later!
    for tex_file in sorted([
        f
        for f in SHOWCASE_DIR.glob(f"*-{kind}.tex")
    ]):
        tex_code.append(
            TMPL_TEX_INCLUDE_PDF.format(
                palname = extract_palname(tex_file.stem),
                kind    = kind,
            )
        )

    tex_code.append(r"\end{document}")

    tex_code = '\n\n'.join(tex_code) + '\n'

    showfile.write_text(tex_code)
