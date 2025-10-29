#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core    import *
from cbutils.mdutils import *

from datetime import datetime

from json import load as json_load
from yaml import safe_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent


TAG_MANUAL  = "manual"
TAG_CHANGES = "changelog"


TNSCHGES_DIR = PROJECT_DIR / "changes" / "stable"

PATTERN_TNS_VERSION = re.compile(
    r'==+\s*\n\s*(\d+)\s+\((\d+\.\d+\.\d+)\)\s*\n\s*==+'
)


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

def build_imports(lang: str) -> (Path, [str]):
    file_imports = _rec_build_imports(TRANSLATE_DIR / fname / TAG_MANUAL)

    tex_imports = []

    for p in file_imports:
        if p.stem == 'abstract':
            asbtract_path = p
            continue

        p = p.relative_to(PROJECT_DIR)

        rel_folder = f"{REL_PREDOC_MANUALS_TAG}/{p.parent}"
        file       = p.name

        tex_imports.append(
            TMPL_IMPORT.format(
                rel_folder = rel_folder,
                file       = file
            )
        )

    return asbtract_path, tex_imports


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


def extract_tex_content(texcode: str) -> str:
    _ , _ , texcode = texcode.partition(r'\begin{document}')
    texcode, _ , _  = texcode.partition(r'\end{document}')

    texcode = texcode.strip()

    return texcode


def build_changes(lang: str) -> (datetime, str, [str]):
    all_texcodes = []

    chges_folder = TRANSLATE_DIR / fname / TAG_MANUAL / TAG_CHANGES

    all_chgefiles = sorted(
        [
            f
            for f in chges_folder.rglob('*')
            if f.is_file() and f.suffix == '.tex'
        ],
        reverse = True
    )

    date_2_versions = dict()

    for chgefile in all_chgefiles:
        if chgefile.stem == "next":
            continue

        year       = chgefile.parent.name
        month_day  = chgefile.stem
        month, day = chgefile.stem.split('-')

        fulldate = f"{year}-{month_day}"

        if not fulldate in date_2_versions:
            tnschgefile = TNSCHGES_DIR / year /f"{month}.txt"

            matches = PATTERN_TNS_VERSION.findall(
                tnschgefile.read_text()
            )

            for d, v in matches:
                date_2_versions[f"{year}-{month}-{d}"] = v

        version = date_2_versions.get(fulldate, None)

        if version is None:
            BUG

        texcode = extract_tex_content(chgefile.read_text())

        _ , _ , texcode = texcode.partition(r'\small')

        texcode = texcode.strip()

        first, *others = texcode.split('\n')

        if first.startswith(r"\tdocstartproj"):
            first += rf"\tdocversion{{{version}}}[{fulldate}]"

        else:
            first += f"[version = {version}, date = {fulldate}]"

        first += f"\n"

        texcode = first + '\n'.join(others)

        all_texcodes.append(texcode)


    for lastdate, lastversion in date_2_versions.items():
        break

    lastdate = datetime(
        *list(
            map(int, lastdate.split('-'))
        )
    )

    return lastdate, lastversion, all_texcodes


# ------------- #
# -- MANUALS -- #
# ------------- #

plurial = '' if len(LANGS) == 1 else 's'

logging.info(f"Building manual{plurial}.")

for lang in LANGS:
    logging.info(f"'{lang}' version.")

    asbtract_path, tex_imports     = build_imports(lang)
    lastdate, lastversion, changes = build_changes(lang)

    abstract = extract_tex_content(asbtract_path.read_text())

    last_change = changes[0]
    changes     = '\n\n\\tdocsep\n\n'.join(changes)

    tex_code = TMPL_TEX_MANUAL.format(
        lang        = lang,
        abstract    = abstract,
        tex_imports = '\n'.join(tex_imports),
        last_change = last_change,
        changes     = changes
    )

    tex_code = tex_code.replace(
        "<<AUTHOR>>",
        "Christophe BAL"
    )

    lastdate = lastdate.strftime("%-d %b %Y")

    tex_code = tex_code.replace(
        "<<DATE-N-VERSION>>",
        f"{lastdate} -- Version {lastversion}"
    )

    manual_file = PREDOC_MANUALS_DIR / f"manual-{lang}.tex"
    manual_file.write_text(tex_code)
