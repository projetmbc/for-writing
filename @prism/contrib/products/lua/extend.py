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
#     code : a RGB ''Lua'' palette definition of a palette (see the fake
#            example below).
#
#     :return: a dictionary ''{'metadata': ..., 'palette': ...}''
#              giving palette metadata as a ''str-str'' dictionary,
#              and the palette colors as a list of lists of 3 floats
#              belonging to `[0, 1]` that will be used to produce
#              the "universal" ''JSON'' version of the palette.
#
#
# A RGB ''Lua'' palette definition looks like this.
#
# lua::
#     PALETTE = {
#       {0.3922, 0.5843, 0.9294},
#       {0.5294, 0.8078, 0.9804},
#       -- ...
#     }
###
def parse(code: str) -> PaletteData:
# Kind.
    metadata = dict()

    comments = re.findall(r'-{6}([\s\S]*?)-{6}', code)

    for block in comments:
        metadata = get_thisdata(
            content = block,
            prefix  = "-- "
        )

        if metadata:
            break

    std_metadata(metadata)

# Palette.
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
        raise ValueError("No Lua PALETTE definition found.")

    palette = match.group(1)

    for old, new in [
        ('{', '['),
        ('}', ']'),
    ]:
        palette = palette.replace(old, new)

    palette = f'[{palette.strip()}]'

# Safe evaluation.
    palette = ast.literal_eval(palette)

# Nothing left to do.
    return {
        'metadata': metadata,
        'palette' : palette
    }


# ---------------------- #
# -- BUILD FINAL CODE -- #
# ---------------------- #

PALETTES_FILE_NAME = "palettes.lua"

###
# prototype::
#     credits  : the credits to the ''@prism'' project that should
#                be added as a comment at the beginning of the final
#                product code.
#     palettes : the ''Python'' dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used, with also a function ''getPal'' to
#              access one palette via its string name, or create new
#              palettes from an existing one.
###
def build_code(
    credits : str,
    palettes: dict[str, PaletteCols]
) -> str:
# Credits.
    _credits = credits.split("\n")

    maxlen = max(map(len, _credits))
    deco   = '-'*(maxlen + 6)

    credits = '\n'.join([
        f'-- {c.ljust(maxlen)} --'
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
--------------------------
-- DEFS OF EACH PALETTE --
--------------------------
        """.strip(),
        '',
    ]

# The palettes.
    indent = " "*4

    for name, colors in palettes.items():
        name = f"pal{name}"

        _paldefs_code.append(f"{name} = {{")

        for r, g, b in colors:
            _paldefs_code.append(
                f"{indent}{{{r}, {g}, {b}}},"
            )

# We remove the last unuseful coma.
        _paldefs_code[-1] = _paldefs_code[-1][:-1]

# Seperating defs with single empty lines.
        _paldefs_code.append("}\n")

    paldefs_code = '\n'.join(_paldefs_code)

# API code.
    _api_code = Path(__file__).parent / "tests" / "palapi.lua"
    api_code  = _api_code.read_text().strip()

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

------
-- this::
--     author = First Name, Last Name
--     kind   = ?
------

-- Lua definition used.

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
