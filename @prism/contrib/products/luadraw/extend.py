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
#     code : a standard ''luadraw'' definition of a palette (see the
#            fake example below).
#
#     :return: a list of lists of 3 floats belonging to `[0, 1]` that
#              will be used to produce the "universal" ''JSON'' version
#              of the palette.
#
#
# A standard ''luadraw'' palette looks like this.
#
# lua::
#     PALETTE = {
#       {0.498039, 0.788235, 0.498039},
#       {0.690196, 0.705881, 0.757298},
#       ...
#     }
###
def parse(code: str) -> list[ [float, float, float] ]:
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
        raise ValueError("No table PALETTE found.")

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

PALETTES_FILE_NAME = "palettes.lua"

###
# prototype::
#     credits  : the credits to the ''@prism'' project that should
#                be added as a comment at the beginning of the final
#                product code.
#     palettes : the Python dictionnary of all the palettes.
#
#     :return: the code of the final product with all the palettes
#              ready to be used, with a function ''getPal'' to access
#              a palette via its string name, or create new palettes
#              from an existing one.
###
def build_code(
    credits : str,
    palettes: dict[ str, list[ [float, float, float] ] ]
) -> str:
# Credits.
    code = []

    code_dict = []

    credits = credits.split("\n")

    maxlen = max(map(len, credits))
    deco   = '-'*(maxlen + 6)

    credits = [
        f'-- {c.ljust(maxlen)} --'
        for c in credits
    ]

    credits = '\n'.join(credits)

    code = [
        deco,
        credits,
        deco,
        '',
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

        code.append(f"{name} = {{")

        for r, g, b in colors:
            code.append(f"{indent}{{{r}, {g}, {b}}},")

# We remove the last unuseful coma.
        code[-1] = code[-1][:-1]

# Seperating defs with single empty lines.
        code.append("}\n")

    code.append(
        """
-----------------------------
-- USE AND CREATE PALETTES --
-----------------------------

------
-- prototype::
--     name    : a palette name with, or without, the prefix
--               ''pal''.
--     options : a dictionary like array (see a full example
--               of use after).
--
--     :return: the expected palette.
--
--
-- Let's consider the following use case where we could also
-- have used ''"palGeoRainbow"''.
--
--
-- lua::
--     mypal = getPal(
--       "GeoRainbow",
--       {
--         extract = {2, 5, 8, 9},
--         shift   = 3,
--         reverse = true
--       }
--     )
--
-- To simplify the explanations, we will refer to the colors
-- in the standard palette ''GistHeat'' as ''coul_1'',
-- ''coul_2'', etc. The options are then processed in the
-- following order.
--
--     1) First,the extraction is done: ''mypal = {coul_2,
--     coul_5, coul_8, coul_9}''.
--
--     2) Then, the shift is applied to the extracted palette,
--     colors moving to the right if ''shift'' is positive:
--     ''mypal = {coul_5, coul_8, coul_9, coul_2}''.
--
--
-- Finally, inversion is applied.
--
-- lua::
--     mypal = {coul_2, coul_9, coul_8, coul_5}
------
function getPal(name, options)
-- Standard palette.
    if string.sub(name, 1, 3) ~= "pal" then
        name = "pal" .. name
    end

    local palette = _G[name]

-- No option used.
    if options == nil then
        return palette
    end

-- Some options used.
    local result = {}

    for i, color in ipairs(palette) do
        result[i] = {color[1], color[2], color[3]}
    end

-- Extraction.
    if options.extract ~= nil then
        local extracted = {}

        for _ , index in ipairs(options.extract) do
            if result[index] ~= nil then
                table.insert(extracted, result[index])
            end
        end

        result = extracted
    end

-- Shifting.
    if options.shift ~= nil and options.shift ~= 0 then
        local shifted  = {}
        local pal_size = #result

        local shift = options.shift % pal_size

        for i = 1, pal_size do
            local new_i    = ((i - 1 + shift) % pal_size) + 1
            shifted[new_i] = result[i]
        end

        result = shifted
    end

-- Reversing.
    if options.reverse == true then
        local reversed = {}

        for i = #result, 1, -1 do
            table.insert(reversed, result[i])
        end

        result = reversed
    end

    return result
end
        """.strip() + '\n'
    )

# Extra code because no getPal inside luadraw...
    all_names = sorted(palettes)
    all_names = [f'"pal{n}"' for n in all_names]
    all_names = ",\n    ".join(all_names)

    code.append(
        f"""
---------------------------------
-- GET ONE PALETTE BY ITS NAME --
---------------------------------

palNames = {{}}

for _ , name in ipairs({{
    {all_names}
}}) do
    palNames[name] = _G[name]
end
        """.strip() + '\n'
    )

# Nothing left to do.
    code = '\n'.join(code)

    return code


# ---------------- #
# -- LOCAL TEST -- #
# ---------------- #

if __name__ == "__main__":
# Code to parse.
    code = r"""
-- ludraw definition used.

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
            palettes = {"TEST": std_data}
        )
    )
