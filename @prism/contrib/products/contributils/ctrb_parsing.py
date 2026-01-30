#!/usr/bin/env python3

import ast
import re


from .ctrb_typing import *

# ------------------------ #
# -- ''THIS'' CONSTANTS -- #
# ------------------------ #

TAG_REMETH_SEARCH  = 'search'
TAG_REMETH_FINDALL = 'find-all'

TAG_METADATA = 'metadata'
TAG_PALETTE  = 'palette'


TAGS_COMMENTS = [
    TAG_MULTICOM_START      := 'multiline-comments-start',
    TAG_MULTICOM_END        := 'multiline-comments-end',
    TAG_SINGLECOM           := 'single-line-comments',
    TAG_MAGIC_MULTICOM_START:= f'magic-{TAG_MULTICOM_START}',
    TAG_MAGIC_MULTICOM_END  := f'magic-{TAG_MULTICOM_END}',
    TAG_MAGIC_SINGLECOM     := f'magic-{TAG_SINGLECOM}'
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

# ------------------ #
# -- PARSING DATA -- #
# ------------------ #

class PaletteParser:
    def __init__(
        self,
        comspecs,
        palpattern,
        remode = TAG_REMETH_SEARCH
    ):
        self.comspecs = comspecs

        self.remode     = remode
        self.palpattern = re.compile(palpattern)

        self.metadata = dict()
        self.palette  = []

# Defining and validating comment specifications.
    @property
    def comspecs(self):
        return self._comspecs

    @comspecs.setter
    def comspecs(self, val):
# Get all the keys.
        std_strdict(val, TAGS_COMMENTS)

# Do we have legal comments specs?
        if len(set(val.values())) == 1:
            raise ValueError("no comment specs found!")

        if (
            val[TAG_MULTICOM_START]
            and
            not val[TAG_MULTICOM_END]
        ) or (
            not val[TAG_MULTICOM_START]
            and
            val[TAG_MULTICOM_END]
        ):
            raise ValueError(
                "multiline comments must use non-empty start and end tags."
            )

# Magic comment are multiline ones.
        if val[TAG_MULTICOM_START]:
            val[TAG_MAGIC_MULTICOM_START]  = val[TAG_MULTICOM_START]
            val[TAG_MAGIC_MULTICOM_START] += val[TAG_MULTICOM_START][-1]*2

            val[TAG_MAGIC_MULTICOM_END]  = val[TAG_MULTICOM_END][0]*2
            val[TAG_MAGIC_MULTICOM_END] += val[TAG_MULTICOM_END]

            self._preline = ''
            self._gobble  = 0

# Magic comment are single linge ones.
        else:
            val[TAG_MAGIC_SINGLECOM]  = val[TAG_SINGLECOM]
            val[TAG_MAGIC_SINGLECOM] += val[TAG_SINGLECOM][-1]*2

            self._preline = f'{val[TAG_SINGLECOM]} '
            self._gobble  = len(self._preline)

# Escaping all values.
        for k, v in val.items():
            val[k] = re.escape(v)

# Nothing left to do.
        self._comspecs = val

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
# Extract comments blocks - Multiline comments.
        if self.comspecs[TAG_MAGIC_MULTICOM_START]:
            comments = re.findall(
                self.comspecs[TAG_MAGIC_MULTICOM_START] +
                r'([\s\S]*?)' +
                self.comspecs[TAG_MAGIC_MULTICOM_END],
                self._code
            )

# Extract comments blocks - Single line comments.
        else:
            TODO

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

            if self._preline:
                if not line.startswith(preline):
                    raise ValueError(
                        "Illegal 'this' magic comment."
                    )

                line = line[self._gobble:]

            if line.rstrip() == 'this::':
                in_this_block = True

            elif in_this_block:
                match = PATTERN_PAL_METADATA.search(line)

                if match:
                    what = match.group(1)
                    val  = match.group(2).strip()

                    self.metadata[what] = val


#
    def build_palette(self):
        cleaned_code = self._code

# Clean multiline comments.
        if self.comspecs[TAG_MULTICOM_START]:
            compattern = re.compile(
                self.comspecs[TAG_MULTICOM_START] +
                r'([\s\S]*?)' +
                self.comspecs[TAG_MULTICOM_END]
            )

            cleaned_code = compattern.sub(
                "",
                cleaned_code
            )

# Clean single line comments.
        if self.comspecs[TAG_SINGLECOM]:
            TODO

# "find all" method.
        if self.remode == TAG_REMETH_FINDALL:
            matches = self.palpattern.findall(cleaned_code)

            if not matches:
                raise ValueError(
                    "No CSS PALETTE definition found."
                )

            self.palette = [
                list(map(lambda x: float(x) / 100, rgb))
                for rgb in matches
            ]

# "search" method.
        elif self.remode == TAG_REMETH_SEARCH:
            TODO

# Unknown method.
        else:
            raise ValueError(f"unknown regex method '{self.remode}'")


# ------------------- #
# -- BUILDING CODE -- #
# ------------------- #

class PaletteParser:
    def __init__(
        self,
        comspecs,
        palpattern,
        remode = TAG_REMETH_SEARCH
    ):
        self.comspecs = comspecs

        self.remode     = remode
        self.palpattern = re.compile(palpattern)

        self.metadata = dict()
        self.palette  = []
