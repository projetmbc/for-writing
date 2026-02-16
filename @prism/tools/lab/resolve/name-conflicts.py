#!/usr/bin/env python3

# CMD: streamlit run ...

# ----------------------------- #
# -- IMPORT LABUTILS - START -- #

from pathlib import Path
import sys
import os
import signal
import streamlit as st

THIS_DIR = Path(__file__).parent
LAB_DIR  = THIS_DIR.parent
sys.path.append(str(LAB_DIR))

from labutils import *

# -- IMPORT LABUTILS - END -- #
# --------------------------- #

@st.cache_data
def load_all_data():
    """
    Charge les conflits et les regroupe par nom.
    Nouveau format JSON : {"ylorrd": [["YlOrRd", "YlOrRd_Alias", "MATPLOTLIB"], ...]}
    """
    if not NAME_CONFLICT_JSON.is_file():
        return {}

    with NAME_CONFLICT_JSON.open("r") as f:
        # Format attendu: {"group_key": [[name, alias, source], ...]}
        conflicts_dict = json_load(f)

    grouped_conflicts = dict()
    json_cache = dict()

    for group_key in sorted(conflicts_dict):
        for name, alias_db, src in conflicts_dict[group_key]:

            # Cache pour éviter de recharger le même fichier source JSON
            if src not in json_cache:
                p = REPORT_DIR / f"{src}.json"
                if p.exists():
                    json_cache[src] = json_load(p.open())

            # Vérification de l'existence de la palette dans la source
            if src in json_cache and name in json_cache[src]:
                if group_key not in grouped_conflicts:
                    grouped_conflicts[group_key] = {}

                # UID unique pour Streamlit
                uid = build_name_n_srcname(name, src)

                grouped_conflicts[group_key][uid] = {
                    "real_name": name,
                    "db_alias": alias_db,
                    "source": src,
                    "colors": json_cache[src][name][TAG_RGB_COLS]
                }

    return grouped_conflicts

# --- CONFIG ---
st.set_page_config(
    page_title = "Audit @prism",
    layout      = "wide"
)

if "save_count" not in st.session_state:
    st.session_state.save_count = 0

palgrps = load_all_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Dashboard")
    mode = st.radio("Style", [GUI_TAG_DARK, GUI_TAG_LIGHT])
    st.divider()

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
    with st.expander(f"Group : {group_name.upper()}", expanded = True):

        available_sources = sorted([m["source"] for m in members.values()])

        for uid, data in members.items():
            name    = data["real_name"]
            db_al   = data["db_alias"]
            src     = data["source"]
            colors  = data["colors"]

            # Header avec info Alias si présent
            title_str = f"📂 **{name}**"
            if db_al and db_al != name:
                title_str += f" *(alias: {db_al})*"

            st.markdown(f"{title_str} (Source: `{src}`) — `{len(colors)}` colors")

            # Preview
            st.markdown(
                f'<div style="background:{generate_gradient_css(colors)};'
                f'height:30px; border-radius:6px; border:1px solid {border};'
                f'margin-bottom:10px;"></div>',
                unsafe_allow_html = True
            )

            # Controls
            col_ign, col_sim, col_nam = st.columns([1, 2, 2])

            is_ign = col_ign.checkbox("Ignore", key=f"i_{uid}")

            possibilities = [GUI_TAG_NONE] + [s for s in available_sources if s != src]
            projref = col_sim.selectbox("Similar to...", possibilities, key=f"ref_{uid}")

            # On met l'alias actuel en placeholder
            new_alias = col_nam.text_input("New name", key=f"al_{uid}", placeholder=db_al)

            # Détection de changement
            # On considère un changement si : Ignore coché, Source Ref choisie, ou Nouveau nom saisi
            has_new_alias = new_alias.strip() != "" and new_alias.strip() != db_al

            if is_ign or projref != GUI_TAG_NONE or has_new_alias:
                nbchges_made += 1
                final_report[uid] = {
                    TAG_IS_IGNORED: is_ign,
                    TAG_REF: projref if projref != GUI_TAG_NONE else '',
                    TAG_ALIAS: new_alias.strip() if new_alias.strip() != "" else db_al
                }

    st.divider()

# --- SAVE LOGIC ---
with st.sidebar:
    if nbchges_made > 0:
        st.success(f"🔄 {nbchges_made} changes detected")
        if st.button("💾 Save audit", type="primary"):
            update_data(final_report)
            st.session_state.save_count += 1
            # Reset session state pour rafraîchir les widgets
            for k in [k for k in st.session_state.keys() if k != "save_count"]:
                del st.session_state[k]
            st.rerun()
    else:
        st.write(f"✨ Ready (Audit #{st.session_state.save_count})")
        st.button("💾 Save audit", disabled=True)

    st.divider()
    with st.expander("🛑 Danger Zone"):
        if st.button("Close the GUI"):
            os.kill(os.getpid(), signal.SIGINT)
