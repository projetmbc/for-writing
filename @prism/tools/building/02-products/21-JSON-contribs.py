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

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

CTXT = TAG_APRISM


PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

PRODS_DIR        = PROJ_DIR / "products"
CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"
REPORT_DIR       = BUILD_TOOLS_DIR / "REPORT"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

PROD_JSON_DIR = PRODS_DIR / "json"
PAL_JSON_FILE = PROD_JSON_DIR / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)


PAL_CREDITS_FILE = REPORT_DIR / "PAL-CREDITS.json"

with PAL_CREDITS_FILE.open(mode = "r") as f:
    PAL_CREDITS = json_load(f)


# ----------------------- #
# -- CONTRIB. PALETTES -- #
# ----------------------- #

contribs_accepted = get_accepted_paths(PROJ_DIR)

if CONTRIB_PROD_DIR in contribs_accepted:
    del contribs_accepted[CONTRIB_PROD_DIR]

if not contribs_accepted:
    logging.warning(f"No contrib found.")

    exit(0)

nb_contribs = len(ALL_PALETTES)

for folder, contribs in sorted(contribs_accepted.items()):
    ctxt = folder.parent.name

    logging.info(f"Work on '{ctxt}'.")

    extend = import_from_path(
        module_name = "extend",
        file_path   = folder.parent / "extend.py"
    )

    for one_contrib in sorted(contribs):
        contrib_file = folder / one_contrib

        palette_name = Path(Path(one_contrib).stem).stem
        palette_name = stdname(palette_name)
        pal_def      = extend.parse(contrib_file.read_text())

        PAL_CREDITS[palette_name] = CTXT

        _ , ALL_PALETTES, PAL_REPORT =  update_palettes(
            context   = CTXT,
            name      = palette_name,
            candidate = pal_def,
            palettes  = ALL_PALETTES,
            ignored   = PAL_REPORT,
            logcom    = logging
        )

# Equal palettes in contribs are forbidden!
TAG_EQUAL_TO   = STATUS_TAG[PAL_STATUS.EQUAL_TO]
TAG_REVERSE_OF = STATUS_TAG[PAL_STATUS.REVERSE_OF]

for namectxt in PAL_REPORT:
    if not '::' in namectxt:
        continue

    name, ctxt = extract_namectxt(namectxt)

    if ctxt == TAG_APRISM:
        info = PAL_REPORT[namectxt]

        if TAG_EQUAL_TO in info:
            other = info[TAG_EQUAL_TO]

        else:
            other = info[TAG_REVERSE_OF]

        log_raise_error(
            context   = "Contrib. palettes.",
            desc      = f"'{name}' = '{other}'.",
            exception = ValueError,
            xtra      = "Two equal palettes found in contribs."
        )

# We continue as usual...
nb_contribs = resume_nbpals_build(
    context     = CTXT,
    nb_new_pals = nb_contribs,
    palettes    = ALL_PALETTES,
    logcom      = logging,
)


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

update_jsons(
    nb_new_pals = nb_contribs,
    credits     = PAL_CREDITS,
    jscredits   = PAL_CREDITS_FILE,
    reports     = PAL_REPORT,
    jsreports   = PAL_REPORT_FILE,
    palettes    = ALL_PALETTES,
    jspalettes  = PAL_JSON_FILE,
    logcom      = logging,
)
