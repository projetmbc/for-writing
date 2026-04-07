#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR.parent.parent

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from json import load  as json_load

from natsort import (
    natsorted,
    ns
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent


AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT


CSS_JS_CORE_DIR = PROJ_DIR / "products" / "css" / "showcase" / "core"

JS_PAL_SIZES_FILE    = CSS_JS_CORE_DIR / "palsizes.js"
JS_PAL_CATEGOS_FILE  = CSS_JS_CORE_DIR / "palcategos.js"
JS_PROD_FORMATS_FILE = CSS_JS_CORE_DIR / "formats.js"


# ----------- #
# -- TOOLS -- #
# ----------- #

def normalize_jscode(
    js_code     : str,
    add_alphabet: bool,
) -> str:
    for old, new in [
        (', ', ',\n  '),
        ("',\n  ", "', "),
        ("'", '"'),
        ('{"', '{\n  "'),
        ("};", '\n};\n'),
    ]:
        js_code = js_code.replace(old, new)

# Alphabet comments
    if add_alphabet:
        _js_code    = []
        last_letter = ''

        for line in js_code.splitlines():
            if line.startswith('  "'):
                letter = line[3]

                if letter != last_letter:
                    _js_code.append(f'// -- {letter} -- //')

                    last_letter = letter

            _js_code.append(line)

        js_code = '\n'.join(_js_code)

    return js_code


# ----------------------------- #
# -- JS DATA - PALETTE SPECS -- #
# ----------------------------- #

logging.info(f"Finalize 'css' product")

_CATEGOS = {}
CATEGOS  = {}

_SIZES = {}
SIZES  = {}

with sqlite3.connect(AUDIT_DIR / 'palettes.db') as conn:
    cursor = conn.cursor()

    query = """
SELECT
    COALESCE(a.alias, h.name),
    h.catego,
    h.size
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1;
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    for prodname, categos, size in rows:
        _SIZES[prodname] = size

        _CATEGOS[prodname] = [
            c.strip()
            for c in categos.split(',')
        ]

        _CATEGOS[prodname].sort()


for prodname in natsorted(
    _SIZES,
    alg = ns.IGNORECASE
):
    SIZES[prodname]   = _SIZES[prodname]
    CATEGOS[prodname] = _CATEGOS[prodname]


for name, data, jsfile, add_alphabet in [
    (
        'PAL_FORMAT',
        {'css': "css"},
        JS_PROD_FORMATS_FILE,
        False,
    ),
    (
        'PAL_CATEGO',
        CATEGOS,
        JS_PAL_CATEGOS_FILE,
        True,
    ),
    (
        'PAL_SIZE',
        SIZES,
        JS_PAL_SIZES_FILE,
        True,
    )
]:
    logging.info(
        f"Update '{jsfile.relative_to(PROJ_DIR)}'"
    )

    js_precode = f"const {name} = {repr(data)};"

    jsfile.write_text(
        normalize_jscode(
            js_precode,
            add_alphabet
        )
    )
