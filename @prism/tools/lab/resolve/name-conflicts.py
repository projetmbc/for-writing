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

from json import load as json_load
from yaml import (
    safe_load,
    dump as yaml_dump
)

import streamlit as st


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = Path(__file__).parent
PROJ_DIR = THIS_DIR

while (PROJ_DIR.name != "@prism" and PROJ_DIR.parent != PROJ_DIR):
    PROJ_DIR = PROJ_DIR.parent

AUDIT_DIR  = PROJ_DIR / "tools" / "building" / "AUDIT"
REPORT_DIR = AUDIT_DIR.parent / "REPORT"

VISUAL_SIMILAR_YAML = AUDIT_DIR / "VISUAL-SIMILAR.yaml"
VISUAL_EQUAL_YAML   = AUDIT_DIR / "VISUAL-EQUAL.yaml"
IGNORED_YAML        = AUDIT_DIR / "IGNORED.yaml"
RENAMED_YAML        = AUDIT_DIR / "RENAMED.yaml"

NAME_CONFLICT_JSON = REPORT_DIR / "AUDIT-NAME-CONFLICT.json"


# ------------------ #
# -- EXTRACT DATA -- #
# ------------------ #

IGNORED = safe_load(IGNORED_YAML.read_text())
RENAMED = safe_load(RENAMED_YAML.read_text())


if not VISUAL_EQUAL_YAML.is_file():
    VISUAL_EQUAL_YAML.touch()

VISUAL_EQUAL = safe_load(VISUAL_EQUAL_YAML.read_text())

if VISUAL_EQUAL is None:
    VISUAL_EQUAL = dict()


if not VISUAL_SIMILAR_YAML.is_file():
    VISUAL_SIMILAR_YAML.touch()

VISUAL_SIMILAR = safe_load(VISUAL_SIMILAR_YAML.read_text())

if VISUAL_SIMILAR is None:
    VISUAL_SIMILAR = []



DEBUG_REPORT = {
    "Gray":{
        "TABLEAU":{"status":TAG_SIMILAR,"ref":None,"alias":"MidGray","size":5},
        "MATPLOTLIB":{"status":TAG_SIMILAR,"ref":"CMOCEAN","alias":"BW","size":2},
        "CMOCEAN":{"status":TAG_IGNORE,"ref":"MATPLOTLIB","alias":"Gray","size":256}
    },
    "YlOrRd":{
        "MATPLOTLIB":{"status":TAG_UNIQUE,"ref":None,"alias":None,"size":9},
        "COLORBREWER":{"status":TAG_SIMILAR,"ref":"MATPLOTLIB","alias":None,"size":8}
    },
    "Hot":{
        "MATPLOTLIB":{"status":TAG_UNIQUE,"ref":None,"alias":None,"size":256},
        "PLOTLY":{"status":TAG_SIMILAR,"ref":"MATPLOTLIB","alias":None,"size":4}
    },
    "Jet":{
        "MATPLOTLIB":{"status":TAG_UNIQUE,"ref":None,"alias":None,"size":256},
        "PLOTLY":{"status":TAG_SIMILAR,"ref":"MATPLOTLIB","alias":None,"size":6}
    },
    "Rainbow":{
        "MATPLOTLIB":{"status":TAG_UNIQUE,"ref":None,"alias":None,"size":256},
        "PLOTLY":{"status":TAG_SIMILAR,"ref":None,"alias":None,"size":9}
    }
}



# ------------------ #
# --  FUNCTIONS   -- #
# ------------------ #

def extract_name_n_srcname(name_srcname: str) -> (str, str):
    return tuple(name_srcname.split('::'))


def build_name_n_srcname(
    name: str,
    srcname: str,
) -> str:
    return '::'.join([name, srcname])


def sauvegarder_resultats(report: dict) -> None:
    # st.success("🚀 Rapport validé : Les données de similarité et d'exclusion sont prêtes.")

    visual_similar = []

    for name, data in report.items():
        for src, infos in data.items():
            if infos[TAG_STATUS] == TAG_UNIQUE:
                continue

# To ignore.
            if infos[TAG_STATUS] == TAG_IGNORE:
# Here we have seen a visual euqality.
                if not infos[TAG_REF] is None:
                    visual_equals = VISUAL_EQUAL.get(name, dict())
                    visual_equals[src] = infos[TAG_REF]

                    VISUAL_EQUAL[name] = visual_equals

                names = IGNORED.get(src, [])
                names.append(name)
                names = list(set(names))
                names.sort()

                IGNORED[src] = names


# Similar with a reference to another source, or
# no similarity seen (so no reference added).
            else:
                if not src in RENAMED[TAG_SUFFIXES]:
                    suffix = input(f"Which suffix for '{src}'?\n")

                    RENAMED[TAG_SUFFIXES][src] = suffix

                renames = RENAMED.get(src, dict())
                renames[name] = (
                    '.'
                    if infos[TAG_ALIAS] is None else
                    infos[TAG_ALIAS]
                )

                RENAMED[src] = renames

                if infos[TAG_REF]:
                    visual_similar.append(
                        set([
                            build_name_n_srcname(name, src),
                            build_name_n_srcname(name, infos[TAG_REF])
                        ])
                    )

# Visual similarities.
    groupes = []

    visual_similar += [
        set(g) for g in VISUAL_SIMILAR
    ]

    for s in visual_similar:
        # On cherche les groupes existants qui ont une intersection avec le set actuel
        nouveaux_groupes = []
        fusion_actuelle = s

        for g in groupes:
            if not g.isdisjoint(s):
                # Si ça se croise, on l'ajoute à notre fusion
                fusion_actuelle = fusion_actuelle.union(g)
            else:
                # Sinon, on garde le groupe tel quel pour le moment
                nouveaux_groupes.append(g)

        # On ajoute le set fusionné à la liste des groupes
        nouveaux_groupes.append(fusion_actuelle)
        groupes = nouveaux_groupes

    _VISUAL_SIMILAR = sorted([
        sorted(list(g)) for g in groupes
    ])

# Update human readable files.
    with IGNORED_YAML.open("w") as f:
        yaml_dump(IGNORED, f)

    with VISUAL_EQUAL_YAML.open("w") as f:
        yaml_dump(VISUAL_EQUAL, f)

    with VISUAL_SIMILAR_YAML.open("w") as f:
        yaml_dump(_VISUAL_SIMILAR, f)

    suffixes  = RENAMED[TAG_SUFFIXES]
    _suffixes = {TAG_SUFFIXES: suffixes}

    del RENAMED[TAG_SUFFIXES]

    suffix_code = yaml_dump(_suffixes).strip()

    comment = f"""
# '.' asks to add the suffix to the existing name.
# '*' is an alias for the suffix.
    """.strip()

    names_code  = yaml_dump(RENAMED).strip()

    full_code = f"""
{suffix_code}

{comment}

{names_code}
    """.strip() + '\n'

    RENAMED_YAML.write_text(full_code)




# sauvegarder_resultats(DEBUG_REPORT)

# exit()



def generate_gradient_css(colors):
    rgb_points = [
        f"rgb({int(c[0]*255)},{int(c[1]*255)},{int(c[2]*255)})"
        for c in colors
    ]

    return f"linear-gradient(to right, {', '.join(rgb_points)})"

@st.cache_data
def load_all_data():
    with NAME_CONFLICT_JSON.open(mode="r") as f:
        conflicts = json_load(f)

    palgrps, json_cache = {}, {}

    for name, sources in conflicts.items():
        paldefs = {}

        for srcname in sources:
            if srcname not in json_cache:
                jsonfile = REPORT_DIR / f"{srcname}.json"

                if jsonfile.exists():
                    with jsonfile.open(mode="r") as f:
                        json_cache[srcname] = json_load(f)

            if srcname in json_cache and name in json_cache[srcname]:
                paldefs[srcname] = json_cache[srcname][name][TAG_RGB_COLS]

        if paldefs:
            palgrps[name] = paldefs

    return palgrps


# --- SETUP UI ---
st.set_page_config(page_title="Audit @prism", layout="wide")

palgrps = load_all_data()

tous_les_projets = sorted(list(set(src for s in palgrps.values() for src in s.keys())))

# Thème
mode = st.sidebar.radio("Thème", ["Sombre", "Clair"])

bg, txt = ("#1e1e1e", "#eeeeee") if mode == "Sombre" else ("#ffffff", "#000000")

st.markdown(f"<style>.stApp {{ background-color: {bg}; color: {txt}; }}</style>", unsafe_allow_html=True)

final_report = {}

st.title("🎯 Validation des Spectres")

for name, sources in palgrps.items():
    with st.container():
        st.subheader(f"Spectre : `{name}`")

        for src, colors in sources.items():
            uid = f"{name}_{src}"
            n_colors = len(colors)

            st.write(f"**Source : {src}** ({n_colors} couleurs)")

            st.markdown(f'<div style="background:{generate_gradient_css(colors)}; height:30px; border-radius:4px; border:1px solid #555; margin-bottom:10px;"></div>', unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns([1, 1, 2, 2])

            is_sim = c1.checkbox("Similaire", key=f"s_{uid}")

            is_ign = c2.checkbox("Ignorer", key=f"i_{uid}")

            ref_project, alias = None, ""

            # La sélection de projet s'affiche si SIMILAIRE est coché,
            # peu importe si IGNORER l'est aussi.
            if is_sim:
                with c3:
                    ref_project = st.selectbox("Référence", ["Aucun"] + tous_les_projets, key=f"ref_{uid}")

                with c4:
                    alias = st.text_input("Alias / Note", key=f"al_{uid}", placeholder="Ex: Doublon parfait...")

            # Logique du statut final
            if is_ign:
                status = TAG_IGNORE

            elif is_sim:
                status = TAG_SIMILAR

            else:
                status = TAG_UNIQUE

            if name not in final_report:
                final_report[name] = {}

            final_report[name][src] = {
                "status": status,
                "ref": ref_project if ref_project != "Aucun" else None,
                "alias": alias if alias else None,
                "size": n_colors
            }
        st.divider()

# --- ACTION ---
if st.sidebar.button("✅ Valider et Sauvegarder", type="primary"):
    sauvegarder_resultats(final_report)
    st.sidebar.json(final_report)
