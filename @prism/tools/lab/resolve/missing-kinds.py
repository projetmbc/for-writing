#!/usr/bin/env python3

import os
import sys
import signal
import yaml
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
    TODO
    """Sauvegarde et fusionne les choix dans le fichier YAML."""
    data = {}
    if HUMAN_KIND_YAML.exists():
        with HUMAN_KIND_YAML.open('r', encoding='utf-8') as f:
            existing = yaml.safe_load(f)
            if existing:
                data = existing

    # Mise à jour (écrase si UID identique, ajoute sinon)
    for uid, content in new_entries.items():
        data[uid] = content

    with HUMAN_KIND_YAML.open('w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=True, indent=4)

@st.cache_data
def load_all_data():
    """Charge les palettes en conflit depuis les rapports JSON."""
    if not MISSING_KIND_JSON.is_file():
        return {}

    with MISSING_KIND_JSON.open("r") as f:
        conflicts = json_load(f)

    palgrps, json_cache = {}, {}

    for nsn in conflicts:
        name, src = extract_name_n_srcname(nsn)
        if src not in json_cache:
            p = REPORT_DIR / f"{src}.json"
            if p.exists():
                json_cache[src] = json_load(p.open())

        if src in json_cache and name in json_cache[src]:
            if name not in palgrps:
                palgrps[name] = {}
            palgrps[name][src] = json_cache[src][name][TAG_RGB_COLS]

    return palgrps

# --- GUI CONFIG ---
st.set_page_config(page_title="Audit @prism - Types", layout="wide")

if "save_count" not in st.session_state:
    st.session_state.save_count = 0

palgrps = load_all_data()

# --- SIDEBAR ---

nbchges_made = 0

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

    # --- NOUVELLE ZONE DE SAUVEGARDE FIXE ---
    st.header("💾 Sauvegarde")
    if nbchges_made > 0:
        st.warning(f"Modifications : **{nbchges_made}**")
        if st.button("CONFIRMER & ENREGISTRER", type="primary", use_container_width=True):
            update_data(final_report)
            st.session_state.save_count += 1
            # Reset
            for k in list(st.session_state.keys()):
                if k.startswith("k_"): del st.session_state[k]
            st.success("Enregistré !")
            st.rerun()
    else:
        st.info("Aucun changement")

    st.divider()
    st.header("⚙️ Style")
    mode = st.radio("Thème", [GUI_TAG_DARK, GUI_TAG_LIGHT], label_visibility="collapsed")

    with st.expander("🛑 Stop"):
        if st.button("Close GUI", use_container_width=True):
            os.kill(os.getpid(), signal.SIGINT)

# --- THEME CSS ---
bg, txt, border = (("#1e1e1e", "#eee", "#444") if mode == GUI_TAG_DARK else ("#fff", "#000", "#ccc"))
st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    label, p {{ color: {txt} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.title("🎯 Classification des Palettes")

final_report = {}

for name, sources in palgrps.items():
    with st.expander(f"Palette : {name}", expanded=True):
        for src, colors in sources.items():
            uid = build_name_n_srcname(name, src)
            nbcols = len(colors)

            st.markdown(f"📂 **Source : {src}** — `{nbcols}` couleurs")

            # Visualisation
            if nbcols <= 30:
                st.markdown(generate_discrete_grid(colors, border), unsafe_allow_html=True)

            st.markdown(
                f'<div style="background:{generate_gradient_css(colors)}; '
                f'height:45px; border-radius:6px; border:1px solid {border}; '
                f'margin-bottom:15px; width: 100%;"></div>',
                unsafe_allow_html=True
            )

            # Sélection
            sel_kinds = st.multiselect(
                "Choisir le(s) type(s) :",
                options=KIND_OPTIONS,
                key=f"k_{uid}",
                placeholder="Sélectionner..."
            )

            if sel_kinds:
                nbchges_made += 1
                final_report[uid] = {"kinds": sel_kinds}

st.divider()

# --- VALIDATION & SAVE ---
col_btn, col_stat = st.columns([1.5, 4])

with col_btn:
    save_trigger = st.button("💾 Enregistrer l'Audit", type="primary",
                             use_container_width=True, disabled=(nbchges_made == 0))
    if save_trigger:
        update_data(final_report)
        st.session_state.save_count += 1

        # Nettoyage du session_state pour vider les multiselects après sauvegarde
        for k in list(st.session_state.keys()):
            if k.startswith("k_"):
                del st.session_state[k]

        st.success(f"Audit #{st.session_state.save_count} enregistré avec succès !")
        st.rerun()

with col_stat:
    if nbchges_made > 0:
        st.info(f"🔄 {nbchges_made} palette(s) prêtes à être sauvegardées.")
    else:
        st.write(f"✨ Catalogue à jour (Dernière sauvegarde : #{st.session_state.save_count})")
