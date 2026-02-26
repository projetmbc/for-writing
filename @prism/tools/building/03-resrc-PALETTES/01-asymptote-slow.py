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

PATTERN_ASY_COLORMAP = re.compile(
    r"list_data\s+([A-Za-z0-9_]+)\s*=.*\{([^}]+)\}",
    re.MULTILINE
)

PATTERN_ASY_RGB = re.compile(
    r"rgb\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)"
)

PATTERN_ASY_SEGPAL = re.compile(
    r"seg_data\s+(\w+)\s*=\s*seg_data\s*\((.*?)\);",
    re.S
)

PATTERN_ASY_TRIPLE = re.compile(
    r"new triple\[\]\s*{(.*?)}",
    re.S
)

PATTERN_ASY_CHANNEL = re.compile(
    r"\(([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\)"
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[1]
THIS_RESRC = THIS_RESRC.upper()
THIS_RESRC = globals()[f"TAG_{THIS_RESRC}"]

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_RESOURCES / THIS_RESRC
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


RESRC_PALS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_PALS_JSON = REPORT_DIR / f"{RESRC_PALS_JSON}.json"


_ASY_CODE = RESRC_DIR / "colormap.asy"
ASY_CODE  = _ASY_CODE.read_text()


# ------------------------------- #
# -- FROM ASYMPTOTE COLOR MAPS -- #
# ------------------------------- #

logging.info(f"Source - Analyze '{THIS_RESRC}'")

pals = dict()

for palname, body in PATTERN_ASY_COLORMAP.findall(ASY_CODE):
    stdname = get_stdname(palname)

    paldef = [
        list(map(float, rgb))
        for rgb in PATTERN_ASY_RGB.findall(body)
    ]

    pals[stdname] = resrc_std_palette(
        palname   = palname,
        palcatego = '',
        paldef    = paldef,
        precision = PAL_PRECISION + 2,
    )


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info(f"JSON - Update '{RESRC_PALS_JSON.relative_to(PROJ_DIR)}'")

pals = get_sorted_dict(pals)

RESRC_PALS_JSON.write_text(
    json_dumps(pals)
)
