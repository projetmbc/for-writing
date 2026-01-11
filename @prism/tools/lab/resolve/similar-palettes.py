#!/usr/bin/env python3

# CMD: streamlit run ...


#!/usr/bin/env python3

from pathlib import Path
import sys
import os
import signal
import streamlit as st

# ----------------------------- #
# -- IMPORT LABUTILS - START -- #
THIS_DIR = Path(__file__).parent
LAB_DIR  = THIS_DIR.parent
sys.path.append(str(LAB_DIR))

from labutils import * # Supposons que build_name_n_srcname existe
# --------------------------- #

# --- CSS & RENDU ---
def normalize_rgb(rgb):
    return [int(c*255) for c in rgb]

def generate_gradient_css(colors):
    rgb_points = [f"rgb({r},{g},{b})" for r, g, b in [normalize_rgb(c) for c in colors]]
    return f"linear-gradient(to right, {', '.join(rgb_points)})"

def generate_discrete_grid(colors, border_color):
    html = '<div style="display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 5px; max-width: 500px;">'
    for c in colors:
        r, g, b = normalize_rgb(c)
        html += f'<div style="width:30px; height:30px; flex:0 0 30px; background:rgb({r},{g},{b}); border-radius:3px; border:1px solid {border_color};"></div>'
    html += '</div>'
    return html

# --- DATA MOCK (Format d'entrée attendu) ---
# groupes_entree = { "Groupe_1": { "pal_uid_1": colors, "pal_uid_2": colors }, ... }
@st.cache_data
def load_similarity_groups():
    # Remplace ceci par ton vrai chargement de JSON
    return {
        "Cluster #01 (Blues)": {
            "Blues::COLORBREWER": [[0.1, 0.2, 0.5]] * 5,
            "Blues::TABLEAU": [[0.12, 0.22, 0.52]] * 5,
            "Ocean::MAPS": [[0.0, 0.0, 0.4]] * 5, # Faux positif potentiel
        },
        "Cluster #02 (Grays)": {
            "Gray::TABLEAU": [[0.5, 0.5, 0.5]] * 3,
            "Greys::COLORBREWER": [[0.51, 0.51, 0.51]] * 3,
        }
    }

# --- CONFIG ---
st.set_page_config(page_title="Audit Similarité", layout="wide")
groups = load_similarity_groups()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Contrôles")
    mode = st.radio("Thème", ["Sombre", "Clair"])
    st.divider()
    with st.expander("🛑 Stop"):
        if st.button("Close GUI", use_container_width=True): os.kill(os.getpid(), signal.SIGINT)

bg, txt, border = (("#1e1e1e", "#eee", "#444") if mode == "Sombre" else ("#fff", "#000", "#ccc"))
st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {txt}; }}</style>", unsafe_allow_html=True)

st.title("🤝 Vérification des Similarités")
st.info("Validez les regroupements ou excluez les faux positifs (❌).")

final_decisions = {}

# --- MAIN RENDER ---
for group_name, palettes in groups.items():
    with st.container():
        st.subheader(f"📦 {group_name}")

        # Pour chaque palette dans le groupe
        for uid, colors in palettes.items():
            # On crée une ligne pour chaque palette du groupe
            col_viz, col_sub, col_del = st.columns([6, 3, 1])

            # État : Supprimé ?
            is_deleted = st.session_state.get(f"del_{uid}", False)

            with col_viz:
                opacity = "0.2" if is_deleted else "1.0"
                st.markdown(f"<div style='opacity: {opacity}'>", unsafe_allow_html=True)
                st.markdown(f"**{uid}** ({len(colors)} pts)")
                if len(colors) <= 20:
                    st.markdown(generate_discrete_grid(colors, border), unsafe_allow_html=True)
                st.markdown(f'<div style="background:{generate_gradient_css(colors)}; height:30px; border-radius:4px; border:1px solid {border};"></div>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_sub:
                # Liste déroulante pour sous-catégoriser si besoin
                sub_cat = st.selectbox(
                    "Sous-groupe",
                    ["Principal", "Variante A", "Variante B", "Doublon exact"],
                    key=f"sub_{uid}",
                    disabled=is_deleted,
                    label_visibility="collapsed"
                )

            with col_del:
                # Bouton Croix pour éliminer
                if not is_deleted:
                    if st.button("❌", key=f"btn_del_{uid}", help="Marquer comme faux positif"):
                        st.session_state[f"del_{uid}"] = True
                        st.rerun()
                else:
                    if st.button("🔄", key=f"btn_rev_{uid}", help="Réintégrer"):
                        st.session_state[f"del_{uid}"] = False
                        st.rerun()

            # Enregistrement des données
            final_decisions[uid] = {
                "group": group_name,
                "sub_cat": sub_cat,
                "is_excluded": is_deleted
            }

        st.markdown("---")

# --- VALIDATION ---
col_save, _ = st.columns([2, 5])
with col_save:
    if st.button("💾 Enregistrer les regroupements", type="primary", use_container_width=True):
        # Ici : update_similarity_data(final_decisions)
        st.success("Données sauvegardées !")
        st.json(final_decisions)
