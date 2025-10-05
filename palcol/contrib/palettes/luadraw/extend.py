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
#     code : GGG
#
#     :return: GGG
###
def parse(code: str) -> list[[int, int, int]]:
    match = re.search(
        r'PALETTE\s*=\s*{(.*)}',
        code,
        re.S  # dot matches all
    )

    if not match:
        raise ValueError("No PALETTE table found.")

    palette = match.group(1)

    for old, new in [
        ('{', '['),
        ('}', ']'),
    ]:
        palette = palette.replace(old, new)

    palette = f'[{palette.strip()}]'
    palette = ast.literal_eval(palette)

    return palette


# ----------------------- #
# -- WRITE FOR LUADRAW -- #
# ----------------------- #

###
# prototype::
#     name : GGG
#     data : GGG
#
#     :return: GGG
###
def write_new_palette(
    name: str,
    data: list[list[float, float, float]]
) -> str:
    luadraw_code = [f"pal{name} = {{"]

    for r, g, b in std_data:
        luadraw_code.append(f"    {{{r}, {g}, {b}}},")

    luadraw_code[-1] = luadraw_code[-1][:-1]

    luadraw_code.append("}\n")

    luadraw_code = '\n'.join(luadraw_code)

    return luadraw_code


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
# Data we have to parse.
    PALETTE_CODE = r"""
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

    std_data  = parse(PALETTE_CODE)

    print(std_data )
    print('---')
    print(
        write_new_palette(
          "TEST",
          std_data
        )
    )
