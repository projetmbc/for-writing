#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
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

from yaml import safe_load


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

# WARNING! Since name conflicts are resolved by the previous script,
# we can work with palette names and sources directly.

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

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

HUMAN_CATEGO_YAML = AUDIT_DIR / 'HUMAN-CATEGO.yaml'


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


# ----------------------- #
# -- GET HUMAN CATEGOS -- #
# ----------------------- #

logging.info("DB - Human catego - 'Get data'")

if HUMAN_CATEGO_YAML.is_file():
    with HUMAN_CATEGO_YAML.open('r') as f:
        XTRA_CATEGOS = safe_load(f)

    if XTRA_CATEGOS is None:
        XTRA_CATEGOS = dict()

else:
    XTRA_CATEGOS = dict()


# ------------------- #
# -- APPLY CATEGOS -- #
# ------------------- #

logging.info("DB - Human catego - 'Apply choices'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for src, namecategos in XTRA_CATEGOS.items():
        for name, catego in namecategos.items():
            query = SQL_UPDATE_CATEGO.format(
                name   = name,
                catego = get_std_catego(catego),
                source = src
            )

            cursor.execute(query)

            if cursor.rowcount == 0:
                log_raise_error(
                    context   = "Apply human catego",
                    desc      = f"Unknown palette '{name}' [{src}]",
                    exception = ValueError,
                )
