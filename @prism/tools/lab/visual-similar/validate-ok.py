#!/usr/bin/env python3

# CMD: streamlit run ...

import streamlit as st
import json
import numpy as np
from scipy.interpolate import interp1d

from pathlib import Path

THIS_DIR = Path(__file__).parent


st.set_page_config(page_title="Palette Similarity Explorer", layout="wide")

def local_css():
    st.markdown("""
        <style>
        .stButton button { width: 100%; }
        .alphabet-box { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 20px; }
        .palette-card {
            border: 1px solid #555; padding: 10px; border-radius: 5px;
            cursor: pointer; text-align: center; transition: 0.3s;
        }
        .palette-card:hover { border-color: #ff4b4b; background: rgba(255,75,75,0.1); }
        </style>
    """, unsafe_allow_html=True)

local_css()


# --- FONCTIONS UTILITAIRES ---
@st.cache_data
def load_data():
    with open(THIS_DIR / 'all-pals.json', 'r') as f:
        palettes = json.load(f)

    with open(THIS_DIR / 'similar-pals.json', 'r') as f:
        similarities = json.load(f)

    return palettes, similarities






def get_gradient_css(colors):
    palette = np.array(colors)
    x_old = np.linspace(0, 100, len(palette))
    x_new = np.linspace(0, 100, 50) # 50 points suffisent pour l'œil
    f = interp1d(x_old, palette, axis=0, kind='linear')
    stops = [f"rgb({int(c[0]*255)},{int(c[1]*255)},{int(c[2]*255)}) {i*2}%"
             for i, c in enumerate(f(x_new))]
    return f"linear-gradient(90deg, {', '.join(stops)})"

# --- INTERFACE ---

palettes_dict, sims_dict = load_data()

# Tri alphabétique des noms
all_names = sorted(palettes_dict.keys())
alphabet = sorted(list(set([n[0].upper() for n in all_names if n])))

st.title("🎨 Palette Similarity Manager")

# Système d'onglets pour l'alphabet
tabs = st.tabs(alphabet)

selected_palette = None

for i, char in enumerate(alphabet):
    with tabs[i]:
        # Filtrer les palettes commençant par cette lettre
        names_in_tab = [n for n in all_names if n.upper().startswith(char)]

        # Affichage en grille (4 colonnes)
        cols = st.columns(4)
        for idx, name in enumerate(names_in_tab):
            with cols[idx % 4]:
                # On utilise un bouton qui ressemble à une carte
                if st.button(name, key=f"select_{name}"):
                    st.session_state.selected_palette = name

# --- ZONE DE COMPARAISON (S'affiche si une palette est sélectionnée) ---

if "selected_palette" in st.session_state:
    target = st.session_state.selected_palette
    st.divider()
    st.header(f"Analyse de : {target}")

    # Rendu de la référence
    st.write("**Dégradé de référence :**")
    st.write(f'<div style="height: 40px; width: 100%; background: {get_gradient_css(palettes_dict[target])}; border-radius: 8px;"></div>', unsafe_allow_html=True)

    st.subheader("Candidats similaires (Superposition)")

    for match in sims_dict.get(target, []):
        m_name = match['name']
        m_score = match['score']

        with st.container():
            c1, c2, c3 = st.columns([2, 6, 1])
            with c1:
                st.write(f"**{m_name}**")
                st.caption(f"Score : {m_score:.2f}")
            with c2:
                # SUPERPOSITION
                grad_ref = get_gradient_css(palettes_dict[target])
                grad_cand = get_gradient_css(palettes_dict[m_name])
                html = f"""
                <div style="border: 1px solid #888; border-radius: 6px; overflow: hidden;">
                    <div style="height: 25px; background: {grad_ref};"></div>
                    <div style="height: 25px; background: {grad_cand}; border-top: 1px dashed white;"></div>
                </div>
                """
                st.write(html, unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key=f"del_{m_name}"):
                    st.toast(f"Marqué : {m_name}")
            st.markdown("<br>", unsafe_allow_html=True)

else:
    st.info("Cliquez sur une palette dans les onglets ci-dessus pour lancer la comparaison.")
