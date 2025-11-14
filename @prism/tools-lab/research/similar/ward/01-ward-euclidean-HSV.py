#!/usr/bin/env python3

FORCING_ALL = True
FORCING_ALL = False

from pathlib import Path
import              sys


_utils_dir_ = Path(__file__).parent

while _utils_dir_.name != "tools-lab":
    _utils_dir_ = _utils_dir_.parent

sys.path.append(str(_utils_dir_))

from labutils import *


from shutil  import rmtree

from json import load as json_load


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR     = Path(__file__).parent
CLUSTERS_DIR = THIS_DIR.parent / "clusters"
XTRA_DIR     = THIS_DIR.parent / "xtra"


PROJ_DIR = THIS_DIR

while PROJ_DIR.name != "@prism":
    PROJ_DIR = PROJ_DIR.parent


PAL_JSON_FILE   = PROJ_DIR / "products" / "json" / "palettes.json"

with PAL_JSON_FILE.open('r') as f:
    ALL_PALETTES = json_load(f)


PAL_SIMILAR_FILE = PROJ_DIR / "tools" / "report" / "PAL-SIMILAR.json"

with PAL_SIMILAR_FILE.open('r') as f:
    ALL_CLUSTERS = json_load(f)


if not CLUSTERS_DIR.is_dir():
    CLUSTERS_DIR.mkdir()

else:
    for p in CLUSTERS_DIR.glob("*"):
        p.unlink() if p.is_file() else rmtree(p)


# ---------------------------- #
# -- UNCLUSTERIZED PALETTES -- #
# ---------------------------- #

print("+ Looking for unclusterized palettes.")

if FORCING_ALL:
    print("+ Forcing all palettes.")
    newpals = list(ALL_PALETTES)

else:
    newpals = set()

    clusterized_names = sum(ALL_CLUSTERS, [])

    for n in ALL_PALETTES:
        if not n in clusterized_names:
            newpals.add(n)


    if not newpals:
        print("+ No new palette.")

        exit()

    nb_pals = len(newpals)

    plurial = "" if nb_pals == 1 else "s"

    print(f"+ {nb_pals} palette{plurial} to analyze.")


# ---------------- #
# -- CLUSTERING -- #
# ---------------- #

print("+ Clustering the palettes.")

newpals = list(newpals)
newpals.sort(key = lambda n: n.lower())

for name in newpals:
    print(name)






import numpy as np
from scipy.spatial.distance import euclidean, cosine



def create_palette_spectrum(colors):
    """Crée un vecteur de spectre de couleurs (histogramme HSV)"""
    spectrum = np.zeros(30)  # 10 pour H, 10 pour S, 10 pour V

    for r, g, b in colors:
        # Convertir en HSV
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val

        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif max_val == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360

        # Saturation
        s = 0 if max_val == 0 else diff / max_val

        # Value
        v = max_val

        # Ajouter aux bins du spectre
        h_bin = min(int(h / 36), 9)  # 10 bins pour hue (0-360)
        s_bin = min(int(s * 10), 9)   # 10 bins pour saturation (0-1)
        v_bin = min(int(v * 10), 9)   # 10 bins pour value (0-1)

        spectrum[h_bin] += 1
        spectrum[10 + s_bin] += 1
        spectrum[20 + v_bin] += 1

    # Normaliser
    return spectrum / np.linalg.norm(spectrum)



def find_similar_palettes(target_name, palettes, n=10, method='euclidean'):
    """Trouve les ALL_PALETTES les plus similaires selon leur spectre"""
    target_spectrum = create_palette_spectrum(palettes[target_name])

    similarities = []

    for name, colors in palettes.items():
        if name == target_name:
            continue

        spectrum = create_palette_spectrum(colors)

        if method == 'euclidean':
            distance = euclidean(target_spectrum, spectrum)
        else:  # cosine
            distance = cosine(target_spectrum, spectrum)

        similarities.append((name, distance))

    # Trier par similarité (distance la plus faible)
    similarities.sort(key=lambda x: x[1])

    return similarities[:n]



for name in newpals:
    blues_family = find_similar_palettes(
        name,
        ALL_PALETTES,
        n=29)

    blues_names = [name] + [name for name, _ in blues_family]

    create_palette_grid(
    blues_names,
    ALL_PALETTES,
    f"'{name}' family.",
    CLUSTERS_DIR / f'{name}.png'
    )


exit()


from scipy.cluster.hierarchy import dendrogram, linkage

from matplotlib.colors import LinearSegmentedColormap




PAL_SIMILAR_FILE = PROJ_DIR / "tools" / "report" / "PAL-CATEGO.json"
PAL_JSON_FILE   = PROJ_DIR / "products" / "json" / "palettes.json"

with PAL_JSON_FILE.open('r') as f:
    ALL_PALETTES = json_load(f)




def compare_palettes_visual(target_name, similar_palettes, palettes):
    """Crée une visualisation comparative des ALL_PALETTES similaires"""
    n_palettes = len(similar_palettes) + 1
    fig, axes = plt.subplots(n_palettes, 1, figsize=(12, n_palettes * 0.8))

    if n_palettes == 1:
        axes = [axes]

    # Palette cible
    visualize_palette(axes[0], palettes[target_name],
                     f"{target_name} (RÉFÉRENCE)")

    # ALL_PALETTES similaires
    for i, (name, distance) in enumerate(similar_palettes):
        visualize_palette(axes[i + 1], palettes[name],
                         f"{name} (distance: {distance:.4f})")

    plt.tight_layout()
    plt.savefig(CLUSTERS_DIR / 'similar-to' /f'{target_name}.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  → Image sauvegardée: similar_to_{target_name}.png")

def create_similarity_matrix(palettes, max_palettes=50):
    """Crée une matrice de similarité entre ALL_PALETTES"""
    palette_names = list(palettes.keys())[:max_palettes]
    n = len(palette_names)

    # Calculer les spectres
    spectra = {}
    for name in palette_names:
        spectra[name] = create_palette_spectrum(palettes[name])

    # Matrice de distance
    distance_matrix = np.zeros((n, n))
    for i, name1 in enumerate(palette_names):
        for j, name2 in enumerate(palette_names):
            if i != j:
                distance_matrix[i, j] = euclidean(spectra[name1], spectra[name2])

    return palette_names, distance_matrix

def visualize_similarity_matrix(palette_names, distance_matrix):
    """Visualise la matrice de similarité"""
    fig, ax = plt.subplots(figsize=(15, 15))

    im = ax.imshow(distance_matrix, cmap='viridis_r', aspect='auto')
    ax.set_xticks(range(len(palette_names)))
    ax.set_yticks(range(len(palette_names)))
    ax.set_xticklabels(palette_names, rotation=90, fontsize=6)
    ax.set_yticklabels(palette_names, fontsize=6)

    plt.colorbar(im, ax=ax, label='Distance (plus sombre = plus similaire)')
    plt.title('Matrice de Similarité des ALL_PALETTES', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(CLUSTERS_DIR / 'similarity_matrix.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  → Matrice de similarité: similarity_matrix.png")

def create_dendrogram_clustering(palettes, max_palettes=50):
    """Crée un dendrogramme pour visualiser les clusters de ALL_PALETTES"""
    palette_names, distance_matrix = create_similarity_matrix(palettes, max_palettes)

    # Clustering hiérarchique
    linkage_matrix = linkage(distance_matrix, method='ward')

    fig, ax = plt.subplots(figsize=(20, 10))
    dendrogram(linkage_matrix, labels=palette_names, ax=ax,
               leaf_font_size=8, orientation='right')

    plt.title('Clustering Hiérarchique des ALL_PALETTES (par spectre)', fontsize=14)
    plt.xlabel('Distance', fontsize=12)
    plt.tight_layout()
    plt.savefig(CLUSTERS_DIR / 'palette_dendrogram.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  → Dendrogramme: palette_dendrogram.png")


# ============================================================================
# EXÉCUTION PRINCIPALE
# ============================================================================

print("=" * 80)
print("ANALYSE DE SIMILARITÉ DES ALL_PALETTES PAR SPECTRE")
print("=" * 80)

# 1. Trouver les ALL_PALETTES similaires pour quelques exemples
print("\n1. ALL_PALETTES SIMILAIRES (exemples)")
print("-" * 80)

exemples = ['Viridis', 'Blues', 'Inferno', 'Twilight', 'Rainbow']

for palette_name in ALL_PALETTES:
    print(f"\nPalettes similaires à '{palette_name}':")
    similar = find_similar_palettes(palette_name, ALL_PALETTES, n=9)
    for i, (name, dist) in enumerate(similar, 1):
        print(f"  {i}. {name} (distance: {dist:.4f})")

    # Créer la visualisation
    compare_palettes_visual(palette_name, similar, ALL_PALETTES)

# 2. Matrice de similarité
print("\n2. MATRICE DE SIMILARITÉ")
print("-" * 80)
palette_names, distance_matrix = create_similarity_matrix(ALL_PALETTES, max_palettes=50)
visualize_similarity_matrix(palette_names, distance_matrix)

# 3. Dendrogramme de clustering
print("\n3. CLUSTERING HIÉRARCHIQUE")
print("-" * 80)
create_dendrogram_clustering(ALL_PALETTES, max_palettes=50)

# 4. Créer des grilles par famille de couleurs
print("\n4. GRILLES PAR FAMILLE")
print("-" * 80)

# Trouver des familles basées sur Blues



# Trouver des familles basées sur Reds
if 'Reds' in ALL_PALETTES:
    reds_family = find_similar_palettes('Reds', ALL_PALETTES, n=19)
    reds_names = ['Reds'] + [name for name, _ in reds_family]
    create_palette_grid(reds_names, ALL_PALETTES,
                       'Famille "Reds" (basée sur similarité spectrale)',
                       'famille_reds.png')

# 5. Sauvegarder toutes les similarités
print("\n5. SAUVEGARDE DES DONNÉES")
print("-" * 80)

all_similarities = {}
for name in ALL_PALETTES.keys():
    similar = find_similar_palettes(name, ALL_PALETTES, n=10)
    all_similarities[name] = [
        {'nom': s_name, 'distance': float(dist)}
        for s_name, dist in similar
    ]

with (CLUSTERS_DIR / 'similarities.json').open('w', encoding='utf-8') as f:
    json_dumps(all_similarities, f, indent=2, ensure_ascii=False)

print("  → Similarités sauvegardées: similarities.json")

print("\n" + "=" * 80)
print("ANALYSE TERMINÉE!")
print("=" * 80)
print("\nFichiers générés:")
print("  - similar_to_*.png : Comparaisons visuelles individuelles")
print("  - similarity_matrix.png : Matrice de similarité globale")
print("  - palette_dendrogram.png : Clustering hiérarchique")
print("  - famille_*.png : Grilles par famille de couleurs")
print("  - similarities.json : Données de similarité")
