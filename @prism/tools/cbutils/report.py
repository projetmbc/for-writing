#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
import numpy             as np

from matplotlib.colors import to_rgb

from .cleanpal import *

def report_gradient_clash(
    all_palettes  : list[list[float, float, float]],
    palette_report: dict,
    name          : str,
    context       : str,
    palette       : list[list[float, float, float]],
    img_dir       : Path,
) -> None:
    def make_gradient(
        colors: list[ [float, float, float] ],
        width : int = 800,
        height: int = 100
    ) -> np.ndarray:
        nbcols   = len(colors)
        gradient = np.linspace(0, 1, width)

        arr        = np.zeros((height, width, 3))
        stops      = np.linspace(0, 1, nbcols)
        rgb_colors = np.array([to_rgb(c) for c in colors])

        for i in range(3):
            arr[:, :, i] = np.interp(gradient, stops, rgb_colors[:, i])

        return arr

    def build_projname(name_n_ctxt):
        infos = palette_report[name_n_ctxt]

        if "equal-to" in infos:
            projname = infos["equal-to"]

        else:
            projname = infos["reverse-of"]

        return projname

    name_n_ctxt = namectxt(name, context)

    if name_n_ctxt in palette_report:
        projname = build_projname(name_n_ctxt)

    else:
        projname = name

    if not projname in all_palettes:
        projname = build_projname(
            namectxt(name, TAG_MPL)
        )

    leg_tested = f"'{name}' from '{context}'"

    grad_1 = make_gradient(palette)
    grad_2 = make_gradient(all_palettes[projname])
    grad_3 = make_gradient(palette[::-1])

    fig, axes = plt.subplots(3, 1, figsize=(8, 3))

    axes[0].imshow(grad_1, aspect="auto")
    axes[0].set_title(
        f"NORMAL - {leg_tested}",
        fontsize = 12,
        pad      = 8
    )
    axes[0].axis("off")

    axes[1].imshow(grad_2, aspect="auto")
    axes[1].set_title(
        f"@prism '{name}'",
        fontsize = 12,
        pad      = 8
    )
    axes[1].axis("off")

    axes[2].imshow(grad_3, aspect="auto")
    axes[2].set_title(
        f"REVERSED - {leg_tested}",
        fontsize = 12,
        pad      = 8
    )
    axes[2].axis("off")

    plt.tight_layout()

    plt.savefig(
        img_dir / f"{name}-{context}.png",
        dpi         = 200,
        bbox_inches = "tight"
    )

    return True
