#!/usr/bin/env python3

# CMD: streamlit run ...

# -- DEBUG - ON -- #
# from rich import print
# -- DEBUG - OFF -- #

# ----------------------------- #
# -- IMPORT LABUTILS - START -- #

from pathlib import Path
import              sys

THIS_DIR = Path(__file__).parent
LAB_DIR  = THIS_DIR.parent

sys.path.append(str(LAB_DIR))

from labutils import *

# -- IMPORT LABUTILS - END -- #
# --------------------------- #


#!/usr/bin/env python3

import streamlit as st
import yaml

# --- DONNÉES ---
data = {
    'Accent::COLORBREWER': [[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6]], # Taille 3
    'Set3::COLORBREWER': [[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75]],   # Taille 3
    'Gray::TABLEAU': [[0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.37, 0.38, 0.41], [0.81, 0.81, 0.81]],                      # Taille 2
    'Viridis::MATPLOTLIB': [[0.26, 0.0, 0.32], [0.12, 0.72, 0.54], [0.99, 0.9, 0.14]] # Taille 3 (mais pourrait être 256)
}

KIND_OPTIONS = ["linear", "diverging", "sequential", "qualitative", "cyclic", "scientific"]

def generate_gradient_css(colors):
    rgb_pts = [f"rgb({int(c[0]*255)},{int(c[1]*255)},{int(c[2]*255)})" for c in colors]
    return f"linear-gradient(to right, {', '.join(rgb_pts)})"

st.set_page_config(page_title="Classification Experte", layout="wide")

# --- SIDEBAR & ACTIONS GLOBALES ---
with st.sidebar:
    st.title("Actions Globales")

    # BOUTON MAGIQUE
    if st.button("🪄 Auto-Qual (taille ≤ 20)", help="Assigne 'qualitative' à toutes les petites palettes"):
        for full_key, colors in data.items():
            if len(colors) <= 20:
                # On récupère la liste actuelle dans le session_state
                current_selection = st.session_state.get(f"m_{full_key}", [])
                if "qualitative" not in current_selection:
                    current_selection.append("qualitative")
                    st.session_state[f"m_{full_key}"] = current_selection
        st.rerun()

    st.divider()
    st.caption("Paramètres")
    mode = st.radio("Thème", ["Sombre", "Clair"])

# --- STYLE ---
bg, txt = ("#1e1e1e", "#eeeeee") if mode == "Sombre" else ("#ffffff", "#000000")
st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {txt}; }}</style>", unsafe_allow_html=True)

st.title("🏷️ Classification Multi-Kind")

final_report = {}

# --- RENDU DES LIGNES ---
for full_key in sorted(data.keys()):
    colors = data[full_key]
    name, source = full_key.split('::')
    n_colors = len(colors)

    with st.container():
        col_info, col_kind = st.columns([3, 1])

        with col_info:
            st.markdown(f"**{name}** <small>({source}) — {n_colors} pts</small>", unsafe_allow_html=True)
            st.markdown(f'''
                <div style="background:{generate_gradient_css(colors)};
                height:25px; border-radius:4px; border:1px solid #444; margin-bottom:20px;">
                </div>''', unsafe_allow_html=True)

        with col_kind:
            # Multiselect lié au session_state
            kinds = st.multiselect(
                f"Kinds pour {full_key}",
                options=KIND_OPTIONS,
                key=f"m_{full_key}",
                label_visibility="collapsed"
            )
            final_report[full_key] = kinds

st.divider()

# --- EXPORT ---
if st.button("✅ Valider et générer le YAML (CSV format)"):
    # Conversion finale : listes -> chaînes CSV
    csv_export = {k: ",".join(v) for k, v in final_report.items()}

    st.success("Audit terminé. Voici le dictionnaire résultant :")
    st.code(yaml.dump(csv_export, sort_keys=False, allow_unicode=True), language='yaml')
