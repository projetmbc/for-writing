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

import hashlib
from collections import defaultdict


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

THIS_RESRC = TAG_SCICOLMAPS

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

GRPS_BY_NAMES = defaultdict(list)
GRPS_BY_PALS  = defaultdict(list)

SAME_NAMES = dict()
SAME_PALS  = []

SAME_NAMES_JSON = REPORT_DIR / f"RESRC-SAME-NAMES.json"
SAME_PALS_JSON  = REPORT_DIR / f"RESRC-SAME-PALS.json"


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_palette_hash(palette: PaletteCols) -> str:
    palette = [
        [round(v, 4) for v in c]
        for c in palette
    ]

    palstr   = json_dumps(palette, sort_keys = True)
    hashcode = hashlib.md5(palstr.encode()).hexdigest()

    return hashcode


def resume_data(
    projname: str,
    data
) -> None:
    for stdname, data in data.items():
        palette = data["rgb-cols"]

        GRPS_BY_NAMES[stdname].append(projname)

        hashcode = get_palette_hash(palette)

        GRPS_BY_PALS[hashcode].append((projname, stdname))


# -------------- #
# -- ANALYSIS -- #
# -------------- #

logging.info(f"Looking for ambiguities.")


for resrc_json in REPORT_DIR.glob("RESRC-PALS-*.json"):
    projname = resrc_json.stem.split('-')
    projname = projname[2:]
    projname = '-'.join(projname)

    resume_data(
        projname = projname,
        data     = json_load(resrc_json.open())
    )


for name, projs in GRPS_BY_NAMES.items():
    if len(projs) > 1:
        SAME_NAMES[name] = projs


for hashcode, infos in GRPS_BY_PALS.items():
    if len(infos) > 1:
        SAME_PALS.append(infos)


TODO_NETTOYER


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

for data, json_file in [
    (SAME_NAMES, SAME_NAMES_JSON),
    (SAME_PALS, SAME_PALS_JSON),
]:
    logging.info(f"'{json_file.relative_to(PROJ_DIR)}' update.")

    json_file.write_text(
        json_dumps(data)
    )
