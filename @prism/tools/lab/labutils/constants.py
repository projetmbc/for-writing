#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
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
