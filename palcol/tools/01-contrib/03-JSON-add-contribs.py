#!/usr/bin/env python3

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *

import ast

from json import (
    dumps as json_dumps,
    load  as json_load,
)

import importlib.util

import matplotlib.pyplot as plt
import numpy as np


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = Path(__file__).parent
PROJECT_DIR = THIS_DIR.parent.parent
REPORT_DIR  = PROJECT_DIR / "tools" / "report"
CONTRIB_DIR = PROJECT_DIR / "contrib" / "palettes"
DATA_DIR    = THIS_DIR.parent.parent / "data"

PALETTES_JSON_FILE = DATA_DIR / "palettes.json"


REPORT_NAME_CONFLICT_FILE = REPORT_DIR / "PALETTE-CONFLICT.png"


# ----------- #
# -- TOOLS -- #
# ----------- #

def report_gradient_name_clash(
    existing_palette: list[list[float, float, float]],
    contrib_palette : list[list[float, float, float]],
    name            : str,
    img_path        : Path
) -> None:
    # --- Créer les dégradés
    def make_gradient(colors, width=800, height=100):
        from matplotlib.colors import to_rgb
        n = len(colors)
        gradient = np.linspace(0, 1, width)
        arr = np.zeros((height, width, 3))
        stops = np.linspace(0, 1, n)
        rgb_colors = np.array([to_rgb(c) for c in colors])
        for i in range(3):
            arr[:, :, i] = np.interp(gradient, stops, rgb_colors[:, i])
        return arr

    grad1 = make_gradient(existing_palette)
    grad2 = make_gradient(contrib_palette)

    # --- Affichage
    fig, axes = plt.subplots(2, 1, figsize=(8, 3))

    axes[0].imshow(grad1, aspect="auto")
    axes[0].set_title(f"Existing palette '{palette_name}'", fontsize=12, pad=8)
    axes[0].axis("off")

    axes[1].imshow(grad2, aspect="auto")
    axes[1].set_title(f"Contrib palette'{palette_name}'", fontsize=12, pad=8)
    axes[1].axis("off")

    plt.tight_layout()

    plt.savefig(
        img_path,
        dpi=200,
        bbox_inches="tight"
    )



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

if not contribs_accepted:
    logging.warning(f"No contrib found.")

    exit(0)

nb_contribs = 0

for folder, contribs in contribs_accepted.items():
    ctxt = folder.parent.name

    logging.info(f"Working on '{ctxt}'.")

    extend = import_from_path("extend", folder.parent / "extend.py")

    for one_contrib in contribs:
        contrib_file = folder / one_contrib
        palette_name = Path(Path(one_contrib).stem).stem
        palette_def  = extend.parse(contrib_file.read_text())

        if palette_name in palettes:
            report_gradient_name_clash(
                existing_palette    = palettes[palette_name],
                contrib_palette = palette_def,
                name            = palette_name,
                img_path        = REPORT_NAME_CONFLICT_FILE
            )

            log_raise_error(
                context = "contrib",
                desc    = (
                    f"Name '{palette_name}' already used."
                ),
                xtra    = (
                     "See 'palcol/tools/report/"
                    f"{REPORT_NAME_CONFLICT_FILE.name}' file."
                ),
                exception = ValueError,
            )

        nb_contribs += 1

        palettes[palette_name] = palette_def

        logging.info(f"New contrib. palette '{palette_name}' added.")

plurial = "" if nb_contribs == 1 else "s"

logging.info(f"{nb_contribs} contrib. palette{plurial} added.")


# ------------------ #
# -- JSON UPDATED -- #
# ------------------ #

logging.info("Updated initial palette JSON file.")

PALETTES_JSON_FILE.write_text(json_dumps(palettes))
