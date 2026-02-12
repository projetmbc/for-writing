#!/usr/bin/env python3

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

PATTERN_CMASHER_KIND = re.compile(
    r'cm_type\s*=\s*["\']([^"\']+)["\']'
)


PATTERN_CMASHER_DATA = re.compile(
    r'cm_data\s*=\s*(\[[\s\S]*?\])\s*(?=\n\n)'
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_RESRC = TAG_CMASHER

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


RESRC_PALS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_PALS_JSON = REPORT_DIR / f"{RESRC_PALS_JSON}.json"


# ------------------ #
# -- FROM CMASHER -- #
# ------------------ #

logging.info(f"Analyze '{THIS_RESRC}' source code")

pals = dict()

for palfile in RESRC_DIR.glob('*.py'):
    content = palfile.read_text()

    palname = palfile.stem
    palkind = PATTERN_CMASHER_KIND.search(content).group(1)
    paldef  = ast.literal_eval(
        PATTERN_CMASHER_DATA.search(content).group(1)
    )

    stdname = get_stdname(palname)


    pals[stdname] = resrc_std_palette(
        palname   = palname,
        palkind   = palkind,
        paldef    = paldef,
        precision = PAL_PRECISION + 2,
    )


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info(f"Update '{RESRC_PALS_JSON.relative_to(PROJ_DIR)}'")


pals = get_sorted_dict(pals)

RESRC_PALS_JSON.write_text(
    json_dumps(pals)
)
