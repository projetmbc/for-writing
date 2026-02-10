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

# --- LOAD METADATA ---
with (CONFIG_DIR / 'METADATA.yaml').open(mode='r') as f:
    METADATA = yaml.safe_load(f)
KIND_OPTIONS = sorted(list(METADATA['CATEGORY']))

# --- FUNCTIONS ---
def update_data(new_entries):
    data = {}

    if HUMAN_KIND_YAML.exists():
        with HUMAN_KIND_YAML.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

    for uid, kinds in new_entries.items():
        if not kinds:
            continue

        name, src = extract_name_n_srcname(uid)

        if src not in data:
            data[src] = {}

        data[src][name] = ', '.join(sorted(kinds))

    # Tri final pour que le YAML reste lisible (Sources A-Z, puis Palettes A-Z)
    sorted_data = {s: dict(sorted(p.items())) for s, p in sorted(data.items())}

    with HUMAN_KIND_YAML.open('w', encoding='utf-8') as f:
        yaml.dump(sorted_data, f, allow_unicode=True, sort_keys=False)


@st.cache_data
def load_all_data():
    """Charge les conflits et groupe les données par source pour l'UI."""
    if not MISSING_KIND_JSON.exists():
        return {}

    with MISSING_KIND_JSON.open("r") as f:
        conflicts = json.load(f)

    # Structure : { source_name: { palette_name: colors_list } }
    by_source = {}
    json_cache = {}

    for name, src in conflicts:
        if src not in json_cache:
            src_file = REPORT_DIR / f"{src}.json"
            if src_file.exists():
                with src_file.open('r') as f:
                    json_cache[src] = json.load(f)
            else:
                continue

        # Extraction des couleurs si le nom correspond
        for n in json_cache[src]:
            if n.lower() == name.lower():
                if src not in by_source:
                    by_source[src] = {}
                by_source[src][name] = json_cache[src][n][TAG_RGB_COLS]

    return by_source

# --- INITIALIZATION ---
st.set_page_config(page_title="Audit @prism - Types", layout="wide")
by_source = load_all_data()

# --- 1. PRE-CALCULATION ---
final_report = {}
nbchges_made = 0

# On parcourt le session_state pour détecter les changements
for k, val in st.session_state.items():
    if k.startswith("k_") and val:
        uid = k.replace("k_", "")
        final_report[uid] = val
        nbchges_made += 1

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("⚡ Actions")

    if st.button(f"🪄 Auto-Assign (≤{AUTO_QUAL_CATEGO_SIZE})", use_container_width=True):
        for src, palettes in by_source.items():
            for name, colors in palettes.items():
                uid = build_name_n_srcname(name, src)
                st.session_state[f"k_{uid}"] = ["qualitative"] if len(colors) <= AUTO_QUAL_CATEGO_SIZE else ["sequential"]
        st.rerun()

    st.divider()

    col_btn, col_stat = st.columns([1, 1])
    with col_btn:
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
bg, txt, border_col = (("#1e1e1e", "#eee", "#444") if mode == GUI_TAG_DARK else ("#fff", "#000", "#ccc"))
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stExpander"] {{ border: 1px solid {border_col}; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. MAIN CONTENT ---
st.title("🎯 Classification des Palettes")

if not by_source:
    st.success("Toutes les palettes sont classées ! 🎉")
else:
    # Navigation rapide par source
    sources_list = list(by_source.keys())
    selected_src = st.multiselect("Filtrer par sources :", sources_list, default=sources_list)

    for src in selected_src:
        with st.expander(f"📂 SOURCE : {src} ({len(by_source[src])} palettes)", expanded=True):
            for name, colors in by_source[src].items():
                uid = build_name_n_srcname(name, src)

                # Container pour grouper visuellement le bloc (comme une minipage LaTeX)
                with st.container():
                    c1, c2 = st.columns([3, 1])

                    with c1:
                        st.markdown(f"**{name}** — `{len(colors)}` couleurs")
                        # Grille discrète si petite taille
                        if len(colors) <= 30:
                            st.markdown(generate_discrete_grid(colors, border_col), unsafe_allow_html=True)
                        # Gradient permanent
                        st.markdown(
                            f'<div style="background:{generate_gradient_css(colors)}; height:35px; border-radius:4px; margin-bottom:10px; border: 1px solid {border_col};"></div>',
                            unsafe_allow_html=True
                        )

                    with c2:
                        st.multiselect("Types :", options=KIND_OPTIONS, key=f"k_{uid}", label_visibility="collapsed")

                    st.divider()

# --- 4. SAVE LOGIC ---
if save_trigger:
    update_data(final_report)
    # Nettoyage
    for k in list(st.session_state.keys()):
        if k.startswith("k_"):
            del st.session_state[k]
    st.toast("Données sauvegardées !")
    st.rerun()
