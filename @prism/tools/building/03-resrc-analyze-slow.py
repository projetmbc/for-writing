#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR  = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR

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

_THIS_VAR_NAMES = [
    'SAME_NAME_DIFF_PAL',
    'DIFF_NAME_SAME_PAL',
    'TWINS',
]

for varname in _THIS_VAR_NAMES:
    globals()[varname] = []

    filestem = varname.replace('_', '-')
    varname += "_JSON"

    globals()[varname] = REPORT_DIR / f"AUTO-{filestem}.json"


# ------------------ #
# -- CONSTANTS #3 -- #
# ------------------ #

PRECISION = YAML_CONFIG['PRECISION']


# ----------- #
# -- TOOLS -- #
# ----------- #

GRPS_BY_NAMES = defaultdict(set)
GRPS_BY_PALS  = defaultdict(set)

def get_palette_hash(palette: PaletteCols) -> str:
    palette = [
        [round(v, PRECISION) for v in c]
        for c in palette
    ]

    palstr   = json_dumps(palette, sort_keys = True)
    hashcode = hashlib.md5(palstr.encode()).hexdigest()

    return hashcode


def resume_data(
    projname: str,
    data
) -> None:
    for palname, data in data.items():
        palette = data["rgb-cols"]

        infos = (projname, palname)

        GRPS_BY_NAMES[palname].add(infos)

        hashcode = get_palette_hash(palette)

        GRPS_BY_PALS[hashcode].add(infos)


# -------------- #
# -- ANALYSIS -- #
# -------------- #

logging.info(f"Looking for ambiguities.")

# Preprocessing.
for resrc_json in REPORT_DIR.glob("RESRC-PALS-*.json"):
    projname = resrc_json.stem.split('-')
    projname = projname[2:]
    projname = '-'.join(projname)

    resume_data(
        projname = projname,
        data     = json_load(resrc_json.open())
    )


# Twins?
TWINS_FOUND = set()

for hashcode, infos in GRPS_BY_PALS.items():
# No repetition.
    if len(infos) == 1:
        continue

# Let's work a little...
    twinprojs    = defaultdict(list)

    for projname, palname in infos:
        twinprojs[palname].append(projname)

    for palname, twinprojnames in twinprojs.items():
        if len(twinprojnames) == 1:
            continue

        twinprojnames = list(twinprojnames)
        twinprojnames.sort()

        TWINS.append((palname, twinprojnames))

        for projname in twinprojnames:
            TWINS_FOUND.add((projname, palname))

TWINS.sort()


# Different name, same palette?
# Same name, different palette?
for finaldata, predata in [
    (DIFF_NAME_SAME_PAL, GRPS_BY_PALS),
    (SAME_NAME_DIFF_PAL, GRPS_BY_NAMES),
]:
    for _ , infos in predata.items():
# No repetition.
        if len(infos) == 1:
            continue

# Let's work a little...
        infos = infos - TWINS_FOUND

# Nothing left.
        if len(infos) == 0:
            continue

# Something to store.
        infos = list(infos)
        infos.sort()

        finaldata.append(infos)

    finaldata.sort()


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

for varname in _THIS_VAR_NAMES:
    data      = globals()[varname]
    varname  += "_JSON"
    json_file = globals()[varname]

    logging.info(f"'{json_file.relative_to(PROJ_DIR)}' update.")

    json_file.write_text(
        json_dumps(data)
    )
