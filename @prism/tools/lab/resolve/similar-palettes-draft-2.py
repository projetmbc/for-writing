#!/usr/bin/env python3

# CMD: streamlit run ...


import streamlit as st
import numpy as np
from scipy.spatial.distance import euclidean

# --- MOCK DATA ---
def get_mock_data():
    pals = {
        "Deep_Ocean": [(0, 0, 50), (0, 50, 150), (0, 100, 255)],
        "Abyssal_Blue": [(2, 2, 55), (0, 48, 140), (5, 95, 240)],
        "Sunset_Red": [(255, 0, 0), (255, 100, 0), (255, 200, 0)],
        "Dusk_Orange": [(240, 10, 5), (250, 95, 10), (255, 190, 5)],
        "Forest_Green": [(0, 50, 0), (0, 150, 50), (100, 255, 100)],
        "Grayscale": [(50, 50, 50), (150, 150, 150), (250, 250, 250)],
        "Soft_Gray": [(55, 55, 55), (145, 145, 145), (245, 245, 245)]
    }
    # Dupliquons un peu pour tester le batching
    for i in range(15):
        pals[f"Extra_Pal_{i}"] = [(10+i, 10, 10), (50+i, 50, 50), (100+i, 100, 100)]
    return pals

# --- MATH LOGIC ---
def resample_palette(colors, samples=5):
    colors = np.array(colors)
    n = len(colors)
    indices = np.linspace(0, n - 1, samples)
    resampled = []
    for i in indices:
        low, high = int(np.floor(i)), int(np.ceil(i))
        frac = i - low
        resampled.append((1 - frac) * colors[low] + frac * colors[high])
    return np.array(resampled)

def calculate_similarity(pal1, pal2):
    sig1 = resample_palette(pal1).flatten()
    sig2 = resample_palette(pal2).flatten()
    return euclidean(sig1, sig2)

def draw_palette_preview(colors):
    cols_html = "".join([f'<div style="background:rgb{tuple(c)}; flex:1; height:25px;"></div>' for c in colors])
    return f'<div style="display:flex; border:1px solid #444; border-radius:4px; overflow:hidden; width:100%;">{cols_html}</div>'

# --- GUI SETUP ---
st.set_page_config(page_title="Similarity Lab v2", layout="wide")

if "ignored_pairs" not in st.session_state: st.session_state.is_kept_pairs = set()
if "results" not in st.session_state: st.session_state.results = []
if "page_index" not in st.session_state: st.session_state.page_index = 0

palettes = get_mock_data()
names = list(palettes.keys())
catego_OPTIONS = ["sequential", "diverging", "qualitative", "other"]

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Analyse")
    threshold = st.slider("Seuil de tolérance", 5, 100, 30)

    if st.button("🚀 Lancer l'analyse complète", use_container_width=True):
        res = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                pair_id = tuple(sorted((names[i], names[j])))
                if pair_id in st.session_state.is_kept_pairs: continue
                dist = calculate_similarity(palettes[names[i]], palettes[names[j]])
                if dist <= threshold:
                    res.append({'p1': names[i], 'p2': names[j], 'dist': dist, 'id': pair_id})
        st.session_state.results = sorted(res, key=lambda x: x['dist'])
        st.session_state.page_index = 0

    st.divider()
    if st.button("🗑️ Reset Ignorés"):
        st.session_state.is_kept_pairs = set()
        st.rerun()

# --- MAIN CONTENT ---
st.title("🔍 Similarity Lab : Gestion des Doublons")

if st.session_state.results:
    # Filtrer les résultats qui auraient été ignorés depuis le dernier scan
    active_results = [r for r in st.session_state.results if r['id'] not in st.session_state.is_kept_pairs]

    total_found = len(active_results)
    batch_size = 10
    start_idx = st.session_state.page_index * batch_size
    end_idx = start_idx + batch_size
    current_batch = active_results[start_idx:end_idx]

    # Pagination
    col_prev, col_page, col_next = st.columns([1, 2, 1])
    with col_page:
        st.write(f"Affichage **{start_idx+1} à {min(end_idx, total_found)}** sur **{total_found}** candidats")
    with col_prev:
        if st.button("⬅️ Précédent", disabled=st.session_state.page_index == 0, use_container_width=True):
            st.session_state.page_index -= 1
            st.rerun()
    with col_next:
        if st.button("Suivant ➡️", disabled=end_idx >= total_found, use_container_width=True):
            st.session_state.page_index += 1
            st.rerun()

    st.divider()

    # Liste des candidats
    for item in current_batch:
        n1, n2, dist, pair_id = item['p1'], item['p2'], item['dist'], item['id']

        with st.container():
            c1, c2, c_act = st.columns([1, 1, 1])

            with c1:
                st.caption(f"**{n1}**")
                st.markdown(draw_palette_preview(palettes[n1]), unsafe_allow_html=True)
            with c2:
                st.caption(f"**{n2}**")
                st.markdown(draw_palette_preview(palettes[n2]), unsafe_allow_html=True)

            with c_act:
                # Actions par paire
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    if st.button("🙈 Ignorer", key=f"ign_{pair_id}"):
                        st.session_state.is_kept_pairs.add(pair_id)
                        st.rerun()
                with sub_col2:
                    st.metric("Distance", f"{dist:.1f}")

                # Choix de classe rapide
                st.selectbox("Classer les deux comme :", ["---"] + catego_OPTIONS,
                             key=f"cls_{pair_id}", label_visibility="collapsed")
            st.divider()

else:
    st.info("Utilisez la barre latérale pour lancer une analyse de similarité.")
