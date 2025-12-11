#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
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

PATTERN_CHGE_PAL_NAME = re.compile(
    r"\\newcommand\{\\PALETTE\}\{(.*)\}"
)

PATTERN_CHGE_PAL_DEF = re.compile(
    r"PALETTE\s*=\s*([^\n]*)"
)

PATTERN_CHGE_PAL_CREDITS  = re.compile(
    r"\\newcommand\{\\SRC\}\{(.*)\}"
)

PATTERN_UPDATE_PALSIZE = re.compile(
    r'^\s*PALSIZE\s*=\s*\d+\s*$',
    flags = re.MULTILINE
)


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


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR = BUILD_TOOLS_DIR / "REPORT"
PRODS_DIR  = PROJ_DIR / "products"
PREDOC_DIR = PROJ_DIR / "pre-doc" / "showcase"
SINGLE_DIR = PREDOC_DIR / "single"


SINGLE_DIR.mkdir(exist_ok = True)


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

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


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"

with PAL_CREDITS_FILE.open(mode = "r") as f:
    ALL_SRC = json_load(f)


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


# ----------- #
# -- TOOLS -- #
# ----------- #

def build_name(name: str) -> str:
    return f"main-{name}"


def extract_palname(filename: str) -> str:
    return filename.split('-')[1]


# ------------------------------------------ #
# -- REMOVED OLD SINGLE PALETTE SHOWCASES -- #
# ------------------------------------------ #

for tex_file in natsorted([
    f
    for f in SINGLE_DIR.glob("main-*.tex")
]):
    palname = extract_palname(tex_file.stem)

    if not palname in ALL_PALETTES:
        logging.warning(f"Removing '{tex_file.name}' and its friends.")

        for ext in TEX_EXT_N_FRIENDS:
            remove_me = tex_file.parent / f"{tex_file.stem}.{ext}"
            remove_me.unlink(missing_ok = True)


# ------------------------------ #
# -- SINGLE PALETTE SHOWCASES -- #
# ------------------------------ #

logging.info("Update the template files (size of palettes).")

texpalsize = f"\n  PALSIZE = {PALSIZE}\n"

for tmp_file in TMPL_TEX_FILES.values():
    texcode = tmp_file.read_text()

    texcode = PATTERN_UPDATE_PALSIZE.sub(texpalsize, texcode)

    tmp_file.write_text(texcode)


# ------------------------------ #
# -- SINGLE PALETTE SHOWCASES -- #
# ------------------------------ #

logging.info("Add 'single palette showcase' TeX files.")

for palname, paldef in ALL_PALETTES.items():
    for kind, texcode in TMPL_SINGLE_SHOWCASE_TEX_CODES.items():
        palfile = SINGLE_DIR / f"{build_name(palname)}-{kind}.tex"

        paldef = str(paldef)

        for old, new in [
            ('[', '{'),
            (']', '}'),
        ]:
            paldef = paldef.replace(old, new)

        palsrc = ALL_SRC.get(palname, None)
        palsrc = (
            "Created with @prism"
            if palsrc == "@prism" else
            f"Source: {palsrc}"
        )

        for repl, pat in [
            (palname, PATTERN_CHGE_PAL_NAME),
            (paldef , PATTERN_CHGE_PAL_DEF),
            (palsrc , PATTERN_CHGE_PAL_CREDITS),
        ]:
            texcode = pat.sub(
                lambda m: m.group(0).replace(
                    m.group(1),
                    repl
                ),
                texcode
            )

        palfile.write_text(texcode)


# ------------------- #
# -- FULL SHOWCASE -- #
# ------------------- #

logging.info("Building 'full palette showcase' TeX files.")

for kind, showfile in ALL_SHOWCASE_TEX_FILES.items():
    tex_code = [
        HEADER_TEX_CODES[kind],
        START_FINAL_TEX_CODE,
    ]

# Compilation will be done later!
    for tex_file in natsorted(
        [
            f
            for f in SINGLE_DIR.glob(f"*-{kind}.tex")
        ],
        key = lambda x: str(x).lower()
    ):
        tex_code.append(
            TMPL_TEX_INCLUDE_PDF.format(
                palname = extract_palname(tex_file.stem),
                kind    = kind,
            )
        )

    tex_code.append(r"\end{document}")

    tex_code = '\n\n'.join(tex_code) + '\n'

    showfile.write_text(tex_code)
