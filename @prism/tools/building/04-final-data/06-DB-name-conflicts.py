#!/usr/bin/env python3

# -- DEBUG - ON -- #
# from rich import print
# -- DEBUG - OFF -- #

from typing import Iterator


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

from itertools import batched


# ----------------- #
# -- SQL QUERIES -- #
# ----------------- #

SQL_NAME_CONFLICT = '''
SELECT
    COALESCE(a1.alias, p1.name),
    p1.name, p1.source,
    COALESCE(a2.alias, p2.name),
    p2.name, p2.source
FROM hash p1
LEFT JOIN alias a1 ON p1.pal_id = a1.pal_id
JOIN hash p2 ON
    LOWER(COALESCE(a1.alias, p1.name))
    =
    LOWER(COALESCE(a2.alias, p2.name))
LEFT JOIN alias a2 ON p2.pal_id = a2.pal_id
WHERE p1.is_kept = 1
  AND p2.is_kept = 1
  AND p1.hash_normal != p2.hash_normal
  AND p1.hash_normal != p2.hash_reverse
  AND p1.pal_id < p2.pal_id
'''


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

AUDIT_DIR = BUILD_TOOLS_DIR / TAG_AUDIT

SQLITE_DB_FILE = AUDIT_DIR / "palettes.db"


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT

NAME_CONFLICT_JSON = REPORT_DIR / f"AUDIT-NAME-CONFLICT.json"

NAME_CONFLICT_IDS   = set()
AUDIT_NAME_CONFLICT = defaultdict(set)


# --------------------- #
# -- NAME CONFLICTS? -- #
# --------------------- #

logging.info("Analyze data - 'Look for lower case name conflicts'")

with sqlite3.connect(SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(SQL_NAME_CONFLICT)


    for data in set(cursor.fetchall()):
        for d in batched(data, 3):
            AUDIT_NAME_CONFLICT[d[0].lower()].add(d)


AUDIT_NAME_CONFLICT = {
    k: list(v)
    for k, v in AUDIT_NAME_CONFLICT.items()
}


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

# NOTE. Error will be indicated after updating the JSON file used
# by the Python helper tool.

logging.info(f"Update '{NAME_CONFLICT_JSON.relative_to(PROJ_DIR)}'")

NAME_CONFLICT_JSON.write_text(
    json_dumps(AUDIT_NAME_CONFLICT)
)


# -------------------------------------- #
# -- NAME CONFLICTS MUST BE RESOLVED! -- #
# -------------------------------------- #

if AUDIT_NAME_CONFLICT:
    reslover = PROJ_DIR / "tools" / "lab" / "resolve" / "name-conflicts.py"

    log_raise_error(
        context   = "Conflicts need NOAI resolution",
        desc      = "Same name for different and not mirror palettes.",
        exception = ValueError,
        xtra      = f'Use:\n---\nstreamlit run "{reslover}"\n---'
    )
