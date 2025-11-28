#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

from shutil import rmtree

from yaml import safe_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR   = Path(__file__).parent
PROJ_DIR   = THIS_DIR.parent.parent
REPORT_DIR = THIS_DIR.parent / "report"


PAL_REPORT_FILE  = REPORT_DIR / "PAL-REPORT.json"


HUMAN_CHOICES_FILE = PROJ_DIR / "tools-lab" / "human-choices" / "ignored" / "last.yaml"
HUMAN_CHOICES      = safe_load(HUMAN_CHOICES_FILE.read_text())


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

def extract_infos(choices: dict) -> [str]:
    if not choices:
        return dict()

    report = dict()

    for ctxt in sorted(
        choices,
        key = lambda x: x.lower()
    ):
        data = choices[ctxt]

        nb_ignored = len(data)

        plurial = "" if nb_ignored == 1 else "s"

        logging.info(
            f"Source '{ctxt}': {nb_ignored} palette{plurial} ignored."
        )

        for d in data:
            if '=' in d:
                status = PAL_STATUS.EQUAL_TO

                oriname, projname = [
                    n.strip()
                    for n in d.split("=")
                ]

            elif '><' in d:
                status = PAL_STATUS.REVERSE_OF

                oriname, projname = [
                    n.strip()
                    for n in d.split("><")
                ]

            else:
                status  = PAL_STATUS.EQUAL_TO
                oriname = projname = d.strip()

            report[namectxt(oriname, ctxt)] = {
                STATUS_TAG[status]: projname,
                TAG_METH          : TAG_HUMAN,
            }

    return report


# ---------------------- #
# -- IGNORED BY HUMAN -- #
# ---------------------- #

logging.info(
    f"Initializing '{PAL_REPORT_FILE.name}' file (human choices)."
)

PAL_REPORT = extract_infos(HUMAN_CHOICES)

PAL_REPORT[TAG_SAME_NAME]     = dict()
PAL_REPORT[TAG_NAMES_IGNORED] = list()

logging.info(f"Create the initial '{PAL_REPORT_FILE.name}' file.")

PAL_REPORT_FILE.write_text(
    json_dumps(PAL_REPORT)
)
