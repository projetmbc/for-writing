#!/usr/bin/env python3

from collections import defaultdict
import re
import yaml
import textwrap

from markdown_it import MarkdownIt
from markdown_it.token import Token


# --------------- #
# -- CONSTANTS -- #
# --------------- #

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


PATTERN_MD_REF_LINK = re.compile(
    # r'(?<!\!)\[([^\]]+)\]\s*\[\s*([^\]]*)\s*\]'
    r'''
        (?<!\!)           # Negative lookbehind: ne doit PAS être précédé d'un !
                        # (pour éviter de matcher ![texte][ref] qui sont des images Markdown)

        \[                # Premier crochet ouvrant littéral [
        ([^\]]+)          # Groupe 1: capture un ou plusieurs caractères qui ne sont pas ]
                        # (c'est le texte du lien)
        \]                # Premier crochet fermant littéral ]

        \s*               # Zéro ou plusieurs espaces blancs (espaces, tabs, retours ligne)

        \[                # Deuxième crochet ouvrant littéral [
        \s*               # Espaces blancs optionnels au début
        ([^\]]*)          # Groupe 2: capture zéro ou plusieurs caractères qui ne sont pas ]
                        # (c'est la référence du lien, peut être vide)
        \s*               # Espaces blancs optionnels à la fin
        \]                # Deuxième crochet fermant littéral ]
    ''',
re.VERBOSE
)

PATTERN_MD_ONE_REF_LINK = re.compile(
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


PATTERN_HTML_COMMENTS = re.compile(
    r'<!--YAML\s*\n(.*?)\n-->',
    re.DOTALL
)


import re

def transform_tdoccodein(text, transformations=None):
    if transformations is None:
        return text

    pattern = r'\\tdoccodein\{text\}\+([^+]+)\+'

    def replacer(match):
        content = match.group(1)

        # Vérifier si le contenu correspond à une règle
        for key, transfo in transformations.items():
            if key == content:
                if isinstance(transfo, str):
                    return transfo

                return transfo(content)

        # Si aucune règle ne correspond, garder tel quel
        return match.group(0)

    result = re.sub(pattern, replacer, text)
    return result


def transform_code_links(text, allowed_words):
    # Créer un pattern qui matche uniquement les mots autorisés
    words_pattern = '|'.join(re.escape(word) for word in allowed_words)
    pattern = rf'\[`({words_pattern})`\]\[[^\]]+\]'

    # Remplacer par \mot
    result = re.sub(pattern, r'`\1`', text)
    return result


def get_inlinline_codes(mdcode):
    matches = PATTERN_HTML_COMMENTS.findall(mdcode)

    result = defaultdict(list)

    for match in matches:
        try:
            data = yaml.safe_load(match)

            if data and 'inlinecode' in data:
                for lang, code_list in data['inlinecode'].items():
                    result[lang].extend(code_list)

        except yaml.YAMLError as e:
            print(f"Erreur de parsing YAML: {e}")

    # Convertir en dict normal
    return dict(result)


def nest_code_in_note(text):
    # Pattern qui matche le contenu de tdocnote de façon minimale (non-greedy)
    # en s'arrêtant au premier \end{tdocnote} rencontré
    pattern = r'\\begin\{tdocnote\}(.*?)\\end\{tdocnote\}\s*\\begin\{tdoccode\}(\{[^}]+\})(.*?)\\end\{tdoccode\}'

    def replacer(match):
        note_content = match.group(1)
        code_lang = match.group(2)
        code_content = match.group(3)

        return f'\\begin{{tdocnote}}{note_content}\n\\begin{{tdoccode}}{code_lang}{code_content}\\end{{tdoccode}}\n\\end{{tdocnote}}'

    result = re.sub(pattern, replacer, text, flags=re.DOTALL)
    return result


def transform_latex_quote(text):
    # Pattern pour capturer tout le bloc quote
    pattern = r'\\begin\{quote\}\s*\\textit\{\\textbf\{(.*?)\}\}\s*\\textit\{(.*?)\}\s*\\end\{quote\}'

    def replacer(match):
        note_label = match.group(1)  # "NOTE." par exemple
        content = match.group(2)      # Le contenu après NOTE.

        # Vérifier que c'est bien une NOTE
        if note_label.strip().upper().startswith('NOTE'):
            return f'\\begin{{tdocnote}}\n{content}\n\\end{{tdocnote}}'

        if note_label.strip().upper().startswith('CAUTION'):
            return f'\\begin{{tdoccaut}}\n{content}\n\\end{{tdoccaut}}'

        return match.group(0)  # Si ce n'est pas une NOTE, ne rien changer

    result = re.sub(pattern, replacer, text, flags=re.DOTALL)
    return result


class MdToLatexConverter:
    """
    Convertisseur Markdown -> LaTeX.
    - Transforme d'abord les reference-style links (full & collapsed) en liens inline.
    - Parse le Markdown avec markdown-it-py et convertit les tokens en LaTeX.
    """
    def __init__(
        self,
        shift_down_level     : int  = 0,
        case_insensitive_refs: bool = True
    ) -> None:
        """
        case_insensitive_refs: si True on stocke les labels en minuscules (comportement courant en Markdown).
        """
        self.shift_down_level      = shift_down_level
        self.case_insensitive_refs = case_insensitive_refs

    # ---------------------- #
    # -- REF HANDLING -- #
    # ---------------------- #
    def _extract_reference_definitions(
        self,
        md_text: str
    ) -> dict[str, str]:
        """
        Lit toutes les définitions de référence et retourne dict {label: url}.
        Ne fait pas de suppression dans md_text — seulement extraction.
        """
        refs: dict[str, str] = {}

        for m in PATTERN_MD_ONE_REF_LINK.finditer(md_text):
            label = m.group('label')
            url = m.group('url')

            if url.startswith('<') and url.endswith('>'):
                url = url[1:-1]

            key = label.lower() if self.case_insensitive_refs else label
            refs[key] = url

        return refs

    def _replace_reference_links(
        self,
        md_text: str,
        refs: dict[str, str]
    ) -> str:
        """
        Remplace occurrences [text][label] et [text][] par [text](url) en utilisant refs.
        Si une référence n'est pas trouvée, on garde l'original et loggue.
        """
        def repl(m: re.Match) -> str:
            text_label = m.group(1)
            label      = m.group(2)

            key = (label if label else text_label)
            key = key.lower() if self.case_insensitive_refs else key

            url = refs.get(key)

            if url:
                return f'[{text_label}]({url})'

        # Eviter de transformer les images : ![alt][id]
        processed = PATTERN_MD_REF_LINK.sub(repl, md_text)

        return processed

    def _remove_reference_definitions(
        self,
        md_text: str
    ) -> str:
        """Supprime toutes les lignes '[label]: ...' du texte."""
        processed = re.sub(r'^[ \t]*\[[^\]]+\]:.*$', '', md_text, flags=re.MULTILINE)

        return processed.strip()

    def md_hard_links(
        self,
        md_text: str
    ) -> str:
        """
        Étape complète :
        1) Extraire définitions [label]: url
        2) Remplacer [text][label] / [text][] par [text](url)
        3) Supprimer lignes de définitions
        """
        refs = self._extract_reference_definitions(md_text)

        if not refs:
            return md_text

        processed = self._replace_reference_links(md_text, refs)
        processed = self._remove_reference_definitions(processed)

        return processed

    # ----------------------- #
    # -- LATEX UTILITIES -- #
    # ----------------------- #
    @classmethod
    def escape_latex(
        cls,
        text: str
    ) -> str:
        """Échappe les caractères spéciaux LaTeX"""
        for char, replacement in TEX_ESCAPE_IT.items():
            text = text.replace(char, replacement)

        return text

    # ----------------------------- #
    # -- TOKEN -> LATEX CONVERSION -#
    # ----------------------------- #
    def process_inline(
        self,
        tokens: list
    ) -> str:
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
                result.append(f'\\tdoccodein{{text}}+{token.content}+')

            elif token.type == 'strong_open':
                result.append(r'\textbf{')

            elif token.type == 'em_open':
                result.append(r'\textit{')

            elif token.type in ['em_close', 'strong_close']:
                result.append('}')


            elif token.type == 'link_open':
                href = token.attrGet('href') or ''

                i += 1

                link_text_parts: list[str] = []

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

            # else:
            #     # cas non gérés explicitement : logging.debug pour info
            #     logging.debug("Token inline non traité: %s", token.type)

            i += 1

        return ''.join(result)

    def convert_tokens_to_latex(
        self,
        tokens: list
    ) -> str:
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

                cmd = section_commands[
                    min(
                        level - self.shift_down_level - 1,
                        len(section_commands) - 1
                    )
                ]

                latex_lines.append(f'\\{cmd}{{{self.escape_latex(content)}}}\n')
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
                latex_lines.append('\\begin{quote}')

            elif token.type == 'blockquote_close':
                latex_lines.append('\\end{quote}')
                latex_lines.append('')

            # ---- ordered lists ----
            elif token.type == 'ordered_list_open':
                latex_lines.append('\\begin{enumerate}')

            elif token.type == 'ordered_list_close':
                latex_lines.append('\\end{enumerate}')
                latex_lines.append('')

            # ---- bullet lists ----
            elif token.type == 'bullet_list_open':
                latex_lines.append('\\begin{itemize}')

            elif token.type == 'bullet_list_close':
                if not latex_lines[-1].strip():
                    latex_lines.pop(-1)

                latex_lines.append('\\end{itemize}')
                latex_lines.append('')

            elif token.type == 'list_item_open':
                latex_lines.append(r'\item')

            # elif token.type == 'list_item_open':
            #     # gather item content until list_item_close
            #     i += 1
            #     item_content: list[str] = []
            #     while i < len(tokens) and tokens[i].type != 'list_item_close':
            #         if tokens[i].type == 'paragraph_open':
            #             i += 1
            #             if i < len(tokens) and tokens[i].children:
            #                 item_content.append(self.process_inline(tokens[i].children))
            #             i += 1  # skip paragraph_close
            #         else:
            #             i += 1
            #     latex_lines.append(f'\\item {" ".join(item_content)}')

            # ---- code fence ----
            elif token.type == 'fence':
                lang = token.info or 'text'
                code = token.content.rstrip('\n')
                latex_lines.append(f'\\begin{{tdoccode}}{{{lang}}}')
                latex_lines.append(code)
                latex_lines.append(f'\\end{{tdoccode}}')
                latex_lines.append('')

            # ---- hrule ----
            elif token.type == 'hr':
                latex_lines.append('\\hrule')
                latex_lines.append('')

            # ---- nothing done ----
            elif token.type in [
                'heading_close',
                'paragraph_close',
                'html_block',
                'list_item_close',
                'ordered_list_close',
            ]:
                ...

            # ---- default for other tokens (debug) ----
            else:
                print(token.type)
                exit()
            #     logging.debug("Token non spécifique rencontré: %s", token.type)

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

        texcode = transform_latex_quote(texcode)
        texcode = nest_code_in_note(texcode)


        inlinecodes = get_inlinline_codes(mdcode)

        for lang, texts in inlinecodes.items():
            for t in texts:
                texcode = texcode.replace(
                    rf"\tdoccodein{{text}}+{t}+",
                    rf"\tdoccodein{{{lang}}}+{t}+"
                )

        return texcode
