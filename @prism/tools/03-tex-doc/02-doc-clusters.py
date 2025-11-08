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
PREDOC_DIR = PROJ_DIR / "pre-doc" / "clusters"


VERSION = PROJ_DIR / "tools" / "VERSION.txt"
VERSION = VERSION.read_text()
VERSION = VERSION.strip()


PAL_CATEGO_FILE = REPORT_DIR / "PAL-CATEGO.json"

with PAL_CATEGO_FILE.open(mode = "r") as f:
    ALL_CATEGOS = json_load(f)


TEX_FILE_KINDS = [
    (STD := 'std'),
    (DARK:= 'dark')
]

TMPL_TEX_FILES = {
    k: PREDOC_DIR / "templates" / f"similar-palettes-{k}.tex"
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


# ------------------------------------------ #
# -- XXX -- #
# ------------------------------------------ #
