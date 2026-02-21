#!/usr/bin/env python3

# CMD: streamlit run ...

import streamlit as st
import fitz  # pymupdf
from daltonlens import simulate
from PIL import Image
import numpy as np
import io

st.set_page_config(
    page_title="Colorblind PDF Checker",
    page_icon="👁️",
    layout="wide"
)

st.title("👁️ Colorblind PDF Checker")
st.caption("Simule comment un daltonien perçoit vos documents PDF")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Paramètres")

    dpi = st.slider("Qualité de rendu (DPI)", 72, 300, 150, step=72)

    severity = st.slider("Sévérité du daltonisme", 0.0, 1.0, 1.0, step=0.1,
                         help="1.0 = daltonisme total, 0.5 = partiel")

    deficiencies_selected = st.multiselect(
        "Types de daltonisme",
        options=["Deutéranopie (rouge-vert)", "Protanopie (rouge)", "Tritanopie (bleu-jaune)"],
        default=["Deutéranopie (rouge-vert)", "Protanopie (rouge)"]
    )

    st.divider()
    st.markdown("**Légende**")
    st.markdown("🟢 Deutéranopie : ~6% hommes")
    st.markdown("🔴 Protanopie : ~2% hommes")
    st.markdown("🔵 Tritanopie : ~0.01%")

DEFICIENCY_MAP = {
    "Deutéranopie (rouge-vert)": ("Deutéranopie", simulate.Deficiency.DEUTAN),
    "Protanopie (rouge)":        ("Protanopie",   simulate.Deficiency.PROTAN),
    "Tritanopie (bleu-jaune)":   ("Tritanopie",   simulate.Deficiency.TRITAN),
}

# --- Upload ---
uploaded_file = st.file_uploader("📄 Dépose ton PDF ici", type=["pdf"])

if not uploaded_file:
    st.info("👆 Upload un fichier PDF pour commencer l'analyse.")
    st.stop()

# --- Process PDF ---
pdf_bytes = uploaded_file.read()
doc = fitz.open(stream=pdf_bytes, filetype="pdf")
total_pages = len(doc)

st.success(f"✅ PDF chargé — {total_pages} page(s) détectée(s)")

page_num = st.number_input("Page à analyser", min_value=1, max_value=total_pages, value=1) - 1

if not deficiencies_selected:
    st.warning("Sélectionne au moins un type de daltonisme dans la barre latérale.")
    st.stop()

# --- Render page ---
with st.spinner("Rendu de la page en cours..."):
    page = doc[page_num]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    if pix.n == 4:
        img_array = img_array[:, :, :3]

simulator = simulate.Simulator_Machado2009()

# --- Display ---
cols = st.columns(1 + len(deficiencies_selected))

with cols[0]:
    st.markdown("**🖼️ Original**")
    st.image(img_array, use_container_width=True)

for i, key in enumerate(deficiencies_selected):
    label, deficiency = DEFICIENCY_MAP[key]
    with st.spinner(f"Simulation {label}..."):
        simulated = simulator.simulate_cvd(img_array, deficiency, severity=severity)

    with cols[i + 1]:
        st.markdown(f"**{label}**")
        st.image(simulated, use_container_width=True)

        # Download button
        img_pil = Image.fromarray(simulated)
        buf = io.BytesIO()
        img_pil.save(buf, format="PNG")
        st.download_button(
            label="⬇️ Télécharger",
            data=buf.getvalue(),
            file_name=f"page{page_num+1}_{label.lower()}.png",
            mime="image/png",
            key=f"dl_{i}"
        )

# --- All pages batch ---
st.divider()
with st.expander("📦 Exporter toutes les pages"):
    if st.button("🚀 Lancer l'export complet"):
        import zipfile
        zip_buf = io.BytesIO()

        with zipfile.ZipFile(zip_buf, "w") as zf:
            progress = st.progress(0)
            for p_idx in range(total_pages):
                page = doc[p_idx]
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=mat)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                if pix.n == 4:
                    img = img[:, :, :3]

                # Original
                buf = io.BytesIO()
                Image.fromarray(img).save(buf, format="PNG")
                zf.writestr(f"page{p_idx+1}/original.png", buf.getvalue())

                for key in deficiencies_selected:
                    label, deficiency = DEFICIENCY_MAP[key]
                    sim = simulator.simulate_cvd(img, deficiency, severity=severity)
                    buf = io.BytesIO()
                    Image.fromarray(sim).save(buf, format="PNG")
                    zf.writestr(f"page{p_idx+1}/{label.lower()}.png", buf.getvalue())

                progress.progress((p_idx + 1) / total_pages)

        st.download_button(
            label="⬇️ Télécharger le ZIP",
            data=zip_buf.getvalue(),
            file_name="colorblind_export.zip",
            mime="application/zip"
        )
