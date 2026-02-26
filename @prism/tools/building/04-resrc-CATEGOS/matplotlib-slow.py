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


RESRC_DIR = PROJ_DIR / TAG_RESOURCES / THIS_RESRC

CMP_PY_FILE = RESRC_DIR / 'colormaps.py'


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PATTERN_COLOR_GRAD = re.compile(
    r"plot_color_gradients\(([\s\S]*?)\)"
)

PATTERN_PARTS = re.compile(r"['\"](.*?)['\"]")


# ----------- #
# -- TOOLS -- #
# ----------- #

def get_stdcatego(desc):
    desc = desc.lower()

    for n in desc.split(' '):
        if n in CATEGO_ALIAS:
            return [CATEGO_ALIAS[n]]

    return []


# --------------------- #
# -- EXTRACT CATEGOS -- #
# --------------------- #

logging.info(f"Categos - Extract - '{THIS_RESRC}'")

_CATEGOS = defaultdict(list)

pycode = CMP_PY_FILE.read_text()

results = []

for match in PATTERN_COLOR_GRAD.finditer(pycode):
    content = match.group(1)

    parts = PATTERN_PARTS.findall(content)

    if parts:
        categos = get_stdcatego(parts[0])

        if categos:
            for palname in parts[1:]:
                _CATEGOS[palname] += categos


# ------------------ #
# -- JSON UPDATES -- #
# ------------------ #

logging.info(
    f"JSON - Update '{RESRC_CATEGOS_JSON.relative_to(PROJ_DIR)}'"
)

# We want a deterministic output.
CATEGOS = {
    n: ', '.join(sorted(_CATEGOS[n]))
    for n in sorted(_CATEGOS)
}

# -- DEBUG - ON -- #
# print(PALS_CATEGOS)
# -- DEBUG - OFF -- #

RESRC_CATEGOS_JSON.write_text(
    json_dumps(CATEGOS)
)
