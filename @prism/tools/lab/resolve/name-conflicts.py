#!/usr/bin/env python3

# CMD: streamlit run ...

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

import os
import signal

import streamlit as st


# --------- #
# -- GUI -- #
# --------- #

@st.cache_data
def load_all_data():
    if not NAME_CONFLICT_JSON.exists():
        return {}

    with NAME_CONFLICT_JSON.open("r") as f:
        conflicts = json_load(f)

    palgrps    = dict()
    json_cache = dict()

    for name, sources in conflicts.items():
        paldefs = {}

        for src in sources:
            if src not in json_cache:
                p = REPORT_DIR / f"{src}.json"

                if p.exists():
                    json_cache[src] = json_load(p.open())

            if (
                src in json_cache
                and
                name in json_cache[src]
            ):
                paldefs[src] = json_cache[src][name][TAG_RGB_COLS]

        if paldefs:
            palgrps[name] = paldefs

    return palgrps


st.set_page_config(
    page_title = "Audit @prism",
    layout     = "wide"
)

if "save_count" not in st.session_state:
    st.session_state.save_count = 0

palgrps = load_all_data()

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
    (
        f"<style>.stApp {{ background-color: {bg}; color: {txt}; }} label,"
        f"p {{ color: {txt} !important; }}</style>"
    ),
    unsafe_allow_html = True
)

final_report = dict()
nbchges_made = 0

st.title("🎯 Conflict management")

for name, sources in palgrps.items():
    with st.expander(
        f"Palette : {name}",
        expanded = True
    ):
        projets_valides = sorted(list(sources.keys()))

        for src, colors in sources.items():
            uid = build_name_n_srcname(name, src)
            nbcols = len(colors)

            st.markdown(
                f"📂 **Source : {src}** — `{nbcols}` colors"
            )

            st.markdown(
                (
                    f'<div style="background:{generate_gradient_css(colors)};'
                    f'height:38px; border-radius:8px; border:1px solid {border};'
                     'margin-bottom:12px;"></div>'
                ),
                unsafe_allow_html = True
            )

            cb_ignore, sel_similar, txt_naming = st.columns([1, 2, 2])

            is_ign = cb_ignore.checkbox(
                "Ignore",
                key = f"i_{uid}"
            )

            possibilities = [GUI_TAG_NONE] + [
                p
                for p in projets_valides
                if p != src
            ]

            projref = sel_similar.selectbox(
                "Similar to...",
                possibilities,
                key = f"ref_{uid}"
            )

            alias = txt_naming.text_input(
                "New name",
                key = f"al_{uid}"
            )


            if (
                is_ign
                or
                projref != GUI_TAG_NONE
                or
                alias.strip() != ""
            ):
                nbchges_made += 1

            if uid not in final_report:
                final_report[uid] = {
                    TAG_IS_IGNORED: is_ign,
                    TAG_REF: (
                        projref
                        if projref != GUI_TAG_NONE else
                        ''
                    ),
                    TAG_ALIAS: (
                        alias
                        if alias else
                        ''
                    ),
                    # TAG_SIZE: nbcols
                }

    st.divider()

# --- SIDEBAR ACTIONS ---
title_save = "💾 Save audit"

with st.sidebar:
    if nbchges_made > 0:
        st.info(
            f"🔄 Modification #{st.session_state.save_count + 1} ({nbchges_made} modifs)"
        )

        if st.button(
            title_save,
            type = "primary"
        ):
            update_data(final_report)

            st.session_state.save_count += 1

            for k in list(st.session_state.keys()):
                if k != "save_count":
                    del st.session_state[k]

            st.rerun()

    else:
        st.write(
            f"✨ Ready (Last: #{st.session_state.save_count})"
        )

        st.button(
            title_save,
            disabled = True
        )

    st.divider()

    with st.expander("🛑 Stop server"):
        if st.button("Close the GUI"):
            os.kill(os.getpid(), signal.SIGINT)
