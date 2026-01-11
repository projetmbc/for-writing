#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

from pathlib import Path
import              yaml


# ------------------ #
# -- THIS PROJECT -- #
# ------------------ #

TAG_APRISM = "@prism"

THIS_DIR = Path(__file__).parent

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_tag_varname(name: str) -> str:
    varname = f"tag_{name}"
    varname = varname.upper()

    return varname


# ------------------ #
# -- YAML CONFIGS -- #
# ------------------ #

YAML_CONFIGS = dict()

for p in (PROJ_DIR / 'tools' / 'config').glob('*.yaml'):
    name    = p.stem
    varname = get_tag_varname(name)

    with p.open(mode = 'r') as f:
         data = yaml.safe_load(f)

    globals()[varname] = name

    YAML_CONFIGS[name] = data


# ---------------------------- #
# -- PALETTE CLASSIFICATION -- #
# ---------------------------- #

TAG_KEPT   = "kept"
TAG_EQUAL  = "equal"
TAG_MIRROR = "mirror"

TAG_SUFFIXES = "_SUFFIXES_"


# -------------------- #
# -- CONTRIB CONFIG -- #
# -------------------- #

TAG_CLEAN  = "clean"
TAG_DATA   = "data"
TAG_GOBBLE = "gobble"


# --------------------------- #
# -- MAIN EXTERNAL SOURCES -- #
# --------------------------- #

PAL_PRECISION = YAML_CONFIGS[TAG_METADATA]['PRECISION']

TAG_ORIGINAL_NAME = "original-name"
TAG_RGB_COLS      = "rgb-cols"

TAG_AUTHOR = "author"
TAG_KIND   = "kind"

TAG_PALETTE  = "palette"


KIND_ALIAS = dict()

for kind, about in YAML_CONFIGS[TAG_METADATA]['CATEGORY'].items():
    alias = about['alias']

    varname = f"tag_{kind}"
    varname = varname.upper()

    globals()[varname] = kind

    KIND_ALIAS[kind] = kind

    if not alias is None:
        for a in alias:
            KIND_ALIAS[a] = kind


TAG_AUDIT     = "AUDIT"
TAG_REPORT    = "REPORT"
TAG_RESOURCES = "RESOURCES"


TAGS_XTRA_PROJS = [
#  + C
    TAG_CARBONPLAN := 'CarbonPlan',
    TAG_CARTOCOLORS:= 'CARTOColors',
    TAG_CMASHER    := 'CMasher',
    TAG_COLORBREWER:= 'Colorbrewer',

#  + M
    TAG_MATPLOTLIB:= 'Matplotlib',

#  + N
    TAG_NCLCOLTABLES:= 'NCAR NCL color tables',

#  + P
    TAG_PALETTABLE:= 'Palettable',
    TAG_PLOTLY    := 'Plotly',

#  + S
    TAG_SCICOLMAPS:= 'Scientific Colour Maps',

# -- COMPLEMENTARY EXTERNAL SOURCES -- #

#  + A
    TAG_ASYMPTOTE:= 'Asymptote',

#  + C
    TAG_COLORMAPS:= 'Colormaps',
]


# ------------------- #
# -- SUB RESOURCES -- #
# ------------------- #

PALETTABLE_SUB_FOLDERS = [
    (TAG_CMOCEAN       := "cmocean"),
    (TAG_CUBEHELIX     := "Cubehelix"),
    (TAG_LIGHT_BARTLEIN:= "Light Bartlein"),
    (TAG_MYCARTA       := "MyCarta"),
    (TAG_PLOTLY        := "Plotly"),
    (TAG_TABLEAU       := "Tableau"),
    (TAG_WESANDERSON   := "Wes Anderson"),
]

PALETTABLE_SUB_FOLDERS = {
    t.replace(' ', '').lower(): t
    for t in PALETTABLE_SUB_FOLDERS
}


# -------------------------- #
# -- EXTERNAL SOURCE URLS -- #
# -------------------------- #

GITHUB_IDS = {
#  + A
    TAG_ASYMPTOTE: "vectorgraphics/asymptote",
#  + C
    TAG_CARBONPLAN : "carbonplan/colormaps",
    TAG_CARTOCOLORS: "CartoDB/cartocolor",
    TAG_CMASHER    : "1313e/CMasher",
    TAG_COLORBREWER: "axismaps/colorbrewer",
    TAG_COLORMAPS  : "pratiman-91/colormaps",
#  + M
    TAG_MATPLOTLIB: "matplotlib/matplotlib",
#  + N
    TAG_NCLCOLTABLES:"andreasplesch/ncl-color-tables",
#  + P
    TAG_PALETTABLE: "jiffyclub/palettable",
}


# GitHub URLs
_github_url = "https://github.com/{ids}/archive/refs/heads/master.zip"

SRC_URLS = {
    t: _github_url.format(ids = GITHUB_IDS[t])
    for t in GITHUB_IDS
}

# Other URLs
SRC_URLS[TAG_SCICOLMAPS] = "https://zenodo.org/api/records/8409685/files-archive"
