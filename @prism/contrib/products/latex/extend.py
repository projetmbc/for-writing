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
#     palettes : the dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used.
#
#
# warning::
#     Except if it is totally impossible, the code returned must
#     offer the ability to access a palette via the string name of
#     the variable associated with it.
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
