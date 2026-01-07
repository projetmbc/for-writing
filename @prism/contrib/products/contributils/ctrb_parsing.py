#!/usr/bin/env python3

import ast
import re


# --------------------- #
# -- THIS EXTRACTION -- #
# --------------------- #

_METADA_NAMES = [
    "author",
    "kind",
]

_PATTERN_PAL_METADATA = re.compile(
    rf' {{4}}({'|'.join(_METADA_NAMES)})\s*=(.*)'
)

def get_thisdata(
    content: str,
    prefix : str = ""
) -> dict[str, str]:
    gobble = len(prefix)

    in_this_block = False

    metadata = dict()

    for line in content.split('\n'):
        if not line.strip():
            continue

        if prefix:
            if not line.startswith(prefix):
                raise ValueError(
                    "Illegal 'this' magic comment."
                )

            line = line[gobble:]

        if line.rstrip() == 'this::':
            in_this_block = True

        elif in_this_block:
            match = _PATTERN_PAL_METADATA.search(line)

            if match:
                what = match.group(1)
                val  = match.group(2).strip()

                metadata[what] = val

    return metadata


def std_metadata(metadata: dict[str, str]) -> None:
    for k in _METADA_NAMES:
        if not k in metadata:
            metadata[k] = ''
