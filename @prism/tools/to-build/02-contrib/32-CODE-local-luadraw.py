#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR     = PROJ_DIR / "products"
EN_MANUAL_DIR = PROJ_DIR / "contrib" / "translate" / "en" / "manual"


LAST_LUADRAW_PALS_FILE = PRODS_DIR / "luadraw" / "palettes.lua"
CFG_TEX_FILE = EN_MANUAL_DIR / "preamble.cfg.sty"


TMPL_TAG_LAST_PALS = "-- AUTO LAST PALETTES - {}"

TAG_LAST_PALS_START = TMPL_TAG_LAST_PALS.format("START")
TAG_LAST_PALS_END   = TMPL_TAG_LAST_PALS.format("END")


# ---------------- #
# -- LET'S WORK -- #
# ---------------- #

logging.info("Update 'palettes' for manual TeX file.")

luacode = LAST_LUADRAW_PALS_FILE.read_text()

content = CFG_TEX_FILE.read_text()

before, _ , after = content.partition(f"\n{TAG_LAST_PALS_START}")

_ , _ , after = after.partition(f"{TAG_LAST_PALS_END}\n")

content = f"""
{before}
{TAG_LAST_PALS_START}
{luacode}
{TAG_LAST_PALS_END}
{after}
""".lstrip()

CFG_TEX_FILE.write_text(content)
