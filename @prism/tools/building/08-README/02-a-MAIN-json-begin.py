#!/usr/bin/env python3

# ---------------------------- #
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

from json import (
    dumps as json_dumps,
    load  as json_load,
)

from natsort import (
    natsorted,
    ns
)


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

TMPL_TAG_JSON_BEGIN = "<!-- JSON PALETTE FIRST LINES. AUTO - {} -->"

TAG_JSON_BEGIN_START = TMPL_TAG_JSON_BEGIN.format("START")
TAG_JSON_BEGIN_END   = TMPL_TAG_JSON_BEGIN.format("END")


PATTERN_JSON_LIST = re.compile(r'\[\s*\n\s*([-\d.,\s]+)\s*\n\s*\]')


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


JSON_PALS_HF_DIR = PROJ_DIR / "products" / 'json' / 'palettes-hf'


MD_PROD_FILE = PROJ_DIR / "readme" / "products.md"


# ----------- #
# -- TOOLS -- #
# ----------- #

def compact_nblists(json_code: str) -> str:
    def myreplace(match: re.Match) -> str:
        content = match.group(1)
        numbers = re.findall(r'[-\d.]+', content)

        return f"[{', '.join(numbers)}]"

    return PATTERN_JSON_LIST.sub(myreplace, json_code)


# --------------------- #
# -- GET 1ST PALETTE -- #
# --------------------- #

logging.info("Get '1st palette'")

for jsonfile in natsorted(
    JSON_PALS_HF_DIR.glob('*.json'),
    alg = ns.IGNORECASE
):
    with jsonfile.open() as f:
        firstpal = json_load(f)

    break


# --------------- #
# -- MD UPDATE -- #
# --------------- #

logging.info(
    msg_creation_update(
        context = f"'{MD_PROD_FILE.relative_to(PROJ_DIR)}' (auto JSON begin)",
        upper   = False,
    )
)

# -- JSON CODE BEGIN -- #

indent = 2

json_code = json_dumps(
    obj       = firstpal,
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
