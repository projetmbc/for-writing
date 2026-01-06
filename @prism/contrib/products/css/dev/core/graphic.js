let colorsArr = [];


function toggleTheme() {
  document.body.classList.toggle('dark-mode');
}


function hexToRgbPercent(hex) {
  let r = parseInt(hex.slice(1, 3), 16);
  let g = parseInt(hex.slice(3, 5), 16);
  let b = parseInt(hex.slice(5, 7), 16);

  let rp = (r / 255 * 100).toFixed(3);
  let gp = (g / 255 * 100).toFixed(3);
  let bp = (b / 255 * 100).toFixed(3);

  return `rgb(${rp}% ${gp}% ${bp}%)`;
}


function anyToHex(str) {
  const ctx = document.createElement('canvas').getContext('2d');

  ctx.fillStyle = str;

  return ctx.fillStyle;
}


function updateAll() {
  const size = parseInt(document.getElementById('pSize').value) || 2;

  colorsArr = document.getElementById('pList').value
    .split('\n')
    .map(c => c.trim())
    .filter(c => c !== "")
    .slice(0, size);

  const preview = document.getElementById('palettePreview');

  if (preview.children.length !== colorsArr.length) {
    preview.innerHTML = colorsArr.map((c, i) => `
<div class="swatch" style="background: ${c}">
  <input type    = "color"
         value   = "${anyToHex(c)}"
         oninput = "editColor(${i}, this.value)">
</div>
    `).join('');
  }

  updateVisuals();
}


function updateVisuals() {
  const spectrum = document.getElementById('spectrum');

  if (colorsArr.length > 1) {
    spectrum.style.background = `linear-gradient(to right, ${colorsArr.join(', ')})`;

  } else {
    spectrum.style.background = colorsArr[0];
  }

  drawSVG(colorsArr);
}


function editColor(index, hex) {
  // Conversion en format RGB % pro
  const rgbPercent = hexToRgbPercent(hex);

  colorsArr[index] = rgbPercent;

  document.getElementById('pList').value = colorsArr.join('\n');

  const swatches = document.querySelectorAll('.swatch');
  if (swatches[index]) {
    swatches[index].style.background = rgbPercent;
  }

  updateVisuals();
}

function drawSVG(colors) {
  const svg = document.getElementById('canvas');

  svg.innerHTML = '';

  const n = colors.length;

  if (n === 0) return;

  // Cercles concentriques
  const step = 150 / n;

  colors.forEach((c, i) => {
    const circ = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "circle"
    );

    circ.setAttribute("cx", 200);
    circ.setAttribute("cy", 200);
    circ.setAttribute("r", 150 - (i * step));
    circ.setAttribute("fill", c);

    svg.appendChild(circ);
  });

  // Ondes sinusoïdales
  colors.forEach((c, i) => {
    const p = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "path"
    );

    const yB = 200 + (i * 6) - (n * 3);
    const startX = 420;
    const initialY = yB + Math.sin(0 * 0.03 + i) * 60;

    let d = `M ${startX} ${initialY}`;

    for (let x = 0; x <= 500; x += 1) {
      d += ` L ${startX + x} ${yB + Math.sin(x * 0.03 + i) * 60}`;
    }

    p.setAttribute("d", d);
    p.setAttribute("stroke", c);
    p.setAttribute("fill", "none");
    p.setAttribute("stroke-width", "5");
    p.setAttribute("stroke-linecap", "round");

    svg.appendChild(p);
  });
}

function downloadCSS() {
  const name = document.getElementById('pName').value.trim();
  const notes = document.getElementById('pNotes').value.trim();

  const stdname = name
    .split(/[\s-_]+/) // Coupe au niveau des espaces, tirets ou underscores
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');

  let css = notes ? `/***\n${notes}\n***/\n\n` : "";
  css += `/* Palette: ${stdname} */\n:root {\n`;
  css += colorsArr.map((c, i) => `  --pal${stdname}-${i + 1}: ${c};`).join('\n');
  css += `\n}`;

  const blob = new Blob([css], { type: 'text/css' });

  const a = document.createElement('a');

  a.href = URL.createObjectURL(blob);
  a.download = `${name.replace(/\s+/g, '')}.css`;
  a.click();
}

function generateRandomPalette(size = 10) {
  let randomColors = [];

  for (let i = 0; i < size; i++) {
    const r = (Math.random() * 100).toFixed(3);
    const g = (Math.random() * 100).toFixed(3);
    const b = (Math.random() * 100).toFixed(3);

    randomColors.push(`rgb(${r}% ${g}% ${b}%)`);
  }

  document.getElementById('pList').value = randomColors.join('\n');
}

// Lancement au chargement de la page
window.onload = () => {
  generateRandomPalette(10);
  updateAll();
};
