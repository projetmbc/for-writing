#!/usr/bin/env python3

# CMD: streamlit run ...


import streamlit as st
import json
import numpy as np
from scipy.interpolate import interp1d
from pathlib import Path

THIS_DIR = Path(__file__).parent
st.set_page_config(page_title="Palette Similarity Explorer", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .stButton button { width: 100%; }
    .divider-line { border-top: 1px dashed rgba(255,255,255,0.4); height: 0px; }
    .superpose-card { border: 1px solid #555; border-radius: 6px; overflow: hidden; margin-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- CHARGEMENT ---
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
    x_new = np.linspace(0, 100, 50)
    f = interp1d(x_old, palette, axis=0, kind='linear')
    stops = [f"rgb({int(c[0]*255)},{int(c[1]*255)},{int(c[2]*255)}) {i*2}%"
             for i, c in enumerate(f(x_new))]
    return f"linear-gradient(90deg, {', '.join(stops)})"

# --- ÉTAT ---
if "decisions" not in st.session_state:
    st.session_state.decisions = {}

palettes_dict, sims_dict = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Filtres")
    # On définit le slider ici
    score_range = st.slider("Scores acceptés", 0.0, 30.0, (0.0, 2.0), step=0.1)

    st.divider()
    if st.session_state.decisions:
        st.download_button("💾 Export JSON", json.dumps(st.session_state.decisions, indent=4), "decisions.json")

# --- LOGIQUE DE FILTRAGE CRUCIALE ---
# On calcule la liste EXACTE des palettes à afficher selon le slider
names_to_show = []
for name in palettes_dict.keys():
    # Est-ce que cette palette a des candidats dans sims_dict ?
    candidates = sims_dict.get(name, [])
    # Est-ce qu'au moins UN candidat est dans la plage de score ?
    valid_matches = [m for m in candidates if score_range[0] <= m['score'] <= score_range[1]]

    if len(valid_matches) > 0:
        names_to_show.append(name)

names_to_show.sort()

# --- INTERFACE PRINCIPALE ---
st.title("🎨 Palette Manager")

if not names_to_show:
    st.warning(f"Aucune palette trouvée avec un score entre {score_range[0]} et {score_range[1]}.")
else:
    # On crée l'alphabet uniquement à partir des noms filtrés
    current_alphabet = sorted(list(set([n[0].upper() for n in names_to_show if n])))
    tabs = st.tabs(current_alphabet)

    for i, char in enumerate(current_alphabet):
        with tabs[i]:
            # Filtrage par lettre parmi les noms déjà filtrés par score
            names_in_tab = [n for n in names_to_show if n.upper().startswith(char)]
            cols = st.columns(4)
            for idx, name in enumerate(names_in_tab):
                with cols[idx % 4]:
                    if st.button(name, key=f"btn_{name}"):
                        st.session_state.selected_palette = name

# --- ZONE D'ANALYSE ---
if "selected_palette" in st.session_state:
    target = st.session_state.selected_palette
    # On revérifie la validité des candidats pour l'affichage
    display_matches = [m for m in sims_dict.get(target, []) if score_range[0] <= m['score'] <= score_range[1]]

    if not display_matches:
        st.info("Cette palette n'a plus de candidats valides avec ces filtres.")
    else:
        st.divider()

        target_size = len(palettes_dict[target])
        st.subheader(f"Analyse de : {target} ({target_size} couleurs)")

        grad_ref = get_gradient_css(palettes_dict[target])
        st.write(f'<div style="height: 35px; background: {grad_ref}; border-radius: 5px; margin-bottom: 20px;"></div>', unsafe_allow_html=True)

        for match in display_matches:
            m_name = match['name']
            m_score = match['score']
            grad_cand = get_gradient_css(palettes_dict[m_name])

            with st.container():
                c_info, c_vis, c_choice = st.columns([2, 5, 2])
                with c_info:
                    st.write(f"**{m_name}**")
                    st.caption(f"Score : {m_score:.2f}")
                with c_vis:
                    st.write(f"""
                        <div class="superpose-card">
                            <div style="height: 25px; background: {grad_ref};"></div>
                            <div class="divider-line"></div>
                            <div style="height: 25px; background: {grad_cand};"></div>
                        </div>
                    """, unsafe_allow_html=True)
                with c_choice:
                    current_val = st.session_state.decisions.get(m_name, None)
                    sub1, sub2 = st.columns(2)
                    # On utilise des on_change pour forcer la sauvegarde immédiate
                    is_eq = sub1.checkbox("Égal", key=f"eq_{m_name}", value=(current_val == "equal"))
                    is_si = sub2.checkbox("Sim.", key=f"si_{m_name}", value=(current_val == "similar"))

                    if is_eq: st.session_state.decisions[m_name] = "equal"
                    elif is_si: st.session_state.decisions[m_name] = "similar"
                    elif m_name in st.session_state.decisions: del st.session_state.decisions[m_name]
