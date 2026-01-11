#!/usr/bin/env python3

exit(0)
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

QUERY_NO_KIND = """
SELECT
    name,
    source
FROM palettes
WHERE kind = ''
"""

QUERY_UPDATE_KIND = """
UPDATE palettes
SET kind = ?
WHERE name = ? AND source = ?"""


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT
AUDIT_DIR  = BUILD_TOOLS_DIR / TAG_AUDIT


FINAL_SQLITE_DB_FILE = AUDIT_DIR / "final-palettes.db"
HUMAN_KIND_YAML      = AUDIT_DIR / 'HUMAN-KIND.yaml'

if HUMAN_KIND_YAML.is_file():
    HUMAN_KINDS = yaml.safe_load(f)

    if HUMAN_KINDS is None:
        HUMAN_KINDS = dict()

else:
    HUMAN_KINDS = dict()


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

MISSING_KIND_JSON = REPORT_DIR / "AUDIT-MISSING-KIND.json"

MISSING_KINDS = []


# ------------------ #
# -- MISING KINDS -- #
# ------------------ #

logging.info(f"KINDS - 'Looking for missing ones'.")

with sqlite3.connect(FINAL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(QUERY_NO_KIND)

    for name, src in cursor.fetchall():
        namesrc = build_name_n_srcname(name, src)

        kind = HUMAN_KINDS.get(namesrc, '')

        if kind:
            cursor.executem(
                QUERY_UPDATE_KIND,
                [kind, name, src]
            )

        else:
            MISSING_KINDS.append(namesrc)


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(f"DATA cleaning - 'Update JSON audit file'.")

MISSING_KIND_JSON.write_text(
    json_dumps(MISSING_KINDS)
)


# ------------------------- #
# -- MISSING KINDS FOUND -- #
# ------------------------- #

if MISSING_KINDS:
    reslover = PROJ_DIR / "tools" / "lab" / "resolve" / "missing-kinds.py"

    log_raise_error(
        context   = "Missing kinds need NOAI resolution",
        desc      = "Palettes need to have at least one kind.",
        exception = ValueError,
        xtra      = (
            f'Use:\n---\nstreamlit run "{reslover}"\n---')
    )
