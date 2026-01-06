#!/usr/bin/env python3

# -------------------- #
# -- IMPORT ALLOWED -- #
# -------------------- #

from typing import (
    Annotated,
    Optional,
    TypeAlias, TypedDict,
)

from pathlib import Path

import ast
import re


# ------------ #
# -- TYPING -- #
# ------------ #

RGBCols    :TypeAlias = Annotated[list[float], 3]
PaletteCols:TypeAlias = list[RGBCols]

class PaletteData(TypedDict):
    metadata: dict[str, str]
    palette : PaletteCols


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


# -------------------- #
# -- EXTRACT COLORS -- #
# -------------------- #

###
# prototype::
#     code : a RGB ''CSS'' palette definition of a palette (see the
#            fake example below).
#
#     :return: a dictionary ''{'metadata': ..., 'palette': ...}''
#              giving palette metadata as a ''str-str'' dictionary,
#              and the palette colors as a list of lists of 3 floats
#              belonging to `[0, 1]` that will be used to produce
#              the "universal" ''JSON'' version of the palette.
#
#
# A RGB ''CSS'' palette definition looks like this.
#
# css::
#     --palPALETTE-1: rgb(39.22% 58.43% 92.94%);
#     --palPALETTE-2: rgb(52.94% 80.78% 98.04%);
#     /* ... */
###
def parse(code: str) -> PaletteData:
# Kind.
    metadata = dict()

    comments = re.findall(r'/\*{3}([\s\S]*?)\*{3}/', code)

    for block in comments:
        metadata = get_thisdata(block)

        if metadata:
            break

    std_metadata(metadata)

# Palette.
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
        raise ValueError("No CSS PALETTE definition found.")

    palette = [
        list(map(lambda x: float(x) / 100, rgb))
        for rgb in matches
    ]

# Nothing left to do.
    return {
        'metadata': metadata,
        'palette' : palette
    }


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
        _x = f"{x:.6f}"
        _x = _x.rstrip('0')
        _x = _x.rstrip('.')

        return f"{_x}%"

# Credits.
    _credits = credits.split("\n")

    maxlen = max(map(len, _credits))
    deco   = '-'*(maxlen + 6)
    deco   = f"/* {deco} */"

    credits = '\n'.join([
        f'/* -- {c.ljust(maxlen)} -- */'
        for c in _credits
    ])

    credits = f"""
{deco}
{credits}
{deco}
    """.strip()

# Palettes.
    _paldefs_code = [
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
            _r, _g, _b = map(float2percentage, [r, g, b])


            _paldefs_code.append(
                f"{indent}{name}-{i}: rgb({_r} {_g} {_b});"
            )

# Seperating defs with single empty lines.
        _paldefs_code.append("")

# We remove the last unuseful empty line.
    _paldefs_code.pop(-1)

# Close the root block.
    _paldefs_code.append("}")

    paldefs_code = '\n'.join(_paldefs_code)

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
/***
this::
    author = First Name, Last Name
    kind   = ?
***/

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
            palettes = {"CHECKER": std_data['palette']}
        )
    )
