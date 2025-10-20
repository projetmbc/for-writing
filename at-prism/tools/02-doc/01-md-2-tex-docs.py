#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

from json import load as json_load

from markdown_it import MarkdownIt
from markdown_it.token import Token


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






PATTERN_REF_LINK = re.compile(r'(?<!\!)\[([^\]]+)\]\s*\[\s*([^\]]*)\s*\]')

PATTERN_ONE_REF_LINK = re.compile(
    r"""
^[ \t]*                              # indentation facultative avant la référence
\[ (?P<label>[^\]]+) \] :            # label de référence entre crochets, suivi de ':'
[ \t]*                               # espaces facultatifs avant l'URL

# URL : soit entre <...>, soit brute jusqu'à un espace, tab ou retour ligne
(?P<url> <[^>\s]+> | [^ \t\n]+ )

# Partie optionnelle : titre entre guillemets, apostrophes ou parenthèses
(?: [ \t]+                           # au moins un espace avant le titre
    (?P<title>                       # groupe nommé pour le titre
        "(?:[^"]*)"                  #   - entre guillemets doubles
        | '(?:[^']*)'                #   - entre apostrophes simples
        | \( [^()]* \)               #   - entre parenthèses
    )
)?

[ \t]*$                              # espaces facultatifs en fin de ligne
    """.strip(),
    re.MULTILINE | re.VERBOSE
)


TEX_ESCAPE_IT = {
        '\\': r'\textbackslash{}',
        '{': r'\{',
        '}': r'\}',
        '$': r'\$',
        '&': r'\&',
        '%': r'\%',
        '#': r'\#',
        '_': r'\_',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}'
    }


class MdToLatexConverter:
    """
    Convertisseur Markdown -> LaTeX.
    - Transforme d'abord les reference-style links (full & collapsed) en liens inline.
    - Parse le Markdown avec markdown-it-py et convertit les tokens en LaTeX.
    """

    # regex pour détecter [texte][label] (label peut être vide => collapsed)
    PATTERN_REF_LINK = re.compile(r'(?<!\!)\[([^\]]+)\]\s*\[\s*([^\]]*)\s*\]')

    # regex verbose pour capturer une définition de référence [label]: url "title"
    PATTERN_ONE_REF_LINK = re.compile(r"""
        ^[ \t]*                             # indentation facultative
        \[(?P<label>[^\]]+)\]:              # [label]:
        [ \t]*                              # espaces
        (?P<url><[^>\s]+>|[^ \t\n]+)        # url (avec ou sans <...>)
        (?:[ \t]+                           # optionnel : espace + title
           (?P<title>"[^"]*"|'[^']*'|\([^()]*\))
        )?
        [ \t]*$                             # fin de ligne
    """, re.VERBOSE | re.MULTILINE)

    TEX_ESCAPE_IT = {
        '\\': r'\textbackslash{}',
        '{': r'\{',
        '}': r'\}',
        '$': r'\$',
        '&': r'\&',
        '%': r'\%',
        '#': r'\#',
        '_': r'\_',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}'
    }

    def __init__(self, case_insensitive_refs: bool = True):
        """
        case_insensitive_refs: si True on stocke les labels en minuscules (comportement courant en Markdown).
        """
        self.case_insensitive_refs = case_insensitive_refs

    # ---------------------- #
    # -- REF HANDLING -- #
    # ---------------------- #
    def _extract_reference_definitions(self, md_text: str) -> dict[str, str]:
        """
        Lit toutes les définitions de référence et retourne dict {label: url}.
        Ne fait pas de suppression dans md_text — seulement extraction.
        """
        refs: dict[str, str] = {}
        for m in self.PATTERN_ONE_REF_LINK.finditer(md_text):
            label = m.group('label')
            url = m.group('url')
            if url.startswith('<') and url.endswith('>'):
                url = url[1:-1]
            key = label.lower() if self.case_insensitive_refs else label
            refs[key] = url
            logging.debug("Found ref: %s -> %s", key, url)
        return refs

    def _replace_reference_links(self, md_text: str, refs: dict[str, str]) -> str:
        """
        Remplace occurrences [text][label] et [text][] par [text](url) en utilisant refs.
        Si une référence n'est pas trouvée, on garde l'original et loggue.
        """
        def repl(m: re.Match) -> str:
            text_label = m.group(1)
            label = m.group(2)
            key = (label if label else text_label)
            key = key.lower() if self.case_insensitive_refs else key
            url = refs.get(key)
            if url:
                return f'[{text_label}]({url})'
            else:
                logging.warning("Label de référence non trouvé pour '%s' (clé cherché: '%s')", text_label, key)
                return m.group(0)  # on ne modifie pas si la ref est inconnue

        # Eviter de transformer les images : ![alt][id]
        processed = self.PATTERN_REF_LINK.sub(repl, md_text)
        return processed

    def _remove_reference_definitions(self, md_text: str) -> str:
        """Supprime toutes les lignes '[label]: ...' du texte."""
        processed = re.sub(r'^[ \t]*\[[^\]]+\]:.*$', '', md_text, flags=re.MULTILINE)
        return processed.strip()

    def md_hard_links(self, md_text: str) -> str:
        """
        Étape complète :
        1) Extraire définitions [label]: url
        2) Remplacer [text][label] / [text][] par [text](url)
        3) Supprimer lignes de définitions
        """
        refs = self._extract_reference_definitions(md_text)
        if not refs:
            # rien à faire
            return md_text

        processed = self._replace_reference_links(md_text, refs)
        processed = self._remove_reference_definitions(processed)
        return processed

    # ----------------------- #
    # -- LATEX UTILITIES -- #
    # ----------------------- #
    @classmethod
    def escape_latex(cls, text: str) -> str:
        """Échappe les caractères spéciaux LaTeX"""
        for char, replacement in cls.TEX_ESCAPE_IT.items():
            text = text.replace(char, replacement)
        return text

    # ----------------------------- #
    # -- TOKEN -> LATEX CONVERSION -#
    # ----------------------------- #
    def process_inline(self, tokens: list) -> str:
        """
        Traite une liste de tokens inline (children d'un token inline).
        Retourne une chaîne LaTeX.
        """
        if not tokens:
            return ""

        result: list[str] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == 'text':
                result.append(self.escape_latex(token.content))

            elif token.type == 'code_inline':
                result.append(f'\\texttt{{{self.escape_latex(token.content)}}}')

            elif token.type == 'strong_open':
                # contenu attendue dans le token suivant
                i += 1
                content = tokens[i].content if i < len(tokens) else ""
                result.append(f'\\textbf{{{self.escape_latex(content)}}}')
                # skip strong_close will happen by normal loop increment

            elif token.type == 'em_open':
                i += 1
                content = tokens[i].content if i < len(tokens) else ""
                result.append(f'\\textit{{{self.escape_latex(content)}}}')

            elif token.type == 'link_open':
                href = token.attrGet('href') or ''
                i += 1
                link_text_parts: list[str] = []
                # collect until link_close
                while i < len(tokens) and tokens[i].type != 'link_close':
                    if tokens[i].type == 'text':
                        link_text_parts.append(self.escape_latex(tokens[i].content))
                    elif tokens[i].type == 'code_inline':
                        link_text_parts.append(f'\\texttt{{{self.escape_latex(tokens[i].content)}}}')
                    i += 1
                text = ''.join(link_text_parts)
                # si href commence par '#' (ancre), on affiche juste le texte sans \href
                if href.startswith('#'):
                    result.append(text)
                else:
                    result.append(f'\\href{{{href}}}{{{text}}}')

            elif token.type == 'softbreak':
                result.append(' ')

            elif token.type == 'hardbreak':
                result.append('\\\\')

            else:
                # cas non gérés explicitement : logging.debug pour info
                logging.debug("Token inline non traité: %s", token.type)

            i += 1

        return ''.join(result)

    def convert_tokens_to_latex(self, tokens: list) -> str:
        """
        Parcours la liste de tokens renvoyée par markdown-it-py et construit le document LaTeX.
        Cette fonction reproduit la logique du code initial, mais organisée par méthodes/classes.
        """
        latex_lines: list[str] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]

            # ---- headings ----
            if token.type == 'heading_open':
                # tag 'h1'..'h6' -> niveau
                level = int(token.tag[1]) if token.tag and len(token.tag) > 1 else 1
                i += 1
                content = tokens[i].content if i < len(tokens) else ""
                section_commands = ['section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph']
                cmd = section_commands[min(level - 1, len(section_commands) - 1)]
                latex_lines.append(f'\\{cmd}{{{self.escape_latex(content)}}}')
                # skip heading_close by continuing loop
                # i will be incremented at end

            # ---- paragraph ----
            elif token.type == 'paragraph_open':
                i += 1
                if i < len(tokens):
                    content_token = tokens[i]
                    # Détecter une éventuelle définition (contenu textuel commençant par [label]:)
                    is_link_def = (content_token.content and content_token.content.strip().startswith('[') and ']:' in content_token.content)
                    if not is_link_def:
                        content = self.process_inline(content_token.children) if content_token.children else ""
                        if content.strip():
                            latex_lines.append(content)
                            latex_lines.append('')  # blank line after paragraph
                # skip paragraph_close later

            # ---- blockquote ----
            elif token.type == 'blockquote_open':
                i += 1
                quote_content: list[str] = []
                while i < len(tokens) and tokens[i].type != 'blockquote_close':
                    if tokens[i].type == 'paragraph_open':
                        i += 1
                        if i < len(tokens) and tokens[i].children:
                            quote_content.append(self.process_inline(tokens[i].children))
                        i += 1  # skip paragraph_close
                    else:
                        i += 1
                latex_lines.append('\\begin{quote}')
                latex_lines.append('\n'.join(quote_content))
                latex_lines.append('\\end{quote}')
                latex_lines.append('')
                # the outer loop will increment i

            # ---- bullet lists ----
            elif token.type == 'bullet_list_open':
                latex_lines.append('\\begin{itemize}')

            elif token.type == 'bullet_list_close':
                latex_lines.append('\\end{itemize}')
                latex_lines.append('')

            elif token.type == 'list_item_open':
                # gather item content until list_item_close
                i += 1
                item_content: list[str] = []
                while i < len(tokens) and tokens[i].type != 'list_item_close':
                    if tokens[i].type == 'paragraph_open':
                        i += 1
                        if i < len(tokens) and tokens[i].children:
                            item_content.append(self.process_inline(tokens[i].children))
                        i += 1  # skip paragraph_close
                    else:
                        i += 1
                latex_lines.append(f'\\item {" ".join(item_content)}')

            # ---- code fence ----
            elif token.type == 'fence':
                lang = token.info or 'text'
                code = token.content.rstrip('\n')
                latex_lines.append(f'\\begin{{minted}}{{{lang}}}')
                latex_lines.append(code)
                latex_lines.append(f'\\end{{minted}}')
                latex_lines.append('')

            # ---- hrule ----
            elif token.type == 'hr':
                latex_lines.append('\\hrule')
                latex_lines.append('')

            # ---- default for other tokens (debug) ----
            else:
                logging.debug("Token non spécifique rencontré: %s", token.type)

            i += 1

        # join and strip
        tex = '\n'.join(latex_lines).strip()
        return tex

    # -------------------------- #
    # -- PUBLIC CONVERTER API -- #
    # -------------------------- #
    def markdown_to_latex(self, mdcode: str) -> str:
        """
        Convertit le Markdown fourni en LaTeX.
        - Applique md_hard_links (transforme les références)
        - Parse avec markdown-it-py
        - Convertit les tokens en LaTeX
        """
        preprocessed = self.md_hard_links(mdcode)
        md = MarkdownIt('commonmark', {'linkify': True})
        tokens = md.parse(preprocessed)
        texcode = self.convert_tokens_to_latex(tokens)
        return texcode


converter = MdToLatexConverter()


md_input = """
Description
-----------

You can use palettes with [`luadraw`][1] which is a package that greatly facilitates the creation of high-quality 2D and 3D plots via `LuaLatex` and `TikZ`.


> ***NOTE.*** *Initially, the `at-prism` project was created to provide ready-to-use palettes for `luadraw`.*


[1]: https://github.com/pfradin/luadraw



Use a luadraw palette
---------------------

The palette names all use the prefix `pal` followed by the name available in the file `at-prism.json`. You can acces a palette by two ways.

  * `palGistHeat` is a palette variable.

  * `getPal("GistHeat")` and `getPal("palGistHeat")` are equal to `palGistHeat`.


> ***NOTE.*** *The palette variables are arrays of arrays of three floats. Here is the definition of the palette `palGistHeat`.*

~~~lua
palGistHeat = {
    {0.0, 0.0, 0.0},
    {0.21176, 0.0, 0.0},
    {0.42941, 0.0, 0.0},
    {0.64117, 0.0, 0.0},
    {0.85882, 0.14509, 0.0},
    {1.0, 0.42745, 0.0},
    {1.0, 0.71764, 0.43529},
    {1.0, 1.0, 1.0}
}
~~~

"""

latex_output = converter.markdown_to_latex(md_input)

print(latex_output)
