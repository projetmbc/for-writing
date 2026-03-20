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

MAX_LINES_SHOWN = 3


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent


PRODUCTS_DIR     = PROJ_DIR / "products"
JSON_PALS_HF_DIR = PRODUCTS_DIR / 'json' / 'palettes-hf'


# ----------- #
# -- TOOLS -- #
# ----------- #

PATTERN_JSON_LIST = re.compile(r'\[\s*\n\s*([-\d.,\s]+)\s*\n\s*\]')

def compact_nblists(json_code: str) -> str:
    def myreplace(match: re.Match) -> str:
        content = match.group(1)
        numbers = re.findall(r'[-\d.]+', content)

        return f"[{', '.join(numbers)}]"

    return PATTERN_JSON_LIST.sub(myreplace, json_code)


def update_mdfile(mdfile, techno, sample):
    tmpl_tag = f"<!-- {techno.upper()} PALETTE SAMPLE - AUTO - {{}} -->"

    tag_start = tmpl_tag.format("START")
    tag_end   = tmpl_tag.format("END")

    content = mdfile.read_text()

    for tag in [tag_start, tag_end]:
        if content.count(tag) != 1:
            raise ValueError(
                f"use the following special comment only once:\n{tag}"
                f"\nSee file:\n{mdfile}"
            )

    before, _ , after = content.partition(f"\n{tag_start}")

    _ , _ , after = after.partition(f"{tag_end}\n")

    content = f"""{before.strip()}

{tag_start}
~~~{techno}
{sample}
~~~
{tag_end}
{after.rstrip()}
""".rstrip() + '\n'

    mdfile.write_text(content)


# --------------------- #
# -- GET 1ST PALETTE -- #
# --------------------- #

logging.info("Pal sample - Get '1st palette'")

for jsonfile in natsorted(
    JSON_PALS_HF_DIR.glob('*.json'),
    alg = ns.IGNORECASE
):
    with jsonfile.open() as f:
        palname_1st  = jsonfile.stem
        json_pal_1st = json_load(f)

    break


# ----------------- #
# -- JSON SAMPLE -- #
# ----------------- #

mdfile = PROJ_DIR / "readme" / "products.md"

logging.info(
    msg_creation_update(
        context = f"Pal sample - 'JSON'",
        upper   = False,
    )
)


if len(json_pal_1st) > MAX_LINES_SHOWN:
    json_pal_1st = json_pal_1st[:MAX_LINES_SHOWN-1]
    json_pal_1st.append('...')


indent = 2

json_code = json_dumps(
    obj       = json_pal_1st,
    indent    = indent,
    sort_keys = True,
)

json_tab = ' '*indent

json_code = compact_nblists(json_code)

json_code = json_code.replace(
    json_tab + "]\n}",
    json_tab + json_tab.join(["],\n", "...\n}"]),
)

json_code = json_code.replace('"..."', '...')

update_mdfile(
    mdfile = mdfile,
    techno = 'json',
    sample = json_code,
)


# ----------------- #
# -- JSON SAMPLE -- #
# ----------------- #









exit(1)
