#!/usr/bin/env python3

# -------------------- #
# -- IMPORT ALLOWED -- #
# -------------------- #

import ast
import re


# -------------------------- #
# -- EXTRACT FROM LUADRAW -- #
# -------------------------- #

###
# prototype::
#     code : a \std \luadraw \def of a palette named lua::''PALETTE''
#            (see the fake example below).
#
#     :return: a list of lists of floats belonging to `[0, 1]` that
#              will be used to produce the "universal" \json version
#              of the palettes.
#
#
# A \std \luadraw palette looks like this.
#
# lua::
#     PALETTE = {
#       {0.502, 0.502, 0.502},
#       {0.4392, 0.502, 0.5647},
#       ...
#     }
###
def parse(code: str) -> list[[float, float, float]]:
    code = '\n'.join(
        line
        for line in code.split('\n')
        if line.strip()[:2] != "--"
    )

    match = re.search(
        r'PALETTE\s*=\s*{(.*)}',
        code,
        re.S  # The dot operator matches all.
    )

    if not match:
        raise ValueError("No table PALETTE found.")

    palette = match.group(1)

    for old, new in [
        ('{', '['),
        ('}', ']'),
    ]:
        palette = palette.replace(old, new)

    palette = f'[{palette.strip()}]'

# Safe evaluation.
    palette = ast.literal_eval(palette)

    return palette


# ----------------------- #
# -- WRITE FOR LUADRAW -- #
# ----------------------- #

PALETTES_FILE_NAME = "palettes.lua"

###
# prototype::
#     name : name of the palette without the prefix ''pal'' which is
#            specific to \luadraw.
#     data : a list of lists of floats that comes from  "universal"
#            \json version of the palettes.
#
#     :return: \std \luadraw \def of the palette whose name is
#              automatically prefixed with lua::''pal''.
###
def build_code(
    name: str,
    data: list[list[float, float, float]]
) -> str:
    luadraw_code = [f"pal{name} = {{"]

    indent = " "*4

    for r, g, b in data:
        luadraw_code.append(f"{indent}{{{r}, {g}, {b}}},")

# We remove the last unuseful coma.
    luadraw_code[-1] = luadraw_code[-1][:-1]

# One final empty line is a good practice.
    luadraw_code.append("}\n")

    luadraw_code = '\n'.join(luadraw_code)

    return luadraw_code


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
# Code to parse.
    code = r"""
-- ludraw definition used.

-- PALETTE = {
--   Gray,
--   SlateGray,
--   LightSkyBlue,
--   LightPink,
--   Pink,
--   LightSalmon,
--   FireBrick,
-- }

PALETTE = {
  {0.502, 0.502, 0.502},
  {0.4392, 0.502, 0.5647},
  {0.5294, 0.8078, 0.9804},
  {1, 0.7137, 0.7569},
  {1, 0.7529, 0.7961},
  {1, 0.6275, 0.4784},
  {0.698, 0.1333, 0.1333},
}
    """

    from rich import print

    print_section = lambda t: print(f'\n--- {t} --\n')

    std_data  = parse(code)

    print_section('STD DATA (JSON)')
    print(std_data)

    print_section('BACK TO CODE')
    print(
        build_code("TEST", std_data)
    )

    print_section('INITIAL CODE')
    print(code.strip())
