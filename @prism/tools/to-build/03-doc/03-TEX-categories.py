#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

EN_SORTED_TITLES = {
    'deficient-blind': "Colorblind-friendly palettes",
    'bicolor'        :  "Two-color palettes",
    'tricolor'       :  "Three-color palettes",
    'rainbow'        :  "Rainbow-style palettes",
    'big-var'        :  "High-contrast palettes",
}


LUA_TMPL_CODE = r"""
% --------------------------------- %
% -- NO TRANSLATION NEEDED HERE! -- %
% --------------------------------- %

\begin{{luacode*}}
PALETTES = {{
  {catego}
}}

drawCategoPals(PALETTES, {catego_id})
\end{{luacode*}}
    """.strip() + '\n'


TMPL_TAG_CATEGO = "% AUTO CATEGOS - {}"

TAG_CATEGO_START = TMPL_TAG_CATEGO.format("START")
TAG_CATEGO_END   = TMPL_TAG_CATEGO.format("END")


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR    = BUILD_TOOLS_DIR / "REPORT"
CATEGO_DIR    = PROJ_DIR / "contrib" / "translate" / "common" / "category"
EN_MANUAL_DIR = PROJ_DIR / "contrib" / "translate" / "en" / "manual"


ALL_PALS_TEX_FILE = EN_MANUAL_DIR / "appendixes" / "all-palettes.tex"


if CATEGO_DIR.is_dir():
    for p in CATEGO_DIR.glob("*.luadraw"):
        if p.is_file():
            p.unlink()

else:
    CATEGO_DIR.mkdir(
        parents  = True,
        exist_ok = True
    )


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PAL_CATEGO_FILE = REPORT_DIR / "PAL-CATEGORY.json"

with PAL_CATEGO_FILE.open(mode = "r") as f:
    ALL_CATEGO = json_load(f)


PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"

with PAL_CREDITS_FILE.open(mode = "r") as f:
    PAL_CREDITS = json_load(f)


if set(EN_SORTED_TITLES) != set(ALL_CATEGO):
    missing_titles = set(ALL_CATEGO) - set(EN_SORTED_TITLES)
    xtra_titles    = set(EN_SORTED_TITLES) - set(ALL_CATEGO)

    message = ['']

    if missing_titles:
        message.append(f"  + Missing title(s): {missing_titles}")

    if xtra_titles:
        message.append(f"  + Extra title(s): {xtra_titles}")

    message = '\n'.join(message)

    raise ValueError(message)


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info("Build 'palette category' TeX files.")

i = 0

nb_titles_sizes = []

for id, title in EN_SORTED_TITLES.items():
    i += 1

    nb_titles_sizes.append((i, title, len(ALL_CATEGO[id])))

    filename = f"catego-{i}.luadraw"

    catego = ',\n  '.join(
        f"{{'{n}', '{PAL_CREDITS[n]}'}}"
        for n in ALL_CATEGO[id]
    )

    luacode = LUA_TMPL_CODE.format(
        catego_id = i,
        catego    = catego
    )

    (CATEGO_DIR / filename).write_text(luacode)


logging.info("Build 'all-palettes' TeX files.")

content = ALL_PALS_TEX_FILE.read_text()

before, _ , after = content.partition(f"\n{TAG_CATEGO_START}")

_ , _ , after = after.partition(f"{TAG_CATEGO_END}\n")

tex_subsections = [
    rf'  {nb}/{{{title} -- {size} palettes}},%'
    for nb, title, size in nb_titles_sizes
]

tex_subsections[-1] = tex_subsections[-1][:-2] + '%'

tex_subsections = '\n'.join(tex_subsections)

content = f"""
{before}
{TAG_CATEGO_START}
{tex_subsections}
{TAG_CATEGO_END}
{after}
""".strip() + '\n'

ALL_PALS_TEX_FILE.write_text(content)
