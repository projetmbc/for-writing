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
#     code : a \std \luadraw \def of a palette named lua::''PALETTE''
#            (see the fake example below).
#
#     :return: a list of lists of 3 floats belonging to `[0, 1]` that
#              will be used to produce the "universal" \json version
#              of the palette.
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
def parse(code: str) -> list[ [float, float, float] ]:
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


# ---------------------- #
# -- BUILD FINAL CODE -- #
# ---------------------- #

PALETTES_FILE_NAME = "palettes.lua"

###
# prototype::
#     credits  : the credits to the ''atprism'' project that should
#                be added as a comment at the beginning of the final
#                product code.
#     palettes : the dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used, with an extra array ''getPal'' to
#              access a palette via its string name.
###
def build_code(
    credits : str,
    palettes: dict[ str, list[ [float, float, float] ] ]
) -> str:
# Credits.
    code = []

    code_dict = []

    credits = credits.split("\n")

    maxlen = max(map(len, credits))
    deco   = '-'*(maxlen + 6)

    credits = [
        f'-- {c.ljust(maxlen)} --'
        for c in credits
    ]

    credits = '\n'.join(credits)

    code = [
        deco,
        credits,
        deco,
        '',
        """
--------------------------
-- DEFS OF EACH PALETTE --
--------------------------
        """.strip(),
        '',
    ]

    code_dict = [
        """
---------------------------------
-- GET ONE PALETTE BY ITS NAME --
---------------------------------

getPal = {}

for _, name in ipairs({
        """.strip()
    ]

# The palettes.
    indent = " "*4

    for name, colors in palettes.items():
        name = f"pal{name}"

        code_dict.append(f'{indent}"{name}",')

        code.append(f"{name} = {{")

        for r, g, b in colors:
            code.append(f"{indent}{{{r}, {g}, {b}}},")

# We remove the last unuseful coma.
        code[-1] = code[-1][:-1]

# Seperating defs with single empty lines.
        code.append("}\n")

    code_dict[-1] = code_dict[-1][:-1]

    code_dict.append(
        f"""
}}) do
{indent}getPal[name] = _G[name]
end
        """.strip() + '\n'
    )

    code += code_dict

# Nothing left to do.
    code = '\n'.join(code)

    return code


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
        build_code({"TEST": std_data})
    )

    print_section('INITIAL CODE')
    print(code.strip())
