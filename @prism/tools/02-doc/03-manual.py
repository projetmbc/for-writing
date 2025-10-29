#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core    import *
from cbutils.mdutils import *

from json import load as json_load
from yaml import safe_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent

TAG_MANUAL = "manual"

TRANSLATE_DIR      = PROJECT_DIR / "contrib" / "translate"
PREDOC_MANUALS_DIR = PROJECT_DIR / "pre-doc" / TAG_MANUAL

REL_PREDOC_MANUALS_TAG = PREDOC_MANUALS_DIR.relative_to(PROJECT_DIR)
REL_PREDOC_MANUALS_TAG = ['..' for _ in REL_PREDOC_MANUALS_TAG.parents]
REL_PREDOC_MANUALS_TAG = '/'.join(REL_PREDOC_MANUALS_TAG)


LANGS = []

for f in TRANSLATE_DIR.glob("*/"):
    fname = f.name

    if (
        fname not in ['changes', 'status']
        and
        TRANSLATE_DIR / fname / TAG_MANUAL
    ):
        LANGS.append(fname)


TMPL_TEX_MANUAL = r"""
% !TEX TS-program = lualatex

\documentclass{{tutodoc}}

\usepackage{{../../contrib/translate/{lang}/manual/preamble.cfg}}

\usepackage[subpreambles = true]{{standalone}}

\makeatletter
\renewcommand{{\minted@cachedir}}{{_minted-xtra-cache}}
\makeatother

\begin{{document}}

{abstract}

\tdocsep

{{
\small

\bgroup
    \addtokomafont{{subsection}}{{\centering}}
    \subsection*{{Last changes}}
\egroup

{last_change}
}}

\newpage
\tableofcontents
\newpage

{tex_imports}

\section{{History}}

\small

{changes}

\end{{document}}
""".strip() + "\n"

TMPL_IMPORT = r"\subimport{{{rel_folder}/}}{{{file}}}"


# ----------- #
# -- TOOLS -- #
# ----------- #

def build_imports(lang: str) -> [str]:
    file_imports = _rec_build_imports(TRANSLATE_DIR / fname / TAG_MANUAL)

    tex_imports = []

    for p in file_imports:
        p = p.relative_to(PROJECT_DIR)

        rel_folder = f"{REL_PREDOC_MANUALS_TAG}/{p.parent}"
        file       = p.name

        tex_imports.append(
            TMPL_IMPORT.format(
                rel_folder = rel_folder,
                file       = file
            )
        )

    return tex_imports


def _rec_build_imports(folder: Path) -> [Path]:
    about_file = folder / "about.yaml"

    with about_file.open(mode = 'r') as f:
        toc = safe_load(f)

    toc = toc['toc']

    imports = []

    for p in toc:
        p = folder / p

        if p.is_file():
            imports.append(p)

        elif p.is_dir():
            imports += _rec_build_imports(p)

        else:
            NOT_EXIST

    return imports



def build_changes():
    return ['', '']


# ------------- #
# -- MANUALS -- #
# ------------- #

plurial = '' if len(LANGS) == 1 else 's'

logging.info(f"Building manual{plurial}.")

for lang in LANGS:
    logging.info(f"'{lang}' version.")

    tex_imports = build_imports(lang)

    changes = build_changes()

    tex_code = TMPL_TEX_MANUAL.format(
        lang        = lang,
        abstract    = tex_imports[0],
        tex_imports = '\n'.join(tex_imports[1:]),
        last_change = changes[0],
        changes     = '\n'.join(changes)
    )

    manual_file = PREDOC_MANUALS_DIR / f"manual-{lang}.tex"
    manual_file.write_text(tex_code)
