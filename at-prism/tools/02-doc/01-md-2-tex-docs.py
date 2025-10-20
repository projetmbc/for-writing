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

THIS_DIR        = Path(__file__).parent
PROJECT_DIR     = THIS_DIR.parent.parent
PRODUCTS_DIR    = PROJECT_DIR / "products"
CONTRIB_DIR     = PROJECT_DIR / "contrib"
MAIN_README_DIR = PROJECT_DIR / "readme"
PROD_README_DIR = MAIN_README_DIR / "products"
TEX_EN_DOC_DIR  = (
    CONTRIB_DIR / "translate" / "en"
                / "doc" / "manual" / "products"
)

MD_FILES_TO_CONVERT = [
    MAIN_README_DIR / "products.md"
]

MD_FILES_TO_CONVERT += [
    f
    for f in PROD_README_DIR.glob("*.md")
]


# --------------- #
# -- CONSTANTS -- #
# --------------- #

logging.info(
    "Updating English doc (product sections)."
)

converter = MdToLatexConverter()

relENdocdir = TEX_EN_DOC_DIR.relative_to(PROJECT_DIR)

for mdfile in MD_FILES_TO_CONVERT:
    relpath_md  = mdfile.relative_to(PROJECT_DIR)

    relpath_tex = (
        "json"
        if mdfile.stem == "products" else
        mdfile.stem
    )

    relpath_tex = f"{relpath_tex}.tex"
    relpath_tex = relENdocdir / f"{relpath_tex}"

    logging.info(
        msg_creation_update(
            context = f"From '{relpath_md}' to '{relpath_tex}' TeX",
            upper = False
        )
    )
