#!/usr/bin/env python3

from pathlib import Path
import              re


# ------------ #
# -- TYPING -- #
# ------------ #

type NestedDictPath = dict[str, Path | NestedDictPath]


# --------------- #
# -- CONSTANTS -- #
# --------------- #

TAG_ROOT_HEADER = ".:-R-O-O-T-:."


# -------------------- #
# -- SPLIT IN PARTS -- #
# -------------------- #

###
# prototype::
#     file        : a file to analyze.
#     pat_headers : the list of regular expressions identifying
#                   the headers used to section the content.
#     strip_parts : set to ''True'', the contents are stripped.
#
#     :return: a dictionary reflecting the structure of the extracted
#              content according to the relevant header level.
#
#
# note::
#     At the beginning of each piece of content that has not yet
#     been analysed, the basic header is ''TAG_ROOT_HEADER''.
###
def hd_split_file(
    file       : Path,
    pat_headers: list[re.Pattern],
    strip_parts: bool = True,
) -> NestedDictPath:
    return _recu_hd_split_file(
        content     = file.read_text(),
        pat_headers = pat_headers,
        strip_parts = strip_parts,
    )


###
# prototype::
#     content     : a content to analyze.
#     pat_headers : :see: hd_split_file
#     strip_parts : :see: hd_split_file
#
#     :return: :see: hd_split_file
###
def _recu_hd_split_file(
    content    : str,
    pat_headers: list[re.Pattern],
    strip_parts: bool,
) -> NestedDictPath:
# No pattern.
    if not pat_headers:
        return content

# Use of the first pattern.
    parts = dict()
    curhd = TAG_ROOT_HEADER # Current header.

    pattern, *other_patterns = pat_headers

    for i, piece in enumerate(pattern.split(content)):
        if i % 2 == 1:
            curhd = piece.strip()

        else:
            if strip_parts:
                piece = piece.strip()

            parts[curhd] = _recu_hd_split_file(
                content     = piece,
                pat_headers = other_patterns,
                strip_parts = strip_parts,
            )

# Nothing left to do.
    return parts
