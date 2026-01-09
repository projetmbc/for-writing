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


# ------------------ #
# -- PALETTE GRID -- #
# ------------------ #

def visualize_palette(ax, colors, title):
    """Visualise une palette de couleurs"""
    ax.imshow([colors], aspect='auto')
    ax.set_title(title, fontsize=10)
    ax.axis('off')


def create_palette_grid(
    palnames: [str],
    palettes: [[float, float, float]],
    title   : str,
    file_   : Path,
) -> None:
    n = len(palnames)

    cols = 5
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(
        rows, cols,
        figsize = (15, rows * 1.2)
    )

    axes = (
        axes.flatten()
        if rows > 1 else
        [axes]
        if cols == 1 else
        axes
    )

    for i, name in enumerate(palnames):
        if i < len(axes):
            visualize_palette(
                axes[i],
                palettes[name],
                name
            )

    for i in range(len(palnames), len(axes)):
        axes[i].axis('off')

    plt.suptitle(
        title,
        y        = 1.02,
        fontsize = 16,
    )

    plt.tight_layout()

    plt.savefig(
        file_,
        dpi         = 150,
        bbox_inches = 'tight'
    )

    plt.close()
