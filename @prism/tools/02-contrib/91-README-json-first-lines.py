#!/usr/bin/env python3

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
TOOLS_DIR = THIS_DIR.parent

sys.path.append(str(TOOLS_DIR))

from cbutils.core import *

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

SRC_DIR   = TOOLS_DIR.parent
PRODS_DIR = SRC_DIR / "products"


MD_PROD_FILE = SRC_DIR / "readme" / "products.md"


PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


TMPL_TAG_JSON_BEGIN = "<!-- JSON PALETTE FIRST LINES. AUTO - {} -->"

TAG_JSON_BEGIN_START = TMPL_TAG_JSON_BEGIN.format("START")
TAG_JSON_BEGIN_END   = TMPL_TAG_JSON_BEGIN.format("END")


PATTERN_JSON_LIST = re.compile(r'\[\s*\n\s*([-\d.,\s]+)\s*\n\s*\]')


# ----------- #
# -- TOOLS -- #
# ----------- #

def compact_nblists(json_code: str) -> str:
    def myreplace(match: re.Match) -> str:
        content = match.group(1)
        numbers = re.findall(r'[-\d.]+', content)

        return f"[{', '.join(numbers)}]"

    return PATTERN_JSON_LIST.sub(myreplace, json_code)


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

logging.info(
    msg_creation_update(
        context = f"'{MD_PROD_FILE.relative_to(SRC_DIR)}' (auto JSON begin)",
        upper   = False,
    )
)

# -- JSON CODE BEGIN -- #

extract_pal = {}

for n, p in ALL_PALETTES.items():
    extract_pal[n] = p

    break

indent = 2

json_code = json_dumps(
    obj       = extract_pal,
    indent    = indent,
    sort_keys = True,
)

json_tab = ' '*indent

json_code = compact_nblists(json_code)
json_code = json_code.replace(
    json_tab + "]\n}",
    json_tab + json_tab.join(["],\n", "...\n}"]),
)

# -- FINAL CONTENT -- #

content = MD_PROD_FILE.read_text()

for tag in [
    TAG_JSON_BEGIN_START,
    TAG_JSON_BEGIN_END,
]:
    if content.count(tag) != 1:
        raise ValueError(
            f"use the following special comment only once:\n{tag}"
        )

before, _ , after = content.partition(f"\n{TAG_JSON_BEGIN_START}")

_ , _ , after = after.partition(f"{TAG_JSON_BEGIN_END}\n")


content = f"""{before.strip()}

{TAG_JSON_BEGIN_START}
~~~json
{json_code}
~~~
{TAG_JSON_BEGIN_END}
{after.rstrip()}
""".rstrip() + '\n'

MD_PROD_FILE.write_text(content)
