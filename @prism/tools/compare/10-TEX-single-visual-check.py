#!/usr/bin/env python3

from typing import TypeAlias

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

from shutil import rmtree


# ------------ #
# -- TYPING -- #
# ------------ #

RGBCols    :TypeAlias = [float, float, float]
PaletteCols:TypeAlias = list[RGBCols]


# --------------- #
# -- CONSTANTS -- #
# --------------- #

JSON_PROD_DIR          = PROJ_DIR / "products" / "json"
DATA_DIR               = THIS_DIR / "data"
HUMAN_CHECK_DIR        = THIS_DIR / "human"
HUMAN_CHECK_SINGLE_DIR = HUMAN_CHECK_DIR / "single"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

SINGLE_TMPL_DIR = THIS_DIR / "human" / "templates"

SINGLE_TMPLS = dict()

for kind in ["dark", "std"]:
    content = (
        SINGLE_TMPL_DIR / f"single-palette-{kind}.tex"
    ).read_text()

    SINGLE_TMPLS[kind] = content


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

PATTERN_CHGE_PAL_NAME = re.compile(
    r"\\newcommand\{\\PALETTE\}\{(.*)\}"
)

PATTERN_CHGE_PAL_DEF = re.compile(
    r"PALETTE = ([^\n]*)"
)

PATTERN_CHGE_SRC = re.compile(
    r"\\newcommand\{\\SRC\}\{(.*)\}"
)


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

if HUMAN_CHECK_SINGLE_DIR.is_dir():
    rmtree(HUMAN_CHECK_SINGLE_DIR)

HUMAN_CHECK_SINGLE_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


LAST_UPDATES_JSON = DATA_DIR / f"LAST_UPDATES.json"

with LAST_UPDATES_JSON.open() as f:
    LAST_UPDATES = json_load(f)

if not LAST_UPDATES:
    logging.info("Nothing to do.")

    exit(0)


LAST_PALETTES_JSON = DATA_DIR / f"LAST_PALETTES.json"

with LAST_PALETTES_JSON.open() as f:
    LAST_PALETTES = json_load(f)


DEV_PALS_JSON = JSON_PROD_DIR / f"palettes.json"

with DEV_PALS_JSON.open() as f:
    DEV_PALETTES = json_load(f)


# ----------- #
# -- TOOLS -- #
# ----------- #

def fill_tex_tmpl(
    palname: str,
    paldef : PaletteCols,
    context: str,
    tmpl   : str,
    file   : Path,
) -> None:
    paldef = repr(paldef)

    for old, new in zip("[]", "{}"):
        paldef = paldef.replace(old, new)

    texcode = tmpl

    for repltxt, pattern in [
        (paldef , PATTERN_CHGE_PAL_DEF),
        (palname, PATTERN_CHGE_PAL_NAME),
        (context, PATTERN_CHGE_SRC),
    ]:
        texcode = pattern.sub(
            lambda m: m.group(0).replace(
                m.group(1),
                repltxt
            ),
            texcode
        )

    file.write_text(texcode)


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Build TeX files for human checking.")

for kind, tmpl in SINGLE_TMPLS.items():
    for palname in LAST_UPDATES:
        logging.info(f"TeX files for '{palname}'.")

        assert LAST_PALETTES[palname] != DEV_PALETTES[palname]

        for palettes, ctxt, tag in [
            (LAST_PALETTES, "PREVIOUS VERSION", "last"),
            (DEV_PALETTES, "CURRENT DEV VERSION", "dev"),
        ]:
            fill_tex_tmpl(
                palname  = palname,
                paldef   = palettes[palname],
                context  = ctxt,
                tmpl     = tmpl,
                file     = HUMAN_CHECK_SINGLE_DIR / f"{kind}-{palname}-{tag}.tex",
            )
