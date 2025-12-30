  function toggleTheme() {
    const body = document.body;
    const btn = document.getElementById('themeBtn');
    body.classList.toggle('dark-mode');
    btn.textContent = body.classList.contains('dark-mode') ? "☀️ Mode Clair" : "🌙 Mode Sombre";
  }

  function draw() {
    const name = document.getElementById('pName').value.trim();
    const size = parseInt(document.getElementById('pSize').value);
    const area = document.getElementById('resultArea');
    const preview = document.getElementById('palettePreview');
    const spectrum = document.getElementById('continuousSpectrum');
    const svg = document.getElementById('canvas');

    if (!name || size < 1) return;

    area.style.display = 'block';

    const colorVars = [];
    for (let i = 1; i <= size; i++) {
      colorVars.push(`var(--pal${name}-${i})`);
    }

    // 1. Blocs Discrets
    preview.innerHTML = colorVars.map(v => `<div class="swatch" style="background: ${v}"></div>`).join('');

    // 2. Spectre Continu (Interpolation Linéaire)
    // On injecte directement la liste des variables dans le gradient CSS
    spectrum.style.background = `linear-gradient(to right, ${colorVars.join(', ')})`;

    // 3. Dessin SVG
    svg.innerHTML = '';
    const centerX = 200, centerY = 200, maxR = 150;
    const rStep = maxR / size;

    colorVars.forEach((v, i) => {
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", centerX);
      circle.setAttribute("cy", centerY);
      circle.setAttribute("r", maxR - (i * rStep));
      circle.setAttribute("fill", v);
      svg.appendChild(circle);
    });

    const startX = 400, width = 350;
    colorVars.forEach((v, i) => {
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      const yBase = 200 + (i * 6) - (size * 3);
      let d = `M ${startX} ${yBase}`;
      for (let x = 0; x <= width; x += 10) {
        d += ` L ${startX + x} ${yBase + Math.sin(x * 0.03 + i) * 30}`;
      }
      path.setAttribute("d", d);
      path.setAttribute("stroke", v);
      path.setAttribute("fill", "none");
      path.setAttribute("stroke-width", "4");
      path.setAttribute("stroke-linecap", "round");
      svg.appendChild(path);
    });
  }
