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

from yaml import (
    safe_load,
    dump as yaml_dump
)

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
    with HUMAN_KIND_YAML.open('r') as f:
        YAML_STORED_KINDS = safe_load(f)

    if YAML_STORED_KINDS is None:
        YAML_STORED_KINDS = dict()

else:
    HUMAN_KIND_YAML.touch()

    YAML_STORED_KINDS = dict()


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

MISSING_KIND_JSON = REPORT_DIR / "AUDIT-MISSING-KIND.json"

EMPTY_KINDS   = []
MISSING_KINDS = []


# ------------------- #
# -- MISSING KINDS -- #
# ------------------- #

logging.info(f"KINDS - 'Looking for missing ones'.")

with sqlite3.connect(FINAL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(QUERY_NO_KIND)

    for name, src in cursor.fetchall():
        namesrc = build_name_n_srcname(name, src)

        kind = YAML_STORED_KINDS.get(namesrc, '')

        if not kind:
            EMPTY_KINDS.append(namesrc)

EMPTY_KINDS.sort()


# ------------------ #
# -- 'AUTO' KINDS -- #
# ------------------ #

logging.info(f"KINDS - 'Resolving undefined kinds'.")

_all_resrc_kinds = defaultdict(str)

for _path_resrc_kinds in REPORT_DIR.glob("KIND-*json"):
    with _path_resrc_kinds.open(mode = 'r') as f:
        _one_resrc_kinds = json_load(f)

    for nsn, k in _one_resrc_kinds.items():
        if nsn in _all_resrc_kinds:
            k = f", {k}"

        _all_resrc_kinds[nsn] += k

for nsn in EMPTY_KINDS:
    resolved_kind = _all_resrc_kinds.get(nsn.lower(), '')

    if not resolved_kind:
        MISSING_KINDS.append(nsn)

        continue

    YAML_STORED_KINDS[nsn] = resolved_kind

    name, src = extract_name_n_srcname(nsn)

    logging.info(f"Resolved '{name} [{src}]' kind.")


# --------------- #
# -- UPDATE DB -- #
# --------------- #

logging.info(f"KINDS - 'SQLite DB - Update file'.")

with sqlite3.connect(FINAL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for namesrc, kind in YAML_STORED_KINDS.items():
        name, src = extract_name_n_srcname(namesrc)

        cursor.execute(
            QUERY_UPDATE_KIND,
            [kind, name, src]
        )


# ------------------ #
# -- YAML UPDATES -- #
# ------------------ #

logging.info(
    f"KINDS - Update '{HUMAN_KIND_YAML.relative_to(PROJ_DIR)}'."
)

with HUMAN_KIND_YAML.open("w") as f:
    yaml_dump(YAML_STORED_KINDS, f)


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(
    f"KINDS - Update '{MISSING_KIND_JSON.relative_to(PROJ_DIR)}'."
)

MISSING_KIND_JSON.write_text(
    json_dumps(EMPTY_KINDS)
)


# ------------------------- #
# -- MISSING KINDS FOUND -- #
# ------------------------- #

if MISSING_KINDS:
    nb = len(MISSING_KINDS)

    plurial = '' if nb == 1 else 's'

    reslover = PROJ_DIR / "tools" / "lab" / "resolve" / "missing-kinds.py"

    log_raise_error(
        context   = f"{nb} missing kind{plurial} need NOAI resolution",
        desc      = "Palettes need to have at least one kind.",
        exception = ValueError,
        xtra      = (
            f'Use:\n---\nstreamlit run "{reslover}"\n---')
    )
