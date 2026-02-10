import streamlit as st
import json
import yaml
import os
import signal
from pathlib import Path
from wordsegment import load, segment


load()


AUDIT_DIR = Path("building/audit")
NAMING_JSON = AUDIT_DIR / "NAMING-PROGRESS.json"  # Pour le suivi temporaire
NAMING_YAML = AUDIT_DIR / "HUMAN-NAMING.yaml"    # Le fichier final pour ton projet
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """Charge le mapping existant depuis le JSON de progression."""
    if NAMING_JSON.exists():
        with open(NAMING_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_to_yaml(mapping):
    """Sauvegarde le dictionnaire final au format YAML."""
    # On trie par clé pour que le YAML soit propre
    sorted_mapping = dict(sorted(mapping.items()))
    with open(NAMING_YAML, 'w', encoding='utf-8') as f:
        yaml.dump(sorted_mapping, f, allow_unicode=True, sort_keys=False)
    # On garde aussi une trace en JSON pour la session Streamlit
    with open(NAMING_JSON, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=4)

# --- INTERFACE ---
st.set_page_config(page_title="Audit Naming", layout="wide")

# 1. État de la session
if 'mapping' not in st.session_state:
    st.session_state.mapping = load_data()

# Simulation de ta liste source (à adapter avec tes vrais noms)
all_palettes = ["Orangegrey", "Bwr", "Viridis", "RdYlGn", "Magma", "Bluesky", "Cividis"]
to_process = [p for p in all_palettes if p not in st.session_state.mapping]

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Contrôles")

    # Bouton SAUVER
    if st.button("💾 SAUVER (YAML)", type="primary", use_container_width=True):
        save_to_yaml(st.session_state.mapping)
        st.success(f"Enregistré dans {NAMING_YAML.name}")
        st.toast("Fichier YAML mis à jour !")

    st.divider()

    # Bouton STOP
    if st.button("🛑 STOP L'APPLI", type="secondary", use_container_width=True):
        st.warning("Arrêt du serveur en cours...")
        os.kill(os.getpid(), signal.SIGINT)

    st.divider()
    st.metric("Traités", f"{len(st.session_state.mapping)} / {len(all_palettes)}")
    st.progress(len(st.session_state.mapping) / len(all_palettes))

# --- MAIN CONTENT ---
st.title("🏷️ Audit des noms de palettes")

if not to_process:
    st.balloons()
    st.success("✨ Toutes les palettes ont été renommées ! N'oubliez pas de SAUVER avant de quitter.")
else:
    for original in to_process:
        # Logique de suggestion auto
        if len(original) <= 4 and not original.isupper():
            suggestion = original.upper()
        else:
            parts = segment(original)
            suggestion = "-".join(p.capitalize() for p in parts) if len(parts) > 1 else original

        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                st.write(f"**Original :** `{original}`")
            with col2:
                new_name = st.text_input("Renommer :", value=suggestion, key=f"in_{original}", label_visibility="collapsed")
            with col3:
                if st.button("OK ✅", key=f"btn_{original}", use_container_width=True):
                    st.session_state.mapping[original] = new_name
                    # On sauve le progrès JSON à chaque étape pour ne rien perdre
                    with open(NAMING_JSON, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.mapping, f, indent=4)
                    st.rerun()

# Aperçu du dictionnaire en cours
if st.session_state.mapping:
    with st.expander("👀 Voir le mapping actuel"):
        st.write(st.session_state.mapping)
