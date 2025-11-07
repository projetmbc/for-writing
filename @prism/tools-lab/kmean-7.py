import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from skimage import color
from scipy.spatial.distance import cdist

from pathlib import Path

THIS_DIR = Path(__file__).parent

# Charger les données de palettes
with (THIS_DIR / 'palettes.json').open('r') as f:
    palettes = json.load(f)

def rgb_to_lab(rgb_array):
    """Convertit RGB [0,1] vers LAB (perceptuellement uniforme)"""
    # Reshape pour skimage: (n, 1, 3)
    rgb_reshaped = np.array(rgb_array).reshape(-1, 1, 3)
    lab = color.rgb2lab(rgb_reshaped)
    return lab.reshape(-1, 3)

def lab_to_rgb(lab_array):
    """Convertit LAB vers RGB [0,1]"""
    lab_reshaped = np.array(lab_array).reshape(-1, 1, 3)
    rgb = color.lab2rgb(lab_reshaped)
    return np.clip(rgb.reshape(-1, 3), 0, 1)






def calculer_caracteristiques_avancees(nom_palette):
    """Caractéristiques perceptuelles enrichies"""
    couleurs_rgb = np.array(palettes[nom_palette])
    couleurs_lab = rgb_to_lab(couleurs_rgb)

    features = []

    # Stats de base par canal LAB
    for i in range(3):  # L, A, B
        features.extend([
            couleurs_lab[:, i].mean(),
            couleurs_lab[:, i].std(),
            couleurs_lab[:, i].min(),
            couleurs_lab[:, i].max(),
            np.percentile(couleurs_lab[:, i], 25),
            np.percentile(couleurs_lab[:, i], 75),
        ])

    # Étendue (range) des valeurs
    features.extend([
        couleurs_lab[:, 0].ptp(),  # Range de luminosité
        couleurs_lab[:, 1].ptp(),  # Range A
        couleurs_lab[:, 2].ptp(),  # Range B
    ])

    # Distances entre couleurs adjacentes (contraste)
    distances_adjacentes = np.sqrt(np.sum(np.diff(couleurs_lab, axis=0)**2, axis=1))
    features.extend([
        distances_adjacentes.mean(),
        distances_adjacentes.std(),
        distances_adjacentes.max(),
    ])

    # Distance moyenne de toutes les paires
    from scipy.spatial.distance import pdist
    distances_paires = pdist(couleurs_lab, metric='euclidean')
    features.extend([
        distances_paires.mean(),
        distances_paires.std(),
    ])

    return np.array(features)




def calculer_diversite_chromatique(nom_palette):
    """Mesure la diversité et la répartition des couleurs"""
    couleurs_rgb = np.array(palettes[nom_palette])
    couleurs_lab = rgb_to_lab(couleurs_rgb)

    features = []

    # Chroma (saturation perceptuelle): sqrt(a² + b²)
    chroma = np.sqrt(couleurs_lab[:, 1]**2 + couleurs_lab[:, 2]**2)
    features.extend([
        chroma.mean(),
        chroma.std(),
        chroma.max(),
    ])

    # Hue angle: arctan2(b, a)
    hue = np.arctan2(couleurs_lab[:, 2], couleurs_lab[:, 1])
    features.extend([
        np.cos(hue).mean(),  # Composante circulaire X
        np.sin(hue).mean(),  # Composante circulaire Y
        np.std(np.diff(np.sort(hue))),  # Régularité des teintes
    ])

    # Ratio luminosité/chroma
    ratio_lum_chroma = couleurs_lab[:, 0] / (chroma + 1e-6)
    features.append(ratio_lum_chroma.mean())

    # Entropie des couleurs (diversité)
    from scipy.stats import entropy
    hist_L, _ = np.histogram(couleurs_lab[:, 0], bins=10, range=(0, 100))
    features.append(entropy(hist_L + 1))  # +1 pour éviter log(0)

    return np.array(features)


def calculer_temperature_tonalite(nom_palette):
    """Analyse la température (chaud/froid) et le mood"""
    couleurs_rgb = np.array(palettes[nom_palette])
    couleurs_lab = rgb_to_lab(couleurs_rgb)

    features = []

    # Température: dominante rouge-orange vs bleu-cyan
    # A positif = rouge, A négatif = vert
    # B positif = jaune, B négatif = bleu
    temperature = couleurs_lab[:, 1].mean() + couleurs_lab[:, 2].mean()
    features.append(temperature)

    # Balance chaud/froid (ratio)
    nb_chaud = np.sum((couleurs_lab[:, 1] > 0) & (couleurs_lab[:, 2] > 0))
    nb_froid = np.sum((couleurs_lab[:, 1] < 0) | (couleurs_lab[:, 2] < 0))
    features.append(nb_chaud / (len(couleurs_lab) + 1e-6))

    # Luminosité moyenne pondérée par chroma (couleurs vives)
    chroma = np.sqrt(couleurs_lab[:, 1]**2 + couleurs_lab[:, 2]**2)
    lum_ponderee = np.average(couleurs_lab[:, 0], weights=chroma + 1)
    features.append(lum_ponderee)

    # Dominante de teinte (catégorie majoritaire)
    hue_categories = []
    for lab in couleurs_lab:
        angle = np.arctan2(lab[2], lab[1]) * 180 / np.pi
        # Rouge: -30 à 30, Jaune: 30-90, Vert: 90-150, etc.
        hue_categories.append(angle // 60)

    from collections import Counter
    most_common = Counter(hue_categories).most_common(1)[0]
    features.append(most_common[1] / len(couleurs_lab))  # Proportion dominante

    return np.array(features)



def calculer_harmonie(nom_palette):
    """Analyse l'harmonie et l'équilibre de la palette"""
    couleurs_rgb = np.array(palettes[nom_palette])
    couleurs_lab = rgb_to_lab(couleurs_rgb)

    features = []

    # Variance du centre de gravité (équilibre)
    centroid = couleurs_lab.mean(axis=0)
    distances_au_centre = np.sqrt(np.sum((couleurs_lab - centroid)**2, axis=1))
    features.extend([
        distances_au_centre.mean(),
        distances_au_centre.std(),
    ])

    # Coefficient de variation (régularité)
    for i in range(3):
        cv = couleurs_lab[:, i].std() / (abs(couleurs_lab[:, i].mean()) + 1e-6)
        features.append(cv)

    # Symétrie chromatique (a et b)
    features.extend([
        abs(couleurs_lab[:, 1].mean()),  # Déviation du vert-rouge
        abs(couleurs_lab[:, 2].mean()),  # Déviation du bleu-jaune
    ])

    # Score d'uniformité (distances entre couleurs consécutives)
    dists = np.sqrt(np.sum(np.diff(couleurs_lab, axis=0)**2, axis=1))
    uniformite = 1 / (dists.std() + 1e-6)  # Plus uniforme = moins de variation
    features.append(uniformite)

    return np.array(features)


def calculer_contraste_lisibilite(nom_palette):
    """Évalue le contraste et la lisibilité potentielle"""
    couleurs_rgb = np.array(palettes[nom_palette])
    couleurs_lab = rgb_to_lab(couleurs_rgb)

    features = []

    # Contraste de luminosité (WCAG-like)
    L_min = couleurs_lab[:, 0].min()
    L_max = couleurs_lab[:, 0].max()
    contraste_lum = (L_max - L_min) / 100
    features.append(contraste_lum)

    # Présence de couleurs très claires/foncées
    nb_clair = np.sum(couleurs_lab[:, 0] > 80)
    nb_fonce = np.sum(couleurs_lab[:, 0] < 20)
    features.extend([nb_clair / len(couleurs_lab), nb_fonce / len(couleurs_lab)])

    # Delta E moyen entre toutes les paires (distinctivité)
    from scipy.spatial.distance import pdist
    delta_e = pdist(couleurs_lab, metric='euclidean')
    features.extend([
        delta_e.mean(),
        delta_e.min(),  # Pire cas de distinction
    ])

    # Écart-type de la luminosité (dynamique)
    features.append(couleurs_lab[:, 0].std())

    return np.array(features)



def calculer_caracteristiques_palette(nom_palette):
    """Combine toutes les métriques pertinentes"""
    return np.concatenate([
        calculer_caracteristiques_avancees(nom_palette),
        calculer_diversite_chromatique(nom_palette),
        calculer_temperature_tonalite(nom_palette),
        calculer_harmonie(nom_palette),
        calculer_contraste_lisibilite(nom_palette),
    ])

# Utilisation avec normalisation
def kmeans_palettes_optimise(n_clusters=5):
    from sklearn.preprocessing import StandardScaler

    noms_palettes = list(palettes.keys())
    X = np.array([calculer_caracteristiques_completes(nom) for nom in noms_palettes])

    # Normalisation cruciale pour K-means
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # ... reste du code




def kmeans_palettes(n_clusters=5, methode='caracteristiques'):
    """
    Applique K-means sur les palettes

    methode:
        - 'caracteristiques': utilise stats des palettes (recommandé)
        - 'couleurs': utilise directement toutes les couleurs concaténées
    """
    noms_palettes = list(palettes.keys())

    if methode == 'caracteristiques':
        # Méthode basée sur les caractéristiques statistiques
        X = np.array([calculer_caracteristiques_palette(nom) for nom in noms_palettes])
    else:
        # Méthode directe: concaténer toutes les couleurs LAB
        X = []
        for nom in noms_palettes:
            couleurs_rgb = np.array(palettes[nom])
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
    """Affiche les palettes regroupées par cluster"""
    n_clusters = len(clusters)

    for cluster_id in sorted(clusters.keys()):
        palettes_cluster = clusters[cluster_id][:max_par_cluster]
        n = len(palettes_cluster)

        print(f"\n{'='*60}")
        print(f"CLUSTER {cluster_id} ({len(clusters[cluster_id])} palettes)")
        print(f"{'='*60}")
        print(", ".join(clusters[cluster_id]))

        fig, axes = plt.subplots(n, 1, figsize=(12, n * 0.6))
        if n == 1:
            axes = [axes]

        for ax, nom in zip(axes, palettes_cluster):
            couleurs = palettes[nom]
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
    Calcule la distance perceptuelle entre deux palettes
    Utilise la distance Delta E (CIE76) en espace LAB
    """
    rgb1 = np.array(palettes[palette1])
    rgb2 = np.array(palettes[palette2])

    lab1 = rgb_to_lab(rgb1)
    lab2 = rgb_to_lab(rgb2)

    # Distance moyenne entre couleurs correspondantes
    distances = np.sqrt(np.sum((lab1 - lab2)**2, axis=1))
    return distances.mean()

def trouver_palettes_similaires(nom_palette, n=5):
    """Trouve les n palettes les plus similaires perceptuellement"""
    if nom_palette not in palettes:
        print(f"Palette '{nom_palette}' non trouvée.")
        return

    distances = {}
    for autre_nom in palettes.keys():
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
    """Affiche plusieurs palettes pour comparaison"""
    n = len(noms_palettes)
    fig, axes = plt.subplots(n, 1, figsize=(12, n * 0.6))

    if n == 1:
        axes = [axes]

    for ax, nom in zip(axes, noms_palettes):
        if nom in palettes:
            couleurs = palettes[nom]
            for i, couleur in enumerate(couleurs):
                ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=couleur))
            ax.set_xlim(0, len(couleurs))
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title(nom, fontsize=10, loc='left', fontweight='bold' if ax == axes[0] else 'normal')

    plt.tight_layout()
    plt.show()

def analyser_espace_couleur():
    """Analyse la distribution des palettes dans l'espace LAB"""
    toutes_couleurs_lab = []

    for nom in palettes.keys():
        couleurs_rgb = np.array(palettes[nom])
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

# ============= EXEMPLE D'UTILISATION =============

if __name__ == "__main__":
    print("🎨 K-MEANS SUR PALETTES DE COULEURS")
    print("=" * 60)

    # 1. Clustering des palettes
    print("\n1. Application du K-means (n_clusters=6)...")
    clusters, model = kmeans_palettes(n_clusters=6, methode='caracteristiques')

    # 2. Afficher les résultats
    print("\n2. Affichage des clusters...")
    afficher_clusters(clusters, max_par_cluster=8)

    # 3. Trouver des palettes similaires
    print("\n3. Recherche de palettes similaires à 'Viridis'...")
    trouver_palettes_similaires('Viridis', n=5)

    # 4. Analyser l'espace couleur
    print("\n4. Analyse de l'espace couleur LAB...")
    analyser_espace_couleur()

    print("\n✅ Analyse terminée!")
