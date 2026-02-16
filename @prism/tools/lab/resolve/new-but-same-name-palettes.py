#!/usr/bin/env python3

# CMD: streamlit run ...

import streamlit as st
import json
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Palette Comparator", layout="wide")

def to_rgb_str(color):
    """Convertit une liste [r, g, b] 0-1 en string CSS rgb(0-255)"""
    try:
        # On s'assure que les valeurs restent dans [0, 1] puis on convertit en 0-255
        r, g, b = [int(max(0, min(1, c)) * 255) for c in color[:3]]
        return f"rgb({r}, {g}, {b})"
    except:
        return "rgb(0,0,0)"

def make_gradient_css(colors):
    """Génère le style CSS pour un dégradé linéaire"""
    if not colors:
        return "background: #222;"
    if len(colors) == 1:
        return f"background: {to_rgb_str(colors[0])};"

    rgb_colors = [to_rgb_str(c) for c in colors]
    return f"background: linear-gradient(to right, {', '.join(rgb_colors)});"

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    # Ici, on charge tes résultats de stats et tes deux fichiers de palettes
    # Remplace par tes chemins de fichiers réels
    try:
        with open('PALS_1.json', 'r') as f1:
            p1 = json.load(f1)
        with open('PALS_2.json', 'r') as f2:
            p2 = json.load(f2)

        # Exemple de dictionnaire de stats (à charger depuis ton calcul ou JSON)
        # Format attendu : {"Nom": [bool_match, float_score]}
        # Si tu as un fichier stats.json, charge-le ici :
        # with open('stats.json', 'r') as fs: stats = json.load(fs)
        stats = {
            "Accent": [False, 79.77],
            "Acton": [True, 100.0],
            "Afmhot": [True, 99.53],
            "AgGrnYl": [False, 99.2]
        }

        return p1, p2, stats
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        return {}, {}, {}

pals_1, pals_2, stats = load_data()

# --- INTERFACE UTILISATEUR ---
st.title("🎨 Comparateur de Palettes (PALS_1 vs PALS_2)")

if not stats:
    st.warning("Aucune donnée chargée. Vérifiez les fichiers JSON.")
else:
    # 1. Préparation des groupes par initiale
    all_names = sorted(stats.keys())
    initiales = sorted(list(set(name[0].upper() for name in all_names)))

    # 2. Création des onglets
    tabs = st.tabs(initiales)

    for i, tab in enumerate(tabs):
        lettre = initiales[i]
        # On définit les palettes de cet onglet
        names_in_tab = [n for n in all_names if n[0].upper() == lettre]

        with tab:
            for name in names_in_tab:
                match, score = stats[name]
                c1 = pals_1.get(name, [])
                c2 = pals_2.get(name, [])

                # Couleurs pour le statut
                status_color = "#28a745" if match else "#dc3545"
                status_text = "CONFORME" if match else "ÉCHEC"

                # Bloc HTML
                html_card = f"""
                <div style="margin-bottom: 25px; border: 1px solid #ddd; border-radius: 8px; padding: 15px; background-color: #f9f9f9;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 1.1em; font-weight: bold; color: #333;">{name}</span>
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <span style="font-weight: bold; color: {status_color};">{score}%</span>
                            <span style="background: {status_color}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8em;">{status_text}</span>
                        </div>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 6px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="width: 50px; font-size: 0.7em; color: #777;">PALS_1</span>
                            <div style="flex-grow: 1; height: 30px; border-radius: 4px; {make_gradient_css(c1)}"></div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="width: 50px; font-size: 0.7em; color: #777;">PALS_2</span>
                            <div style="flex-grow: 1; height: 30px; border-radius: 4px; {make_gradient_css(c2)}"></div>
                        </div>
                    </div>
                </div>
                """

                # Rendu du HTML
                st.markdown(html_card, unsafe_allow_html=True)
