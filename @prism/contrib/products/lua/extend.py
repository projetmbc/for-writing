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
# The following snippet defines the ''PALETTE'' palette.
#
# lua::
#     PALETTE = {
#       {0.3922, 0.5843, 0.9294},
#       {0.5294, 0.8078, 0.9804},
#       -- ...
#     }
###


# --------------------------------- #
# -- SINGLE PALETTE CODE BUILDER -- #
# --------------------------------- #

###
# prototype::
#     name    : name of one single palette.
#     palette : one single palette.
#
#     :return: the \latex code of ''palette'' for the final
#              product codes.
###
def _build_palette(
    name   : str,
    palette: PaletteCols
) -> str:
    name    = f"pal{name}"
    indent  = " "*4
    _paldef = [f"{name} = {{"]

    for rgb in palette:
        r, g, b = map(float2str, rgb)

        _paldef.append(
            f"{indent}{{{r}, {g}, {b}}},"
        )

# We remove the last unuseful coma.
    _paldef[-1] = _paldef[-1][:-1]

# Seperating defs with single empty lines.
    _paldef.append("}")

    paldef = '\n'.join(_paldef)

    return paldef


# ---------------------- #
# -- API CODE BUILDER -- #
# ---------------------- #

###
# prototype::
#     :return: the \latex code of the \api the final product codes.
###
def _build_api() -> str:
    _api_code = Path(__file__).parent / "tests" / "palapi.lua"
    api_code  = _api_code.read_text().strip()

    return api_code


# ------------------------- #
# -- PALETTE TRANSFORMER -- #
# ------------------------- #

paltransfo = PaletteTransformer(
    extension  = 'lua',
    comspecs   = {TAG_SINGLECOM: '--'},
    palpattern = re.compile(
        r"\{([\d.]+),\s*([\d.]+),\s*([\d.]+)\},?\s*"
    ),
    pal_builder = _build_palette,
    api_builder = _build_api,
)


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
# Code to parse.
    code = r"""

------
-- this::
--     author = First Name, Last Name
--     catego = ?
------

-- Luadraw definition used.

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
  {0.502,0.502,0.502},
  {0.4392, 0.502, 0.5647},
  {0.5294, 0.8078, 0.9804},
  {1, 0.7137, 0.7569},
  {1, 0.7529, 0.7961},
  {1, 0.6275, 0.4784},
  {0.698, 0.1333, 0.1333},
-- Fake for test.
  {1.0, 0.1333, 0.0}
}
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
    std_data = paltransfo.get_pydef(code)
    print(std_data)

    print_section('PYTHON 2 CODE')
    coded_data = paltransfo.get_palcode(
        name    = 'OnePalName',
        palette = std_data[TAG_PALETTE]
    )
    # print(paltransfo.header)
    print(coded_data)
    # print(paltransfo.footer)

    print_section('CREDITS IN CODE')
    print(paltransfo.get_credits('Credits. OK? KO?'))

    print_section('API CODE')
    coded_api = paltransfo.get_apicode()

    if coded_api:
         if input('Print API (y/n)? ') == 'y':
             print(coded_api)

    else:
        print('NO API!')
