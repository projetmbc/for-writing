#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
PRODUCTS_DIR = PROJECT_DIR / "products"
CONTRIB_DIR  = PROJECT_DIR / "contrib"

CONTRIB_PRODUCTS   = CONTRIB_DIR / "products"
CONTRIB_EN_DOC_DIR = (
    CONTRIB_DIR / "translate" / "en"
                / "doc" / "manual" / "products"
)

PAL_JSON_FILE = PRODUCTS_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


# ------------------- #
# -- PARSING TOOLS -- #
# ------------------- #
markdown_input = """Description
-----------
You can use palettes with [`luadraw`][1] which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLatex` and `TikZ`.
> ***NOTE.*** *Initially, the `at-prism` project was created to provide ready-to-use palettes for `luadraw`.*
> ligne bis
[1]: https://github.com/pfradin/luadraw
"""


import re

def parse_markdown_to_latex(markdown_text):
    """
    Convertit un document Markdown simple en LaTeX.
    """
    lines = markdown_text.split('\n')
    latex_output = []
    in_code_block = False
    in_list = False
    in_quote = False
    code_language = ""
    link_refs = {}  # Stockage des références de liens

    # Première passe : extraire les références de liens [id]: url
    for line in lines:
        link_ref_match = re.match(r'^\[(\d+)\]:\s+(.+)$', line)
        if link_ref_match:
            ref_id = link_ref_match.group(1)
            url = link_ref_match.group(2).strip()
            link_refs[ref_id] = url

    i = 0
    while i < len(lines):
        line = lines[i]

        # Bloc de code avec ~~~
        if line.startswith('~~~'):
            if not in_code_block:
                # Début du bloc de code
                code_language = line[3:].strip() or "text"
                latex_output.append(f"\\begin{{lstlisting}}[language={code_language}]")
                in_code_block = True
            else:
                # Fin du bloc de code
                latex_output.append("\\end{lstlisting}")
                in_code_block = False
                code_language = ""
            i += 1
            continue

        # Si on est dans un bloc de code, ajouter tel quel
        if in_code_block:
            latex_output.append(line)
            i += 1
            continue

        # Titre de niveau 2 (ligne suivie de -----)
        if i + 1 < len(lines) and re.match(r'^-{3,}$', lines[i + 1]):
            latex_output.append(f"\\section{{{line}}}")
            i += 2
            continue

        # Titre de niveau 1 (ligne suivie de =====)
        if i + 1 < len(lines) and re.match(r'^={3,}$', lines[i + 1]):
            latex_output.append(f"\\chapter{{{line}}}")
            i += 2
            continue

        # Ignorer les lignes de définition de liens [id]: url
        if re.match(r'^\[\d+\]:\s+', line):
            i += 1
            continue

        # Citation (ligne commençant par >)
        if line.startswith('>'):
            if not in_quote:
                # Vérifier si c'est une citation NOTE spéciale
                content = line[1:].strip()
                if content.startswith('***NOTE.***'):
                    latex_output.append("\\begin{tdocnote}")
                    in_quote = 'tdocnote'
                else:
                    latex_output.append("\\begin{quote}")
                    in_quote = 'quote'
            # Enlever le > et l'espace
            content = line[1:].strip()
            content = process_inline_formatting(content, link_refs)
            latex_output.append(content)
            i += 1
            continue
        else:
            if in_quote:
                if in_quote == 'tdocnote':
                    latex_output.append("\\end{tdocnote}")
                else:
                    latex_output.append("\\end{quote}")
                latex_output.append("")
                in_quote = False

        # Liste à puces (ligne commençant par *)
        if re.match(r'^\s*\*\s+', line):
            if not in_list:
                latex_output.append("\\begin{itemize}")
                in_list = True
            # Extraire le contenu après *
            content = re.sub(r'^\s*\*\s+', '', line)
            content = process_inline_formatting(content, link_refs)
            latex_output.append(f"    \\item {content}")
            i += 1
            continue
        else:
            if in_list:
                latex_output.append("\\end{itemize}")
                latex_output.append("")
                in_list = False

        # Ligne vide
        if line.strip() == '':
            latex_output.append("")
            i += 1
            continue

        # Texte normal
        processed_line = process_inline_formatting(line, link_refs)
        latex_output.append(processed_line)
        i += 1

    # Fermer les environnements ouverts
    if in_list:
        latex_output.append("\\end{itemize}")
    if in_quote:
        if in_quote == 'tdocnote':
            latex_output.append("\\end{tdocnote}")
        else:
            latex_output.append("\\end{quote}")
    if in_code_block:
        latex_output.append("\\end{lstlisting}")

    return '\n'.join(latex_output)

def process_inline_formatting(text, link_refs=None):
    """
    Traite les formatages inline (gras, italique, code, liens).
    """
    if link_refs is None:
        link_refs = {}

    # Liens avec référence [texte][id]
    def replace_link(match):
        link_text = match.group(1)
        ref_id = match.group(2)
        if ref_id in link_refs:
            url = link_refs[ref_id]
            return f"\\href{{{url}}}{{{link_text}}}"
        return match.group(0)

    text = re.sub(r'\[([^\]]+)\]\[(\d+)\]', replace_link, text)

    # Liens directs [texte](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\\href{\2}{\1}', text)

    # Code inline `code`
    text = re.sub(r'`([^`]+)`', r'\\texttt{\1}', text)

    # Gras + italique ***texte***
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\\textbf{\\textit{\1}}', text)

    # Gras **texte**
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)

    # Italique *texte*
    text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)

    return text

latex_output = parse_markdown_to_latex(markdown_input)
print(latex_output)
print("\n" + "="*50)
print("Note: Ajoutez les packages suivants dans votre préambule LaTeX:")
print("  \\usepackage{hyperref}")
print("  % Et l'environnement tdocnote doit être défini")
