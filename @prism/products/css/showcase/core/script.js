let colors = [];
let colorComments = [];

function toggleTheme() {
  document.body.classList.toggle('dark-mode');
}

function parseColors(input) {
  const lines = input.split('\n');
  const parsed = [];
  const comments = [];

  for (let line of lines) {
    line = line.trim();
    if (!line || line.startsWith('/*')) continue;

    const match = line.match(/#[0-9A-Fa-f]{6}/);
    if (match) {
      parsed.push(match[0].toUpperCase());

      // Extract comment if present
      const commentMatch = line.match(/\/\*\s*(.+?)\s*\*\//);
      comments.push(commentMatch ? commentMatch[1] : '');
    }
  }

  return { colors: parsed, comments: comments };
}

function loadPalette() {
  const input = document.getElementById('colorInput').value;
  const error = document.getElementById('error');

  const result = parseColors(input);
  colors = result.colors;
  colorComments = result.comments;

  if (colors.length < 2) {
    error.textContent = 'Veuillez entrer au moins 2 couleurs valides';
    return;
  }

  // No maximum limit for input colors

  error.textContent = '';
  renderPalette();
  renderVisualizations();
}

function renderPalette() {
  const grid = document.getElementById('paletteGrid');
  grid.innerHTML = '';

  // Update title with color count
  const title = document.querySelector('.palette-display .viz-title');
  title.textContent = `Votre Palette (${colors.length} couleur${colors.length > 1 ? 's' : ''})`;

  colors.forEach((color, index) => {
    const item = document.createElement('div');
    item.className = 'color-item';

    item.innerHTML = `
      <div class="color-number">${index + 1}</div>
      <div class="color-box" style="background-color: ${color}" onclick="openColorPicker(${index})"></div>
      <div class="color-code">${color}</div>
      <input type="text" class="color-input" value="${color}" onchange="updateColor(${index}, this.value)" onclick="openColorPicker(${index})" readonly>
      <input type="color" class="color-picker" id="picker-${index}" value="${color}" onchange="updateColorFromPicker(${index}, this.value)">
      <button class="remove-btn" onclick="removeColor(${index})" ${colors.length <= 2 ? 'disabled style="display:none"' : ''}>×</button>
    `;

    grid.appendChild(item);
  });

  const addBtn = document.createElement('div');
  addBtn.className = 'add-color-btn';
  addBtn.textContent = '+';
  addBtn.onclick = addColor;
  grid.appendChild(addBtn);

  // Render interpolated palette if different from original
  renderInterpolatedPalette();
}

function renderInterpolatedPalette() {
  const interpolatedSection = document.getElementById('interpolatedSection');
  const interpolatedGrid = document.getElementById('interpolatedGrid');

  if (colors.length === 10) {
    interpolatedSection.style.display = 'none';
    return;
  }

  interpolatedSection.style.display = 'block';
  interpolatedGrid.innerHTML = '';

  const tenColors = generateTenColors(colors);

  tenColors.forEach((color, index) => {
    const item = document.createElement('div');
    item.className = 'color-item';

    item.innerHTML = `
      <div class="color-number">${index + 1}</div>
      <div class="color-box" style="background-color: ${color}"></div>
      <div class="color-code">${color}</div>
    `;

    interpolatedGrid.appendChild(item);
  });
}

function updateColor(index, newColor) {
  newColor = newColor.trim().toUpperCase();
  if (/^#[0-9A-F]{6}$/.test(newColor)) {
    colors[index] = newColor;
    renderPalette();
    renderVisualizations();
  }
}

function openColorPicker(index) {
  const picker = document.getElementById(`picker-${index}`);
  if (picker) {
    picker.click();
  }
}

function updateColorFromPicker(index, newColor) {
  colors[index] = newColor.toUpperCase();
  renderPalette();
  renderVisualizations();
}

function removeColor(index) {
  if (colors.length > 2) {
    colors.splice(index, 1);
    colorComments.splice(index, 1);
    renderPalette();
    renderVisualizations();
  }
}

function addColor() {
  colors.push('#808080');
  colorComments.push('');
  renderPalette();
  renderVisualizations();
}

function renderVisualizations() {
  const gradient = document.getElementById('gradientBar');
  gradient.style.background = `linear-gradient(90deg, ${colors.join(', ')})`;

  renderConcentricCircles();
  renderSineWave();
}

function renderConcentricCircles() {
  const svg = document.getElementById('concentricCircles');
  svg.innerHTML = '';

  const centerX = 200;
  const centerY = 200;
  const maxRadius = 180;
  const numCircles = colors.length;

  for (let i = numCircles - 1; i >= 0; i--) {
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    const radius = maxRadius * ((i + 1) / numCircles);

    circle.setAttribute('cx', centerX);
    circle.setAttribute('cy', centerY);
    circle.setAttribute('r', radius);
    circle.setAttribute('fill', colors[i]);
    circle.setAttribute('stroke', 'none');

    svg.appendChild(circle);
  }
}

function renderSineWave() {
  const svg = document.getElementById('sineWave');
  const width = svg.clientWidth;
  const height = 400;
  svg.innerHTML = '';

  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

  const numWaves = colors.length;
  const amplitude = 60;
  const centerY = height / 2;
  const frequency = 0.02;
  const points = 200;

  colors.forEach((color, index) => {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    let d = '';

    const phaseShift = (index * Math.PI * 2) / numWaves;
    const yOffset = ((index - (numWaves - 1) / 2) * 20);

    for (let i = 0; i <= points; i++) {
      const x = (i / points) * width;
      const y = centerY + yOffset + amplitude * Math.sin(frequency * x + phaseShift);

      if (i === 0) {
        d += `M ${x} ${y}`;
      } else {
        d += ` L ${x} ${y}`;
      }
    }

    path.setAttribute('d', d);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', color);
    path.setAttribute('stroke-width', '3');
    path.setAttribute('stroke-linecap', 'round');

    svg.appendChild(path);
  });
}

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return { r, g, b };
}

function rgbToHex(r, g, b) {
  const toHex = (n) => {
    const hex = Math.round(n).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`.toUpperCase();
}

function interpolateColor(color1, color2, factor) {
  const c1 = hexToRgb(color1);
  const c2 = hexToRgb(color2);

  const r = c1.r + factor * (c2.r - c1.r);
  const g = c1.g + factor * (c2.g - c1.g);
  const b = c1.b + factor * (c2.b - c1.b);

  return rgbToHex(r, g, b);
}

function generateTenColors(inputColors) {
  if (inputColors.length === 10) {
    return inputColors;
  }

  if (inputColors.length > 10) {
    // Sample 10 colors evenly from the input
    const result = [];
    for (let i = 0; i < 10; i++) {
      const index = Math.floor(i * (inputColors.length - 1) / 9);
      result.push(inputColors[index]);
    }
    return result;
  }

  // Interpolate to get 10 colors
  const result = [];
  const segments = 9; // 10 colors = 9 segments

  for (let i = 0; i < 10; i++) {
    const position = i / segments;
    const scaledPosition = position * (inputColors.length - 1);
    const lowerIndex = Math.floor(scaledPosition);
    const upperIndex = Math.min(lowerIndex + 1, inputColors.length - 1);
    const factor = scaledPosition - lowerIndex;

    result.push(interpolateColor(inputColors[lowerIndex], inputColors[upperIndex], factor));
  }

  return result;
}

function downloadCSS() {
  if (colors.length === 0) {
    alert('Veuillez d\'abord charger une palette');
    return;
  }

  // Generate exactly 10 colors through interpolation
  const tenColors = generateTenColors(colors);

  const headerText = document.getElementById('headerInput').value.trim();

  let css = '/***\n';

  // Add custom header text or default
  if (headerText) {
    css += headerText + '\n';
  } else {
    css += 'this::\n    author = First Name, Last Name\n';
  }

  css += 'css::\n';

  // Only color codes in css:: section, no comments
  tenColors.forEach(color => {
    css += `    ${color}\n`;
  });

  css += '***/\n:root {\n';

  // Individual color variables (exactly 10)
  tenColors.forEach((color, index) => {
    css += `  --color-${index + 1}: ${color};\n`;
  });

  css += '\n  /* Gradients */\n';
  css += `  --gradient-palette: linear-gradient(90deg, ${tenColors.join(', ')});\n`;
  css += `  --gradient-palette-reverse: linear-gradient(90deg, ${[...tenColors].reverse().join(', ')});\n`;

  // Shifted versions
  const shifted1 = [...tenColors.slice(1), tenColors[0]];
  const shifted2 = [...tenColors.slice(2), ...tenColors.slice(0, 2)];
  css += `  --gradient-palette-shift1: linear-gradient(90deg, ${shifted1.join(', ')});\n`;
  css += `  --gradient-palette-shift2: linear-gradient(90deg, ${shifted2.join(', ')});\n`;

  css += '}\n';

  const blob = new Blob([css], { type: 'text/css' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'palette.css';
  a.click();
  URL.revokeObjectURL(url);
}

function resetPalette() {
  document.getElementById('colorInput').value = '';
  colors = [];
  document.getElementById('paletteGrid').innerHTML = '';
  document.getElementById('gradientBar').style.background = '#f0f0f0';
  document.getElementById('circlesContainer').innerHTML = '';
  document.getElementById('barsContainer').innerHTML = '';
  document.getElementById('error').textContent = '';
}
