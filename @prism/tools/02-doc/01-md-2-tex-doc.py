#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core    import *
from cbutils.mdutils import *

from yaml import dump as yaml_dump


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

MD_PRE_REPLACEMENTS = {
    '@prism' : r'{\thisproj}',
    'luadraw': r'{\LUADRAW}',
}

MD_PRE_REPLACEMENTS |= {
    m: f'{{\\{m.lower()}}}'
    for m in [
        'Lua',
    ]
}

MD_PRE_REPLACEMENTS |= {
    m: f'{{\\{m}}}'
    for m in [
        'LuaLaTeX',
        'TikZ',
    ]
}


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent


MAIN_README_DIR = PROJECT_DIR / "readme"
PROD_README_DIR = MAIN_README_DIR / "products"


TRANSLATE_DIR      = PROJECT_DIR / "contrib" / "translate"
EN_MANUAL_DIR      = TRANSLATE_DIR / "en" / "manual" / "products"
_SUB_EN_MANUAL_DIR = EN_MANUAL_DIR.relative_to(TRANSLATE_DIR)


MANUAL_PROD_ABOUT_YAML = EN_MANUAL_DIR / "about.yaml"


MD_FILES_TO_CONVERT = [
    MAIN_README_DIR / "products.md"
]

MD_FILES_TO_CONVERT += [
    f
    for f in sorted(PROD_README_DIR.glob("*.md"))
]


CONVERTER_MD_2_TEX = MdToLatexConverter(shift_down_level = 1)



TMPL_TEX = r"""
% !TEX TS-program = lualatex

% ------------------------------------------------- %
% -- DO NOT MODIFY. FILE GENERATED AUTOMATICALLY -- %
% ------------------------------------------------- %

\documentclass{{tutodoc}}

\usepackage{{../preamble.cfg}}


\begin{{document}}

% -- AUTOMATICALLY GENERATED UGLY CODE - START -- %

{content}

% -- AUTOMATICALLY GENERATED UGLY CODE - END -- %

\end{{document}}
""".strip() + '\n'


PATTERN_TEX_SECTION = re.compile(
    r'(\\section\{[^}]+\})'
)
PATTERN_TEX_SUBSECTION = re.compile(
    r'(\\subsection\{[^}]+\})'
)


# ----------- #
# -- TOOLS -- #
# ----------- #

def add_label(
    texcode: str,
    fname  : str
) -> str:
# Just for the preamble file.
    if fname == "products":
        texcode = PATTERN_TEX_SECTION.sub(
            r'\1\n\\label{products-all}',
            texcode,
            count = 1
        )

# For all files.
    label = (
        "json"
        if fname == "products" else
        fname
    )

    texcode = PATTERN_TEX_SUBSECTION.sub(
        rf'\1\n\\label{{products-{label}}}',
        texcode,
        count = 1
    )

    return texcode


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
            upper   = False
        )
    )

# Let's work.
    mdcontent = mdfile.read_text()
    mdcontent = transform_code_links(mdcontent, ['luadraw'])

    texcode = CONVERTER_MD_2_TEX.markdown_to_latex(mdcontent)
    texcode = TMPL_TEX.format(content = texcode)
    texcode = transform_tdoccodein(texcode, MD_PRE_REPLACEMENTS)
    texcode = add_label(texcode, mdfile.stem)

    texfile = EN_MANUAL_DIR / f"{relpath_tex}.tex"
    texfile.write_text(texcode)

# about.yaml hard coded.
logging.info(
    msg_creation_update(
        context = f"'{_SUB_EN_MANUAL_DIR}/about.yaml'",
        upper   = False
    )
)

MANUAL_PROD_ABOUT_YAML.touch()

toc = {
    'toc': [
        "preamble.tex"
        if f.stem == "products" else
        f"{f.stem}.tex"
        for f in MD_FILES_TO_CONVERT
    ]
}

with MANUAL_PROD_ABOUT_YAML.open("w") as f:
    yaml.dump(toc, f)

content = MANUAL_PROD_ABOUT_YAML.read_text()
content = content.replace('\n-', '\n  -')

MANUAL_PROD_ABOUT_YAML.write_text(content)
