### The 'extend.py' file

This file must follow the following template.

~~~python
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
#     code : a definition of a palette with the technology chosen.
#
#     :return: a list of lists of 3 floats belonging to `[0, 1]` that
#              will be used to produce the "universal" \json version
#              of the palette.
###
def parse(code: str) -> list[ [float, float, float] ]:
    ...


# ---------------------- #
# -- BUILD FINAL CODE -- #
# ---------------------- #

PALETTES_FILE_NAME = "..."

###
# prototype::
#     name : name of the palette.
#     data : a list of lists of 3 floats belonging to `[0, 1]` that
#            comes from "universal" \json version of the palette.
#
#     :return: code of the palette for the technology chosen.
###
def build_code(
    name: str,
    data: list[ [float, float, float] ]
) -> str:
    ...


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
    ...
~~~
