  let colorsArr = [];

  function toggleTheme() {
    document.body.classList.toggle('dark-mode');
  }

  function updateAll() {
    const name = document.getElementById('pName').value.trim();
    const size = parseInt(document.getElementById('pSize').value) || 2;
    const rawData = document.getElementById('pList').value;

    colorsArr = rawData.split('\n').map(c => c.trim()).filter(c => c !== "").slice(0, size);

    // MAJ Discrète
    const preview = document.getElementById('palettePreview');
    preview.innerHTML = colorsArr.map((c, i) => `
      <div class="swatch" style="background: ${c}">
        <input type="color" value="${anyToHex(c)}" oninput="editColor(${i}, this.value)">
      </div>
    `).join('');

    // MAJ Spectre Continu (Interpolation via Gradient)
    const spectrum = document.getElementById('spectrum');
    if (colorsArr.length > 1) {
      spectrum.style.background = `linear-gradient(to right, ${colorsArr.join(', ')})`;
    } else {
      spectrum.style.background = colorsArr[0] || 'transparent';
    }

    drawSVG(colorsArr);
  }

  function drawSVG(colors) {
    const svg = document.getElementById('canvas');
    svg.innerHTML = '';
    const n = colors.length;
    if (n === 0) return;

    // Cercles
    const step = 150 / n;
    colors.forEach((c, i) => {
      const circ = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circ.setAttribute("cx", 200); circ.setAttribute("cy", 200);
      circ.setAttribute("r", 150 - (i * step));
      circ.setAttribute("fill", c);
      svg.appendChild(circ);
    });

    // Ondes
    colors.forEach((c, i) => {
      const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
      const yB = 200 + (i * 6) - (n * 3);
      let d = `M 420 ${yB}`;
      for (let x = 0; x <= 330; x += 10) {
        d += ` L ${420 + x} ${yB + Math.sin(x * 0.03 + i) * 30}`;
      }
      p.setAttribute("d", d); p.setAttribute("stroke", c);
      p.setAttribute("fill", "none"); p.setAttribute("stroke-width", "5");
      p.setAttribute("stroke-linecap", "round");
      svg.appendChild(p);
    });
  }

  function editColor(index, hex) {
    colorsArr[index] = hex.toUpperCase();
    document.getElementById('pList').value = colorsArr.join('\n');
    updateAll();
  }

  function anyToHex(str) {
    const ctx = document.createElement('canvas').getContext('2d');
    ctx.fillStyle = str;
    return ctx.fillStyle;
  }

  function downloadCSS() {
    const name = document.getElementById('pName').value.trim();
    const notes = document.getElementById('pNotes').value.trim();
    let cssContent = notes ? `/*\n${notes}\n*/\n\n` : "";
    cssContent += `/* Palette: ${name} */\n:root {\n`;
    colorsArr.forEach((c, i) => cssContent += `  --pal${name}-${i+1}: ${c};\n`);
    cssContent += `}`;
    const blob = new Blob([cssContent], {type: 'text/css'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    const filename = name
    .split(/\s+/) // Découpe sur n'importe quel nombre d'espaces
    .filter(word => word.length > 0) // Supprime les entrées vides
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
    a.download = `${filename}.css`;
    a.click();
  }

  updateAll();
