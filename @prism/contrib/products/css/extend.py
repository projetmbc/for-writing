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
# An RGB ''CSS'' palette named ''PALETTE'' is defined as follows.
#
# css::
#     --palPALETTE-1: rgb(39.22% 58.43% 92.94%);
#     --palPALETTE-2: rgb(52.94% 80.78% 98.04%);
#     /* ... */
###
def parse(code: str) -> PaletteData:
# Metadata (we delegate).
    metadata = get_this_data(
        content  = code,
        comspecs = {
            TAG_MULTICOM_START: '/*',
            TAG_MULTICOM_END  : '*/',
        },
    )

# Palette definition (we dirty our hands).
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
    return final_paldef(metadata, palette)


# ------------------- #
# -- BUILD CREDITS -- #
# ------------------- #

###
# prototype::
#     credits  : the credits to the ''@prism'' project that
#                should be added as a comment at the beginning
#                of the final product codes.
#
#     :return: the credits inside a decorated \css comment.
###
def build_credits(credits : str) -> str:
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

    return credits


###
# prototype::
#     :return: ????
###
def build_palette_header() -> str:
    header = """
/* -------------------------- */
/* -- DEFS OF EACH PALETTE -- */
/* -------------------------- */

:root {
    """.strip()

    return header


###
# prototype::
#     :return: ????
###
def build_palette_footer() -> str:
# WE must close '':root {''.
    return '}'


###
# prototype::
#     name    : name of one single palette.
#     palette : one single palette.
#
#     :return: the \css code of ''palette'' for the final
#              product codes.
###
def build_palette(
    name   : str,
    palette: PaletteCols
) -> str:
# -- Internal function -- #
    def float2percentage(x: float) -> str:
        x *= 100
        _x = f"{x:.6f}"
        _x = _x.rstrip('0')
        _x = _x.rstrip('.')

        return f"{_x}%"

# -- Let's work! -- #
    indent = " "*4

    name = f"--pal{name}"

    _paldefs_code = []

    for i, (r, g, b) in enumerate(colors, start = 1):
        _r, _g, _b = map(float2percentage, [r, g, b])

        _paldefs_code.append(
            f"{indent}{name}-{i}: rgb({_r} {_g} {_b});"
        )

    paldefs_code = '\n'.join(_paldefs_code)

    return paldefs_code







# ---------------------- #
# -- BUILD FINAL CODE -- #
# ---------------------- #

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


# The palettes.

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
--palPALETTE-2: rgb(0% 0% 0%);
--palPALETTE-3: rgb(40% 0% 20%);
--palPALETTE-4: rgb(80% 20% 0%);
--palPALETTE-5: rgb(100% 60% 0%);
--palPALETTE-6: rgb(100% 100% 45.678%);
    """

    from rich import print

    print_section = lambda t: print(f'\n--- {t} --\n')

    print_section('INITIAL CODE')
    print(code.strip())

    std_data = parse(code)

    print_section('STD DATA (JSON)')
    print(std_data)

    exit(1)
    print_section('SPECIFIC CODE')
    print(
        build_code(
            credits  = 'Credits...',
            palettes = {"CHECKER": std_data['palette']}
        )
    )
