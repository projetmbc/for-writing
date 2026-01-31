function togglePaletteFile() {
  const link = document.getElementById('theme-link');
  const btn = document.getElementById('btn-palette');

  const fileA = "../palettes-hf.css";
  const fileB = "../palettes-s40.css";

  if (link.getAttribute('href') === fileA) {
    link.setAttribute('href', fileB);
    btn.innerText = "📂 MODE: S40";

  } else {
    link.setAttribute('href', fileA);
    btn.innerText = "📂 MODE: HF";
  }
}

window.onload = togglePaletteFile;
