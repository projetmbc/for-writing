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

from collections import defaultdict


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[2]
THIS_RESRC = THIS_RESRC.upper()
THIS_RESRC = globals()[f"TAG_{THIS_RESRC}"]

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


# -------------------- #
# -- FROM COLORMAPS -- #
# -------------------- #

logging.info(f"Analyze '{THIS_RESRC}' source code")

pals_by_resec = defaultdict(dict)

for palfile in RESRC_DIR.glob('*/*.rgb'):
    palname = palfile.stem

    stdname = get_stdname(palname)


    content = palfile.read_text()

    paldef = []

    for line in content.splitlines():
        if line.startswith('ncolors'):
            continue

        if line.startswith('#'):
            continue

        rgb = [
            float(c.strip()) / 256
            for c in line.split(' ')
        ]

        assert len(rgb) == 3

        paldef.append(rgb)

    resrc_name = palfile.parent.name.upper()

    pals_by_resec[resrc_name][stdname] = resrc_std_palette(
        palname   = palname,
        palkind   = '',
        paldef    = paldef,
        precision = PAL_PRECISION + 2,
    )


# -------------------------- #
# -- REMOVE SHIFT VERSION -- #
# -------------------------- #

PATTERN_LAST_DIGITS = re.compile(r"(.+?)(\d+)$")

for resrc, pals in pals_by_resec.items():
    cleaned_pals = dict()

    for palname in pals:
        match = PATTERN_LAST_DIGITS.search(palname)

        if match:
            prefix = match.group(1)

            if prefix in pals:
                continue

            cleaned_pals[palname] = pals[palname]

    pals_by_resec[resrc] = cleaned_pals.copy()


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

for resrc, pals in pals_by_resec.items():
    resrc_pals_json = REPORT_DIR / f"{resrc}.json"

    logging.info(
        f"Update '{resrc_pals_json.relative_to(PROJ_DIR)}'"
    )

    pals = get_sorted_dict(pals)

    resrc_pals_json.write_text(
        json_dumps(pals)
    )
