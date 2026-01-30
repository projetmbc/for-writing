#!/usr/bin/env python3

import ast
import re


from .ctrb_typing import *

# ------------------------ #
# -- ''THIS'' CONSTANTS -- #
# ------------------------ #

TAG_METADATA = 'metadata'
TAG_PALETTE  = 'palette'


TAGS_COMMENTS = [
    TAG_MULTICOM_START:= 'multiline-comments-start',
    TAG_MULTICOM_END  := 'multiline-comments-end',
    TAG_SINGLECOM     := 'single-line-comments',
]

_TAG_MAGICCOM_START = 'magic-comments-start'
_TAG_MAGICCOM_END   = 'magic-comments-end'

TAG_MAGICCOM_BLOCK = 'magic-comments'
TAG_MULTICOM_BLOCK = 'multiline-comments'

_REMOVED_TAGS = [
    TAG_MULTICOM_START,
    TAG_MULTICOM_END
]

METADA_NAMES = [
    "author",
    "kind",
]

PATTERN_PAL_METADATA = re.compile(
    rf' {{4}}({'|'.join(METADA_NAMES)})\s*=(.*)'
)


# ----------- #
# -- TOOLS -- #
# ----------- #

def std_strdict(
    onedict: dict[str, str],
    stdkeys: [str],
) -> None:
    for k in stdkeys:
        onedict[k] = onedict.get(k, '')


def float2percentage(x: float) -> str:
    x *= 100
    _x = f"{x:.6f}"
    _x = _x.rstrip('0')
    _x = _x.rstrip('.')

    return f"{_x}%"


# ------------------------- #
# -- PALETTE TRANSFORMER -- #
# ------------------------- #

class PaletteTransformer:
    def __init__(
        self,
        comspecs,
        palpattern,
        titledeco   = '-',
        header      = '',
        footer      = '',
        pal_builder = None,
        api_builder = lambda: '', # No API!
    ):
        self.get_palcode = pal_builder
        self.get_apicode = api_builder

        self.build_patterns(
            comspecs   = comspecs,
            palpattern = palpattern,
        )

        self.metadata = dict()
        self.palette  = []

        self.titledeco = titledeco

        self.header = header
        self.footer = footer


    def build_patterns(
        self,
        comspecs,
        palpattern,
    ):
# Nothing to do for the palette pattern.
        self.patterns = {
            TAG_PALETTE: palpattern,
        }

# Let's work on comments.
        std_strdict(comspecs, TAGS_COMMENTS)

# Do we have legal comments specs?
        if len(set(comspecs.values())) == 1:
            raise ValueError("no comment specs found!")

        if (
            comspecs[TAG_MULTICOM_START]
            and
            not comspecs[TAG_MULTICOM_END]
        ) or (
            not comspecs[TAG_MULTICOM_START]
            and
            comspecs[TAG_MULTICOM_END]
        ):
            raise ValueError(
                "multiline comments must use non-empty start and end tags."
            )

# Building codes.
        if comspecs[TAG_MULTICOM_START]:
            self._leftcom  = comspecs[TAG_MULTICOM_START]
            self._rightcom = comspecs[TAG_MULTICOM_END]

        else:
            self._leftcom  = comspecs[TAG_SINGLECOM]
            self._rightcom = comspecs[TAG_SINGLECOM]

        self._leftcom  = self._leftcom + ' '
        self._rightcom = ' ' + self._rightcom

# Magic comment are multiline ones.
        if comspecs[TAG_MULTICOM_START]:
            comspecs[_TAG_MAGICCOM_START]  = comspecs[TAG_MULTICOM_START]
            comspecs[_TAG_MAGICCOM_START] += comspecs[TAG_MULTICOM_START][-1]*2

            comspecs[_TAG_MAGICCOM_END]  = comspecs[TAG_MULTICOM_END][0]*2
            comspecs[_TAG_MAGICCOM_END] += comspecs[TAG_MULTICOM_END]

# Magic comment are single linge ones.
        else:
            comspecs[_TAG_MAGICCOM_START]  = comspecs[TAG_SINGLECOM]
            comspecs[_TAG_MAGICCOM_START] += comspecs[TAG_SINGLECOM][-1]*2
            comspecs[_TAG_MAGICCOM_END]    = comspecs[_TAG_MAGICCOM_START]

# Regex escaping all values.
        for k, v in comspecs.items():
            comspecs[k] = re.escape(v)

# Multiline comment regex.
        if comspecs[TAG_MULTICOM_START]:
            self.patterns[TAG_MULTICOM_BLOCK] = re.compile(
                comspecs[_TAG_MAGICCOM_START] +
                r'([\s\S]*?)' +
                comspecs[_TAG_MAGICCOM_END]
            )

        else:
            self.patterns[TAG_MULTICOM_BLOCK] = None

# Single line comment regex.
        if comspecs[TAG_SINGLECOM]:
            self.patterns[TAG_SINGLECOM] = re.compile(
                comspecs[TAG_SINGLECOM] + r'(.*)'
            )

        else:
            self.patterns[TAG_SINGLECOM] = None

# Magic comment regex.
        self.patterns[TAG_MAGICCOM_BLOCK] = re.compile(
            comspecs[_TAG_MAGICCOM_START] +
            r'([\s\S]*?)' +
            comspecs[_TAG_MAGICCOM_END]
        )


# -- PÄRSING -- #

    def get_pydef(
        self,
        code,
    ):
        self._code = code

        self.build_metadata()
        self.build_palette()

        return {
            TAG_METADATA: self.metadata,
            TAG_PALETTE : self.palette,
        }


    def build_metadata(self):
# Get magic comments.
        comments = self.patterns[TAG_MAGICCOM_BLOCK].findall(self._code)

# Only single line comments need some cleaning!
        if not self.patterns[TAG_MULTICOM_BLOCK]:
            for i, block in enumerate(comments):
                _block = []

                for line in block.split('\n'):
                    if (
                        line.strip()
                        and
                        not self.patterns[TAG_SINGLECOM].fullmatch(line)
                    ):
                        raise ValueError(
                           f'illegal line in THIS magic block, see the line:\n{line}'
                        )

                    if not line.strip():
                        _line = ''

                    else:
                        match = self.patterns[TAG_SINGLECOM].match(line)

                        _line = match.group(1)

                        if _line[0].strip():
                            raise ValueError(
                                 'missing initial space in '
                                 'THIS magic block, '
                                f'see the line:\n{line}'
                            )

                        _line = _line[1:]

                    _block.append(_line)

                comments[i] = '\n'.join(_block)

# Analyze comments blocks.
        self.metadata = dict()

        for block in comments:
            self._this_from_one_block(block)

            if self.metadata:
                break

        std_strdict(self.metadata, METADA_NAMES)

#
    def _this_from_one_block(
        self,
        block: str,
    ) -> dict[str, str]:
        in_this_block = False

        for line in block.split('\n'):
            if not line.strip():
                continue

            if line.rstrip() == 'this::':
                in_this_block = True

            elif in_this_block:
                match = PATTERN_PAL_METADATA.search(line)

                if match:
                    what = match.group(1)
                    comspecs  = match.group(2).strip()

                    self.metadata[what] = comspecs

#
    def build_palette(self):
        cleaned_code = self._code

# Clean multiline comments.
        if self.patterns[TAG_MULTICOM_BLOCK]:
            cleaned_code = self.patterns[TAG_MULTICOM_BLOCK].sub(
                "",
                cleaned_code
            )

# Clean single line comments.
        if self.patterns[TAG_SINGLECOM]:
            cleaned_code = '\n'.join([
                self.patterns[TAG_SINGLECOM].sub(
                    "",
                    l
                )
                for l in cleaned_code.split('\n')
            ])

# "find all" method.
        matches = self.patterns[TAG_PALETTE].findall(cleaned_code)

        if not matches:
            raise ValueError(
                "No PALETTE definition found."
            )

        self.palette = [
            list(map(lambda x: float(x) / 100, rgb))
            for rgb in matches
        ]


# -- BUILDING -- #
    def get_credits(
        self,
        credits : str
    ) -> str:
# Let's work.
        _credits = credits.split("\n")

        maxlen = max(map(len, _credits))
        deco   = (
            self._leftcom +
            self.titledeco*(maxlen + 6) +
            self._rightcom
        )

        dble_deco_char = self.titledeco*2

        credits = '\n'.join([
            self._leftcom +
            f'{dble_deco_char} {c.ljust(maxlen)} {dble_deco_char}' +
            self._rightcom
            for c in _credits
        ])



        credits = f"""
{deco}
{credits}
{deco}
        """.strip()

        return credits
