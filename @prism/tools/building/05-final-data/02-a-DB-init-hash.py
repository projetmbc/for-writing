#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
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

SQL_TABLE_CREATE = '''
DROP TABLE IF EXISTS hash;
CREATE TABLE hash (
--
    pal_id INTEGER PRIMARY KEY,
    name   VARCHAR(30) NOT NULL,
    source VARCHAR(30) NOT NULL,
--
    is_kept  INTEGER DEFAULT 1,
    equal_to INTEGER REFERENCES hash(pal_id),
    kind     TEXT DEFAULT '',
--
    hash_normal  TEXT NOT NULL,
    hash_reverse TEXT NOT NULL
);
'''

SQL_TABLE_INSERT = '''
INSERT INTO hash (
--
    name,
    source,
--
    is_kept,
    kind,
--
    hash_normal,
    hash_reverse
) VALUES ({placeholders})
'''

SQL_SET_DEFAULT_EQUAL_TO = '''
UPDATE hash
SET equal_to = pal_id
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

if SQLITE_DB_FILE.is_file():
    SQLITE_DB_FILE.unlink()


MAX_SIZE = YAML_CONFIGS['SEMANTIC']['MAX_SIZE']


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PRECISION = YAML_CONFIGS[TAG_METADATA]['PRECISION']


IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'
IGNORED_YAML.touch()

with IGNORED_YAML.open(mode = 'r') as f:
    _IGNORED = yaml.safe_load(f)

IGNORED = set()

if not _IGNORED is None:
    for src, metadata in _IGNORED.items():
        for n in metadata:
            IGNORED.add((n, src))


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
    is_kept     : bool,
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
                is_kept, kind,
                hash_normal, hash_reverse
            )
        )

        conn.commit()

    except Exception:
        conn.close()

        log_raise_error(
            context   = "hash DB.",
            desc      = f"Insertion fails for '[{source}] {name}'.",
            exception = Exception,
        )


# ----------------------- #
# -- DB INITIALIZATION -- #
# ----------------------- #

logging.info("hash DB - 'Init table'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.executescript(SQL_TABLE_CREATE)


# ------------------ #
# -- PALETTE hash -- #
# ------------------ #

logging.info("hash DB - 'Populate' (ignored palette handling)")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    for resrc_json in sorted(REPORT_DIR.glob("*.json")):
        src = resrc_json.stem

        if (
            src.startswith('KIND-')
            or
            src.startswith('AUDIT-')
        ):
            continue

        logging.info(f"Add '{resrc_json.relative_to(REPORT_DIR).stem}'")

        data = json_load(resrc_json.open())

        for name, infos in data.items():
            if (name, src) in IGNORED:
                is_kept = 0

                logging.warning(
                    f"Ignore '{name}' [{src}] "
                     "(metadata retained for future reporting)"
                )

            else:
                is_kept = 1

            paldef = infos[TAG_RGB_COLS]

            if len(paldef) > MAX_SIZE:
                is_kept = 0

                logging.warning(
                    f"Remove '{name}' [{src}] - 'size > {MAX_SIZE}' "
                     "(metadata retained for future reporting)"
                )

            std_kind = get_std_kind(infos[TAG_KIND])

            hash_normal  = get_hash_pal(paldef)
            hash_reverse = get_hash_pal(paldef[::-1])

            dbadd_hashpals(
                conn         = conn,
                name         = name,
                source       = src,
                is_kept      = is_kept,
                kind         = std_kind,
                hash_normal  = hash_normal,
                hash_reverse = hash_reverse
            )

# Default value of ''equal_to'' attributes.
    cursor = conn.cursor()
    cursor.execute(SQL_SET_DEFAULT_EQUAL_TO)
