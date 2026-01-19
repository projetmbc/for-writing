#!/usr/bin/env python3

# DEBUG - ON
from rich import print
# DEBUG - OFF

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

PATTERN_CHGE_palname = re.compile(
    r"\\newcommand\{\\PALETTE\}\{(.*)\}"
)

PATTERN_CHGE_paldef = re.compile(
    r"PALETTE\s*=\s*([^\n]*)"
)

PATTERN_CHGE_PAL_CREDITS = re.compile(
    r"\\newcommand\{\\CREDIT\}\{(.*)\}"
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

\title{\raisebox{-.20ex}{@}prism palettes -- Version """.lstrip() \
+ VERSION + \
r"""  \\ __CATEGO__}
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
]{{../single/main-{palname}-{kind}.pdf}}
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

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT
PRODS_DIR  = PROJ_DIR / "products"
PREDOC_DIR = PROJ_DIR / "pre-doc" / "showcase"
SINGLE_DIR = PREDOC_DIR / "single"
CATEGO_DIR = PREDOC_DIR / "catego"


SINGLE_DIR.mkdir(exist_ok = True)
CATEGO_DIR.mkdir(exist_ok = True)


JSON_EN_TITLES = REPORT_DIR / 'CATEGORY-EN-TITLES.json'


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
TMPL_TEX_FILES = {
    k: PREDOC_DIR / "template" / f"single-palette-{k}.tex"
    for k in TEX_FILE_KINDS
}

TMPL_SINGLE_SHOWCASE_TEX_CODES = {
    k: TMPL_TEX_FILES[k].read_text()
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
    ALL_CREDITS = json_load(f)


PAL_CATEGO_JSON_FILE = REPORT_DIR / "PAL-CATEGORY.json"

with PAL_CATEGO_JSON_FILE.open(mode = "r") as f:
    ALL_CATEGOS = json_load(f)


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


with JSON_EN_TITLES.open(mode = "r") as f:
    CATEGO_TITLES = json_load(f)


# ----------- #
# -- TOOLS -- #
# ----------- #

def build_name(
    name: str,
    kind: str
) -> str:
    return f"main-{name}-{kind}"


def extract_palname(filename: str) -> str:
    return filename.split('-')[1]


# ------------------------------- #
# -- PALETTE SIZE IN TEMPLATES -- #
# ------------------------------- #

logging.info("Update the template files: value of palette size.")

texpalsize = f"\n  PALSIZE = {PALSIZE}\n"

for tmp_file in TMPL_TEX_FILES.values():
    texcode = tmp_file.read_text()

    texcode = PATTERN_UPDATE_PALSIZE.sub(texpalsize, texcode)

    tmp_file.write_text(texcode)


# ------------------------------ #
# -- REMOVED OBSOLETE FILES -- #
# ------------------------------ #

for folder, globpat, paldict in [
    (
        SINGLE_DIR,
        "main-*.tex",
        ALL_PALETTES
    ),
    (
        CATEGO_DIR,
        f"*-[{'|'.join(TEX_FILE_KINDS)}].tex",
        ALL_CATEGOS
    ),
]:
    for tex_file in natsorted([
        f
        for f in folder.glob(globpat)
    ]):
        palname = extract_palname(tex_file.stem)

        if not palname in paldict:
            logging.warning(
                 "Removing "
                f"'{tex_file.parent.name}/{tex_file.name}'"
                 " and its friends."
            )

            for ext in TEX_EXT_N_FRIENDS:
                remove_me = tex_file.parent / f"{tex_file.stem}.{ext}"
                remove_me.unlink(missing_ok = True)


# -------------------------- #
# -- UPDATED SINGLE FILES -- #
# -------------------------- #

logging.info("Add 'single palette showcase' TeX files.")

# Compilation will be done later!
for palname, paldef in ALL_PALETTES.items():
    for kind, texcode in TMPL_SINGLE_SHOWCASE_TEX_CODES.items():
        palfile = SINGLE_DIR / f"{build_name(palname, kind)}.tex"

        paldef = str(paldef)

        for old, new in [
            ('[', '{'),
            (']', '}'),
        ]:
            paldef = paldef.replace(old, new)

        palcredit = ALL_CREDITS.get(palname, None)
        palcredit = (
            "Created with @prism"
            if palcredit == "@prism" else
            f"Source: {palcredit}"
        )

        for repl, pat in [
            (palname  , PATTERN_CHGE_palname),
            (paldef   , PATTERN_CHGE_paldef),
            (palcredit, PATTERN_CHGE_PAL_CREDITS),
        ]:
            texcode = pat.sub(
                lambda m: m.group(0).replace(
                    m.group(1),
                    repl
                ),
                texcode
            )

        palfile.write_text(texcode)


# ----------------------- #
# -- CATEGO. SHOWCASES -- #
# ----------------------- #

# Compilation will be done later!
for kind in natsorted(TEX_FILE_KINDS):
    logging.info(
        f"Building '[{kind.upper()}] catego showcase' TeX files."
    )

    single_paths = {
        extract_palname(f.name): f
        for f in SINGLE_DIR.glob(f"*-{kind}.tex")
    }

    for catego, palettes in ALL_CATEGOS.items():
        tex_code = [
            HEADER_TEX_CODES[kind],
            START_FINAL_TEX_CODE.replace(
                '__CATEGO__',
                CATEGO_TITLES[catego]
            ),
        ]

        for palname in natsorted(
            palettes,
            key = lambda x: str(x).lower()
        ):
            tex_file = SINGLE_DIR / f"{build_name(palname, kind)}.tex"

            tex_code.append(
                TMPL_TEX_INCLUDE_PDF.format(
                    palname = extract_palname(tex_file.stem),
                    kind    = kind,
                )
            )

        tex_code.append(r"\end{document}")

        tex_code = '\n\n'.join(tex_code) + '\n'

        (CATEGO_DIR / f"{catego}-{kind}.tex").write_text(tex_code)
