#!/usr/bin/env python3

# -------------------- #
# -- IMPORT ALLOWED -- #
# -------------------- #

import ast
import re


# -------------------- #
# -- EXTRACT COLORS -- #
# -------------------- #

###
# prototype::
#     code : a standard ''CSS'' definition of a palette (see the fake
#            example below).
#
#     :return: a list of lists of 3 floats belonging to `[0, 1]` that
#              will be used to produce the "universal" ''JSON'' version
#              of the palette.
#
#
# A standard ''CSS'' palette looks like this.
#
# css::
#     ???
###
def parse(code: str) -> list[ [float, float, float] ]:
    TODO


# ---------------------- #
# -- BUILD FINAL CODE -- #
# ---------------------- #

PALETTES_FILE_NAME = "palettes.lua"

###
# prototype::
#     credits  : the credits to the ''at-prism'' project that should
#                be added as a comment at the beginning of the final
#                product code.
#     palettes : the Python dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used, with ???
###
def build_code(
    credits : str,
    palettes: dict[ str, list[ [float, float, float] ] ]
) -> str:
    TODO


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
# Code to parse.
    code = r"""
TODO
    """

    from rich import print

    print_section = lambda t: print(f'\n--- {t} --\n')

    std_data = parse(code)

    print_section('STD DATA (JSON)')
    print(std_data)

    print_section('BACK TO CODE')
    print(
        build_code({"TEST": std_data})
    )

    print_section('INITIAL CODE')
    print(code.strip())
