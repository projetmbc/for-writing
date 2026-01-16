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

SQL_DROP = 'DROP TABLE IF EXISTS palettes;'

SQL_CREATE = '''
CREATE TABLE palettes (
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


SQL_INSERT_WITHOUT_EQUAL_TO = '''
INSERT INTO palettes (
--
    priority,
--
    name,
    source,
    kind,
--
    hash_normal,
    hash_reverse
) VALUES ({placeholders})
'''


SQL_SET_DEFAULT_EQUAL_TO = '''
UPDATE palettes
SET equal_to = id
'''


SQL_SET_IGNORED = '''
UPDATE palettes
SET is_kept = 0
WHERE name = '{name}' AND source = '{source}';
'''


SQL_RENAME = '''
UPDATE palettes
SET name = '{newname}'
WHERE name = '{name}' AND source = '{source}';
'''


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


PRIORITY = YAML_CONFIGS['PRIORITY']


RENAMED_YAML = AUDIT_DIR / 'RENAMED.yaml'
RENAMED_YAML.touch()

with RENAMED_YAML.open(mode = 'r') as f:
    _RENAMED = yaml.safe_load(f)

RENAMED = (
    dict()
    if _RENAMED is None else
    builde_new_palnames(_RENAMED)
)


IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'

with IGNORED_YAML.open(mode = 'r') as f:
    _IGNORED = yaml.safe_load(f)

IGNORED = set()

if not _IGNORED is None:
    for src, names in _IGNORED.items():
        for n in names:
            IGNORED.add((n, src))


# ------------------ #
# -- CONSTANTS #3 -- #
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

    palstr = json_dumps(paldef)
    palstr = clean_pal_json(palstr)

    hashcode = hashlib.md5(palstr.encode()).hexdigest()

    return hashcode


# Automatic qualitative categorization will be performed later.
def get_std_kind(kind: str) -> str:
    kind = kind.strip()

    if not kind:
        return kind

    _stdkind = set()

    _xtra_pb_kinds = []

    for k in kind.split(','):
        _k = k

        k = k.strip()
        k = KIND_ALIAS.get(k, '')

        if (
            not k
            and
            not _k in _xtra_pb_kinds
        ):
            _xtra_pb_kinds.append(_k)

        _stdkind.add(k)

    std_kind = ','.join(sorted(_stdkind))

    if not std_kind and kind or _xtra_pb_kinds:
        xtra = ''

        if _xtra_pb_kinds:
            plurial = '' if len(_xtra_pb_kinds) == 1 else 's'

            tab = '\n  + '

            xtra_pb_kinds = tab.join([
                f"'{k}'" for k in _xtra_pb_kinds
            ])

            xtra = (
                f' See the folowing kind{plurial}.'
                f'{tab}{xtra_pb_kinds}'
            )

        log_raise_error(
            context   = "Palette SQLite DB creation",
            desc      = f"Unmanaged palette kind '{kind}'.",
            exception = ValueError,
            xtra      = xtra
        )

    return std_kind


def dbadd_palette(
    conn,
    priority    : int,
    name        : str,
    source      : str,
    kind        : str,
    hash_normal : str,
    hash_reverse: str
) -> None:
    placeholders = ['?']*(len(locals()) - 1)
    placeholders = ','.join(placeholders)

    if not source:
        print(name)
        TODO

    try:
        cursor = conn.cursor()

        cursor.execute(
            SQL_INSERT_WITHOUT_EQUAL_TO.format(
                placeholders = placeholders
            ), (
                # --
                priority,
                # --
                name,
                source,
                # --
                kind,
                # --
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

logging.info(f"SQLite DB - 'Init table'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_DROP)
    cursor.execute(SQL_CREATE)


# ----------------------- #
# -- PALETTES METADATA -- #
# ----------------------- #

logging.info(f"SQLite DB - 'Populate with hard data'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    for resrc_json in REPORT_DIR.glob("*.json"):
        src = resrc_json.stem

        if (
            src.startswith('KIND-')
            or
            src.startswith('AUDIT-')
        ):
            continue

        data = json_load(resrc_json.open())

        for name, infos in data.items():
            kind   = infos[TAG_KIND]
            paldef = infos[TAG_RGB_COLS]

            std_kind = get_std_kind(kind)

            hash_normal  = get_palhash(paldef)
            hash_reverse = get_palhash(paldef[::-1])

            dbadd_palette(
                conn         = conn,
                priority     = PRIORITY[src],
                name         = name,
                source       = src,
                kind         = std_kind,
                hash_normal  = hash_normal,
                hash_reverse = hash_reverse
            )

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
