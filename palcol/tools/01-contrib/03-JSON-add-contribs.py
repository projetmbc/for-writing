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

import matplotlib.pyplot as plt
import numpy as np


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
PROJECT_DIR  = THIS_DIR.parent.parent
REPORT_DIR   = PROJECT_DIR / "tools" / "report"
CONTRIB_DIR  = PROJECT_DIR / "contrib" / "palettes"
PRODUCTS_DIR = THIS_DIR.parent.parent / "products"

PALETTES_JSON_FILE = PRODUCTS_DIR / "palettes.json"


REPORT_NAME_CONFLICT_FILE = REPORT_DIR / "PALETTE-CONFLICT.png"


# ----------------- #
# -- REPORT TOOL -- #
# ----------------- #

def report_gradient_clash(
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


# ----------------------- #
# -- CONTRIB. PALETTES -- #
# ----------------------- #

with PALETTES_JSON_FILE.open(mode = "r") as f:
    ALL_PALETTES = json_load(f)

contribs_accepted = get_accepted_paths(PROJECT_DIR)

if not contribs_accepted:
    logging.warning(f"No contrib found.")

    exit(0)

nb_contribs = 0

for folder, contribs in contribs_accepted.items():
    ctxt = folder.parent.name

    logging.info(f"Work on '{ctxt}'.")

    extend = import_from_path(
        module_name = "extend",
        file_path   = folder.parent / "extend.py"
    )

    for one_contrib in contribs:
        contrib_file = folder / one_contrib
        palette_name = Path(Path(one_contrib).stem).stem
        palette_def  = extend.parse(contrib_file.read_text())

        if palette_name in ALL_PALETTES:
            report_gradient_clash(
                existing_palette    = ALL_PALETTES[palette_name],
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

        ALL_PALETTES[palette_name] = palette_def

        logging.info(f"New contrib. palette '{palette_name}' added.")

plurial = "" if nb_contribs == 1 else "s"

logging.info(f"{nb_contribs} contrib. palette{plurial} added.")


# ----------------- #
# -- JSON UPDATE -- #
# ----------------- #

logging.info("Update palette JSON file.")

PALETTES_JSON_FILE.write_text(json_dumps(ALL_PALETTES))
