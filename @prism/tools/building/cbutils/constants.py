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
TAG_KIND   = "kind"

TAG_ALIAS   = "alias"
TAG_PALETTE = "palette"


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
TAG_SEMANTIC  = "SEMANTIC"


# --------------- #
# -- RESOURCES -- #
# --------------- #

ALL_RESRC_TAGS    = set()
RESRC_SUBDIR_NAME = dict()
GITHUB_IDS        = dict()
RESRC_FILE_NAMES  = dict()
RESRC_ALIAS       = dict()


_subdir_name = defaultdict(dict)

for cfgname, data in YAML_CONFIGS[TAG_RESRC].items():
    realname = data['name']

    ALL_RESRC_TAGS.add(realname)

    # varname = varname.upper()
    varname = f"TAG_{cfgname}"

    globals()[varname] = realname

    RESRC_FILE_NAMES[globals()[varname]] = cfgname

    github_ID = data.get('github', '')
    inside    = data.get('inside', '')

    if inside:
        _subdir_name[inside][get_nospace_lower(realname)] = realname

    elif github_ID:
        GITHUB_IDS[globals()[varname]] = github_ID

    RESRC_ALIAS[realname.lower()] = realname

    if TAG_ALIAS in data:
        for alias in data[TAG_ALIAS]:
            RESRC_ALIAS[alias.lower()] = realname

RESRC_SUBDIR_NAME = {
    globals()[f"TAG_{k}"]: v
    for k, v in _subdir_name.items()
}


# GitHub URLs
__github_url = "https://github.com/{ids}/archive/refs/heads/master.zip"

SRC_URLS = {
    t: __github_url.format(ids = GITHUB_IDS[t])
    for t in GITHUB_IDS
}


# Other URLs
SRC_URLS[TAG_SCICOLMAPS] = "https://zenodo.org/api/records/8409685/files-archive"
