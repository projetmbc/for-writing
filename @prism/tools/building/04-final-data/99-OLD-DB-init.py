IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'

with IGNORED_YAML.open(mode = 'r') as f:
    _IGNORED = yaml.safe_load(f)

IGNORED = set()

if not _IGNORED is None:
    for src, names in _IGNORED.items():
        for n in names:
            IGNORED.add((n, src))









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


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #







exit(1)











SQL_TABLE_CREATE = '''
DROP TABLE IF EXISTS same_pals;
CREATE TABLE same_pals (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    pal_id_kept    INTEGER NOT NULL,
    pal_id_ignored INTEGER NOT NULL
)
'''

SQL_TABLE_INSERT = '''
INSERT INTO same_pals (
    pal_id_kept,
    pal_id_ignored
) VALUES ({placeholders})
'''

SQL_GET_PALID = """
SELECT
    p.pal_id
FROM hash_pals p
WHERE p.name = ?
  AND p.source = ?
"""


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT


SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'
IGNORED_YAML.touch()

with IGNORED_YAML.open(mode = 'r') as f:
    _IGNORED = yaml.safe_load(f)

IGNORED = set()

if not _IGNORED is None:
    for src, names in _IGNORED.items():
        for n in names:
            IGNORED.add((n, src))


print(IGNORED)
exit(1)



# -------------- #
# -- TOOLS #2 -- #
# -------------- #

def dbadd_aliaspals(
    conn,
    pal_id: int,
    alias : str
) -> None:
    placeholders = ['?']*(len(locals()) - 1)
    placeholders = ','.join(placeholders)

    try:
        cursor = conn.cursor()

        cursor.execute(
            SQL_TABLE_INSERT.format(
                placeholders = placeholders
            ),
            (
                pal_id,
                alias
            )
        )

        conn.commit()

    except Exception:
        conn.close()

        log_raise_error(
            context   = "Alias DB.",
            desc      = f"Insertion fails for '{alias}'.",
            exception = Exception,
        )


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info(f"Alias DB - 'Init table'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.executescript(SQL_TABLE_CREATE)


if not RENAMED:
    logging.info(f"Alias DB - No alias.")

    exit(0)


# ----------- #
# -- ALIAS -- #
# ----------- #

logging.info(f"Alias DB - 'Populate'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for nsn, alias in get_pal_alias(RENAMED).items():
        cursor.execute(
            SQL_GET_PALID,
            (*nsn,)
        )

        pal_id = cursor.fetchall()[0][0]

        dbadd_aliaspals(
            conn   = conn,
            pal_id = pal_id,
            alias  = alias,
        )


# -- DEBUG - ON -- #
# print(RENAMED)
# print(IGNORED)
# print(PRIORITY)
# exit(1)
# -- DEBUG - OFF -- #


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_hash_pal(palette: PaletteCols) -> str:
    paldef = [
        [round(v, PRECISION) for v in c]
        for c in palette
    ]

    palstr = json_dumps(paldef)
    palstr = clean_pal_json(palstr)

    hashcode = hashlib.md5(palstr.encode()).hexdigest()

    return hashcode







SQL_CREATE_RAW_TABLE = '''

CREATE TABLE hashpals (
    mirror_of INTEGER,
    priority  INTEGER,
)
'''

SQL_CREATE_EQUAL_TABLE = '''
CREATE TABLE equal_pals (
--
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    is_kept   INTEGER DEFAULT 1,
    equal_to  INTEGER,
    mirror_of INTEGER,
    priority  INTEGER,
--
    name   TEXT NOT NULL,
    source TEXT NOT NULL,
    kind   TEXT NOT NULL,
--
    hash_normal  TEXT NOT NULL,
    hash_reverse TEXT NOT NULL
)
'''





SQL_SET_DEFAULT_EQUAL_TO = '''
UPDATE hashpals
SET equal_to = id
'''


SQL_SET_IGNORED = '''
UPDATE hashpals
SET is_kept = 0
WHERE name = '{name}' AND source = '{source}';
'''


SQL_RENAME = '''
UPDATE hashpals
SET name = '{newname}'
WHERE name = '{name}' AND source = '{source}';
'''




# ----------- #
# -- TOOLS -- #
# ----------- #

# Automatic qualitative categorization will be performed later.






# Default value of ''equal_to'' attributes.
    cursor = conn.cursor()
    cursor.execute(SQL_SET_DEFAULT_EQUAL_TO)

# Value of ''ignored'' for ignored pals.
    for (name, src) in IGNORED:
        query = SQL_SET_IGNORED.format(
            name    = name,
            source  = src,
        )

        cursor.execute(query)

# Renaming.
    for (name, src), newname in RENAMED.items():
        query = SQL_RENAME.format(
            name    = name,
            source  = src,
            newname = newname,
        )

        cursor.execute(query)


# ----------------------- #
# -- PALETTES METADATA -- #
# ----------------------- #

logging.info(f"SQLite DB - Store alias for reports.")

alias = {}

for nsn, aprism_name in RENAMED.items():
    alias[aprism_name] = list(nsn)

ALIAS_JSON_FILE.write_text(yaml_dump(alias))

exit(1)
