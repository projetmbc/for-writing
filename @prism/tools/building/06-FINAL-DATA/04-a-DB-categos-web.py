#!/usr/bin/env python3

DIRECT_DEBUG = False

# -- DEBUG - ON -- #
# from rich import print
# DIRECT_DEBUG = True
# -- DEBUG - OFF -- #

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


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

# WARNING! Since name conflicts are resolved by the previous script,
# we can work with palette names and srcs directly.

SQL_GET_CATEGO = '''
SELECT name, source, catego
FROM hash
WHERE LOWER(name) = '{lowername}'
  AND is_kept = 1
'''


SQL_UPDATE_CATEGO = '''
UPDATE hash
SET catego = '{catego}'
WHERE name = '{name}'
  AND source = '{source}'
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_std_catego(catego):
    _CATEGO = sorted(
        list(
            set(
                k.strip()
                for k in catego.split(',')
                if k.strip()
            )
        )
    )

    return ','.join(_CATEGO)


def join_categos(catego_1, catego_2):
    return get_std_catego(f'{catego_1}, {catego_2}')


# ----------------- #
# -- WEB CATEGOS -- #
# ----------------- #

logging.info("DB - Web catego - 'Looking for data'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for categojson in REPORT_DIR.glob('CATEGO-*.json'):
        src = categojson.stem.split('-')[1]

        logging.info(f"DB - Web catego - '{src}' data")

        with categojson.open('r') as f:
            data = json_load(f)

        for name, catego in data.items():
            cursor.execute(
                SQL_GET_CATEGO.format(
                    lowername = name.lower(),
                )
            )

            for name, src, dbcatego, in cursor.fetchall():
                if DIRECT_DEBUG:
                    print(f'--- {name} [{src}]')
                    print(f"{catego   = }")
                    print(f"{dbcatego = }")

                catego = join_categos(catego, dbcatego)

                if DIRECT_DEBUG:
                    input(f"{catego   = }")

            query = SQL_UPDATE_CATEGO.format(
                name   = name,
                catego = catego,
                source = src
            )

            cursor.execute(query)
