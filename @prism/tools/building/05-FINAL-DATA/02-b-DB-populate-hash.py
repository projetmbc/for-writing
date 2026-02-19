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

from yaml import (
    safe_load,
    dump as yaml_dump
)

# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

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


SQL_UPDATE_UNKEPT = '''
UPDATE hash
SET is_kept = 0
WHERE name = ?
  AND source = ?;
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


MAX_SIZE = YAML_CONFIGS['SEMANTIC']['MAX_SIZE']


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PRECISION = YAML_CONFIGS[TAG_METADATA]['PRECISION']


IGNORED_YAML = AUDIT_DIR / 'IGNORED.yaml'
IGNORED_YAML.touch()

with IGNORED_YAML.open(mode = 'r') as f:
    FINAL_IGNORED = yaml.safe_load(f)

UPDATE_IGNORED_YAML = False

IGNORED = set()

UPDATE_IGNORED_YAML = False

# Validatae and normalize the ''IGNORED'' dict.
for resrc, namedata in FINAL_IGNORED.items():
    for name, data in namedata.items():
        IGNORED.add((name, resrc))

        keys_used = list(data.keys())

        if keys_used == [TAG_WHY]:
            data[TAG_WHY] = data[TAG_WHY].strip()
            continue

        for needed_tag in [
            TAG_PAL,
            TAG_REL,
        ]:
            if not needed_tag in keys_used:
                log_raise_error(
                    context   = "'IGNORED.yaml' file",
                    desc      = f"Missing '{needed_tag}' key",
                    exception = ValueError,
                    xtra      = f"\nSee '{name}' [{resrc}]"
                )


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


# ------------------ #
# -- PALETTE HASH -- #
# ------------------ #

logging.info("DB - Hash - 'Just populate' (auto removeing big palettes)")

conn = sqlite3.connect(SQLITE_DB_FILE)


with sqlite3.connect(SQLITE_DB_FILE) as conn:
    for resrc_json in sorted(REPORT_DIR.glob("*.json")):
        src = resrc_json.stem

        if (
            src.startswith('KIND-')
            or
            src.startswith('AUDIT-')
        ):
            continue

        logging.info(f"(hash) Add '{resrc_json.relative_to(REPORT_DIR).stem}'")

        data = json_load(resrc_json.open())

        for name, infos in data.items():
            is_kept = 1
            paldef  = infos[TAG_RGB_COLS]

            if len(paldef) > MAX_SIZE:
                is_kept = 0

                logging.warning(
                    f"(hash) [{src}] Remove "
                    f"'{name} (size > {MAX_SIZE})' "
                     "(metadata retained for future reporting)"
                )

                if not name in FINAL_IGNORED.get(src, []):
                    if not src in FINAL_IGNORED:
                        FINAL_IGNORED[src] = dict()

                    UPDATE_IGNORED_YAML = True

                    FINAL_IGNORED[src][name] = {
                        TAG_WHY: f'Too big (size > {MAX_SIZE}).'
                    }

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


# --------------------- #
# -- REMOVE PALETTES -- #
# --------------------- #

if UPDATE_IGNORED_YAML:
    logging.info(
        f"JSON - Update '{IGNORED_YAML.relative_to(PROJ_DIR)}'"
    )

    IGNORED_YAML.write_text(
        yaml_dump(FINAL_IGNORED)
    )


# --------------------- #
# -- REMOVE PALETTES -- #
# --------------------- #

if not IGNORED:
    exit(0)

logging.info("DB - Hash - 'Remove palettes' (human choice)")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for name, source in IGNORED:

        cursor.execute(
            SQL_UPDATE_UNKEPT,
            (name, source)
        )
