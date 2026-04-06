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


AUDIT_DIR   = BUILD_TOOLS_DIR / TAG_AUDIT


JS_CORE_DIR         = PROJ_DIR / "products" / "css" / "showcase" / "core"
JS_PAL_SIZES_FILE   = JS_CORE_DIR / "palsizes.js"
JS_PAL_CATEGOS_FILE = JS_CORE_DIR / "palcategos.js"


# ----------- #
# -- TOOLS -- #
# ----------- #

def normalize_jscode(js_precode):
    for old, new in [
        ("'", '"'),
        (', ', ',\n  '),
        ('{"', '{\n  "'),
        ("};", '\n};\n'),
    ]:
        js_precode = js_precode.replace(old, new)

# Alphabet comments
    _js_code    = []
    last_letter = ''

    for line in js_precode.splitlines():
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


for name, data, jsfile in [
    (
        'palcategories',
        CATEGOS,
        JS_PAL_CATEGOS_FILE,
    ),
    (
        'palsize',
        SIZES,
        JS_PAL_SIZES_FILE,
    )
]:
    js_precode = f"const {name} = {repr(data)};"

    jsfile.write_text(
        normalize_jscode(js_precode)
    )
