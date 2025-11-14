#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# -------------------- #
# -- SINGLE PALETTE -- #
# -------------------- #

def create_palette_img(
    name  : str,
    colors: [[float, float, float]],
    folder:Path
) -> None:
    fig, ax = plt.subplots(figsize=(12, 3))

    fig.suptitle(
        f'{name} - {folder.name.upper()}',
        fontsize   = 16,
        fontweight = 'bold',
    )


    for i, color in enumerate(colors):
        rect = mpatches.Rectangle(
            (i, 0), 1, 1,
            facecolor = color,
            edgecolor = 'black',
            linewidth = 2
        )

        ax.add_patch(rect)

    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-0.3, 1.4)
    ax.axis('off')

    plt.tight_layout()

    plt.savefig(
        folder / f"{name}.png",
        dpi         = 150,
        bbox_inches = 'tight',
        facecolor   = 'white'
    )

    plt.close()
