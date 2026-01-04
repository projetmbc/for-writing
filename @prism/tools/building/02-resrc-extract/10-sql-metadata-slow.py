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

import hashlib
import sqlite3


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


SQLITE_DB_FILE = REPORT_DIR / "palettes.db"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PRECISION = YAML_CONFIG['PRECISION']


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_palhash(palette: PaletteCols) -> str:
    paldef = [
        [round(v, PRECISION) for v in c]
        for c in palette
    ]

    palstr   = json_dumps(paldef, sort_keys = True)
    hashcode = hashlib.md5(palstr.encode()).hexdigest()

    return hashcode


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info(f"Building SQLite DB.")

conn = sqlite3.connect(SQLITE_DB_FILE)

cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS palettes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stdname TEXT NOT NULL,
    projname TEXT NOT NULL,
    hash_normal TEXT NOT NULL,
    hash_reverse TEXT NOT NULL
)
''')

conn.commit()

for resrc_json in REPORT_DIR.glob("RESRC-PALS-*.json"):
    projname = resrc_json.stem.split('-')
    projname = projname[2:]
    projname = '-'.join(projname)

    data = json_load(resrc_json.open())

    for stdname, infos in data.items():
        paldef = infos[TAG_RGB_COLS]

        hash_normal  = get_palhash(paldef)
        hash_reverse = get_palhash(paldef[::-1])

        try:
            cursor = conn.cursor()
            cursor.execute(
                '''
INSERT INTO palettes (stdname, projname, hash_normal, hash_reverse)
VALUES (?, ?, ?, ?)
                ''',
                (
                    stdname,
                    projname,
                    hash_normal,
                    hash_reverse
                )
            )

            conn.commit()

        except Exception:
            conn.close()

            log_raise_error(
                context   = "SQLite database.",
                desc      = f"Insertion fails for '{stdname}'.",
                exception = Exception,
            )

conn.close()

logging.info(
    f"SQLite DB '{SQLITE_DB_FILE.relative_to(PROJ_DIR)}' build."
)
