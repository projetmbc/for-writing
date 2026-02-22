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


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

CVD_TXT    = 'CVD-friendly'
CVD_CATEGO = 'colorblind'


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[0]
THIS_RESRC = THIS_RESRC.upper()


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

THIS_RESRC_DIR = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)

REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


_RESRC_CATEGOS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_CATEGOS_JSON  = REPORT_DIR / f"CATEGO-{_RESRC_CATEGOS_JSON}.json"


# -------------------- #
# -- ADDING CATEGOS -- #
# -------------------- #

logging.info(f"Categos - Extract '{CVD_TXT}' from '{THIS_RESRC}'")

_CVD_PALS = defaultdict(set)

for restpath in sorted(THIS_RESRC_DIR.glob('*.rst')):
    content = restpath.read_text()

    if not CVD_TXT in content:
        continue

    uid = build_name_n_srcname(
        restpath.stem,
        THIS_RESRC
    )

    _CVD_PALS[uid].add(CVD_CATEGO)


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(
    f"JSON - Update '{RESRC_CATEGOS_JSON.relative_to(PROJ_DIR)}'"
)

# We want a deterministic output.
CVD_PALS = {
    uid: ', '.join(sorted(_CVD_PALS[uid]))
    for uid in sorted(_CVD_PALS)
}

# -- DEBUG - ON -- #
# print(PALS_CATEGOS)
# -- DEBUG - OFF -- #

RESRC_CATEGOS_JSON.write_text(
    json_dumps(CVD_PALS)
)
