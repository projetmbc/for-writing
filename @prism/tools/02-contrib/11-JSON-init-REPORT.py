#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from shutil import rmtree

from json import dumps as json_dumps


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR   = Path(__file__).parent
PROJ_DIR   = THIS_DIR.parent.parent
REPORT_DIR = THIS_DIR.parent / "report"

HUMAN_CHOICES_FILE = PROJ_DIR / "tools-lab" / "human-choices" / "ignored" / "last.txt"


PAL_REPORT_FILE  = REPORT_DIR / "PAL-REPORT.json"


# ----------------------------- #
# -- EMPTY THE REPORT FOLDER -- #
# ----------------------------- #

REPORT_DIR  = THIS_DIR.parent / "report"

if REPORT_DIR.is_dir():
    rmtree(REPORT_DIR)

REPORT_DIR.mkdir(
    parents  = True,
    exist_ok = True
)


# ------------- #
# -- EXTRACT -- #
# ------------- #

def extract_infos(file: Path) -> [str]:
    report = dict()

    data = [
        l.strip()
        for l in file.read_text().splitlines()
        if l.strip() and l.strip()[0] != "#"
    ]

    for d in data:
        ignored, kept = d.split('=')

        ignored = ignored.strip()
        kept    = kept.strip()

        status = PAL_STATUS.EQUAL_TO

        report[ignored] = {
            "context"         : "Human",
            STATUS_TAG[status]: kept
        }

        logging.warning(
            f"'{ignored}' ignored - {STATUS_MSG[status]} '{kept}' (human choice)."
        )

    return report


# ---------------------- #
# -- IGNORED BY HUMAN -- #
# ---------------------- #

logging.info(
    f"Initializing '{PAL_REPORT_FILE.name}' file (human choices)."
)

PAL_REPORT = extract_infos(HUMAN_CHOICES_FILE)

PAL_REPORT[TAG_SAME_NAME] = dict()

logging.info(f"Create the initial '{PAL_REPORT_FILE.name}' file.")

PAL_REPORT_FILE.write_text(
    json_dumps(PAL_REPORT)
)
