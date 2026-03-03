#!/usr/bin/env python3

from collections import defaultdict
from pathlib     import Path

from yaml import safe_load


THIS_DIR = Path(__file__).parent

PROJ_DIR = THIS_DIR.parent

while(PROJ_DIR.name != '@prism'):
    PROJ_DIR = PROJ_DIR.parent

IGNORED_YAML  = PROJ_DIR / 'tools' / 'building' / 'AUDIT' / 'IGNORED.yaml'

IGNORED = safe_load(IGNORED_YAML.read_text())

NORMALIZED_IGNORED = defaultdict(dict)

for src, data in IGNORED.items():
    for palname, infos in data.items():
        print(f"{src=} , {palname=} , {infos=}")
