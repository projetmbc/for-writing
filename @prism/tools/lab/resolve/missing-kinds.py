#!/usr/bin/env python3

import streamlit as st
import yaml
import os
import signal

# --- DATA ---
data = {
    'Accent::COLORBREWER': [[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8],],
    'Set3::COLORBREWER': [[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],[0.49, 0.78, 0.31], [0.99, 0.41, 0.23], [1.0, 1.0, 0.6],[0.55, 0.71, 0.8], [1.0, 1.0, 0.7], [0.75, 0.5, 0.75],],
    'Gray::TABLEAU': [[0.37, 0.38, 0.41]] * 56 + [[0.81, 0.81, 0.81]],
    'Viridis::MATPLOTLIB': [[0.26, 0.0, 0.32], [0.12, 0.72, 0.54], [0.99, 0.9, 0.14]]
}











KIND_OPTIONS = ["linear", "diverging", "sequential", "qualitative", "cyclic", "scientific"]

# --- FONCTIONS DE RENDU ---
def to_rgb(c):
    return f"rgb({int(c[0]*255)},{int(c[1]*255)},{int(c[2]*255)})"

def generate_gradient_css(colors):
    rgb_pts = [to_rgb(c) for c in colors]
    return f"linear-gradient(to right, {', '.join(rgb_pts)})"

def generate_discrete_grid(colors, border_color):
    """Génère une grille de carrés (10 max par ligne)."""
    # Flex-wrap permet de passer à la ligne automatiquement
    # width: calc(10% - gap) assure exactement 10 carrés par ligne
    html = '<div style="display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 10px;">'
    for c in colors:
        html += f'''
            <div style="
                width: calc(10% - 4px);
                aspect-ratio: 1 / 1;
                background: {to_rgb(c)};
                border-radius: 3px;
                border: 1px solid {border_color};"
                title="{to_rgb(c)}">
            </div>'''
    html += '</div>'
    return html

# --- CONFIG ---
st.set_page_config(page_title="Audit Expert", layout="wide")

if "save_count" not in st.session_state:
    st.session_state.save_count = 0

# --- CALCUL DES MODIFICATIONS ---
final_report = {}
changes_detected = 0
for k in data.keys():
    val = st.session_state.get(f"m_{k}", [])
    final_report[k] = val
    if val:
        changes_detected += 1

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚡ Actions Globales")
    if st.button("🪄 Auto-Qual (≤ 20)", use_container_width=True):
        for full_key, colors in data.items():
            if len(colors) <= 20:
                curr = st.session_state.get(f"m_{full_key}", [])
                if "qualitative" not in curr:
                    curr.append("qualitative")
                    st.session_state[f"m_{full_key}"] = curr
        st.rerun()

    st.divider()
    st.header("⚙️ Paramètres")
    mode = st.radio("Thème", ["Sombre", "Clair"])

    st.divider()
    with st.expander("🛑 Danger Zone"):
        if st.button("Éteindre le Serveur", use_container_width=True, type="secondary"):
            os.kill(os.getpid(), signal.SIGINT)

# --- STYLE ---
bg, txt, border = ("#1e1e1e", "#eee", "#444") if mode == "Sombre" else ("#fff", "#000", "#ccc")
st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {txt}; }}</style>", unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.title("🏷️ Classification Multi-Kind")

for full_key in sorted(data.keys()):
    colors = data[full_key]
    name, source = full_key.split('::')
    n_colors = len(colors)

    col_info, col_kind = st.columns([3, 1])
    with col_info:
        st.markdown(f"**{name}** — `{n_colors}` pts <small>({source})</small>", unsafe_allow_html=True)

        # 1. Grille discrète si taille <= 30 (10 par ligne)
        if n_colors <= 30:
            st.markdown(generate_discrete_grid(colors, border), unsafe_allow_html=True)

        # 2. Spectre continu (plus fin, servant de référence)
        st.markdown(f'''
            <div style="background:{generate_gradient_css(colors)};
            height:8px; border-radius:4px; border:1px solid {border}; margin-bottom:25px; opacity: 0.6;">
            </div>''', unsafe_allow_html=True)

    with col_kind:
        st.multiselect("Kind", options=KIND_OPTIONS, key=f"m_{full_key}", label_visibility="collapsed")

st.divider()

# --- ZONE DE VALIDATION ---
col_btn, col_stat = st.columns([1.5, 4])

with col_btn:
    if st.button("✅ Valider l'Audit", type="primary", use_container_width=True, disabled=(changes_detected == 0)):
        csv_export = {k: ",".join(v) for k, v in final_report.items() if v}
        st.session_state.last_result = yaml.dump(csv_export, sort_keys=False, allow_unicode=True)
        st.session_state.save_count += 1
        for k in list(st.session_state.keys()):
            if k.startswith("m_"): del st.session_state[k]
        st.rerun()

with col_stat:
    if changes_detected > 0:
        st.info(f"🔄 Modification n°{st.session_state.save_count + 1} : {changes_detected} palette(s) qualifiée(s)")
    else:
        st.write(f"✨ Prêt (Dernière validation : n°{st.session_state.save_count})")

if "last_result" in st.session_state:
    st.markdown("---")
    st.subheader("📄 Dernier export généré")
    st.code(st.session_state.last_result, language='yaml')
