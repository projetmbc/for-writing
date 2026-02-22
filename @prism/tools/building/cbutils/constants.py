#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

from pathlib import Path
import              yaml

from collections import defaultdict

from .normval import get_nospace_lower


# ------------------ #
# -- THIS PROJECT -- #
# ------------------ #

__TAG_APRISM         = '@prism'
TAG_APRISM_LAST_MAIN = f'{__TAG_APRISM.upper()}-LAST-MAIN'


PROJ_DIR = Path(__file__).parent

while (PROJ_DIR.name != __TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_tag_varname(name: str) -> str:
    varname = f"tag_{name}"
    varname = varname.upper()

    return varname


# -------------- #
# -- FOR DOCS -- #
# -------------- #

TAG_USED_BY_TOOLS = "used-by-tools"


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


# ----------- #
# -- AUDIT -- #
# ----------- #

PAL_PRECISION = YAML_CONFIGS[TAG_METADATA]['PRECISION']

TAG_ORIGINAL_NAME = "original-name"
TAG_RGB_COLS      = "rgb-cols"

TAG_AUTHOR = "author"
TAG_CATEGO = "catego"

TAG_ALIAS   = "alias"
TAG_PALETTE = "palette"


CATEGO_ALIAS = dict()

for catego, about in YAML_CONFIGS[TAG_METADATA]['CATEGORY'].items():
    alias = about['alias']

    varname = f"tag_{catego}"
    varname = varname.upper()

    globals()[varname] = catego

    CATEGO_ALIAS[catego] = catego

    if not alias is None:
        for a in alias:
            CATEGO_ALIAS[a] = catego


TAG_AUDIT     = "AUDIT"
TAG_REPORT    = "REPORT"
TAG_RESOURCES = "RESOURCES"
TAG_SEMANTIC  = "SEMANTIC"


TAG_WHY = 'why'
TAG_SRC = 'src'
TAG_REL = 'relation'
TAG_PAL = 'palette'


# --------------- #
# -- RESOURCES -- #
# --------------- #

RESRC_SUBDIR_NAME = defaultdict(list)
GITHUB_IDS        = dict()
RESRC_ALIAS       = dict()


for cfgname, data in YAML_CONFIGS[TAG_RESRC].items():
    realname = data['name']

    # varname = varname.upper()
    varname = f"TAG_{cfgname}"

    globals()[varname] = cfgname

    github_ID = data.get('github', '')
    inside    = data.get('inside', '')

    if inside:
        RESRC_SUBDIR_NAME[inside].append(cfgname)

    elif github_ID:
        GITHUB_IDS[cfgname] = github_ID

    RESRC_ALIAS[cfgname] = realname

    if TAG_ALIAS in data:
        for alias in data[TAG_ALIAS]:
            RESRC_ALIAS[alias.upper()] = realname


# GitHub URLs
__github_url = "https://github.com/{ids}/archive/refs/heads/master.zip"

SRC_URLS = {
    t: __github_url.format(ids = GITHUB_IDS[t])
    for t in GITHUB_IDS
}


# Other URLs
SRC_URLS[TAG_SCICOLMAPS] = "https://zenodo.org/api/records/8409685/files-archive"
