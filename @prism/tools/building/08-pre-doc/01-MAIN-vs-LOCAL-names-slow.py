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

SQL_GET_NAMES = '''
SELECT
    COALESCE(a.alias, h.name)
FROM hash h
LEFT JOIN alias a ON h.pal_id = a.pal_id
WHERE h.is_kept = 1;
'''


SQL_GET_METADATA = '''
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

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR = PROJ_DIR / "products"
RESRC_DIR = PROJ_DIR / "RESOURCES" / TAG_APRISM_LAST_MAIN


REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

REPORT_NAME_NEW_JSON     = REPORT_DIR / f"AUDIT-LOCMAIN-NAMES-NEW.json"
REPORT_NB_NEW_TXT        = REPORT_DIR / f"AUDIT-LOCMAIN-NAMES-NEW-NB.txt"
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


# --------------------- #
# -- LAST MAIN NAMES -- #
# --------------------- #

logging.info("Get 'Last Main Names'")

with (RESRC_DIR / 'palettes.json').open(mode = "r") as f:
    LAST_MAIN_NAMES = set(json_load(f))


# --------------------------- #
# -- CURRENT VERSION NAMES -- #
# --------------------------- #

logging.info("Get 'Current Version Names'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_GET_NAMES)

    CURRENT_NAMES = set(
        a
        for a, in cursor.fetchall()
    )


# ---------------------------- #
# -- FIND NEW/REMOVED NAMES -- #
# ---------------------------- #

logging.info("Get 'Current Version Names'")

NEW_NAMES     = lower_names_kept(CURRENT_NAMES, LAST_MAIN_NAMES)
REMOVED_NAMES = lower_names_kept(LAST_MAIN_NAMES, CURRENT_NAMES)


# ---------------------------- #
# -- FIND NEW/REMOVED NAMES -- #
# ---------------------------- #

for names, what in [
    (NEW_NAMES    , 'new' ),
    (REMOVED_NAMES, 'removed'),
]:
    if not names:
        logging.info(f"NAMES - 'No {what}'")

    else:
        nb = len(names)

        logging.info(f"NAMES - '{nb} {what}'")


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
            SQL_GET_METADATA,
            (n, n)
        )

        for alias, *ons in cursor.fetchall():
            report[alias] = list(ons)

REPORT_NAME_NEW_JSON.write_text(
    json_dumps(report)
)


# -------------------------- #
# -- SAVE NB OF NEW NAMES -- #
# -------------------------- #

REPORT_NB_NEW_TXT.write_text(
    f'{len(report)}\n'
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
###
# Complete with one of the following regarding new palettes.
#
#    1) ''<alias>: renamed''
#
#    (the palette identifier has changed, requiring a mapping
#    from the old name to the new one)
#
#    2) ''<alias>: ignored''
#
#    (the palette exists but is intentionally excluded, using
#    a fictive mapping from the name to itself)
#
#    3) ''<alias>: superseded''
#
#    (the palette no longer exists but has a direct equivalent,
#    requiring a mapping from the old name to the new one).
#
#    4) ''<upset>: subset''
#
#    (the palette is a subset of another).
###

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
