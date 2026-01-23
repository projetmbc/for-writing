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

SQL_GET_ORIGINAL_INFO = '''
SELECT
    COALESCE(a.alias, h.name),
    h.name,
    h.source
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1
  AND (h.name = ? OR a.alias = ?);
'''


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != '@prism'):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR = PROJ_DIR / "products"


REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

REPORT_NAME_NEW_JSON     = REPORT_DIR / f"AUDIT-LOCMAIN-NAMES-NEW.json"
REPORT_NAME_REMOVED_JSON = REPORT_DIR / f"AUDIT-LOCMAIN-NAMES-REMOVED.json"
REPORT_LAST_MAIN_JSON    = REPORT_DIR / f"AUDIT-LAST-MAIN.json"

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"

WHY_REMOVED_YAML = AUDIT_DIR / f"LOCMAIN-REMOVED-EXPLAINED.yaml"
WHY_REMOVED_YAML.touch()

with WHY_REMOVED_YAML.open("r") as f:
    WHY_REMOVED = safe_load(f)

if WHY_REMOVED is None:
    WHY_REMOVED = dict()


# ----------- #
# -- TOOLS -- #
# ----------- #

def lower_names_kept(
    main_set: set[str],
    alt_set : set[str]
) -> list[str]:
    lower_2_std = {
        x.lower(): x
        for x in main_set
    }

    _main_set = set(x.lower() for x in main_set)
    _alt_set  = set(x.lower() for x in alt_set)

    return sorted(
        lower_2_std[x]
        for x in _main_set - _alt_set
    )


# ------------------- #
# -- LOCAL VERSION -- #
# ------------------- #

logging.info("MAIN/LOCAL - Get 'last local' version")

JSON_PROD_FILE = PROJ_DIR / "products" / "json" / "palettes.json"

with JSON_PROD_FILE.open(mode = "r") as f:
    LOCAL_PALS = json_load(f)


# ------------------------- #
# -- MAIN ONLINE VERSION -- #
# ------------------------- #

logging.info("MAIN/LOCAL - Get 'main online' version")

url = (
    "https://raw.githubusercontent.com/"
    "projetmbc/for-writing/main/"
    "%40prism/products/json/palettes.json"
)

response = requests.get(url)
response.raise_for_status()

MAIN_PALS = response.json()


# ------------------------- #
# -- NEW NAMES JSONIFIED -- #
# ------------------------- #

logging.info(
    f"Update '{REPORT_LAST_MAIN_JSON.relative_to(PROJ_DIR)}'"
)

REPORT_LAST_MAIN_JSON.write_text(
    json_dumps(MAIN_PALS)
)


# ----------------------- #
# -- NEW/REMOVED NAMES -- #
# ----------------------- #

NEW_NAMES     = lower_names_kept(LOCAL_PALS, MAIN_PALS)
REMOVED_NAMES = lower_names_kept(MAIN_PALS, LOCAL_PALS)

for names, what, xtra in [
    (NEW_NAMES    , 'new'    , '(cf. doc)'   ),
    (REMOVED_NAMES, 'removed', '(explanations needed)'),
]:
    if not names:
        logging.info(f"NAMES - 'No {what}'")

    else:
        nb   = len(names)
        xtra = f' {xtra}'

        logging.info(f"NAMES - '{nb} {what}'{xtra}")

# -- DEBUG - ON -- #
# print(NEW_NAMES)
# print(REMOVED_NAMES)
# exit()
# -- DEBUG - OFF -- #


# ------------------------- #
# -- NEW NAMES JSONIFIED -- #
# ------------------------- #

logging.info(
    f"Update '{REPORT_NAME_NEW_JSON.relative_to(PROJ_DIR)}'"
)

report = dict()

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for n in NEW_NAMES:
        cursor.execute(
            SQL_GET_ORIGINAL_INFO,
            (n, n)
        )

        for alias, *ons in cursor.fetchall():
            report[alias] = list(ons)

REPORT_NAME_NEW_JSON.write_text(
    json_dumps(report)
)


# ----------------------------- #
# -- REMOVED NAMES YAMLIFIED -- #
# ----------------------------- #

logging.info(
    f"Update '{WHY_REMOVED_YAML.relative_to(PROJ_DIR)}'"
)

for n in REMOVED_NAMES:
    if n in WHY_REMOVED:
        continue

    WHY_REMOVED[n] = None

yaml_code = yaml_dump(WHY_REMOVED)
yaml_code = f'''
# Complete with one of the following regarding new palettes.
#
#    1) ''<alias>: renamed''
#
#    (the palette identifier has changed, requiring a mapping
#    from the old name to the new one)
#
#    2) ''<alias>: ignored''
#
#    (the palette exists but is intentionally excluded)
#
#    3) ''<alias>: superseded''
#
#    (the palette no longer exists but has a direct equivalent).

{yaml_code}
'''.lstrip()

WHY_REMOVED_YAML.write_text(yaml_code)


# -------------------------------------- #
# -- MISSING WHY-REMOVED EXPLANATIONS -- #
# -------------------------------------- #

if None in WHY_REMOVED.values():
    nb = len([
        x
        for x in WHY_REMOVED.values()
        if x is None
    ])

    plurial = '' if nb == 1 else 's'

    log_raise_error(
        context = (
            f"{nb} missing explanation{plurial} about "
             "removed names need NOAI resolution"
        ),
        desc = (
            "Removed names must be documented with a "
            "specific reason."
        ),
        exception = ValueError,
        xtra      = f"Open '{WHY_REMOVED_YAML}'"
    )
