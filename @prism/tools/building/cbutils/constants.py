#!/usr/bin/env python3

# --------------------------- #
# -- MAIN EXTERNAL SOURCES -- #
# --------------------------- #

TAG_APRISM = "@prism"

TAG_ORIGINAL_NAME = "original-name"
TAG_KIND          = "kind"
TAG_RGB_COLS      = "rgb-cols"

TAG_SEQ = "sequential"
TAG_QUAL = "qualitiative"

TAG_REPORT     = "REPORT"
TAG_XTRA_RESRC = "EXTRA-RESOURCES"


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
#  + N
    TAG_NCLCOLTABLES:"andreasplesch/ncl-color-tables",
#  + P
    TAG_PALETTABLE: "jiffyclub/palettable",
}


_github_url = "https://github.com/{ids}/archive/refs/heads/master.zip"
SRC_URLS = {
#  + A
    TAG_ASYMPTOTE: _github_url.format(ids = GITHUB_IDS[TAG_ASYMPTOTE]),
#  + C
    TAG_CARBONPLAN : _github_url.format(ids = GITHUB_IDS[TAG_CARBONPLAN]),
    TAG_CARTOCOLORS: _github_url.format(ids = GITHUB_IDS[TAG_CARTOCOLORS]),
    TAG_CMASHER    : _github_url.format(ids = GITHUB_IDS[TAG_CMASHER]),
    TAG_COLORBREWER: _github_url.format(ids = GITHUB_IDS[TAG_COLORBREWER]),
    TAG_COLORMAPS  : _github_url.format(ids = GITHUB_IDS[TAG_COLORMAPS]),
#  + N
    TAG_NCLCOLTABLES: _github_url.format(ids = GITHUB_IDS[TAG_NCLCOLTABLES]),
#  + P
    TAG_PALETTABLE: _github_url.format(ids = GITHUB_IDS[TAG_PALETTABLE]),
#  + S
    TAG_SCICOLMAPS : "https://zenodo.org/api/records/8409685/files-archive",
}
