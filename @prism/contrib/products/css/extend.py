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
#     code : a RGB ''CSS'' palette definition of a palette (see the
#            fake example below).
#
#     :return: a list of lists of 3 floats belonging to `[0, 1]` that
#              will be used to produce the "universal" \json version
#              of the palette.
#
#
# A RGB ''CSS'' palette definition looks like this.
#
# css::
#     --palPALETTE-1: rgb(39.22% 58.43% 92.94%);
#     --palPALETTE-2: rgb(52.94% 80.78% 98.04%);
#     /* ... */
###
def parse(code: str) -> PaletteCols:
    code = '\n'.join(
        line
        for line in code.split('\n')
        if line.strip()[:2] != "/*"
    )

    pattern = re.compile(
        r"--palPALETTE-\d+"
        r"\s*:\s*rgb\(\s*"
        r"([\d.]+)%\s+([\d.]+)%\s+([\d.]+)%\s*"
        r"\);"
    )

    matches = pattern.findall(code)

    if not matches:
        raise ValueError("No CSS PALETTE creation found.")

    palette = [
        list(map(lambda x: float(x) / 100, rgb))
        for rgb in matches
    ]

    return palette


# ---------------------- #
# -- BUILD FINAL CODE -- #
# ---------------------- #

PALETTES_FILE_NAME = "palettes.css"

###
# prototype::
#     credits  : the credits to the ''@prism'' project that should
#                be added as a comment at the beginning of the final
#                product code.
#     palettes : the ''Python'' dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used (no API here).
###
def build_code(
    credits : str,
    palettes: dict[str, PaletteCols]
) -> str:
    def float2percentage(x: float) -> str:
        x *= 100
        x = f"{x:.6f}"
        x = x.rstrip('0')
        x = x.rstrip('.')

        return f"{x}%"

# Credits.
    credits = credits.split("\n")

    maxlen = max(map(len, credits))
    deco   = '-'*(maxlen + 6)
    deco   = f"/* {deco} */"

    credits = '\n'.join([
        f'/* -- {c.ljust(maxlen)} -- */'
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
/* -------------------------- */
/* -- DEFS OF EACH PALETTE -- */
/* -------------------------- */
        """.strip(),
        '',
        ':root {'
    ]

# The palettes.
    indent = " "*4

    for name, colors in palettes.items():
        name = f"--pal{name}"

        for i, (r, g, b) in enumerate(colors, start = 1):
            r, g, b = map(float2percentage, [r, g, b])


            paldefs_code.append(
                f"{indent}{name}-{i}: rgb({r} {g} {b});"
            )

# Seperating defs with single empty lines.
        paldefs_code.append("")

# We remove the last unuseful empty line.
    paldefs_code.pop(-1)

# Close the root block.
    paldefs_code.append("}")

    paldefs_code = '\n'.join(paldefs_code)

# Nothing left to do.
    code = f"""
{credits}

/* CSS does not provide a color transformation API. */

{paldefs_code}
    """.strip() + '\n'

    return code


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
# Code to parse.
    code = r"""
/* CSS definition. */

--palPALETTE-1: rgb(0% 0% 0%);
--palPALETTE-2: rgb(40% 0% 20%);
--palPALETTE-3: rgb(80% 20% 0%);
--palPALETTE-4: rgb(100% 60% 0%);
--palPALETTE-5: rgb(100% 100% 45.678%);
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
