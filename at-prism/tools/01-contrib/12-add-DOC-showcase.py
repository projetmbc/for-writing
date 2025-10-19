#!/usr/bin/env python3

from pathlib import Path
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
PREDOC_DIR   = PROJECT_DIR / "showcase"
SHOWCASE_DIR = PREDOC_DIR / "single"

PAL_JSON_FILE = PRODUCTS_DIR / "palettes.json"
TMPL_TEX_FILE = PREDOC_DIR / "templates" / "palette-showcase.tex"

# We don't use the 'main' prefix since each showcase PDF needs
# to be compiled separately beforehand. A Bash script will handle
# this accordingly.
ALL_SHOWCASE_TEX_FILE = PREDOC_DIR / "showcase-en.tex"


with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)

TMPL_SINGLE_SHOWCASE_TEX = TMPL_TEX_FILE.read_text()

SHOWCASE_DIR.mkdir(exist_ok = True)


PATTERN_CHGE_PAL_NAME = re.compile(r"\\newcommand\{\\PALETTE\}\{(.*)\}")


START_FINAL_TEX_CODE = r"""\documentclass[a4paper]{article}

\usepackage[
  landscape,
  margin = 1.5cm
]{geometry}

\usepackage{hyperref}
\usepackage{pdfpages}
\usepackage{multicol}

\title{Palettes in Action -- Version 1.1.1}
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
]{{single/main-{palname}.pdf}}
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

PREFIX_LEN = len("main-")

def build_name(name):
    return f"main-{name}"

def extract_palname(filename):
    return filename[PREFIX_LEN:]


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
    palfile = SHOWCASE_DIR / f"{build_name(palname)}.tex"

    texcode = PATTERN_CHGE_PAL_NAME.sub(
        lambda m: m.group(0).replace(
            m.group(1),
            palname
        ),
        TMPL_SINGLE_SHOWCASE_TEX
    )

    palfile.write_text(texcode)


# ------------------- #
# -- FULL SHOWCASE -- #
# ------------------- #

logging.info("Building full palette showcase TeX file.")

tex_code = [START_FINAL_TEX_CODE]

# Compilation will be done later!
for tex_file in sorted([f for f in SHOWCASE_DIR.glob("*.tex")]):
    tex_code.append(
        TMPL_TEX_INCLUDE_PDF.format(
            palname = extract_palname(tex_file.stem)
        )
    )

tex_code.append(r"\end{document}")

tex_code = '\n\n'.join(tex_code) + '\n'

ALL_SHOWCASE_TEX_FILE.write_text(tex_code)
