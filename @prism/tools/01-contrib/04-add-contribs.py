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

CTXT = "@prism"

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
PRODUCTS_DIR = PROJECT_DIR / "products"

PAL_JSON_FILE   = PRODUCTS_DIR / "palettes.json"
PAL_REPORT_FILE = THIS_DIR / "pal-report.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)

with PAL_REPORT_FILE.open(mode = "r") as f:
    IGNORED = json_load(f)


REPORT_NAME_CONFLICT_FILE = THIS_DIR / "PALETTE-CONFLICT.png"

if REPORT_NAME_CONFLICT_FILE.is_file():
    REPORT_NAME_CONFLICT_FILE.unlink()


# ----------------------- #
# -- CONTRIB. PALETTES -- #
# ----------------------- #

contribs_accepted = get_accepted_paths(PROJECT_DIR)

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
                     "See 'at-prism/tools/report/"
                    f"{REPORT_NAME_CONFLICT_FILE.name}' file."
                ),
                exception = ValueError,
            )

        ALL_PALETTES, IGNORED =  update_palettes(
            context   = CTXT,
            name      = palette_name,
            candidate = palette_def,
            palettes  = ALL_PALETTES,
            ignored   = IGNORED,
            logcom    = logging
        )

nb_contribs = len(ALL_PALETTES) - nb_contribs

if nb_contribs != 0:
    plurial = "" if nb_contribs == 1 else "s"

    logging.info(f"{nb_contribs} palette{plurial} added.")


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

PAL_REPORT_FILE.write_text(json_dumps(IGNORED))

logging.info("Update palette JSON file.")

PAL_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
