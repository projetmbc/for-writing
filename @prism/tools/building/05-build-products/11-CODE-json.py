exit(1)


#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
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


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

VERSION = (BUILD_TOOLS_DIR / 'VERSION.txt').read_text()

CREDITS = (BUILD_TOOLS_DIR / 'CREDITS.txt').read_text()
CREDITS = CREDITS.strip()
CREDITS = CREDITS.format(VERSION = VERSION)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

QUERY_ALL_PALS = """
SELECT
    uid,
    name
FROM palettes
"""


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR     = PROJ_DIR / "products"


PROD_JSON_DIR = PRODS_DIR / "json"

PROD_JSON_DIR.mkdir(
    parents  = True,
    exist_ok = True,
)

PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"
PAL_JSON_FILE.touch()

PAL_JSON_CREDITS_MD = PROD_JSON_DIR / "CREDITS.md"


REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT
AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT


SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ------------------ #
# -- GET PAL DEFS -- #
# ------------------ #

uid_2_pal = dict()

for p in REPORT_DIR.glob('*.json'):
    tokeep = True

    for prefix in [
        'AUDIT',
        'KIND',
    ]:
        if p.name.startswith(f'{prefix}-'):
            tokeep = False

            break

    if not tokeep:
        continue

    src = p.stem

    logging.info(f"Get '{src}' palette defs.")

    with p.open('r') as f:
        paldata = json_load(f)

    for name, data in paldata.items():
        uid = build_name_n_srcname(name, src)
        uid = uid.lower()

        uid_2_pal[uid] = data[TAG_RGB_COLS]


# ------------------- #
# -- ALL PALS DICT -- #
# ------------------- #

logging.info(f"Build 'palette defs'.")

allpals = dict()

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(QUERY_ALL_PALS)

    for uid, name in cursor.fetchall():
        allpals[name] = uid_2_pal[uid]


# -------------------------- #
# -- ALL PALS JSON UPDATE -- #
# -------------------------- #

logging.info(f"Update '{PAL_JSON_FILE.relative_to(PROJ_DIR)}'.")

PAL_JSON_FILE.write_text(
    clean_pal_json(
        json_dumps(allpals)
    )
)


# ---------------------------------- #
# -- MD CREDITS FOR THE JSON FILE -- #
# ---------------------------------- #

logging.info(f"Update '{PAL_JSON_CREDITS_MD.relative_to(PROJ_DIR)}'.")

# warning::
#     Credits in the JSON files via an extra key just complicates
#     their future use (this is a bad practice).

md_credtits = CREDITS + '\n'
md_credtits = md_credtits.replace("''", "`")
md_credtits = re.sub(
    r'(https?://[^\s]+)',
    r'[\1](\1)',
    md_credtits
)

PAL_JSON_CREDITS_MD.touch()
PAL_JSON_CREDITS_MD.write_text(md_credtits)
