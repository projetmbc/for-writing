#!/usr/bin/env python3

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


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_RESRC = TAG_ASYMPTOTE

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_XTRA_RESRC / get_stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


RESRC_PALS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_PALS_JSON = REPORT_DIR / f"RESRC-PALS-{RESRC_PALS_JSON}.json"


ASY_CODE = RESRC_DIR / "colormap.asy"
ASY_CODE = ASY_CODE.read_text()


# ------------------------------- #
# -- FROM ASYMPTOTE COLOR MAPS -- #
# ------------------------------- #

logging.info(f"Analyzing '{THIS_RESRC}' source code.")

pals = dict()

for palname, body in PATTERN_ASY_COLORMAP.findall(ASY_CODE):
    stdname = get_stdname(palname)

    paldef = [
        list(map(float, rgb))
        for rgb in PATTERN_ASY_RGB.findall(body)
    ]

    pals[stdname] = resrc_std_palette(
        palname,
        '',
        paldef,
    )


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info(f"'{RESRC_PALS_JSON.relative_to(PROJ_DIR)}' update.")

RESRC_PALS_JSON.write_text(
    json_dumps(pals)
)
