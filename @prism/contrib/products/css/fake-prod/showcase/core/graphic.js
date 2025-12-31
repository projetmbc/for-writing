// 1. Tableau associatif : Nom -> Taille
const palettesData = {
  "Accent": 10,
  "Alizari": 12,
  "Amber": 9,
  "Azure": 8,
  "Bordeaux": 11,
  "Bronze": 10,
  "Berry": 14,
  "Cyan": 10,
  "Cobalt": 12,
  "Crimson": 8,
  "Default": 5,
  "DeepSea": 15,
  "Dragon": 10,
  "Emerald": 10,
  "Electric": 7,
  "Earthy": 12,
  "Fuchsia": 10,
  "Forest": 11,
  "Fire": 9,
  "Gold": 8,
  "Graphite": 10,
  "Grape": 13,
  "Hot": 10,
  "Heliotrope": 10,
  "Indigo": 10,
  "Ice": 6
};

// 2. Génération des onglets (Groupes de 4 lettres)
function initTabs() {
  const container = document.getElementById('tabsInterface');
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const alphaArray = alphabet.split('');

  let htmlTabs = '<div class="tabs-header">';
  let htmlContent = '';

  for (let i = 0; i < alphaArray.length; i += 4) {
    const groupe = alphaArray.slice(i, i + 4);
    const label = `${groupe[0]}-${groupe[groupe.length - 1]}`;
    const tabId = `tab-${label}`;

    // Bouton
    htmlTabs += `<button class="tab-btn" onclick="openTab(event, '${tabId}')">${label}</button>`;

    // Panneau
    htmlContent += `<div id="${tabId}" class="tab-content">`;

    // Filtrer les palettes
    const palettesFiltrees = Object.keys(palettesData).filter(p =>
      groupe.includes(p[0].toUpperCase())
    );

    if (palettesFiltrees.length === 0) {
      htmlContent += `<p style="grid-column: 1/-1; opacity: 0.5;">Aucune palette</p>`;
    } else {
      palettesFiltrees.forEach(nom => {
        htmlContent += `
          <button class="palette-choice" onclick="selectPalette('${nom}', ${palettesData[nom]})">
            <strong>${nom}</strong><br>
            <small>${palettesData[nom]} couleurs</small>
          </button>`;
      });
    }
    htmlContent += `</div>`;
  }

  container.innerHTML = htmlTabs + '</div>' + htmlContent;

  // Ouvrir le premier onglet par défaut
  document.querySelector('.tab-btn').click();
}

function openTab(evt, tabId) {
  document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(tb => tb.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  evt.currentTarget.classList.add('active');
}

// 3. Sélection et Dessin
function selectPalette(nom, taille) {
  document.getElementById('pName').value = nom;
  document.getElementById('pSize').value = taille;
  document.getElementById('currentTitle').textContent = `Palette : ${nom}`;
  draw();
}

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

  preview.innerHTML = colorVars.map(v => `<div class="swatch" style="background: ${v}"></div>`).join('');
  spectrum.style.background = `linear-gradient(to right, ${colorVars.join(', ')})`;

  // SVG graphics
  svg.innerHTML = '';
  const centerX = 200;
  const centerY = 200;
  const maxR = 150;
  const rStep = maxR / size;

  // Dessiner les cercles concentriques
  colorVars.forEach((v, i) => {
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", centerX);
    circle.setAttribute("cy", centerY);
    circle.setAttribute("r", maxR - (i * rStep));
    circle.setAttribute("fill", v);
    svg.appendChild(circle);
  });

  // Dessiner les ondes sinusoïdales
  const startX = 400;
  const width = 350;

  colorVars.forEach((v, i) => {
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    const yBase = 200 + (i * 6) - (size * 3);

    // CORRECTION : Calculer la position Y de départ avec le sinus dès le 'M'
    let startY = yBase + Math.sin(0 * 0.03 + i) * 30;
    let d = `M ${startX} ${startY}`;

    // La boucle commence à 10 pour continuer le tracé
    for (let x = 10; x <= width; x += 10) {
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

// Lancement au chargement
window.onload = initTabs;
