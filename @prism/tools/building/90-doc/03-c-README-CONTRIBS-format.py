#!/usr/bin/env python3

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

from yaml import safe_load


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

TAG_MODULAR    = 'modular'
TAG_MONOLITHIC = 'monolithic'


SMALL_EXPLANATIONS = {
    TAG_MODULAR   : "each palette is in a dedicated file",
    TAG_MONOLITHIC: "files provide all the palettes",
}


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PRODS_DIR = PROJ_DIR / "contrib" / "products"


TMPL_TAG_STRUCT = "<!-- FORMAT SUPPORTED - AUTO - {} -->"

TAG_STRUCT_START = TMPL_TAG_STRUCT.format("START")
TAG_STRUCT_END   = TMPL_TAG_STRUCT.format("END")


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

for prod_dir in sorted(CONTRIB_PRODS_DIR.glob("*/*")):
    if (
        not prod_dir.is_dir()
        or
        prod_dir.name != "readme"
    ):
        continue

    name = prod_dir.parent.name

    if name in [
        "json",
        "template-stucture",
    ]:
        continue

    readme = prod_dir / 'how-to-use.md'

    with (prod_dir.parent / 'about.yaml').open('r') as f:
        about = safe_load(f)

    formats = []

    for f in [
        TAG_MODULAR,
        TAG_MONOLITHIC,
    ]:
        if about.get(f, True):
            formats.append(f)

    subcontent = ' and '.join(
        f"{f} ({SMALL_EXPLANATIONS[f]})"
        for f in formats
    )

    if len(formats) == 1:
        subcontent = f"Just one kind of format is provided: {subcontent}."

    else:
        subcontent = f"All formats are provided: {subcontent}."

    subcontent = f"> ***NOTE.*** *{subcontent}*"

    tag_update(
        logger          = logging,
        log_raise_error = log_raise_error,
        txtfile         = readme,
        tag_start       = TAG_STRUCT_START,
        tag_end         = TAG_STRUCT_END,
        subcontent      = subcontent,
        error_about     = {
            TAG_CONTEXT  : f"README - CONTRIBS - {name} formats in '{readme.name}'",
            TAG_FILE_PATH: f"{readme.relative_to(PROJ_DIR)}",
        },
    )
