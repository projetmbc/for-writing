#!/usr/bin/env python3

# CMD: streamlit run ...

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- SIMULATION DE DONNÉES (À remplacer par tes vraies listes de triplets) ---
# On crée un dictionnaire : { "Nom": [(r,g,b), (r,g,b), ...] }
@st.cache_data
def load_mock_palettes():
    palettes = {}
    # On génère 300 palettes aléatoires pour le test
    for i in range(300):
        size = np.random.randint(50, 256)
        palettes[f"Palette_{i}"] = np.random.rand(size, 3).tolist()

    # On crée une "vraie" sous-palette pour tester l'algo
    parent = np.linspace([0, 0, 0], [1, 0.5, 0], 100) # Un dégradé Orange
    palettes["PARENTE_TEST"] = parent.tolist()
    palettes["SOUS_PALETTE_CIBLE"] = parent[20:45].tolist() # Indices 20 à 44

    return palettes

# --- LOGIQUE D'EXTRACTION ---
def find_strict_subpalette(parent_rgb, sub_rgb, tol=1e-5):
    """
    Recherche sub_rgb dans parent_rgb par balayage de fenêtre.
    """
    p, s = np.array(parent_rgb), np.array(sub_rgb)
    n_p, n_s = len(p), len(s)

    if n_s > n_p: return None

    for i in range(n_p - n_s + 1):
        window = p[i : i + n_s]
        if np.allclose(window, s, atol=tol):
            return {
                "start_idx": i,
                "end_idx": i + n_s - 1,
                "range_norm": (i / (n_p - 1), (i + n_s - 1) / (n_p - 1))
            }
    return None

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Sub-Palette Finder", layout="wide")
st.title("🔍 Détecteur de Sous-Palettes Strictes")

data = load_mock_palettes()

# Sélection de la palette "Enfant" (celle qu'on cherche à caser ailleurs)
target_name = st.selectbox("Sélectionnez la sous-palette à tester :", list(data.keys()), index=len(data)-1)
target_rgb = data[target_name]

st.subheader(f"Analyse de '{target_name}' ({len(target_rgb)} couleurs)")

# Lancement du scan
results = []
for name, rgb_list in data.items():
    if name == target_name: continue
    match = find_strict_subpalette(rgb_list, target_rgb)
    if match:
        results.append({"Parent": name, **match})

# --- AFFICHAGE DES RÉSULTATS ---
if results:
    st.success(f"✅ Trouvée dans {len(results)} palettes parentes !")

    for res in results:
        with st.expander(f"Détails : {res['Parent']}", expanded=True):
            col1, col2 = st.columns([1, 3])

            with col1:
                st.metric("Plage d'indices", f"{res['start_idx']} → {res['end_idx']}")
                st.write(f"**Plage flottante :** \n `{res['range_norm'][0]:.3f}` à `{res['range_norm'][1]:.3f}`")

            with col2:
                # Visualisation comparative
                fig, ax = plt.subplots(2, 1, figsize=(8, 2))

                # Parent
                ax[0].imshow([data[res['Parent']]], aspect='auto')
                ax[0].set_title(f"Parente: {res['Parent']}", fontsize=10)
                ax[0].axis('off')
                # Rectangle pour surligner la zone trouvée
                rect = plt.Rectangle((res['start_idx']-0.5, -0.5), len(target_rgb), 1,
                                     linewidth=2, edgecolor='white', facecolor='none')
                ax[0].add_patch(rect)

                # Enfant
                ax[1].imshow([target_rgb], aspect='auto')
                ax[1].set_title("Sous-palette extraite (Cible)", fontsize=10)
                ax[1].axis('off')

                plt.tight_layout()
                st.pyplot(fig)
else:
    st.warning("❌ Cette palette n'est la sous-palette stricte d'aucune autre dans la base.")

st.divider()
st.caption("Note : La détection utilise une tolérance de 1e-5 pour les comparaisons RGB flottantes.")
