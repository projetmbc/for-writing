#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from json import (
    dumps as json_dumps,
    load  as json_load,
)


# --------------- #
# -- CONSTANTS -- #
# --------------- #

CTXT = TAG_APRISM

THIS_DIR         = Path(__file__).parent
PROJ_DIR         = THIS_DIR.parent.parent
PRODS_DIR        = PROJ_DIR / "products"
CONTRIB_PROD_DIR = PROJ_DIR / "contrib" / "products"
REPORT_DIR       = THIS_DIR.parent / "report"


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


REPORT_NAME_CONFLICT_FILE = THIS_DIR / "PALETTE-CONFLICT.png"

if REPORT_NAME_CONFLICT_FILE.is_file():
    REPORT_NAME_CONFLICT_FILE.unlink()


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
        palette_def  = extend.parse(contrib_file.read_text())

        if palette_name in ALL_PALETTES:
            report_gradient_clash(
                existing_palette = ALL_PALETTES[palette_name],
                contrib_palette  = palette_def,
                palette_name     = palette_name,
                img_path         = REPORT_NAME_CONFLICT_FILE
            )

            log_raise_error(
                context = "contrib",
                desc    = (
                    f"Name '{palette_name}' already used."
                ),
                xtra    = (
                     "See '@prism/tools/report/"
                    f"{REPORT_NAME_CONFLICT_FILE.name}' file."
                ),
                exception = ValueError,
            )

        ALL_PALETTES, PAL_REPORT =  update_palettes(
            context   = CTXT,
            name      = palette_name,
            candidate = palette_def,
            palettes  = ALL_PALETTES,
            ignored   = PAL_REPORT,
            logcom    = logging
        )

        if not palette_name in PAL_REPORT:
            PAL_CREDITS[palette_name] = CTXT

nb_contribs = len(ALL_PALETTES) - nb_contribs

if nb_contribs != 0:
    plurial = "" if nb_contribs == 1 else "s"

    logging.info(f"{nb_contribs} palette{plurial} added.")


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

PAL_CREDITS_FILE.write_text(
    json_dumps(PAL_CREDITS)
)

PAL_REPORT_FILE.write_text(
    json_dumps(PAL_REPORT)
)


logging.info("Update palette JSON file.")

PAL_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
