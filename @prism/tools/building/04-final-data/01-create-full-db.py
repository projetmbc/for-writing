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


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


FULL_SQLITE_DB_FILE = REPORT_DIR / "full-palettes.db"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PRECISION = YAML_CONFIGS[TAG_METADATA]['PRECISION']


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


# Automatic qualitative categorization will be performed later.
def get_std_kind(kind: str) -> str:
    _stdkind = set()

    for k in kind.split(','):
        k = k.strip()
        k = KIND_ALIAS.get(k, '')

        _stdkind.add(k)

    stdkind = '|'.join(sorted(_stdkind))

    if not stdkind and kind:
        log_raise_error(
            context   = "Palette SQLite DB creation",
            desc      = f"Unmanaged palette kind '{kind}'.",
            exception = ValueError,
        )

    return stdkind


def dbadd_palette(
    conn,
    name        : str,
    source      : str,
    kind        : str,
    hash_normal : str,
    hash_reverse: str
) -> None:
    placeholders = ['?']*(len(locals()) - 1)
    placeholders = ",".join(placeholders)

    if not source:
        print(name)
        TODO

    try:
        cursor = conn.cursor()

        cursor.execute(
            f'''
INSERT INTO palettes (
    name,
    source,
    kind,
    hash_normal,
    hash_reverse
) VALUES ({placeholders})
            ''',
            (
                name,
                source,
                kind,
                hash_normal,
                hash_reverse
            )
        )

        conn.commit()

    except Exception:
        conn.close()

        log_raise_error(
            context   = "SQLite database.",
            desc      = f"Insertion fails for '{name}'.",
            exception = Exception,
        )


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info(f"Full SQLite DB - 'Init table'.")

with sqlite3.connect(FULL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS palettes;')
    cursor.execute('''
CREATE TABLE palettes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    source       TEXT NOT NULL,
    kind         TEXT NOT NULL,
    hash_normal  TEXT NOT NULL,
    hash_reverse TEXT NOT NULL
)
    ''')


# ----------------------- #
# -- PALETTES METADATA -- #
# ----------------------- #

logging.info(f"Full SQLite DB - 'Populate table'.")

with sqlite3.connect(FULL_SQLITE_DB_FILE) as conn:
    for resrc_json in REPORT_DIR.glob("*.json"):
        projname = resrc_json.stem

        if projname.startswith('KIND-'):
            continue

        data = json_load(resrc_json.open())

        for name, infos in data.items():
            kind   = infos[TAG_KIND]
            paldef = infos[TAG_RGB_COLS]

            stdkind = get_std_kind(kind)

            hash_normal  = get_palhash(paldef)
            hash_reverse = get_palhash(paldef[::-1])

            dbadd_palette(
                conn         = conn,
                name         = name,
                source       = projname,
                kind         = stdkind,
                hash_normal  = hash_normal,
                hash_reverse = hash_reverse
            )


# ------------------------ #
# -- NOTHING LEFT TO DO -- #
# ------------------------ #

logging.info(
     "Full SQLite DB - File "
    f"'{FULL_SQLITE_DB_FILE.relative_to(PROJ_DIR)}' "
     "build."
)
