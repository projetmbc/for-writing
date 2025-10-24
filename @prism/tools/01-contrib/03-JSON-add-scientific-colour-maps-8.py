#!/usr/bin/env python3

# Source code.
#     + https://www.fabiocrameri.ch/colourmaps

from pathlib import Path
import              sys

sys.path.append(str(Path(__file__).parent.parent))

from cbutils.core import *
from cbutils      import *

import numpy as np


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR            = Path(__file__).parent
PROJECT_DIR         = THIS_DIR.parent.parent
PRODUCTS_DIR        = PROJECT_DIR / "products"
SCI_COL_MAP_SRC_DIR = THIS_DIR / "ScientificColourMaps8"

PAL_JSON_FILE   = PRODUCTS_DIR / "palettes.json"


PATTERN_CMP_LIST = re.compile(
    r'cm_data\s*=\s*(\[\[.*?\]\])',
    re.DOTALL
)


# ----------- #
# -- TOOLS -- #
# ----------- #


# --------------------- #
# -- GET SOURCE CODE -- #
# --------------------- #



def lire_palette_python(fichier_path):
    with open(fichier_path, 'r', encoding='utf-8') as f:
        contenu = f.read()

    # Chercher cm_data = [[...]]
    match = re.search(r'cm_data\s*=\s*(\[\[.*?\]\])', contenu, re.DOTALL)

    if not match:
        raise ValueError("cm_data non trouvé dans le fichier")

    # Évaluer la liste
    cm_data_str = match.group(1)
    couleurs = eval(cm_data_str)

    return couleurs


def creer_palette_reduite(couleurs_rgb, n_couleurs=15):
    """
    Crée une palette réduite en échantillonnant uniformément.

    Args:
        couleurs_rgb: Liste de couleurs RGB dans [0, 1]
        n_couleurs: Nombre de couleurs dans la palette réduite

    Returns:
        Liste de couleurs RGB dans [0, 1]
    """
    n_total = len(couleurs_rgb)

    # Échantillonnage uniforme
    indices = np.linspace(0, n_total - 1, n_couleurs, dtype=int)
    palette_reduite = [couleurs_rgb[i] for i in indices]

    return palette_reduite


def sauvegarder_lua(palette, fichier_sortie, nom_palette="palette"):
    """
    Sauvegarde la palette au format Lua.

    Args:
        palette: Liste de couleurs RGB
        fichier_sortie: Nom du fichier de sortie
        nom_palette: Nom de la palette (pour les commentaires)
    """
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        f.write(f"-- Palette {nom_palette} ({len(palette)} couleurs)\n")
        f.write("-- Format RGB normalisé [0, 1]\n\n")
        f.write("local palette = {\n")
        for couleur in palette:
            f.write(f"    {{{couleur[0]:.6f}, {couleur[1]:.6f}, {couleur[2]:.6f}}},\n")
        f.write("}\n\n")
        f.write("return palette\n")


# Programme principal
if __name__ == "__main__":
    # Nom du fichier d'entrée
    fichier_entree = "palette.py"
    n_couleurs = 15

    # Permettre de spécifier le fichier en argument
    if len(sys.argv) > 1:
        fichier_entree = sys.argv[1]
    if len(sys.argv) > 2:
        n_couleurs = int(sys.argv[2])

    try:
        # Lire la palette depuis le fichier Python
        print(f"Lecture de '{fichier_entree}'...")
        couleurs = lire_palette_python(fichier_entree)
        print(f"✓ Palette complète chargée : {len(couleurs)} couleurs")

        # Créer la palette réduite
        palette_reduite = creer_palette_reduite(couleurs, n_couleurs=n_couleurs)
        print(f"✓ Palette réduite à {len(palette_reduite)} couleurs")

        # Affichage format Lua
        print("\nFormat Lua :")
        print("-" * 50)
        print("local palette = {")
        for i, couleur in enumerate(palette_reduite):
            print(f"    {{{couleur[0]:.6f}, {couleur[1]:.6f}, {couleur[2]:.6f}}},  -- {i+1}")
        print("}")
        print("\nreturn palette")

        # Sauvegarder dans un fichier Lua
        fichier_sortie = f"palette_{n_couleurs}.lua"
        sauvegarder_lua(palette_reduite, fichier_sortie, "Managua")
        print(f"\n✓ Fichier '{fichier_sortie}' créé avec succès !")

    except FileNotFoundError:
        print(f"✗ Erreur : Le fichier '{fichier_entree}' n'existe pas")
    except ValueError as e:
        print(f"✗ Erreur : {e}")
    except Exception as e:
        print(f"✗ Erreur inattendue : {e}")
