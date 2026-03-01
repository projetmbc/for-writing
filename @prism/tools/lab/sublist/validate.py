#!/usr/bin/env python3

# CMD: streamlit run ...

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- LOGIQUE DE RECHERCHE MULTI-INDEX ---
def scanner_associations_exhaustif(bibliotheque, tolerance=1e-5):
    associations = []
    noms = list(bibliotheque.keys())

    for nom_cible in noms:
        cible = np.array(bibliotheque[nom_cible])
        n_c = len(cible)

        for nom_parent, donnees_parent in bibliotheque.items():
            if nom_cible == nom_parent: continue

            parent = np.array(donnees_parent)
            n_p = len(parent)
            if n_c > n_p: continue

            # On cherche TOUTES les positions de début
            for start_idx in range(n_p - n_c + 1):
                fenetre = parent[start_idx : start_idx + n_c]
                if np.allclose(fenetre, cible, atol=tolerance):
                    associations.append({
                        "enfant": nom_cible,
                        "parent": nom_parent,
                        "debut": start_idx,
                        "fin": start_idx + n_c - 1,
                        "data_enfant": bibliotheque[nom_cible],
                        "data_parent": donnees_parent
                    })
    return associations

# --- AFFICHAGE HYBRIDE (Carrés si petit, Ligne si grand) ---
def dessiner_palette_adaptative(rgb_list, titre, highlight=None):
    n = len(rgb_list)
    # Si n > 50, on utilise imshow pour la fluidité, sinon des carrés
    fig, ax = plt.subplots(figsize=(10, 0.8))

    data_plot = np.array(rgb_list).reshape(1, n, 3)
    ax.imshow(data_plot, aspect='auto', extent=[-0.5, n-0.5, -0.5, 0.5])

    if highlight:
        # On dessine un rectangle de sélection
        rect_width = highlight[1] - highlight[0] + 1
        rect = plt.Rectangle((highlight[0]-0.5, -0.5), rect_width, 1,
                              fill=False, edgecolor='white', lw=3)
        ax.add_patch(rect)
        # Ombre portée pour le contraste sur couleurs claires
        rect_out = plt.Rectangle((highlight[0]-0.5, -0.5), rect_width, 1,
                                  fill=False, edgecolor='black', lw=1)
        ax.add_patch(rect_out)

    ax.set_title(titre, fontsize=9, loc='left')
    ax.set_yticks([])
    # On n'affiche les chiffres que si la palette n'est pas trop dense
    if n <= 50:
        ax.set_xticks(range(n))
        ax.tick_params(labelsize=7)
    else:
        ax.set_xticks([0, n//2, n-1])

    return fig

# --- INTERFACE ---
st.set_page_config(layout="wide")
st.title("Validateur de Structure Modulaire Haute Résolution")

# Simulation de données 256 couleurs
if 'palettes' not in st.session_state:
    lib = {}
    # Une palette parente de 256 couleurs (dégradé complexe)
    base = [plt.cm.turbo(x/255)[:3] for x in range(256)]
    lib["source_master_256"] = base
    # Une sous-palette qui apparaît deux fois (si on duplique des segments)
    lib["segment_extrait"] = base[50:100]

    # Ajout de 300 palettes bidon pour tester la charge
    for i in range(298):
        lib[f"random_{i}"] = np.random.rand(256, 3).tolist()

    st.session_state.palettes = lib

if st.button("Lancer le Scan Exhaustif"):
    results = scanner_associations_exhaustif(st.session_state.palettes)

    if results:
        st.success("Last Main Comparison complies to the new modular format")
        st.info(f"{len(results)} occurrences trouvées.")

        for res in results:
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.pyplot(dessiner_palette_adaptative(res['data_enfant'], f"Enfant : {res['enfant']}"))
                with c2:
                    st.pyplot(dessiner_palette_adaptative(res['data_parent'],
                                                        f"Parent : {res['parent']} (Position {res['debut']} à {res['fin']})",
                                                        highlight=(res['debut'], res['fin'])))
    else:
        st.error("Aucune correspondance.")
