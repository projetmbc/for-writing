#!/usr/bin/env python3

# -------------------- #
# -- IMPORT ALLOWED -- #
# -------------------- #

from typing import TypeAlias

from pathlib import Path

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
#     code : a RGB ''LaTeX'' palette definition of a palette (see the
#            fake example below).
#
#     :return: a list of lists of 3 floats belonging to `[0, 1]` that
#              will be used to produce the "universal" ''JSON'' version
#              of the palette.
#
#
# A RGB ''LaTeX'' palette definition looks like this.
#
# lua::
#     \palCreateFromRGB{PALETTE}{
#       {0.3922, 0.5843, 0.9294},
#       {0.5294, 0.8078, 0.9804},
#       ...
#     }
###
def parse(code: str) -> PaletteCols:
    code = '\n'.join(
        line
        for line in code.split('\n')
        if line.strip()[:1] != "%"
    )

    match = re.search(
        r'\\palCreateFromRGB{PALETTE}{(.*)}',
        code,
        re.S  # The dot operator matches all.
    )

    if not match:
        raise ValueError("No LaTeX PALETTE creation found.")

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

PALETTES_FILE_NAME = "palettes.sty"

###
# prototype::
#     credits  : the credits to the ''@prism'' project that should
#                be added as a comment at the beginning of the final
#                product code.
#     palettes : the ''Python'' dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used. dd
###
def build_code(
    credits : str,
    palettes: dict[str, PaletteCols]
) -> str:
    def float2dec(x: float) -> str:
        x = f"{x:.6f}"
        x = x.rstrip('0')
        x = x.rstrip('.')

        return x

# Credits.
    credits = credits.split("\n")

    maxlen = max(map(len, credits))
    deco   = '-'*(maxlen + 6)
    deco   = f"% {deco} %"

    credits = '\n'.join([
        f'% -- {c.ljust(maxlen)} -- %'
        for c in credits
    ])

    credits = f"""
{deco}
{credits}
{deco}
    """.strip()

# Palettes.
    paldefs_code = [
        """
% -------------------------- %
% -- DEFS OF EACH PALETTE -- %
% -------------------------- %
        """.strip(),
        '',
    ]

# The palettes.
    indent = " "*2

    for name, colors in palettes.items():
        name = rf"\palCreateFromRGB{{{name}}}"

        paldefs_code.append(f"{name}{{")

        for r, g, b in colors:
            r, g, b = map(float2dec, [r, g, b])
            paldefs_code.append(f"{indent}{{{r}, {g}, {b}}},")

# We remove the last unuseful coma.
        paldefs_code[-1] = paldefs_code[-1][:-1]

# Seperating defs with single empty lines.
        paldefs_code.append("}\n")

    paldefs_code = '\n'.join(paldefs_code)

# API code.
    api_code = Path(__file__).parent / "tests" / "palapi.sty"
    api_code = api_code.read_text().strip()

# Nothing left to do.
    code = f"""
{credits}


{api_code}


{paldefs_code}
    """.strip() + '\n'

    return code


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
# Code to parse.
    code = r"""
% latex definition used.

% PALETTE = {
%   Gray,
%   SlateGray,
%   LightSkyBlue,
%   LightPink,
%   Pink,
%   LightSalmon,
%   FireBrick,
% }

\palCreateFromRGB{PALETTE}{
  {0.0, 0.0, 0.0},
  {0.4, 0.0, 0.2},
  {0.8, 0.2, 0.0},
  {1.0, 0.6, 0.0},
  {1.0, 1.0, 0.45678},
}
    """

    from rich import print

    print_section = lambda t: print(f'\n--- {t} --\n')

    print_section('INITIAL CODE')
    print(code.strip())

    std_data = parse(code)

    print_section('STD DATA (JSON)')
    print(std_data)

    print_section('SPECIFIC CODE')
    print(
        build_code(
            credits  = 'Credits...',
            palettes = {"TEST": std_data}
        )
    )
