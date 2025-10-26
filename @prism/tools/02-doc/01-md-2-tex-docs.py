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

MAIN_README_DIR = PROJECT_DIR / "readme"
PROD_README_DIR = MAIN_README_DIR / "products"

TRANSLATE_DIR     = PROJECT_DIR / "contrib" / "translate"
EN_MANUAL_DIR     = TRANSLATE_DIR / "en" / "manual" / "products"
_SUB_EN_MANUAL_DIR = EN_MANUAL_DIR.relative_to(TRANSLATE_DIR)

MD_FILES_TO_CONVERT = [
    MAIN_README_DIR / "products.md"
]

MD_FILES_TO_CONVERT += [
    f
    for f in PROD_README_DIR.glob("*.md")
]


CONVERTER_MD_2_TEX = MdToLatexConverter(shift_down_level = 1)


TMPL_TEX = r"""
% !TEX TS-program = lualatex

\documentclass{{tutodoc}}

\usepackage{{../preamble.cfg}}


\begin{{document}}

{content}

\end{{document}}
""".strip() + '\n'


MD_PRE_REPLACEMENTS = {
    'luadraw': '{\\LUADRAW}',
    '@prism' : '{\\thisproj}',
}


# --------------- #
# -- LET'S GO! -- #
# --------------- #

logging.info(
    "Updating English doc (product sections)."
)



for mdfile in MD_FILES_TO_CONVERT:
# Let's communicate.
    relpath_md  = mdfile.relative_to(PROJECT_DIR)

    relpath_tex = (
        "preamble"
        if mdfile.stem == "products" else
        mdfile.stem
    )

    _relpath_tex = _SUB_EN_MANUAL_DIR / f"{relpath_tex}.tex"

    logging.info(
        msg_creation_update(
            context = f"From '{relpath_md}' to '{_relpath_tex}' TeX",
            upper = False
        )
    )

    texfile = EN_MANUAL_DIR / f"{relpath_tex}.tex"


# Let's work.
    mdcontent = mdfile.read_text()
    mdcontent = transform_code_links(mdcontent, ['luadraw'])

    texcode = CONVERTER_MD_2_TEX.markdown_to_latex(mdcontent)
    texcode = TMPL_TEX.format(content = texcode)
    texcode = transform_tdoccodein(texcode, MD_PRE_REPLACEMENTS)

    texfile.write_text(texcode)
