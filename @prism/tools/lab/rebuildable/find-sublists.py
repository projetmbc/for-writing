#!/usr/bin/env python3

from collections import defaultdict
from pathlib     import Path

from yaml import safe_load


THIS_DIR = Path(__file__).parent

PROJ_DIR = THIS_DIR.parent

while(PROJ_DIR.name != '@prism'):
    PROJ_DIR = PROJ_DIR.parent


ALL_PALS = dict()

for paljson in (
    PROJ_DIR / 'products' / 'json' / 'palettes-hf'
).glob('*.json'):
    print(paljson.stem)
