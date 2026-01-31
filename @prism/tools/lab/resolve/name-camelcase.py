#!/usr/bin/env python3

# CMD: streamlit run ...

import streamlit as st
import re
import json

# Dictionnaire de référence
TECH_DICT = {"orange", "blue", "grey", "gist", "dark", "light", "red", "green", "slate", "gold", "silver"}

def suggest_camel_case(word, dictionary):
    low_word = word.lower()
    for i in range(2, len(low_word)):
        part1 = low_word[:i]
        part2 = low_word[i:]
        if part1 in dictionary and part2 in dictionary:
            return f"{part1.capitalize()}{part2.capitalize()}"
    return word

st.title("JSON Name Mapper")

# 1. Entrée des données
input_text = st.text_area("Entrez vos variables (ex: --palPALETTE-Orangeblue) :",
                         value="--palPALETTE-Orangeblue\n--palPALETTE-Gistgrey\n--palPALETTE-Darkred",
                         height=150)

raw_names = re.findall(r"--palPALETTE-([A-Za-z0-9]+)", input_text)

if raw_names:
    st.subheader("Validation des correspondances")

    # Bouton de sélection globale
    master_checkbox = st.checkbox("Tout valider par défaut", value=True)

    mapping_suggestions = {}

    # Affichage ligne par ligne avec case à cocher
    for name in sorted(set(raw_names)): # On évite les doublons
        proposal = suggest_camel_case(name, TECH_DICT)

        col1, col2 = st.columns([3, 1])
        with col1:
            is_valid = st.checkbox(f"`{name}` ➔ `{proposal}`", value=master_checkbox, key=name)

        # Si coché, on prend la proposition, sinon on garde l'original (ou on ignore)
        if is_valid:
            mapping_suggestions[name] = proposal

    st.divider()

    # 2. Production du JSON
    if mapping_suggestions:
        st.subheader("Résultat JSON")
        json_output = json.dumps(mapping_suggestions, indent=4)
        st.code(json_output, language="json")

        st.download_button(
            label="Télécharger le mapping.json",
            data=json_output,
            file_name="palette_mapping.json",
            mime="application/json"
        )
else:
    st.info("Aucun nom détecté avec le pattern '--palPALETTE-'.")
