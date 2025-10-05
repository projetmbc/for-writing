#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

import ast

from json import load as json_load

import importlib.util

import matplotlib.pyplot as plt
import numpy as np


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent
CONTRIB_DIR = PROJECT_DIR / "contrib" / "palettes"
DATA_DIR    = THIS_DIR.parent.parent / "data"

PALETTES_JSON_FILE = DATA_DIR / "palettes.json"


# ----------- #
# -- TOOLS -- #
# ----------- #

# src::
#     url = https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
def import_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path
    )

    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module

    spec.loader.exec_module(module)

    return module


# ----------------- #
# -- LET'S WORK! -- #
# ----------------- #

with PALETTES_JSON_FILE.open(mode = "r") as f:
    palettes = json_load(f)

contribs_accepted = get_accepted_paths(PROJECT_DIR)

nb_impl = 0

for folder in sorted(contribs_accepted):
    nb_impl += 1

    ctxt = folder.parent.name

    logging.info(f"Adding '{ctxt}' implementation.")

    extend = import_from_path("extend", folder.parent / "extend.py")

    code = []

    for name, data in palettes.items():
        code.append(extend.build_code(name, data))

    code = "\n".join(code)

    final_file = DATA_DIR / ctxt / extend.PALETTES_FILE_NAME

    final_file.parent.mkdir(
        parents  = True,
        exist_ok = True
    )

    final_file.write_text(code)


plurial = "" if nb_impl == 1 else "s"

logging.info(f"{nb_impl} implementation{plurial} added.")
