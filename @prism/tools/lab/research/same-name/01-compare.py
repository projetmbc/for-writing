#!/usr/bin/env python3

# ---------------------------- #
# -- IMPORT CBUTILS - START -- #

from pathlib import Path
import              sys

LAB_DIR = Path(__file__).parent

while LAB_DIR.name != "lab":
    LAB_DIR = LAB_DIR.parent

BUILD_TOOLS_DIR = LAB_DIR.parent / "building"

sys.path.append(str(BUILD_TOOLS_DIR))

from cbutils import *

# -- IMPORT CBUTILS - END -- #
# -------------------------- #

from shutil  import rmtree

from yaml import safe_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism"):
    PROJ_DIR = PROJ_DIR.parent

REPORT_DIR  = BUILD_TOOLS_DIR / "REPORT"
COMPARE_DIR = THIS_DIR / "compare"


PAL_JSON_FILE = PROJ_DIR / "products" / "json" / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)


HUMAN_RENAMING_FILE = LAB_DIR / "human-choices" / "rename" / "last.yaml"
HUMAN_RENAMING      = safe_load(HUMAN_RENAMING_FILE.read_text())


if COMPARE_DIR:
    rmtree(COMPARE_DIR)

COMPARE_DIR.mkdir(
    parents = True,
    exist_ok = True
)


TAB_1 = " "*4
TAB_2 = TAB_1*2


# --------------------------- #
# -- IMAGES FOR CAMPARISON -- #
# --------------------------- #

print("+ Looking for images to build.")

for name, ctxts_pals in PAL_REPORT[TAG_SAME_NAME].items():
    for (ctxt, pal) in ctxts_pals:
        if name in HUMAN_RENAMING[ctxt]:
            continue

        imgadded = report_gradient_clash(
            all_palettes   = ALL_PALETTES,
            palette_report = PAL_REPORT,
            name           = name,
            context        = ctxt,
            palette        = pal,
            img_dir        = COMPARE_DIR,
        )

        if imgadded:
            print(f"{TAB_1}> Building '{name}' image.")
            print(f"{TAB_2}[{ctxt}]")
