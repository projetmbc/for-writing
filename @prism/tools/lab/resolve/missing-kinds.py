#!/usr/bin/env python3

# -- DEBUG - ON -- #
from rich import print
# -- DEBUG - OFF -- #

import os
import sys
import signal
import yaml
import json
from pathlib import Path
import streamlit as st

# ----------------------------- #
# -- IMPORT LABUTILS - START -- #
THIS_DIR = Path(__file__).parent
LAB_DIR  = THIS_DIR.parent
sys.path.append(str(LAB_DIR))

# On suppose que ces fonctions/constantes viennent de labutils
from labutils import * # --------------------------- #

# --- PATHS ---
CONFIG_DIR = LAB_DIR.parent / 'config'
AUDIT_DIR  = LAB_DIR.parent / "building" / "audit"
REPORT_DIR = AUDIT_DIR.parent / "REPORT"

HUMAN_KIND_YAML   = AUDIT_DIR / "HUMAN-KIND.yaml"
MISSING_KIND_JSON = REPORT_DIR / "AUDIT-MISSING-KIND.json"

# --- CONFIG & METADATA ---
with (CONFIG_DIR / 'METADATA.yaml').open(mode='r') as f:
    METADATA = yaml.safe_load(f)

KIND_OPTIONS = sorted(list(METADATA['CATEGORY']))

# --- FUNCTIONS ---
def update_data(new_entries):
    data = {}
    if HUMAN_KIND_YAML.exists():
        with HUMAN_KIND_YAML.open('r', encoding='utf-8') as f:
            existing = yaml.safe_load(f)
            if existing: data = existing

    for uid, kinds in new_entries.items():
        name, src = extract_name_n_srcname(uid)
        stored = data.get(src, dict())
        stored[name] = ', '.join(kinds)
        data[src] = stored

    with HUMAN_KIND_YAML.open('w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=True, indent=4)

@st.cache_data
def load_all_data():
    if not MISSING_KIND_JSON.is_file(): return {}
    with MISSING_KIND_JSON.open("r") as f:
        conflicts = json_load(f)
    palgrps, json_cache = {}, {}
    for nsn in conflicts:
        name, src = extract_name_n_srcname(nsn)
        if src not in json_cache:
            p = REPORT_DIR / f"{src}.json"
            if p.exists(): json_cache[src] = json_load(p.open())
        if src in json_cache and name in json_cache[src]:
            if name not in palgrps: palgrps[name] = {}
            palgrps[name][src] = json_cache[src][name][TAG_RGB_COLS]
    return palgrps

# --- GUI CONFIG ---
st.set_page_config(page_title="Audit @prism - Types", layout="wide")

if "save_count" not in st.session_state:
    st.session_state.save_count = 0

palgrps = load_all_data()
nbchges_made = 0
final_report = {}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚡ Actions")

    # Bouton Auto-Assign
    if st.button("🪄 Auto-Assign (30)", use_container_width=True):
        for name, sources in palgrps.items():
            for src, colors in sources.items():
                uid = build_name_n_srcname(name, src)
                st.session_state[f"k_{uid}"] = ["qualitative"] if len(colors) <= 30 else ["sequential"]
        st.rerun()

    st.divider()

    # --- PAVAGE DANS LA SIDEBAR ---
    # Ici on utilise des colonnes plus étroites car la sidebar est moins large
    col_btn, col_stat = st.columns([1, 1])

    with col_btn:
        save_trigger = st.button(
            "💾 SAUVER",
            type="primary",
            use_container_width=True,
            disabled=(nbchges_made == 0)
        )
        if save_trigger:
            # On récupère final_report qui est rempli plus bas dans le script
            # Note : Streamlit exécute le script de haut en bas,
            # pour que final_report soit plein ici, il faut qu'il soit défini avant.
            pass

    with col_stat:
        if nbchges_made > 0:
            st.warning(f"**{nbchges_made}** modifs")
        else:
            st.caption("À jour")

    st.divider()
    st.header("⚙️ Style")
    mode = st.radio("Thème", [GUI_TAG_DARK, GUI_TAG_LIGHT], label_visibility="collapsed")

    with st.expander("🛑 Stop"):
        if st.button("Close GUI", use_container_width=True):
            os.kill(os.getpid(), signal.SIGINT)

# --- THEME CSS ---
bg, txt, border = (("#1e1e1e", "#eee", "#444") if mode == GUI_TAG_DARK else ("#fff", "#000", "#ccc"))
st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {txt}; }}</style>", unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.title("🎯 Classification des Palettes")

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

            sel_kinds = st.multiselect("Types :", options=KIND_OPTIONS, key=f"k_{uid}")
            if sel_kinds:
                nbchges_made += 1
                final_report[uid] = sel_kinds

# Logique de sauvegarde déportée (nécessaire car Streamlit lit de haut en bas)
if save_trigger:
    update_data(final_report)
    st.session_state.save_count += 1
    for k in list(st.session_state.keys()):
        if k.startswith("k_"): del st.session_state[k]
    st.rerun()
