#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils.cleanpal import PALSIZE
from cbutils.version  import VERSION

from json import load as json_load
from os   import makedirs

# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR      = Path(__file__).parent
PROJ_DIR      = THIS_DIR.parent.parent
REPORT_DIR    = PROJ_DIR / "tools" / "report"
CATEGO_DIR    = PROJ_DIR / "contrib" / "translate" / "common" / "category"
EN_MANUAL_DIR = PROJ_DIR / "contrib" / "translate" / "en" / "manual"


ALL_PALS_TEX_FILE = EN_MANUAL_DIR / "appendixes" / "all-palettes.tex"


if CATEGO_DIR.is_dir():
    for p in CATEGO_DIR.glob("*.luadraw"):
        if p.is_file():
            p.unlink()

else:
    makedirs(CATEGO_DIR, exist_ok=True)


PAL_CATEGO_FILE = REPORT_DIR / "PAL-CATEGORY.json"

with PAL_CATEGO_FILE.open(mode = "r") as f:
    ALL_CATEGO = json_load(f)


TMPL_TAG_CATEGO = "% AUTO CATEGOS - {}"

TAG_CATEGO_START = TMPL_TAG_CATEGO.format("START")
TAG_CATEGO_END   = TMPL_TAG_CATEGO.format("END")


LUA_TMPL_CODE = r"""
% --------------------------------- %
% -- NO TRANSLATION NEEDED HERE! -- %
% --------------------------------- %

\begin{{luacode*}}
PALETTES = {{
  {catego}
}}

drawCategoPals(PALETTES)
\end{{luacode*}}
    """.strip() + '\n'


EN_SORTED_TITLES = {
    'deficient-blind': "Colorblind-friendly palettes",
    'bicolor'        : "Two-color palettes",
    'tricolor'       : "Three-color palettes",
    'rainbow'        : "Rainbow-style palettes",
    'big-var'        : "High-contrast palettes",
}

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

nb_titles = []

for id, title in EN_SORTED_TITLES.items():
    i += 1

    nb_titles.append((i, title))

    filename = f"catego-{i}.luadraw"

    luacode = LUA_TMPL_CODE.format(
        catego = ',\n  '.join(
            repr(n) for n in ALL_CATEGO[id]
        )
    )

    (CATEGO_DIR / filename).write_text(luacode)


logging.info("Build 'all-palettes' TeX files.")

content = ALL_PALS_TEX_FILE.read_text()

before, _ , after = content.partition(f"\n{TAG_CATEGO_START}")

_ , _ , after = after.partition(f"{TAG_CATEGO_END}\n")

nb_titles = [
    f'  {nb}/{{{title}}},%'
    for nb, title in nb_titles
]

nb_titles[-1] = nb_titles[-1][:-2] + '%'

nb_titles = '\n'.join(nb_titles)

content = f"""
{before}
{TAG_CATEGO_START}
{nb_titles}
{TAG_CATEGO_END}
{after}
""".strip() + '\n'

ALL_PALS_TEX_FILE.write_text(content)
