#!/usr/bin/env python3
"""
Analyseur de palettes de couleurs
Permet de comparer, inverser, et analyser des palettes RGB
Avec affichage Rich et visualisation Matplotlib
"""

import numpy as np
from typing import List, Tuple, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.columns import Columns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

console = Console()

class PaletteAnalyzer:
    def __init__(self, palette: List[List[float]], name: str = "Palette"):
        """
        Initialise l'analyseur avec une palette
        :param palette: Liste de couleurs RGB (valeurs entre 0 et 1)
        :param name: Nom de la palette
        """
        self.palette = np.array(palette)
        self.name = name

    def reverse(self) -> 'PaletteAnalyzer':
        """Inverse l'ordre de la palette"""
        return PaletteAnalyzer(self.palette[::-1].tolist(), f"{self.name} (inversée)")

    def invert_colors(self) -> 'PaletteAnalyzer':
        """Inverse les couleurs (1 - valeur)"""
        return PaletteAnalyzer((1 - self.palette).tolist(), f"{self.name} (couleurs inversées)")

    def compare(self, other: 'PaletteAnalyzer', tolerance: float = 0.001) -> dict:
        """
        Compare deux palettes
        :param other: Autre palette à comparer
        :param tolerance: Tolérance pour considérer deux valeurs égales
        :return: Dictionnaire avec les résultats de la comparaison
        """
        if self.palette.shape != other.palette.shape:
            return {
                'equal': False,
                'reason': 'Tailles différentes',
                'size1': len(self.palette),
                'size2': len(other.palette)
            }

        differences = np.abs(self.palette - other.palette)
        max_diff = np.max(differences)
        mean_diff = np.mean(differences)

        equal = max_diff < tolerance

        result = {
            'equal': equal,
            'max_difference': float(max_diff),
            'mean_difference': float(mean_diff),
            'tolerance': tolerance,
            'differences': differences.tolist()
        }

        if not equal:
            # Trouver les indices où les différences sont les plus grandes
            max_indices = np.where(differences == max_diff)
            result['max_diff_locations'] = list(zip(max_indices[0], max_indices[1]))

        return result

    def get_statistics(self) -> dict:
        """Calcule des statistiques sur la palette"""
        return {
            'nb_colors': len(self.palette),
            'min_value': float(np.min(self.palette)),
            'max_value': float(np.max(self.palette)),
            'mean_value': float(np.mean(self.palette)),
            'is_grayscale': self._is_grayscale(),
            'is_uniform': self._is_uniform_spacing()
        }

    def _is_grayscale(self) -> bool:
        """Vérifie si la palette est en niveaux de gris"""
        return np.allclose(self.palette[:, 0], self.palette[:, 1]) and \
               np.allclose(self.palette[:, 1], self.palette[:, 2])

    def _is_uniform_spacing(self, tolerance: float = 0.01) -> bool:
        """Vérifie si les couleurs sont uniformément espacées"""
        if not self._is_grayscale():
            return False

        values = self.palette[:, 0]
        if len(values) < 2:
            return True

        diffs = np.diff(values)
        return np.std(diffs) < tolerance

    def to_hex(self) -> List[str]:
        """Convertit la palette en codes hexadécimaux"""
        rgb_255 = (self.palette * 255).astype(int)
        return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in rgb_255]

    def to_rgb_255(self) -> List[Tuple[int, int, int]]:
        """Convertit la palette en RGB (0-255)"""
        rgb_255 = (self.palette * 255).astype(int)
        return [tuple(color) for color in rgb_255]

    def extract_channel(self, channel: int) -> List[float]:
        """
        Extrait un canal de couleur
        :param channel: 0=Rouge, 1=Vert, 2=Bleu
        """
        return self.palette[:, channel].tolist()

    def display_rich(self):
        """Affiche la palette avec Rich (carrés de couleurs unicode)"""
        colors = []
        for i, color in enumerate(self.palette):
            r, g, b = (color * 255).astype(int)
            hex_code = f"#{r:02x}{g:02x}{b:02x}"
            # Utiliser un bloc de couleur
            color_block = f"[on rgb({r},{g},{b})]    [/]"
            colors.append(f"{color_block} {hex_code}")

        table = Table(title=f"[bold cyan]{self.name}[/bold cyan]",
                     box=box.ROUNDED, show_header=False)
        table.add_column("Couleur", style="white")

        for color_display in colors:
            table.add_row(color_display)

        return table

    def print_comparison_rich(self, other: 'PaletteAnalyzer'):
        """Affiche une comparaison détaillée avec Rich"""
        console.print(f"\n[bold yellow]{'='*70}[/bold yellow]")
        console.print(f"[bold cyan]COMPARAISON: {self.name} vs {other.name}[/bold cyan]")
        console.print(f"[bold yellow]{'='*70}[/bold yellow]\n")

        comp = self.compare(other)

        # Résultat de la comparaison
        if comp['equal']:
            status = "[green]✓ IDENTIQUES[/green]"
        else:
            status = "[red]✗ DIFFÉRENTES[/red]"

        console.print(Panel(status, title="Résultat", border_style="cyan"))

        # Statistiques de comparaison
        comp_table = Table(title="Statistiques de comparaison", box=box.ROUNDED)
        comp_table.add_column("Métrique", style="cyan")
        comp_table.add_column("Valeur", style="yellow")

        comp_table.add_row("Différence maximale", f"{comp['max_difference']:.6f}")
        comp_table.add_row("Différence moyenne", f"{comp['mean_difference']:.6f}")
        comp_table.add_row("Tolérance", f"{comp['tolerance']:.6f}")

        console.print(comp_table)

        # Statistiques des palettes
        stats1 = self.get_statistics()
        stats2 = other.get_statistics()

        stats_table = Table(title="Statistiques des palettes", box=box.ROUNDED)
        stats_table.add_column("Propriété", style="cyan")
        stats_table.add_column(self.name, style="green")
        stats_table.add_column(other.name, style="magenta")

        for key in stats1.keys():
            stats_table.add_row(
                key.replace('_', ' ').title(),
                str(stats1[key]),
                str(stats2[key])
            )

        console.print(stats_table)

    def visualize_matplotlib(self, ax=None, show_values=True):
        """Visualise la palette avec Matplotlib (carrés de couleurs)"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, len(self.palette) * 0.5))

        n_colors = len(self.palette)

        for i, color in enumerate(self.palette):
            # Créer un carré de couleur
            rect = mpatches.Rectangle((0, n_colors - i - 1), 1, 1,
                                     facecolor=color, edgecolor='black', linewidth=1)
            ax.add_patch(rect)

            if show_values:
                # Ajouter le texte avec les valeurs RGB
                r, g, b = color
                text_color = 'white' if np.mean(color) < 0.5 else 'black'
                hex_code = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                rgb_text = f"RGB: ({r:.3f}, {g:.3f}, {b:.3f})"

                ax.text(0.5, n_colors - i - 0.7, hex_code,
                       ha='center', va='center', fontsize=10,
                       color=text_color, weight='bold')
                ax.text(0.5, n_colors - i - 0.3, rgb_text,
                       ha='center', va='center', fontsize=8,
                       color=text_color)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, n_colors)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(self.name, fontsize=14, weight='bold', pad=10)

        return ax

    @staticmethod
    def compare_visualize(palette1: 'PaletteAnalyzer', palette2: 'PaletteAnalyzer',
                         show_values=True, figsize=(16, 8)):
        """Compare visuellement deux palettes côte à côte"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        palette1.visualize_matplotlib(ax1, show_values)
        palette2.visualize_matplotlib(ax2, show_values)

        plt.tight_layout()
        plt.show()


# Exemple d'utilisation
if __name__ == "__main__":
    # Palette 1 (blanc vers noir)
    palette1_data = [
        [1.0, 1.0, 1.0],
        [0.929411, 0.929411, 0.929411],
        [0.858823, 0.858823, 0.858823],
        [0.788235, 0.788235, 0.788235],
        [0.713725, 0.713725, 0.713725],
        [0.643137, 0.643137, 0.643137],
        [0.572549, 0.572549, 0.572549],
        [0.498039, 0.498039, 0.498039],
        [0.42745, 0.42745, 0.42745],
        [0.356862, 0.356862, 0.356862],
        [0.286274, 0.286274, 0.286274],
        [0.211764, 0.211764, 0.211764],
        [0.141176, 0.141176, 0.141176],
        [0.070588, 0.070588, 0.070588],
        [0.0, 0.0, 0.0]
    ]

    # Palette 2 (noir vers blanc)
    palette2_data = [
        [0.0, 0.0, 0.0],
        [0.070588, 0.070588, 0.070588],
        [0.141176, 0.141176, 0.141176],
        [0.211764, 0.211764, 0.211764],
        [0.286274, 0.286274, 0.286274],
        [0.356862, 0.356862, 0.356862],
        [0.42745, 0.42745, 0.42745],
        [0.501959, 0.501959, 0.501959],
        [0.572549, 0.572549, 0.572549],
        [0.643137, 0.643137, 0.643137],
        [0.713725, 0.713725, 0.713725],
        [0.788235, 0.788235, 0.788235],
        [0.858823, 0.858823, 0.858823],
        [0.929411, 0.929411, 0.929411],
        [1.0, 1.0, 1.0]
    ]

    # Créer les analyseurs
    p1 = PaletteAnalyzer(palette1_data, "Palette 1 (Blanc→Noir)")
    p2 = PaletteAnalyzer(palette2_data, "Palette 2 (Noir→Blanc)")

    # Afficher les palettes avec Rich
    console.print("\n[bold cyan]Visualisation des palettes (Rich)[/bold cyan]\n")
    console.print(Columns([p1.display_rich(), p2.display_rich()]))

    # Comparer directement
    console.print("\n[bold magenta]Comparaison directe[/bold magenta]")
    p1.print_comparison_rich(p2)

    # Inverser palette 2 et comparer
    p2_reversed = p2.reverse()
    console.print("\n[bold magenta]Comparaison avec Palette 2 inversée[/bold magenta]")
    p1.print_comparison_rich(p2_reversed)

    # Visualisation Matplotlib
    console.print("\n[bold green]Ouverture de la visualisation Matplotlib...[/bold green]")
    PaletteAnalyzer.compare_visualize(p1, p2, show_values=True)
    PaletteAnalyzer.compare_visualize(p1, p2_reversed, show_values=True)
