from pathlib import Path

from json import load as json_load
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

THIS_DIR     = Path(__file__).parent
CLUSTERS_DIR = THIS_DIR.parent / "clusters"

for dir in [
    MONOCHROME_DIR := CLUSTERS_DIR / "monochrome",
    BICHROME_DIR   := CLUSTERS_DIR / "bicolor",
    TRICHROME_DIR  := CLUSTERS_DIR / "tricolor",
    MULTICHROME_DIR:= CLUSTERS_DIR / "multicolor",
    RAINBOW_DIR    := CLUSTERS_DIR / "rainbow",
    BIF_VAR_DIR    := CLUSTERS_DIR / "big-var",
]:
    os.makedirs(dir, exist_ok=True)


PROJ_DIR = THIS_DIR

while PROJ_DIR.name != "@prism":
    PROJ_DIR = PROJ_DIR.parent


PAL_CATEGO_FILE = PROJ_DIR / "tools" / "report" / "PAL-CATEGO.json"
PAL_JSON_FILE   = PROJ_DIR / "products" / "json" / "palettes.json"

with PAL_JSON_FILE.open('r') as f:
    ALL_PALETTES = json_load(f)


def classify_palette_colors(palette, n_clusters):
    """Classifie les couleurs d'une palette en n clusters"""
    colors = np.array(palette)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(colors)
    distribution = Counter(labels)
    inertia = kmeans.inertia_

    return {
        'labels': labels,
        'centers': kmeans.cluster_centers_,
        'distribution': distribution,
        'inertia': inertia
    }

def is_monochrome(palette, threshold=0.08):
    """Détermine si une palette est monochrome (1 couleur)"""
    result = classify_palette_colors(palette, n_clusters=1)
    normalized_inertia = result['inertia'] / len(palette)
    return normalized_inertia < threshold, normalized_inertia, result

def is_bicolor(palette, threshold=0.15):
    """Détermine si une palette est bicolore (2 couleurs)"""
    result = classify_palette_colors(palette, n_clusters=2)
    normalized_inertia = result['inertia'] / len(palette)
    return normalized_inertia < threshold, normalized_inertia, result

def create_palette_image(name, colors, classification, inertia, result, output_path):
    """Crée une image individuelle pour une palette"""
    fig, ax = plt.subplots(figsize=(12, 3))

    # Titre avec classification
    if classification == 'monochrome':
        title_color = '#E74C3C'
        class_label = 'MONOCHROME'
    elif classification == 'bicolor':
        title_color = '#3498DB'
        class_label = 'BICOLORE'
    else:
        title_color = '#2ECC71'
        class_label = 'MULTICOLORE'

    fig.suptitle(f'{name} - {class_label}',
                 fontsize=16, fontweight='bold', color=title_color)

    # Afficher la palette
    for i, color in enumerate(colors):
        rect = mpatches.Rectangle((i, 0), 1, 1,
                                  facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)

        # Afficher les valeurs RGB
        rgb_text = f'R:{color[0]:.2f}\nG:{color[1]:.2f}\nB:{color[2]:.2f}'
        text_color = 'white' if sum(color) < 1.5 else 'black'
        ax.text(i + 0.5, 0.5, rgb_text,
               ha='center', va='center', fontsize=7,
               color=text_color, fontweight='bold')

    # Marqueurs pour les clusters (bicolore)
    if classification == 'bicolor' and result is not None:
        for j in range(2):
            cluster_indices = [i for i, label in enumerate(result['labels']) if label == j]
            if cluster_indices:
                avg_pos = np.mean(cluster_indices)
                ax.plot(avg_pos + 0.5, 1.1, 'v', color='red', markersize=15,
                       markeredgecolor='black', markeredgewidth=1)
                ax.text(avg_pos + 0.5, 1.25, f'Cluster {j+1}',
                       ha='center', fontsize=9, fontweight='bold')

                # Afficher la couleur centrale du cluster
                center = result['centers'][j]
                center_text = f'RGB({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})'
                ax.text(avg_pos + 0.5, -0.15, center_text,
                       ha='center', fontsize=8, style='italic')

    # Marqueur pour monochrome
    if classification == 'monochrome' and result is not None:
        center = result['centers'][0]
        ax.plot(5, 1.1, 'o', color='gold', markersize=20,
               markeredgecolor='black', markeredgewidth=2)
        ax.text(5, 1.25, 'Couleur centrale',
               ha='center', fontsize=9, fontweight='bold')
        center_text = f'RGB({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})'
        ax.text(5, -0.15, center_text,
               ha='center', fontsize=8, style='italic')

    # Info sur l'inertie
    ax.text(10, 0.5, f'Inertie:\n{inertia:.4f}',
           ha='center', va='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-0.3, 1.4)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

# Analyser et classifier toutes les palettes
classifications = {
    'monochrome': [],
    'bicolor': [],
    'multicolor': []
}

print("🎨 Analyse et classification des palettes...\n")

for name, colors in ALL_PALETTES.items():
    is_mono, inertia_mono, result_mono = is_monochrome(colors)
    is_bi, inertia_bi, result_bi = is_bicolor(colors)

    if is_mono:
        classification = 'monochrome'
        inertia = inertia_mono
        result = result_mono
    elif is_bi:
        classification = 'bicolor'
        inertia = inertia_bi
        result = result_bi
    else:
        classification = 'multicolor'
        inertia = inertia_mono
        result = None

    classifications[classification].append({
        'name': name,
        'colors': colors,
        'inertia': inertia,
        'result': result
    })

# Trier chaque catégorie par inertie
for cat in classifications:
    classifications[cat].sort(key=lambda x: x['inertia'])

# Générer les images pour chaque palette
total = sum(len(classifications[cat]) for cat in classifications)
counter = 0

print("📁 Génération des images...\n")

# Monochromes
for idx, palette_info in enumerate(classifications['monochrome'], 1):
    counter += 1
    filename = f"{idx:03d}_{palette_info['name']}_inertia_{palette_info['inertia']:.4f}.png"
    output_path = MONOCHROME_DIR / filename

    create_palette_image(
        palette_info['name'],
        palette_info['colors'],
        'monochrome',
        palette_info['inertia'],
        palette_info['result'],
        output_path
    )
    print(f"[{counter}/{total}] ✓ Monochrome: {palette_info['name']}")

# Bicolores
for idx, palette_info in enumerate(classifications['bicolor'], 1):
    counter += 1
    filename = f"{idx:03d}_{palette_info['name']}_inertia_{palette_info['inertia']:.4f}.png"
    output_path = BICHROME_DIR / filename

    create_palette_image(
        palette_info['name'],
        palette_info['colors'],
        'bicolor',
        palette_info['inertia'],
        palette_info['result'],
        output_path
    )
    print(f"[{counter}/{total}] ✓ Bicolore: {palette_info['name']}")

# Multicolores (top 30 pour ne pas surcharger)
for idx, palette_info in enumerate(classifications['multicolor'][:30], 1):
    counter += 1
    filename = f"{idx:03d}_{palette_info['name']}_inertia_{palette_info['inertia']:.4f}.png"
    output_path = MULTICHROME_DIR / filename

    create_palette_image(
        palette_info['name'],
        palette_info['colors'],
        'multicolor',
        palette_info['inertia'],
        palette_info['result'],
        output_path
    )
    print(f"[{counter}/{total}] ✓ Multicolore: {palette_info['name']}")

# Rapport final
print(f"\n{'='*70}")
print("📊 RAPPORT DE CLASSIFICATION")
print(f"{'='*70}")
print(f"\n📁 Structure des dossiers créés:")
print(f"   palettes_output/")
print(f"   ├── 1_monochromes/     ({len(classifications['monochrome'])} palettes)")
print(f"   ├── 2_bicolores/       ({len(classifications['bicolor'])} palettes)")
print(f"   └── 3_multicolores/    ({min(30, len(classifications['multicolor']))} palettes sur {len(classifications['multicolor'])})")

print(f"\n📈 Statistiques:")
print(f"   Total de palettes:     {len(palettes)}")
print(f"   Monochromes:           {len(classifications['monochrome'])} ({len(classifications['monochrome'])/len(palettes)*100:.1f}%)")
print(f"   Bicolores:             {len(classifications['bicolor'])} ({len(classifications['bicolor'])/len(palettes)*100:.1f}%)")
print(f"   Multicolores:          {len(classifications['multicolor'])} ({len(classifications['multicolor'])/len(palettes)*100:.1f}%)")

print(f"\n🏆 Top 5 des palettes les plus monochromes:")
for i, p in enumerate(classifications['monochrome'][:5], 1):
    print(f"   {i}. {p['name']:20s} (inertie: {p['inertia']:.6f})")

print(f"\n🏆 Top 5 des palettes les plus bicolores:")
for i, p in enumerate(classifications['bicolor'][:5], 1):
    print(f"   {i}. {p['name']:20s} (inertie: {p['inertia']:.6f})")

print(f"\n✅ Toutes les images ont été générées avec succès!")
print(f"{'='*70}\n")
