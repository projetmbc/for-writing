#!/usr/bin/env python3

import os
import sys
import signal
import yaml
import json
from pathlib import Path
import streamlit as st

# --- IMPORT LABUTILS ---
THIS_DIR = Path(__file__).parent
LAB_DIR  = THIS_DIR.parent
sys.path.append(str(LAB_DIR))
from labutils import * # --- CONFIG & PATHS ---
AUTO_QUAL_CATEGO_SIZE = 40
CONFIG_DIR = LAB_DIR.parent / 'config'
AUDIT_DIR  = LAB_DIR.parent / "building" / "audit"
REPORT_DIR = AUDIT_DIR.parent / "REPORT"
HUMAN_KIND_YAML   = AUDIT_DIR / "HUMAN-KIND.yaml"
MISSING_KIND_JSON = REPORT_DIR / "AUDIT-MISSING-KIND.json"

with (CONFIG_DIR / 'METADATA.yaml').open(mode='r') as f:
    METADATA = yaml.safe_load(f)
KIND_OPTIONS = sorted(list(METADATA['CATEGORY']))

# --- FUNCTIONS ---
def update_data(new_entries):
    data = {}

    if HUMAN_KIND_YAML.exists():
        with HUMAN_KIND_YAML.open('r', encoding='utf-8') as f:

            existing = yaml.safe_load(f)

            if existing:
                data = existing

    for uid, kinds in new_entries.items():
        name, _ = extract_name_n_srcname(uid)

        data[name] = '|'.join(sorted(kinds))

    data = get_sorted_dict(data)

    with HUMAN_KIND_YAML.open('w', encoding='utf-8') as f:
        yaml.dump(data, f)

@st.cache_data
def load_all_data():
    with MISSING_KIND_JSON.open("r") as f:
        conflicts = json_load(f)

    palgrps, json_cache = {}, {}

    for uid, aprism_name in conflicts:
        name, src = extract_name_n_srcname(uid)

        src = src.upper()

        if src not in json_cache:
            with (REPORT_DIR / f"{src}.json").open('r') as f:
                json_cache[src] = json_load(f)

        for n in json_cache[src]:
            if n.lower() == name.lower():
                palgrps[aprism_name] = {
                    src: json_cache[src][n][TAG_RGB_COLS]
                }

    return palgrps

# --- INITIALIZATION ---
st.set_page_config(page_title="Audit @prism - Types", layout="wide")
palgrps = load_all_data()

# --- 1. PRE-CALCULATION (Crucial pour le bouton Save) ---
# On calcule l'état des changements AVANT de dessiner la sidebar
final_report = {}
nbchges_made = 0

for name, sources in palgrps.items():
    for src, colors in sources.items():
        uid = build_name_n_srcname(name, src)
        # On regarde si une valeur existe déjà en session pour cette clé
        current_val = st.session_state.get(f"k_{uid}", [])
        if current_val:
            final_report[uid] = current_val
            nbchges_made += 1

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("⚡ Actions")

    if st.button(f"🪄 Auto-Assign ({AUTO_QUAL_CATEGO_SIZE})", use_container_width=True):
        for name, sources in palgrps.items():
            for src, colors in sources.items():
                uid = build_name_n_srcname(name, src)
                st.session_state[f"k_{uid}"] = ["qualitative"] if len(colors) <= AUTO_QUAL_CATEGO_SIZE else ["sequential"]
        st.rerun()

    st.divider()

    col_btn, col_stat = st.columns([1, 1])
    with col_btn:
        # Le bouton est maintenant correctement activé car nbchges_made est calculé plus haut
        save_trigger = st.button(
            "💾 SAUVER",
            type="primary",
            use_container_width=True,
            disabled=(nbchges_made == 0)
        )

    with col_stat:
        if nbchges_made > 0:
            st.warning(f"**{nbchges_made}** modifs")
        else:
            st.caption("À jour")

    st.divider()
    st.header("⚙️ Style")
    mode = st.radio("Thème", [GUI_TAG_DARK, GUI_TAG_LIGHT], label_visibility="collapsed")

    if st.expander("🛑 Stop").button("Close GUI", use_container_width=True):
        os.kill(os.getpid(), signal.SIGINT)

# --- THEME CSS ---
bg, txt, border = (("#1e1e1e", "#eee", "#444") if mode == GUI_TAG_DARK else ("#fff", "#000", "#ccc"))
st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {txt}; }}</style>", unsafe_allow_html=True)

# --- 3. MAIN CONTENT ---
st.title("🎯 Classification des Palettes")

if not palgrps:
    st.success("Toutes les palettes sont classées ! 🎉")
else:
    for name, sources in palgrps.items():
        with st.expander(f"Palette : {name}", expanded=True):
            for src, colors in sources.items():
                uid = build_name_n_srcname(name, src)
                st.markdown(f"📂 **Source : {src}** — `{len(colors)}` couleurs")

                if len(colors) <= 30:
                    st.markdown(generate_discrete_grid(colors, border), unsafe_allow_html=True)

                st.markdown(
                    f'<div style="background:{generate_gradient_css(colors)}; height:45px; border-radius:6px; margin-bottom:15px;"></div>',
                    unsafe_allow_html=True
                )

                # Le multiselect utilise la clé stockée en session state
                st.multiselect("Types :", options=KIND_OPTIONS, key=f"k_{uid}")

# --- 4. SAVE LOGIC ---
if save_trigger:
    update_data(final_report)
    # Nettoyage de la session après sauvegarde
    for k in list(st.session_state.keys()):
        if k.startswith("k_"):
            del st.session_state[k]
    st.toast("Données sauvegardées avec succès !")
    st.rerun()
