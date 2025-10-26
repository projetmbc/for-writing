#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
import numpy             as np

from matplotlib.colors import to_rgb


def report_gradient_clash(
    existing_palette: list[list[float, float, float]],
    contrib_palette : list[list[float, float, float]],
    palette_name    : str,
    img_path        : Path
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

    grad_1 = make_gradient(existing_palette)
    grad_2 = make_gradient(contrib_palette)

    fig, axes = plt.subplots(2, 1, figsize=(8, 3))

    axes[0].imshow(grad_1, aspect="auto")
    axes[0].set_title(
        f"Existing palette '{palette_name}'",
        fontsize = 12,
        pad      = 8
    )
    axes[0].axis("off")

    axes[1].imshow(grad_2, aspect="auto")
    axes[1].set_title(
        f"Candidate '{palette_name}'",
        fontsize = 12,
        pad      = 8
    )
    axes[1].axis("off")

    plt.tight_layout()

    plt.savefig(
        img_path,
        dpi         = 200,
        bbox_inches = "tight"
    )
