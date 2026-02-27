#!/usr/bin/env python3

# ---------------------------- #     NETTOYER CE QUI EST EN TROP !!!
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent


HF_PALS_DIR  = PROJ_DIR / "products" / "json" / "palettes-hf"
SHOWCASE_DIR = PROJ_DIR / "contrib" / "translate" / "common" / "showcase"

SHOWCASE_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


SEM_PAL_SIZE = YAML_CONFIGS[TAG_SEMANTIC]['MAX_SEM_SIZE']


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

TAB = " "*4


TEX_HEADER = rf"""
% !TEX TS-program = lualatex

{TEX_NO_EDIT}

""".lstrip() + r"""

\documentclass{standalone}

\usepackage[svgnames]{xcolor}
\usepackage[3d]{luadraw}

\directlua{
  dofile('../../../../products/lua/palettes-hf/<PAL-NAME>.lua')
}

\begin{document}
""".strip()


TEX_FOOTER = r"\end{document}"


TEX_TMPL_PALETTE = r"""
\begin{luadraw}{name = <PAL-NAME>-palette}
local PAL = pal<PAL-NAME>

local WIDTH = 10

local PALSIZE  = #PAL
local PALDIM   = .6
local PALDELTA = .1

local g = graph:new{
  window = {-WIDTH - 5, WIDTH + 5, -5, 4.4},
  bbox   = false
}

g:Linewidth(2)

local A = Z(-WIDTH, 4)
local v = Z(0, -PALDIM)

for k = 1, PALSIZE do
  local color = rgb(PAL[k])

  g:Drectangle(
    A, A + PALDIM, A + PALDIM + v,
    "color = black, fill = " .. color
  )

  g:Dlabel(
    "\\footnotesize$" .. k .. "$",
    A + Z(PALDIM, .85*PALDIM) / 2,
    {
      pos          = "S",
      node_options = "inner sep = 0pt, outer ysep = 0.5pt"
    }
  )

  A = A + PALDIM + PALDELTA

  if k % 10 == 0 then
    A = A + Z(-10*(PALDIM + PALDELTA), -2*PALDIM)
  end
end

g:Show()
\end{luadraw}
""".strip()


TEX_TMPL_SPECTRUM = r"""
\begin{luadraw}{name = <PAL-NAME>-spectrum}
local PAL      = pal<PAL-NAME>
local NB_CELLS = <NB-CELLS>

local WIDTH = 8

local A = Z(-WIDTH / 2, 4)
local HEIGHT = Z(0, -.7)

local g = graph:new{
  window = {
    -WIDTH / 2,
    WIDTH / 2,
    -5, 5
  },
  bbox = false
}

local dl = WIDTH / NB_CELLS

for k = 1, NB_CELLS do
  local color = palette(
    PAL,
    (k - 1) / (NB_CELLS - 1)
  )

  g:Drectangle(
    A,
    A + HEIGHT,
    A + HEIGHT + dl,
    "color=" .. color .. ", fill=" .. color
  )

  A = A + dl
end

g:Drectangle(
  A,
  A + HEIGHT,
  A + HEIGHT - WIDTH,
  "color=black"
)

g:Show()
\end{luadraw}
""".strip()


TEX_TMPL_ANGULAR_SPECTRUM = r"""
\begin{luadraw}{name = <PAL-NAME>-angular}
require 'luadraw_shadedforms'

local g = graph:new{
  size   = {10,10},
  margin = {0,0,0,0},
  bbox   = false
}

L = circle(0, 1)

local f = function(x,y)
  return cpx.arg(Z(x,y))
end

g:Dshadedpolyline(
  L,
  pal<PAL-NAME>,
  {
    values = f,
    width  = 300
  }
)

g:Show()
\end{luadraw}
"""

# ---------------------- #
# -- PALETTE GRAPHICS -- #
# ---------------------- #

logging.info(
  "Build 'palette, spectrum and angular gradient graphics' files"
)

ALL_NAMES = set()

for hfpal in sorted(HF_PALS_DIR.glob('*.json')):
    name = hfpal.stem

    ALL_NAMES.add(name)

    with hfpal.open('r') as f:
        palsize = len(json_load(f))

# One palette.
    if palsize < SEM_PAL_SIZE:
        _texcode = [
            TEX_HEADER.replace(
                '<PAL-NAME>',
                name
            ),
            TEX_TMPL_PALETTE.replace(
                '<PAL-NAME>',
                name
            ),
            TEX_FOOTER
        ]

        texcode = '\n'.join(_texcode) + '\n'

        (
            SHOWCASE_DIR / f"{name}-palette.tex"
        ).write_text(texcode)

# Spectrum.
    nbcells = max(200, palsize)

    _texcode = [
        TEX_HEADER.replace(
            '<PAL-NAME>',
            name
        ),
        TEX_TMPL_SPECTRUM.replace(
            '<PAL-NAME>',
            name
        ).replace(
            '<NB-CELLS>',
            str(nbcells)
        ),
        TEX_FOOTER
    ]

    texcode = '\n'.join(_texcode) + '\n'

    (
        SHOWCASE_DIR / f"{name}-spectrum.tex"
    ).write_text(texcode)


# Angular gradient.
    _texcode = [
        TEX_HEADER.replace(
            '<PAL-NAME>',
            name
        ),
        TEX_TMPL_ANGULAR_SPECTRUM.replace(
            '<PAL-NAME>',
            name
        ),
        TEX_FOOTER
    ]

    texcode = '\n'.join(_texcode) + '\n'

    (
        SHOWCASE_DIR / f"{name}-angular.tex"
    ).write_text(texcode)


# ---------------------- #
# -- CLEANING -- #
# ---------------------- #

logging.info("Clean 'palette and spectrum graphics' folder")

for f in sorted(SHOWCASE_DIR.glob('*')):
    parts = f.stem.split('-')

    if (
      f.is_dir()
      or
      f.name[0] == '.'
      or
      (
          len(parts) == 2
          and
          parts[0] in ALL_NAMES
          and
          parts[1] in [
              'angular',
              'palette',
              'spectrum'
          ]
      )
    ):
        continue

    logging.warning(f"Remove '{f.name}'")

    f.unlink()
