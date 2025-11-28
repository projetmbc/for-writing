#!/usr/bin/env python3

from pathlib import Path
import              sys


TOOLS_DIR = Path(__file__).parent

while TOOLS_DIR.name != "tools-lab":
    TOOLS_DIR = TOOLS_DIR.parent

TOOLS_DIR = TOOLS_DIR.parent / "tools"

sys.path.append(str(TOOLS_DIR))

from cbutils import *

from shutil  import rmtree

from yaml import safe_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = Path(__file__).parent
PRODS_DIR   = TOOLS_DIR.parent / "products"
REPORT_DIR  = TOOLS_DIR / "report"
COMPARE_DIR = THIS_DIR / "compare"


PAL_JSON_FILE = PRODS_DIR / "json" / "palettes.json"

with PAL_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)


PAL_REPORT_FILE = REPORT_DIR / "PAL-REPORT.json"

with PAL_REPORT_FILE.open(mode = "r") as f:
    PAL_REPORT = json_load(f)


HUMAN_CHOICES_FILE = TOOLS_DIR.parent / "tools-lab" / "human-choices" / "rename" / "last.yaml"
HUMAN_CHOICES      = safe_load(HUMAN_CHOICES_FILE.read_text())


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
        if name in HUMAN_CHOICES[ctxt]:
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
