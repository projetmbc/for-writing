### The extend.py file

This file must follow the following template. The comments help you get started with coding.

<!-- EXTEND.PY AUTO - START -->
~~~python
#!/usr/bin/env python3

###
# To simplify coding, the small ''contributils'' module imported
# below provides the following functionality.
#
#     1) ''get_thisdata(content, prefix)'' removes any prefix at
#     the beginning of lines of the content, then extracts the
#     metadata provided via the special ''this'' block.
#
#     2) ''std_metadata(metadata)'' is used to provide a complete
#     metadata dictionary, potentially with empty data fields.
###

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


# -------------------- #
# -- EXTRACT COLORS -- #
# -------------------- #

###
# prototype::
#     code : a definition of a palette with the technology chosen.
#
#     :return: a dictionary ''{'metadata': ..., 'palette': ...}''
#              giving palette metadata as a ''str-str'' dictionary,
#              and the palette colors as a list of lists of 3 floats
#              belonging to `[0, 1]` that will be used to produce
#              the "universal" ''JSON'' version of the palette.
###
def parse(code: str) -> PaletteData:
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
#     palettes : the ''Python'' dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used.
#
#
# warning::
#     Except if it is totally impossible, the code build must offer
#     the ability to access a palette via the string name of the
#     variable associated with it, and also to propose ways to
#     transform palettes (extraction, shift and reverse order).
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

# Code to parse.
#     code = r"""
#
# ------
# -- this::
# --     author = Jhon, Doe
# --     kind   = qualtitatice, dark
# ------
#
# -- Luadraw definition used.
#
# -- PALETTE = {
# --   Gray,
# --   SlateGray,
# --   LightSkyBlue,
# --   LightPink,
# --   Pink,
# --   LightSalmon,
# --   FireBrick,
# -- }
#
# PALETTE = {
#   {0.502, 0.502, 0.502},
#   {0.4392, 0.502, 0.5647},
#   {0.5294, 0.8078, 0.9804},
#   {1, 0.7137, 0.7569},
#   {1, 0.7529, 0.7961},
#   {1, 0.6275, 0.4784},
#   {0.698, 0.1333, 0.1333},
# }
#     """
#
#     print_section = lambda t: print(f'\n--- {t} --\n')
#
#     print_section('INITIAL CODE')
#     print(code.strip())
#
#     std_data = parse(code)
#
#     print_section('STD DATA (JSON)')
#     print(std_data)
#
#     print_section('SPECIFIC CODE')
#     print(
#         build_code(
#             credits  = 'Credits...',
#             palettes = {"CHECKER": std_data['palette']}
#         )
#     )

~~~
<!-- EXTEND.PY AUTO - END -->
