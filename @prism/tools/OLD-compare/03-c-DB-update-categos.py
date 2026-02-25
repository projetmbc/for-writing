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

from yaml import (
    safe_load,
    dump as yaml_dump
)


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


SQL_GET_NO_CATEGO = '''
SELECT
    h.name,
    h.source
FROM hash h
WHERE h.catego = ''
  AND h.is_kept = 1;
'''


SQL_RESOLVE_EMPTY_CATEGO = '''
SELECT
    p1.name,
    p1.source,
    (
        SELECT GROUP_CONCAT(p2.catego, ',')
        FROM hash p2
        WHERE p2.catego != ''
          AND (
              p2.equal_to = p1.pal_id
              OR
              EXISTS (
                  SELECT 1 FROM mirror m
                  WHERE (
                      m.cand_pal_id_1 = p1.pal_id
                      AND
                      m.cand_pal_id_2 = p2.pal_id
                  ) OR (
                      m.cand_pal_id_1 = p2.pal_id
                      AND
                      m.cand_pal_id_2 = p1.pal_id
                  )
              )
          )
    ) AS all_CATEGOs
FROM hash p1
WHERE p1.catego = ''
  AND p1.is_kept = 1;
'''


SQL_GET_CAMELCASE_NAMES = '''
SELECT
    name,
    source
FROM hash h
WHERE name = '{name}' COLLATE NOCASE
  AND source = '{source}' COLLATE NOCASE;
'''


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

MISSING_CATEGO_JSON = REPORT_DIR / "AUDIT-MISSING-CATEGO.json"

HUMAN_CATEGO_YAML = AUDIT_DIR / 'HUMAN-CATEGO.yaml'

MISSING_CATEGOS = []


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
# -- GET EXTRA CATEGOS -- #
# ----------------------- #

logging.info("DB - Catego - 'Get WEB data'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for jsonfile in REPORT_DIR.glob('CATEGO-*.json'):
        with jsonfile.open('r') as f:
            xtra_categos = json_load(f)

        for uid, catego in xtra_categos.items():
            name, src = extract_name_n_srcname(uid)

            query = SQL_GET_CAMELCASE_NAMES.format(
                name   = name,
                source = src
            )

            cursor.execute(query)

            std_data = [
                (n, s)
                for n, s, in cursor.fetchall()
            ]

            if len(std_data) == 0:
                log_raise_error(
                    context   = "WEB categos",
                    desc      = f"Unknown palette name '{name}' [{src}]",
                    exception = ValueError,
                )

            if len(std_data) > 1:
                log_raise_error(
                    context = "WEB categos",
                    desc    = (
                         "Too much palette names and/or sources "
                        f"for '{name}' [{src}] (why?)"
                    ),
                    exception = ValueError,
                )

            name, src = std_data[0]

            if not src in XTRA_CATEGOS:
                XTRA_CATEGOS[src] = dict()

            XTRA_CATEGOS[src][name] = catego

            # else:
            #     XTRA_CATEGOS[src][name] += f',{catego}'


# ----------------------- #
# -- GET HUMAN CATEGOS -- #
# ----------------------- #

logging.info("DB - Catego - 'Get human data'")

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

logging.info("DB - Catego - 'Add xtra data'")

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


# -------------------------- #
# -- DB CATEGO RESOLUTION -- #
# -------------------------- #

logging.info("DB - Catego - 'Resolve missing data'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_RESOLVE_EMPTY_CATEGO)

    for name, src, catego in cursor.fetchall():
# No matches found.
        if catego is None:
            continue

# At least one match found.
        catego = get_std_catego(catego)

        logging.info(f"'{name}' [{src}] is '{catego}'")

        query = SQL_UPDATE_CATEGO.format(
            name   = name,
            catego = catego,
            source = src
        )

        cursor.execute(query)


# --------------------- #
# -- MISSING CATEGOS -- #
# --------------------- #

logging.info("DB - Catego - 'Unresolved missing categos?'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_GET_NO_CATEGO)

    MISSING_CATEGOS.extend([
        list(x) for x in cursor.fetchall()
    ])


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(
    f"DB - Catego - Update '{MISSING_CATEGO_JSON.relative_to(PROJ_DIR)}'"
)

MISSING_CATEGO_JSON.write_text(
    json_dumps(MISSING_CATEGOS)
)


# ------------------------- #
# -- MISSING categoS FOUND -- #
# ------------------------- #

if not MISSING_CATEGOS:
    logging.info(
        f"DB - Catego - 'No problem!'"
    )

    exit(0)


nb = len(MISSING_CATEGOS)

plurial = '' if nb == 1 else 's'

reslover = PROJ_DIR / "tools" / "lab" / "resolve" / "missing-categos.py"

log_raise_error(
    context   = f"{nb} missing catego{plurial} need NOAI resolution",
    desc      = "Palettes need to have at least one catego.",
    exception = ValueError,
    xtra      = (
        f'Use:\n---\nstreamlit run "{reslover}"\n---'
    )
)
