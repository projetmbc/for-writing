#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils.cleanpal import PALSIZE

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR   = Path(__file__).parent
PROJ_DIR   = THIS_DIR.parent.parent
REPORT_DIR = PROJ_DIR / "tools" / "report"
PRODS_DIR  = PROJ_DIR / "products"
PREDOC_DIR = PROJ_DIR / "pre-doc" / "similar"


VERSION = PROJ_DIR / "tools" / "VERSION.txt"
VERSION = VERSION.read_text()
VERSION = VERSION.strip()


PAL_CATEGO_FILE = REPORT_DIR / "PAL-SIMILAR.json"

with PAL_CATEGO_FILE.open(mode = "r") as f:
    ALL_CATEGOS = json_load(f)


TEX_FILE_KINDS = [
    (STD := 'std'),
    (DARK:= 'dark')
]


CLS_TEX_CODES = {
    STD : "",
    DARK: "[theme = dark]",
}

CLS_TEX_CODES = {
    k: rf"\documentclass{opt}{{tutodoc}}"
    for k, opt in CLS_TEX_CODES.items()
}


TMPL_TEX_FILES = PREDOC_DIR / "templates" / "similar-palettes.tex"


TMPL_TEX_CODE = TMPL_TEX_FILES.read_text()
TMPL_TEX_CODE = TMPL_TEX_CODE.replace(
    r"\directlua{dofile('../../../",
    r"\directlua{dofile('../../",
)

HEADER_TEX_CODE, _ , SECTION_TEX_CODE = TMPL_TEX_CODE.partition(
    "% -- SECTION - START -- %"
)
SECTION_TEX_CODE, _ , _ = SECTION_TEX_CODE.partition(
    "% -- SECTION - END -- %"
)


TEX_CLS_CODES = {
    STD : "",
    DARK: "[theme = dark]",
}


PATTERN_TEX_SECTION = re.compile(
    r'(\\subsection\*\{Cluster \\#)(\d+)(\})'
)


PATTERN_PAL_LIST = re.compile(
    r'(PALETTES\s*=\s*\{)([^}]*)(\})'
)


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Add similar palette TeX files.")

texcode = [HEADER_TEX_CODE]

for i, cluster in enumerate(ALL_CATEGOS, 1):
    section = PATTERN_TEX_SECTION.sub(
        rf'\g<1>{i}\g<3>',
        SECTION_TEX_CODE
    )

    cluster = ", ".join(f'"{n}"' for n in cluster)

    section = PATTERN_PAL_LIST.sub(
        rf'\g<1>{cluster}\g<3>',
        section
    )

    texcode.append(section.strip())

texcode.append(r'\end{document}')

texcode = "\n\n".join(texcode)

for kind in TEX_FILE_KINDS:
    texcode = texcode.replace(
        r'\documentclass{tutodoc}',
        CLS_TEX_CODES[kind]
    )

    texfile = PREDOC_DIR / f"similar-palettes-en-{kind}.tex"
    texfile.touch()

    texfile.write_text(texcode)
