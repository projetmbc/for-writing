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

from matplotlib import colors


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

PATTERN_CARTO_BLOCK = re.compile(
    r"const\s+(\w+)\s*=\s*(\{.*?\});",
    re.DOTALL
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[1]
THIS_RESRC = THIS_RESRC.upper()
THIS_RESRC = globals()[f"TAG_{THIS_RESRC}"]

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != RESRC_ALIAS[TAG_APRISM]):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


RESRC_PALS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_PALS_JSON = REPORT_DIR / f"{RESRC_PALS_JSON}.json"


_CARTO_CODE = RESRC_DIR / "carto.ts"
CARTO_CODE  = _CARTO_CODE.read_text()


# ----------- #
# -- TOOLS -- #
# ----------- #

def extract_palette(pal_data: dict) -> [str, PaletteCols]:
    kind = ', '.join(
        sorted(pal_data['tags'])
    )

    del pal_data['tags']

    _bigger_size = sorted(
        pal_data,
        key = lambda k: int(k)
    )

    bigger_size = _bigger_size[-1]

    paldef = [
        colors.to_rgb(c)
        for c in pal_data[bigger_size]
    ]

    return kind, paldef


# ---------------------- #
# -- FROM CARTOCOLORS -- #
# ---------------------- #

logging.info(f"Source - Analyze '{THIS_RESRC}'")

pals = dict()

for match in PATTERN_CARTO_BLOCK.finditer(CARTO_CODE):
    palname = match.group(1)

    stdname = get_stdname(palname)

    tsdict = match.group(2)

    pycode = re.sub(
        r"(\s+)(\w+):",
        r'\1"\2":',
        tsdict
    )

    pycode = re.sub(
        r",\s*([\]\}])",
        r"\1",
        pycode
    )

    pal_data = ast.literal_eval(pycode)

    palkind, paldef = extract_palette(pal_data)

    pals[stdname] = resrc_std_palette(
        palname   = palname,
        palkind   = palkind,
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
