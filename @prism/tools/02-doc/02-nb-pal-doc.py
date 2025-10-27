#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core    import *
from cbutils.mdutils import *

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent

TRANSLATE_DIR = PROJECT_DIR / "contrib" / "translate"
EN_MANUAL_DIR = TRANSLATE_DIR / "en" / "manual"

PRODUCTS_DIR = PROJECT_DIR / "products"

PAL_JSON_FILE = PRODUCTS_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)

NB_PALETTES = len(ALL_PALETTES)


TEMPL_TAG_NB_PAL = "% NB PALETTES AUTO - {}"

TAG_NB_PAL_START = TEMPL_TAG_NB_PAL.format("START")
TAG_NB_PAL_END   = TEMPL_TAG_NB_PAL.format("END")


# --------------------- #
# -- DOC - SEARCHING -- #
# --------------------- #

logging.info(
    "Updating English doc (number of palettes)."
)

tex_search_file = EN_MANUAL_DIR / "to-know" / "searching.tex"

content = tex_search_file.read_text()

for tag in [
    TAG_NB_PAL_START,
    TAG_NB_PAL_END,
]:
    if content.count(tag) != 1:
        raise ValueError(
            f"use the following special comment only once:\n{tag}"
        )

before, _ , after = content.partition(TAG_NB_PAL_START)

_ , _ , after = after.partition(TAG_NB_PAL_END)

content = f"""
{before.strip()}
{TAG_NB_PAL_START}
{NB_PALETTES}
{TAG_NB_PAL_END}
{after.strip()}
""".strip()

tex_search_file.write_text(content)
