#!/usr/bin/env python3

# CMD: streamlit run ...

# ----------------------------- #
# -- IMPORT LABUTILS - START -- #

from pathlib import Path
import sys

THIS_DIR = Path(__file__).parent
LAB_DIR  = THIS_DIR.parent
sys.path.append(str(LAB_DIR))

from labutils import *

# -- IMPORT LABUTILS - END -- #
# --------------------------- #

import os
import signal
import streamlit as st

# --------- #
# -- GUI -- #
# --------- #

@st.cache_data
def load_all_data():
    """
    Charge les conflits et les regroupe par nom (insensible à la casse).
    Structure de sortie : { "bluered": { "uid1": data, "uid2": data }, ... }
    """
    if not NAME_CONFLICT_JSON.exists():
        return {}

    with NAME_CONFLICT_JSON.open("r") as f:
        conflicts_list = json_load(f)  # Format attendu: [["Name", "Source"], ...]

    grouped_conflicts = dict()
    json_cache = dict()

    for group in conflicts_list:
        for name, src in group:
            group_key = name.lower()

        # Cache des fichiers JSON sources pour éviter les lectures disques répétées
            if src not in json_cache:
                p = REPORT_DIR / f"{src}.json"
                if p.exists():
                    json_cache[src] = json_load(p.open())

            if src in json_cache and name in json_cache[src]:
                if group_key not in grouped_conflicts:
                    grouped_conflicts[group_key] = {}

            # Identifiant unique pour Streamlit (Nom|Source)
                uid = build_name_n_srcname(name, src)

                grouped_conflicts[group_key][uid] = {
                    "real_name": name,
                    "source": src,
                    "colors": json_cache[src][name][TAG_RGB_COLS]
                }

    return grouped_conflicts


st.set_page_config(
    page_title = "Audit @prism",
    layout     = "wide"
)

# Initialisation du compteur de sauvegarde
if "save_count" not in st.session_state:
    st.session_state.save_count = 0

# Chargement des données groupées
palgrps = load_all_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Dashboard")
    mode = st.radio("Style", [GUI_TAG_DARK, GUI_TAG_LIGHT])
    st.divider()

# Gestion des couleurs de l'interface
bg, txt, border = (
    ("#1e1e1e", "#eee", "#444")
    if mode == GUI_TAG_DARK else
    ("#fff", "#000", "#ccc")
)

st.markdown(
    f"<style>.stApp {{ background-color: {bg}; color: {txt}; }} "
    f"label, p {{ color: {txt} !important; }}</style>",
    unsafe_allow_html = True
)

# --- MAIN UI ---
final_report = dict()
nbchges_made = 0

st.title("🎯 Conflict management")
st.info(f"Grouping: **Case Insensitive** ({len(palgrps)} groups found)")

for group_name, members in palgrps.items():
    # Un expander par groupe de nom (ex: regroupe "BlueRed" et "Bluered")
    with st.expander(f"Group : {group_name.upper()}", expanded = True):

        # Liste de toutes les sources du groupe pour le "Similar to"
        available_sources = sorted([m["source"] for m in members.values()])

        for uid, data in members.items():
            name   = data["real_name"]
            src    = data["source"]
            colors = data["colors"]
            nbcols = len(colors)

            st.markdown(f"📂 **{name}** (Source: `{src}`) — `{nbcols}` colors")

            # Aperçu visuel de la palette
            st.markdown(
                f'<div style="background:{generate_gradient_css(colors)};'
                f'height:38px; border-radius:8px; border:1px solid {border};'
                f'margin-bottom:12px;"></div>',
                unsafe_allow_html = True
            )

            # Contrôles d'audit
            cb_ignore, sel_similar, txt_naming = st.columns([1, 2, 2])

            is_ign = cb_ignore.checkbox("Ignore", key=f"i_{uid}")

            possibilities = [GUI_TAG_NONE] + [s for s in available_sources if s != src]
            projref = sel_similar.selectbox("Similar to...", possibilities, key=f"ref_{uid}")

            alias = txt_naming.text_input("New name", key=f"al_{uid}")

            # Collecte des données si modifiées
            if is_ign or projref != GUI_TAG_NONE or alias.strip() != "":
                nbchges_made += 1
                final_report[uid] = {
                    TAG_IS_IGNORED: is_ign,
                    TAG_REF: projref if projref != GUI_TAG_NONE else '',
                    TAG_ALIAS: alias.strip()
                }

    st.divider()

# --- SIDEBAR ACTIONS ---
title_save = "💾 Save audit"

with st.sidebar:
    if nbchges_made > 0:
        st.success(f"🔄 {nbchges_made} changes detected")
        if st.button(title_save, type="primary"):
            update_data(final_report)
            st.session_state.save_count += 1
            # Nettoyage du cache session pour forcer le rafraîchissement
            for k in list(st.session_state.keys()):
                if k != "save_count":
                    del st.session_state[k]
            st.rerun()
    else:
        st.write(f"✨ Ready (Audit #{st.session_state.save_count})")
        st.button(title_save, disabled=True)

    st.divider()
    with st.expander("🛑 Danger Zone"):
        if st.button("Close the GUI"):
            os.kill(os.getpid(), signal.SIGINT)
