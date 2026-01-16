#!/usr/bin/env python3


exit(1)


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
    uid,
    name,
    kind
FROM palettes
WHERE kind = ''
"""

QUERY_UPDATE_KIND = """
UPDATE palettes
SET kind = ?
WHERE uid = ?"""


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
        HUMAN_KIND = safe_load(f)

    if HUMAN_KIND is None:
        HUMAN_KIND = dict()

else:
    HUMAN_KIND_YAML.touch()

    HUMAN_KIND = dict()


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

MISSING_KIND_JSON = REPORT_DIR / "AUDIT-MISSING-KIND.json"

EMPTY_KINDS   = []
MISSING_KINDS = []
NAME_2_UID    = {}


# ------------------- #
# -- MISSING KINDS -- #
# ------------------- #

logging.info(f"KINDS - 'Looking for missing ones'.")

with sqlite3.connect(FINAL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute(QUERY_NO_KIND)

    for uid, name, src in cursor.fetchall():
        NAME_2_UID[name] = uid

        namesrc = build_name_n_srcname(name, src)

        kind = HUMAN_KIND.get(name, '')

        if not kind:
            EMPTY_KINDS.append((uid, name))


# ------------------ #
# -- 'AUTO' KINDS -- #
# ------------------ #

logging.info(f"KINDS - 'Resolving undefined kinds'.")

_all_resrc_kinds = defaultdict(str)

for _path_resrc_kinds in REPORT_DIR.glob("KIND-*json"):
    with _path_resrc_kinds.open(mode = 'r') as f:
        _one_resrc_kinds = json_load(f)

    for uid, k in _one_resrc_kinds.items():
        if uid in _all_resrc_kinds:
            k = f"|{k}"

        _all_resrc_kinds[uid] += k

for uid, name in EMPTY_KINDS:
    resolved_kind = _all_resrc_kinds.get(uid, '')

    if not resolved_kind:
        MISSING_KINDS.append((uid, name))

        continue

    HUMAN_KIND[name] = resolved_kind

    logging.info(f"Resolved '{name}' kind.")


# --------------- #
# -- UPDATE DB -- #
# --------------- #

logging.info(f"KINDS - 'SQLite DB - Update file'.")

with sqlite3.connect(FINAL_SQLITE_DB_FILE) as conn:
    cursor = conn.cursor()

    for name, kind in HUMAN_KIND.items():
        cursor.execute(
            QUERY_UPDATE_KIND,
            [kind, NAME_2_UID[name]]
        )


# ------------------ #
# -- YAML UPDATES -- #
# ------------------ #

logging.info(
    f"KINDS - Update '{HUMAN_KIND_YAML.relative_to(PROJ_DIR)}'."
)

with HUMAN_KIND_YAML.open("w") as f:
    yaml_dump(HUMAN_KIND, f)


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(
    f"KINDS - Update '{MISSING_KIND_JSON.relative_to(PROJ_DIR)}'."
)

MISSING_KIND_JSON.write_text(
    json_dumps(MISSING_KINDS)
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
