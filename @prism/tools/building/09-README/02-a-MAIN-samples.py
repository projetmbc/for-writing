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

PAL_KEPT = 'Accent'


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent


PRODUCTS_DIR     = PROJ_DIR / "products"
JSON_PALS_HF_DIR = PRODUCTS_DIR / 'json' / 'palettes-hf'


CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"


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
            logging.warning(
                f"No special comment '{tag}'. "
                f"If it is a bug, see:\n{mdfile}"
            )

            return

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


# ----------------- #
# -- JSON SAMPLE -- #
# ----------------- #

mdfile = PROJ_DIR / "readme" / "products.md"

logging.info(f"Pal samples - 'json'")

for jsonfile in natsorted(
    JSON_PALS_HF_DIR.glob('*.json'),
    alg = ns.IGNORECASE
):
    with jsonfile.open() as f:
        if jsonfile.stem != PAL_KEPT:
            continue

        json_pal = json_load(f)

    break


json_pal = json_pal[:MAX_LINES_SHOWN-1]
json_pal.append('...')


indent = 2

json_code = json_dumps(
    obj       = json_pal,
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


# -------------------- #
# -- TECHNO SAMPLES -- #
# -------------------- #

sample_def = json_pal[:-1]
sample_def.append([-123456789, -123456789, -123456789])

for techfolder in PRODUCTS_DIR.glob('*'):
    techno = techfolder.name

    if (
        not techfolder.is_dir()
        or
        techno == 'json'
    ):
        continue

    logging.info(f"Pal samples - '{techno}'")

    logging.info(f"({techno}) Import 'extend.py'")

    contribfolder = CONTRIB_PROD_DIR / techno

    extend = import_from_path(
        module_name = "extend",
        file_path   = contribfolder / "extend.py"
    )

    logging.info(f"({techno}) Build sample")

    paltransfo = extend.paltransfo

    _pal_code = []

    if paltransfo.header:
        _pal_code.append(paltransfo.header)

    _pal_code.append(
        paltransfo.get_palcode(
            name    = PAL_KEPT,
            palette = sample_def
        )
    )

    if paltransfo.footer:
        _pal_code.append(paltransfo.footer)

    pal_code  = '\n'.join(_pal_code)
    _pal_code = pal_code.split('\n')

    for i, line in enumerate(_pal_code):
        if '-123456789' in line:
            nb_left_spaces = len(line) - len(line.lstrip())

            _pal_code[i] = ' '*nb_left_spaces + '...'

    pal_code = '\n'.join(_pal_code)

    logging.info(f"({techno}) Update MD file sample")

    mdfile = CONTRIB_PROD_DIR / techno / "readme" / "how-to-use.md"

    update_mdfile(
        mdfile = mdfile,
        techno = techno,
        sample = pal_code,
    )
