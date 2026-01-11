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

from labutils import * # --------------------------- #

from yaml import safe_load


CONFIG_DIR = LAB_DIR.parent / 'config'

with (CONFIG_DIR / 'METADATA.yaml').open(mode = 'r') as f:
    METADATA = safe_load(f)

KIND_OPTIONS = list(METADATA['CATEGORY'])
KIND_OPTIONS.sort()


AUDIT_DIR = LAB_DIR.parent / "building" / "audit"

HUMAN_KIND_YAML = AUDIT_DIR / "HUMAN-KIND.yaml"


REPORT_DIR = AUDIT_DIR.parent / "REPORT"

MISSING_KIND_JSON = REPORT_DIR / "AUDIT-MISSING-KIND.json"

# --------- #
# -- GUI -- #
# --------- #



@st.cache_data
def load_all_data():
    if not MISSING_KIND_JSON.is_file():
        return {}

    with MISSING_KIND_JSON.open("r") as f:
        conflicts = json_load(f)

    palgrps, json_cache = {}, {}

    for nsn in conflicts:
        name, src = extract_name_n_srcname(nsn)

        paldefs = {}

        if src not in json_cache:
            p = REPORT_DIR / f"{src}.json"

            if p.exists():
                json_cache[src] = json_load(p.open())

        if src in json_cache and name in json_cache[src]:
            paldefs[src] = json_cache[src][name][TAG_RGB_COLS]

        if paldefs:
            palgrps[name] = paldefs

    return palgrps

st.set_page_config(page_title="Audit @prism - Types", layout="wide")

if "save_count" not in st.session_state:
    st.session_state.save_count = 0

palgrps = load_all_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚡ Actions")
    # Nouveau bouton avec la règle hybride (Qualitatif <= 30, sinon Séquentiel)
    if st.button("🪄 Auto-Assign (30)", use_container_width=True):
        for name, sources in palgrps.items():
            for src, colors in sources.items():
                uid = build_name_n_srcname(name, src)

                # Logique de décision
                if len(colors) <= 30:
                    st.session_state[f"k_{uid}"] = ["qualitative"]
                else:
                    st.session_state[f"k_{uid}"] = ["sequential"]
        st.rerun()

    st.divider()
    st.header("⚙️ Style")
    mode = st.radio("Thème", [GUI_TAG_DARK, GUI_TAG_LIGHT], label_visibility="collapsed")

    st.divider()
    with st.expander("🛑 Stop"):
        if st.button("Close GUI", use_container_width=True):
            os.kill(os.getpid(), signal.SIGINT)

# --- THEME ---
bg, txt, border = (("#1e1e1e", "#eee", "#444") if mode == GUI_TAG_DARK else ("#fff", "#000", "#ccc"))
st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {txt}; }} label, p {{ color: {txt} !important; }}</style>", unsafe_allow_html=True)

# --- CONTENT ---
st.title("🎯 Classification des Palettes")

final_report = {}
nbchges_made = 0

for name, sources in palgrps.items():
    with st.expander(f"Palette : {name}", expanded=True):
        for src, colors in sources.items():
            uid = build_name_n_srcname(name, src)
            nbcols = len(colors)

            st.markdown(f"📂 **Source : {src}** — `{nbcols}` couleurs")

            # --- VISUALISATION ---
            if nbcols <= 30:
                st.markdown(generate_discrete_grid(colors, border), unsafe_allow_html=True)

            st.markdown(
                f'<div style="background:{generate_gradient_css(colors)}; '
                f'height:45px; border-radius:6px; border:1px solid {border}; '
                f'margin-bottom:15px; width: 100%;"></div>',
                unsafe_allow_html=True
            )

            # --- SELECTION DU TYPE ---
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

# --- VALIDATION ---
col_btn, col_stat = st.columns([1.5, 4])

with col_btn:
    if st.button("💾 Enregistrer l'Audit", type="primary", use_container_width=True, disabled=(nbchges_made == 0)):
        # On passe le rapport simplifié à update_data
        update_data(final_report)
        st.session_state.save_count += 1
        # Reset des widgets
        for k in list(st.session_state.keys()):
            if k.startswith("k_"): del st.session_state[k]
        st.rerun()

with col_stat:
    if nbchges_made > 0:
        st.info(f"🔄 {nbchges_made} palette(s) qualifiée(s) pour la modification #{st.session_state.save_count + 1}")
    else:
        st.write(f"✨ Prêt (Dernière sauvegarde : #{st.session_state.save_count})")
