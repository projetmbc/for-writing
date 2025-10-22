#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core    import *
from cbutils.mdutils import *


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
PRODUCTS_DIR = PROJECT_DIR / "products"

README_TAG = "readme"

MAIN_README_DIR = PROJECT_DIR / README_TAG
PROD_README_DIR = MAIN_README_DIR / "products"

CONTRIB_DIR      = PROJECT_DIR / "contrib"
CONTRIB_PROD_DIR = CONTRIB_DIR / "products"
TEX_EN_DOC_DIR   = CONTRIB_DIR / "translate" / "en" / "manual" / "products"


MD_FILES_TO_CONVERT = [
    MAIN_README_DIR / "products.md"
]

MD_FILES_TO_CONVERT += [
    f
    for f in PROD_README_DIR.glob("*.md")
]

MD_USEFUL_PARTS= [
    f"{n}.md"
    for n in [
        "desc",
        "how-to-use",
    ]
]


TEMPL_TAG_JSON_BEGIN = "<!-- JSON DESC. - {} -->"

TAG_JSON_BEGIN_START = TEMPL_TAG_JSON_BEGIN.format("START")
TAG_JSON_BEGIN_END   = TEMPL_TAG_JSON_BEGIN.format("END")


CONVERTER_MD_2_TEX = MdToLatexConverter()


# ----------- #
# -- TOOLS -- #
# ----------- #

def extract_md(mdfile: Path) -> str:
# Special case of the versatile JSON file.
    if mdfile.parent == MAIN_README_DIR:
        content = mdfile.read_text()

        _ , _ , content = content.partition(f"{TAG_JSON_BEGIN_START}")
        content , _ , _ = content.partition(f"{TAG_JSON_BEGIN_END}")

# Standard case.
    else:
        content = []

        readme_dir = CONTRIB_PROD_DIR / mdfile.stem / README_TAG

        for mdfile_part in MD_USEFUL_PARTS:
            mdfile_part = readme_dir / mdfile_part

            content.append(mdfile_part.read_text())

        content = '\n\n'.join(content)

# Nothing left to do.
    return content



# --------------- #
# -- CONSTANTS -- #
# --------------- #

logging.info(
    "Updating English doc (product sections)."
)

relENdocdir = TEX_EN_DOC_DIR.relative_to(PROJECT_DIR)

for mdfile in MD_FILES_TO_CONVERT:
# Let's communicate.
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

    texfile = PROJECT_DIR / relpath_tex

# Let's work.
    mdcontent = extract_md(mdfile)

    print(f'--- {mdfile.name}')
    print(mdcontent)
