### The extend.py file

This file must follow the following template. The comments help you get started with coding. Take also a look at the existing products.

<!-- EXTEND.PY AUTO - START -->
~~~python
#!/usr/bin/env python3

###
# To simplify coding, the small ''contributils'' module
# imported below provides the ''PaletteTransformer'' class,
# which streamlines feature engineering.
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


# --------------------------------- #
# -- SINGLE PALETTE CODE BUILDER -- #
# --------------------------------- #

###
# prototype::
#     name    : name of one single palette.
#     palette : one single palette.
#
#     :return: the code of ''palette'' for the final product
#              versions.
#
#
# warning::
#     All tecnhologies must implement a ''_build_palette''
#     function.
###
def _build_palette(
    name   : str,
    palette: PaletteCols
) -> str:
    ...


# ---------------------- #
# -- API CODE BUILDER -- #
# ---------------------- #

###
# prototype::
#     :return: the code of the \api of the final product.
#
#
# warning::
#     Except if it is totally impossible, the code build must
#     offer the ability to access a palette via the string name
#     of the variable associated with it, and also to propose
#     ways totransform palettes (extraction, shift and reverse
#     order). Therefore, the lines below should be removed if
#     the technology does not provide an API.
###
def _build_api() -> str:
    ...


# ------------------------- #
# -- PALETTE TRANSFORMER -- #
# ------------------------- #

###
# The ''PaletteTransformer'' class requires four mandatory
# arguments and offers five optional parameters.
#
#     1) ''extension'' is the extension of the files to build.
#
#     1) ''comspecs'' is a dictionnary to specify multiline
#     and/or single comments.
#
#     1) ''palpattern'' is a regex to extract colors from a
#     palette defined in a specific technology.
#
#     1) ''pal_builder'' is a function that builds the code of
#     a single palette.
#
#     1) ''api_builder'' is a function that builds the API code
#     (if there is one).
#
#     1) ''floatify'' is used to make a flot from one string color
#     extracted.
#
#     1) ''header'' can be used to add some specific lines before
#     the palette codes.
#
#     1) ''footer'' can be used to add some specific lines after
#     the palette codes.
#
#     1) ''titledeco'' is the single character used to frame the
#     titles in special comments.
###
paltransfo = PaletteTransformer(
    extension   = ...,
    comspecs    = ...,
    palpattern  = ...,
    pal_builder = ...,
    api_builder = ...,  # OPTIONAL.
    floatify    = ...,  # OPTIONAL.
    titledeco   = ...,  # OPTIONAL.
    header      = ...,  # OPTIONAL.
    footer      = ...,  # OPTIONAL.
)


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
    ...
~~~
<!-- EXTEND.PY AUTO - END -->
