#!/usr/bin/env python3

# --------------------------------- #
# -- IMPORT CONTRIBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR          = Path(__file__).parent
CONTRIB_PRODS_DIR = THIS_DIR.parent

sys.path.append(str(CONTRIB_PRODS_DIR))

from contributils import *

# -- IMPORT CONTRIBUTILS - END -- #
# ------------------------------- #


###
# The following snippet defines the ''PALETTE'' palette (one
# variable per color).
#
# css::
#     --palPALETTE-1: rgb(39.22% 58.43% 93%);
#     --palPALETTE-2: rgb(52.94% 80% 98.04%);
#     /* ... */
###


# ---------------------------- #
# -- SINGLE PALETTE BUILDER -- #
# ---------------------------- #

###
# prototype::
#     name    : name of one single palette.
#     palette : one single palette.
#
#     :return: the \css code of ''palette'' for the final
#              product codes.
###
def _build_palette(
    name   : str,
    palette: PaletteCols
) -> str:
    indent = " "*4
    name   = f"--pal{name}"

    _paldef = []

    for i, (r, g, b) in enumerate(palette, start = 1):
        r, g, b = map(float2percentage, [r, g, b])

        _paldef.append(
            f"{indent}{name}-{i}: rgb({r} {g} {b});"
        )

    paldef = '\n'.join(_paldef)

    return paldef


# ------------------------- #
# -- PALETTE TRANSFORMER -- #
# ------------------------- #

palparser = PaletteTransformer(
    comspecs = {
        TAG_MULTICOM_START: '/*',
        TAG_MULTICOM_END  : '*/',
    },
    palpattern = (
        r"--palPALETTE-\d+"
        r"\s*:\s*rgb\(\s*"
        r"([\d.]+)%\s+([\d.]+)%\s+([\d.]+)%\s*"
        r"\);"
    ),
    remode      = TAG_REMETH_FINDALL,
    header      = ':root {',
    footer      = '}',
    pal_builder = _build_palette,
)


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
--palPALETTE-2: rgb(0% 0% 0%);
--palPALETTE-3: rgb(40% 0% 20%);
--palPALETTE-4: rgb(80% 20% 0%);
--palPALETTE-5: rgb(100% 60% 0%);
--palPALETTE-6: rgb(100% 100% 45.678%);
    """

    from rich import print

    print_section = lambda t: print(
        '\n\n' + '~'*(len(t) +6) + '\n' +
        f'~~ {t} ~~' +
        '\n' + '~'*(len(t) +6) + '\n'
    )

    print_section('INITIAL CODE')
    print(code.strip())

    print_section('EXTRACTED DATA')
    std_data = palparser.get_pydef(code)
    print(std_data)

    print_section('PYTHON 2 CODE')
    css_data = palparser.get_palcode(
        name    = 'PalName',
        palette = std_data[TAG_PALETTE]
    )
    print(palparser.header)
    print(css_data)
    print(palparser.footer)

    print_section('CREDITS IN CODE')
    print(palparser.get_credits('Credits. OK? KO?'))
