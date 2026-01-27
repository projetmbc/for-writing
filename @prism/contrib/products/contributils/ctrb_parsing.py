#!/usr/bin/env python3

import ast
import re


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

METADA_NAMES = [
    "author",
    "kind",
]

PATTERN_PAL_METADATA = re.compile(
    rf' {{4}}({'|'.join(METADA_NAMES)})\s*=(.*)'
)


# ------------------------- #
# -- ''THIS'' EXTRACTION -- #
# ------------------------- #

def effective_code(
    content : str,
    comspecs: dict[str, str],
) -> str:
    ...


def final_paldef(
    metadata,
    palette,
):
    return {
        TAG_METADATA: metadata,
        TAG_PALETTE : palette
    }





def _std_dict(
    onedict: dict[str, str],
    stdkeys: [str],
) -> None:
    for k in stdkeys:
        onedict[k] = onedict.get(k, '')


def std_metadata(metadata: dict[str, str]) -> None:
    _std_dict(metadata, METADA_NAMES)


def std_comspecs(comspecs):
    _std_dict(comspecs, TAGS_COMMENTS)


def get_this_data(
    content : str,
    comspecs: dict[str, str],
) -> dict[str, str]:
# For searching comments.
    std_comspecs(comspecs)

    comstart  = comspecs[TAG_MULTICOM_START]
    comend    = comspecs[TAG_MULTICOM_END]
    singlecom = comspecs[TAG_SINGLECOM]

# Extract comments blocks - Multiline comments.
    if comstart:
        comments = re.findall(
            rf'{comstart}([\s\S]*?){comend}',
            content
        )

# Extract comments blocks - Single line comments.
    else:
        TODO

# Analyze comments blocks.
    metadata = dict()

    for block in comments:
        print(block)
        metadata = _this_from_one_block(
            block   = block,
            preline = comments_preline,
        )

        if metadata:
            break

    std_metadata(metadata)

    return metadata



def _this_from_one_block(
    block  : str,
    preline: str,
) -> dict[str, str]:
    in_this_block = False

    metadata = dict()

    for line in block.split('\n'):
        if not line.strip():
            continue

        if preline:
            if not line.startswith(preline):
                raise ValueError(
                    "Illegal 'this' magic comment."
                )

            line = line[gobble:]

        if line.rstrip() == 'this::':
            in_this_block = True

        elif in_this_block:
            match = PATTERN_PAL_METADATA.search(line)

            if match:
                what = match.group(1)
                val  = match.group(2).strip()

                metadata[what] = val

    return metadata
