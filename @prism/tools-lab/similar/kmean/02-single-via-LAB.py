#!/usr/bin/env python3

from pathlib import Path

from json import (
    dumps as json_dumps,
    load  as json_load,
)


import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from skimage import color
from scipy.spatial.distance import cdist


THIS_DIR     = Path(__file__).parent
PROJ_DIR     = THIS_DIR.parent.parent.parent
CLUSTERS_DIR = THIS_DIR.parent / "clusters" / Path(__file__).stem

for f in CLUSTERS_DIR.glob('*'):
    f.unlink()


PAL_CATEGO_FILE = PROJ_DIR / "tools" / "report" / "PAL-SIMILAR.json"

with PAL_CATEGO_FILE.open('r') as f:
    ALL_CATEGOS = json_load(f)

IN_CLUSTERS = [
    n
    for c in ALL_CATEGOS
    for n in c
]

PAL_JSON_FILE   = PROJ_DIR / "products" / "json" / "palettes.json"

with PAL_JSON_FILE.open('r') as f:
    ALL_PALETTES = json_load(f)


def rgb_to_lab(rgb_array):
    rgb_reshaped = np.array(rgb_array).reshape(-1, 1, 3)
    lab          = color.rgb2lab(rgb_reshaped)

    return lab.reshape(-1, 3)


def lab_to_rgb(lab_array):
    lab_reshaped = np.array(lab_array).reshape(-1, 1, 3)
    rgb          = color.lab2rgb(lab_reshaped)

    return np.clip(rgb.reshape(-1, 3), 0, 1)


def calculer_caracteristiques_palette(nom_palette):
    couleurs_rgb = np.array(ALL_PALETTES[nom_palette])
    couleurs_lab = rgb_to_lab(couleurs_rgb)

    features = np.concatenate([
        couleurs_lab.mean(axis=0),  # Moyenne L, A, B
        couleurs_lab.std(axis=0),   # Écart-type L, A, B
        couleurs_lab.min(axis=0),   # Min L, A, B
        couleurs_lab.max(axis=0),   # Max L, A, B
        couleurs_lab.flatten()      # Toutes les couleurs
    ])

    return features

def kmeans_palettes(n_clusters=5, methode='caracteristiques'):
    noms_palettes = list(ALL_PALETTES.keys())

    if methode == 'caracteristiques':
        # Méthode basée sur les caractéristiques statistiques
        X = np.array([calculer_caracteristiques_palette(nom) for nom in noms_palettes])
    else:
        # Méthode directe: concaténer toutes les couleurs LAB
        X = []
        for nom in noms_palettes:
            couleurs_rgb = np.array(ALL_PALETTES[nom])
            couleurs_lab = rgb_to_lab(couleurs_rgb)
            X.append(couleurs_lab.flatten())
        X = np.array(X)

    # K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    # Organiser les résultats
    clusters = {}
    for i, nom in enumerate(noms_palettes):
        cluster_id = labels[i]
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(nom)

    return clusters, kmeans

def afficher_clusters(clusters, max_par_cluster=10):
    """Affiche les ALL_PALETTES regroupées par cluster"""
    n_clusters = len(clusters)

    for cluster_id in sorted(clusters.keys()):
        palettes_cluster = clusters[cluster_id]#[:max_par_cluster]
        n = len(palettes_cluster)

        print(f"\n{'='*60}")
        print(f"CLUSTER {cluster_id} ({len(clusters[cluster_id])} ALL_PALETTES)")
        print(f"{'='*60}")
        print(", ".join(clusters[cluster_id]))

        fig, axes = plt.subplots(n, 1, figsize=(12, n * 0.6))
        if n == 1:
            axes = [axes]

        for ax, nom in zip(axes, palettes_cluster):
            couleurs = ALL_PALETTES[nom]
            for i, couleur in enumerate(couleurs):
                ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=couleur))
            ax.set_xlim(0, len(couleurs))
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title(nom, fontsize=9, loc='left')

        plt.suptitle(f'Cluster {cluster_id}', fontsize=12, fontweight='bold')
        plt.tight_layout()
        plt.show()

def distance_perceptuelle(palette1, palette2):
    """
    Calcule la distance perceptuelle entre deux ALL_PALETTES
    Utilise la distance Delta E (CIE76) en espace LAB
    """
    rgb1 = np.array(ALL_PALETTES[palette1])
    rgb2 = np.array(ALL_PALETTES[palette2])

    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)

    # Distance moyenne entre couleurs correspondantes
    distances = np.sqrt(np.sum((lab1 - lab2)**2, axis=1))
    return distances.mean()

def trouver_palettes_similaires(nom_palette, n=5):
    """Trouve les n ALL_PALETTES les plus similaires perceptuellement"""
    if nom_palette not in ALL_PALETTES:
        print(f"Palette '{nom_palette}' non trouvée.")
        return

    distances = {}
    for autre_nom in ALL_PALETTES.keys():
        if autre_nom != nom_palette:
            distances[autre_nom] = distance_perceptuelle(nom_palette, autre_nom)

    # Trier par distance
    similaires = sorted(distances.items(), key=lambda x: x[1])[:n]

    print(f"\nPalettes similaires à '{nom_palette}':")
    print("-" * 50)
    for nom, dist in similaires:
        print(f"{nom:20s} - Distance: {dist:.2f}")

    # Visualiser
    noms_a_afficher = [nom_palette] + [nom for nom, _ in similaires]
    visualiser_comparaison(noms_a_afficher)

def visualiser_comparaison(noms_palettes):
    """Affiche plusieurs ALL_PALETTES pour comparaison"""
    n = len(noms_palettes)
    fig, axes = plt.subplots(n, 1, figsize=(12, n * 0.6))

    if n == 1:
        axes = [axes]

    for ax, nom in zip(axes, noms_palettes):
        if nom in ALL_PALETTES:
            couleurs = ALL_PALETTES[nom]
            for i, couleur in enumerate(couleurs):
                ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=couleur))
            ax.set_xlim(0, len(couleurs))
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title(nom, fontsize=10, loc='left', fontweight='bold' if ax == axes[0] else 'normal')

    plt.tight_layout()
    plt.show()

def enregistrer_clusters(clusters, dossier_sortie="clusters", max_par_cluster=None):
    """
    Enregistre les rendus matplotlib de chaque cluster dans un dossier.
    Chaque fichier sera nommé `cluster_<id>.png`
    """
    import os
    os.makedirs(dossier_sortie, exist_ok=True)

    n_clusters = len(clusters)

    for cluster_id in sorted(clusters.keys()):
        palettes_cluster = clusters[cluster_id][:max_par_cluster] if max_par_cluster else clusters[cluster_id]
        n = len(palettes_cluster)

        print(f"\n💾 Enregistrement du cluster {cluster_id} ({n} palettes)...")

        fig, axes = plt.subplots(n, 1, figsize=(12, n * 0.6))
        if n == 1:
            axes = [axes]

        for ax, nom in zip(axes, palettes_cluster):
            couleurs = ALL_PALETTES[nom]
            for i, couleur in enumerate(couleurs):
                ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=couleur))
            ax.set_xlim(0, len(couleurs))
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title(nom, fontsize=9, loc='left')

        plt.suptitle(f'Cluster {cluster_id}', fontsize=12, fontweight='bold')
        plt.tight_layout()

        chemin_fichier = os.path.join(dossier_sortie, f"cluster_{cluster_id}.png")
        plt.savefig(chemin_fichier, dpi=150, bbox_inches='tight')
        plt.close(fig)  # Important : libère la mémoire

    print(f"\n✅ Tous les clusters ont été enregistrés dans le dossier '{dossier_sortie}'")



def analyser_espace_couleur():
    """Analyse la distribution des ALL_PALETTES dans l'espace LAB"""
    toutes_couleurs_lab = []

    for nom in ALL_PALETTES.keys():
        couleurs_rgb = np.array(ALL_PALETTES[nom])
        couleurs_lab = rgb_to_lab(couleurs_rgb)
        toutes_couleurs_lab.append(couleurs_lab)

    toutes_couleurs_lab = np.vstack(toutes_couleurs_lab)

    # Visualisation 3D
    fig = plt.figure(figsize=(12, 4))

    # L vs A
    ax1 = fig.add_subplot(131)
    ax1.scatter(toutes_couleurs_lab[:, 1], toutes_couleurs_lab[:, 0],
                alpha=0.3, s=10, c=lab_to_rgb(toutes_couleurs_lab))
    ax1.set_xlabel('A (vert-rouge)')
    ax1.set_ylabel('L (luminosité)')
    ax1.set_title('Espace LAB: L vs A')
    ax1.grid(True, alpha=0.3)

    # L vs B
    ax2 = fig.add_subplot(132)
    ax2.scatter(toutes_couleurs_lab[:, 2], toutes_couleurs_lab[:, 0],
                alpha=0.3, s=10, c=lab_to_rgb(toutes_couleurs_lab))
    ax2.set_xlabel('B (bleu-jaune)')
    ax2.set_ylabel('L (luminosité)')
    ax2.set_title('Espace LAB: L vs B')
    ax2.grid(True, alpha=0.3)

    # A vs B
    ax3 = fig.add_subplot(133)
    ax3.scatter(toutes_couleurs_lab[:, 1], toutes_couleurs_lab[:, 2],
                alpha=0.3, s=10, c=lab_to_rgb(toutes_couleurs_lab))
    ax3.set_xlabel('A (vert-rouge)')
    ax3.set_ylabel('B (bleu-jaune)')
    ax3.set_title('Espace LAB: A vs B')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

def enregistrer_palettes_similaires(nom_palette, dossier_sortie, n=5, allready_clustered =set()):
    """
    Trouve les n palettes les plus similaires perceptuellement
    et enregistre la comparaison dans un fichier PNG.
    """
    import os
    os.makedirs(dossier_sortie, exist_ok=True)

    if nom_palette not in ALL_PALETTES:
        print(f"❌ Palette '{nom_palette}' non trouvée.")
        return

    # Calculer les distances perceptuelles
    distances = {}
    for autre_nom in ALL_PALETTES.keys():
        if autre_nom in allready_clustered:
            continue

        if autre_nom != nom_palette:
            distances[autre_nom] = distance_perceptuelle(nom_palette, autre_nom)

    # Trier par distance croissante
    similaires = sorted(distances.items(), key=lambda x: x[1])[:n]

    print(f"\n🔎 Palettes similaires à '{nom_palette}':")
    print("-" * 50)
    for nom, dist in similaires:
        print(f"{nom:20s} - Distance: {dist:.2f}")

    # Noms à visualiser (la palette de référence + les similaires)
    noms_a_afficher = [nom_palette] + [nom for nom, _ in similaires]
    n_total = len(noms_a_afficher)

    # Création du rendu
    fig, axes = plt.subplots(n_total, 1, figsize=(12, n_total * 0.6))
    if n_total == 1:
        axes = [axes]

    for ax, nom in zip(axes, noms_a_afficher):
        if nom in ALL_PALETTES:
            couleurs = ALL_PALETTES[nom]
            for i, couleur in enumerate(couleurs):
                ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=couleur))
            ax.set_xlim(0, len(couleurs))
            ax.set_ylim(0, 1)
            ax.axis('off')
            title_style = dict(fontsize=10, loc='left')
            if nom == nom_palette:
                title_style['fontweight'] = 'bold'
            ax.set_title(nom, **title_style)

    plt.suptitle(f"Palettes similaires à '{nom_palette}'", fontsize=12, fontweight='bold')
    plt.tight_layout()

    # Enregistrement
    chemin_fichier = os.path.join(dossier_sortie, f"sim_{nom_palette}.png")
    plt.savefig(chemin_fichier, dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f"💾 Image enregistrée : {chemin_fichier}")

    return set(n for n, _ in similaires)

# ============= EXEMPLE D'UTILISATION =============

if __name__ == "__main__":
    print("🎨 K-MEANS SUR ALL_PALETTES DE COULEURS")
    print("=" * 60)

    # 1. Clustering des ALL_PALETTES
    print("\n1. Application du K-means (n_clusters=6)...")
    clusters, model = kmeans_palettes(n_clusters=6, methode='caracteristiques')

    # # 2. Afficher les résultats
    # print("\n2. Affichage des clusters...")
    # afficher_clusters(clusters, max_par_cluster=8)

    # print("\n2. Enregistrement des clusters...")
    # enregistrer_clusters(clusters, dossier_sortie=CLUSTERS_DIR)

    # 3. Trouver des ALL_PALETTES similaires
    # print("\n3. Recherche de ALL_PALETTES similaires à 'Viridis'...")
    # trouver_palettes_similaires('Rainbow', n=5)

    # # 4. Analyser l'espace couleur
    # print("\n4. Analyse de l'espace couleur LAB...")
    # analyser_espace_couleur()

    # print("\n✅ Analyse terminée!")

    allready_clustered = set()

    nb_clusters = 0

    for name in ALL_PALETTES:
        if name in IN_CLUSTERS:
            continue

        nb_clusters += 1

        new_cluster = enregistrer_palettes_similaires(name, CLUSTERS_DIR, 10)
