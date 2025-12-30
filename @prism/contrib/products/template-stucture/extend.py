#!/usr/bin/env python3

# -------------------- #
# -- IMPORT ALLOWED -- #
# -------------------- #

from typing import TypeAlias

import ast
import re


# ------------ #
# -- TYPING -- #
# ------------ #

RGBCols    :TypeAlias = [float, float, float]
PaletteCols:TypeAlias = list[RGBCols]


# -------------------- #
# -- EXTRACT COLORS -- #
# -------------------- #

###
# prototype::
#     code : a definition of a palette with the technology chosen.
#
#     :return: a list of lists of 3 floats belonging to `[0, 1]` that
#              will be used to produce the "universal" \json version
#              of the palette.
###
def parse(code: str) -> PaletteCols:
    ...


# ---------------------- #
# -- BUILD FINAL CODE -- #
# ---------------------- #

PALETTES_FILE_NAME = "..."

###
# prototype::
#     credits  : the credits to the ''@prism'' project that should
#                be added as a comment at the beginning of the final
#                product code.
#     palettes : the ''Python'' dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used.
#
#
# warning::
#     Except if it is totally impossible, the code build must offer
#     the ability to access a palette via the string name of the
#     variable associated with it, and also to propose ways to
#     transform palettes (extraction, shift and reverse order).
###
def build_code(
    credits : str,
    palettes: dict[str, PaletteCols]
) -> str:
    ...


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
    ...

# Code to parse.
#     code = r"""
# -- Lua definition used.

# -- PALETTE = {
# --   Gray,
# --   SlateGray,
# --   LightSkyBlue,
# --   LightPink,
# --   Pink,
# --   LightSalmon,
# --   FireBrick,
# -- }

# PALETTE = {
#   {0.502, 0.502, 0.502},
#   {0.4392, 0.502, 0.5647},
#   {0.5294, 0.8078, 0.9804},
#   {1, 0.7137, 0.7569},
#   {1, 0.7529, 0.7961},
#   {1, 0.6275, 0.4784},
#   {0.698, 0.1333, 0.1333},
# }
#     """

#     from rich import print

#     print_section = lambda t: print(f'\n--- {t} --\n')

#     print_section('INITIAL CODE')
#     print(code.strip())

#     std_data = parse(code)

#     print_section('STD DATA (JSON)')
#     print(std_data)

#     print_section('SPECIFIC CODE')
#     print(
#         build_code(
#             credits  = 'Credits...',
#             palettes = {"TEST": std_data}
#         )
#     )
