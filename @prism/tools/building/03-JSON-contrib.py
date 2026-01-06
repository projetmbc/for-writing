#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR        = Path(__file__).parent
BUILD_TOOLS_DIR = THIS_DIR

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils.core import *
from cbutils      import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #


# ------------------ #
# -- CONSTANTS #1 -- #
# ------------------ #

THIS_RESRC = TAG_APRISM

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != TAG_APRISM):
    PROJ_DIR = PROJ_DIR.parent

CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"
REPORT_DIR       = BUILD_TOOLS_DIR / TAG_REPORT


RESRC_PALS_JSON = THIS_RESRC.replace(' ', '-').upper()
RESRC_PALS_JSON = REPORT_DIR / f"PALS-{RESRC_PALS_JSON}.json"


# ------------------ #
# -- CONSTANTS #2 -- #
# ------------------ #

PRECISION = YAML_CONFIG['PRECISION']


# ---------------------------- #
# -- FROM CONTRIB. PALETTES -- #
# ---------------------------- #

contribs_accepted = get_accepted_paths(PROJ_DIR)

if CONTRIB_PROD_DIR in contribs_accepted:
    del contribs_accepted[CONTRIB_PROD_DIR]

if not contribs_accepted:
    logging.warning(f"No contrib found.")

    exit(0)


pals = dict()

for folder, contribs in sorted(contribs_accepted.items()):
    technno = folder.parent.name

    logging.info(f"'{technno}' contribs.")

    extend = import_from_path(
        module_name = "extend",
        file_path   = folder.parent / "extend.py"
    )

    for one_contrib in sorted(contribs):
        logging.info(f"Contrib '{one_contrib}'.")

        palname = Path(one_contrib).stem
        stdname = get_stdname(palname)

        contrib_file = folder / one_contrib
        contrib_code = contrib_file.read_text()

        paldata = extend.parse(contrib_code)

        pals[stdname] = resrc_std_palette(
            palname,
            paldata[TAG_METADATA][TAG_KIND],
            paldata[TAG_PALETTE],
            PRECISION + 2
        )


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info(f"'{RESRC_PALS_JSON.relative_to(PROJ_DIR)}' update.")

RESRC_PALS_JSON.write_text(
    json_dumps(pals)
)
