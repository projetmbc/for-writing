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

PATTERN_PALETTE = re.compile(
    r'cm_data\s*=\s*(\[\[.*?\]\])',
    re.DOTALL
)


PATTERN_KIND = re.compile(
    r'<Kind>(.*?)</Kind>'
)


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

THIS_RESRC = Path(__file__).stem
THIS_RESRC = THIS_RESRC.split('-')[2]
THIS_RESRC = THIS_RESRC.upper()
THIS_RESRC = globals()[f"TAG_{THIS_RESRC}"]

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

RESRC_DIR  = PROJ_DIR / TAG_RESOURCES / get_stdname(THIS_RESRC)
REPORT_DIR = BUILD_TOOLS_DIR / TAG_REPORT


RESRC_PALS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_PALS_JSON = REPORT_DIR / f"{RESRC_PALS_JSON}.json"


# ----------- #
# -- TOOLS -- #
# ----------- #

def extract_palette(file: Path) -> tuple[str, PaletteCols]:
    rep = []

    for e, p, k in [
        ('xcmap', PATTERN_KIND, 'kind'),
        ('py', PATTERN_PALETTE, 'value'),
    ]:
        content = (
            file.parent / f"{file.stem}.{e}"
        ).read_text()

        match = p.search(content)

        if not match:
            log_raise_error(
                context   = "Extra resource",
                desc      = f"'{THIS_RESRC}' - Matching palette {k}fails",
                exception = ValueError,
            )

        rep.append(match.group(1))

    return rep[0], eval(rep[1])


# -------------------------- #
# -- FROM SCI. COLOR MAPS -- #
# -------------------------- #

logging.info(f"Analyze '{THIS_RESRC}' source code")

pals = dict()

for pyfile in sorted(RESRC_DIR.glob("*.py"), key = lambda x: str(x).lower()):
    palname = pyfile.stem
    stdname = get_stdname(palname)

    _ , paldef = extract_palette(pyfile)

    pals[stdname] = resrc_std_palette(
        palname   = palname,
        palkind  = TAG_COLORBLIND,
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
