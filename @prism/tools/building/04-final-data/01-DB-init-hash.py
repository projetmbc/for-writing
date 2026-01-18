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

SQL_TABLE_CREATE = '''
DROP TABLE IF EXISTS hash;
CREATE TABLE hash (
--
    pal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name   VARCHAR(30) NOT NULL,
    source VARCHAR(30) NOT NULL,
--
    is_kept  INTEGER DEFAULT 1,
    kind     VARCHAR(60) DEFAULT '',
--
    hash_normal  VARCHAR(60) NOT NULL,
    hash_reverse VARCHAR(60) NOT NULL
)
'''

SQL_TABLE_INSERT = '''
INSERT INTO hash (
--
    name,
    source,
--
    kind,
--
    hash_normal,
    hash_reverse
) VALUES ({placeholders})
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

if SQLITE_DB_FILE.is_file():
    SQLITE_DB_FILE.unlink()


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PRECISION = YAML_CONFIGS[TAG_METADATA]['PRECISION']


# -------------- #
# -- TOOLS #1 -- #
# -------------- #

def get_hash_pal(palette: PaletteCols) -> str:
    paldef = [
        [round(v, PRECISION) for v in c]
        for c in palette
    ]

    palstr = json_dumps(paldef)
    palstr = clean_pal_json(palstr)

    hashcode = hashlib.md5(palstr.encode()).hexdigest()

    return hashcode


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


# -------------- #
# -- TOOLS #2 -- #
# -------------- #

def dbadd_hashpals(
    conn,
    name        : str,
    source      : str,
    kind        : str,
    hash_normal : str,
    hash_reverse: str
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
                name, source,
                kind,
                hash_normal, hash_reverse
            )
        )

        conn.commit()

    except Exception:
        conn.close()

        log_raise_error(
            context   = "Hash DB.",
            desc      = f"Insertion fails for '[{source}] {name}'.",
            exception = Exception,
        )


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info(f"Hash DB - 'Init table'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.executescript(SQL_TABLE_CREATE)


# ------------------ #
# -- PALETTE HASH -- #
# ------------------ #

logging.info(f"Hash DB - 'Populate'.")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    for resrc_json in REPORT_DIR.glob("*.json"):
        src = resrc_json.stem

        if (
            src.startswith('KIND-')
            or
            src.startswith('AUDIT-')
        ):
            continue

        logging.info(f"Add '{resrc_json.relative_to(REPORT_DIR).stem}'.")

        data = json_load(resrc_json.open())

        for name, infos in data.items():
            kind   = infos[TAG_KIND]
            paldef = infos[TAG_RGB_COLS]

            std_kind = get_std_kind(kind)

            hash_normal  = get_hash_pal(paldef)
            hash_reverse = get_hash_pal(paldef[::-1])

            dbadd_hashpals(
                conn         = conn,
                name         = name,
                source       = src,
                kind         = std_kind,
                hash_normal  = hash_normal,
                hash_reverse = hash_reverse
            )
