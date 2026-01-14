#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

from pathlib import Path
import requests
import json

# URL brute (raw) du fichier JSON
url = "https://raw.githubusercontent.com/projetmbc/for-writing/main/%40prism/products/json/palettes.json"

response = requests.get(url)
response.raise_for_status()

main_pals = response.json()



THIS_DIR  = Path(__file__).parent


from json import (
    dumps as json_dumps,
    load  as json_load,
)



PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != '@prism'):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR   = PROJ_DIR / "products"
PROD_JSON_DIR = PRODS_DIR / "json"

PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"


with PAL_JSON_FILE.open(mode = "r") as f:
    local_pals = json_load(f)


print("""
---
NEW
---
""".lstrip())

for n in sorted(set(local_pals) - set(main_pals)):
    print(n)


print("""
-------
REMOVED
-------
""")

for n in sorted(set(main_pals) - set(local_pals)):
    print(n)



print("""
-------
COMPARE
-------
""")

for n1, n2 in [
    ('D3', 'Tab10'),
]:
    print(f"{n1} > {local_pals[n1]}")
    print(f"{n2} > {local_pals[n2]}")
    print(f"EQUAL: {local_pals[n1] == local_pals[n2]}")
    print(f"MIRROR: {local_pals[n1] == local_pals[n2][::-1]}")
