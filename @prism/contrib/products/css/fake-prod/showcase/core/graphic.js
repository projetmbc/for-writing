// ─── Utilitaire : palettes visibles selon les catégories cochées ──────────────

function getActiveCategories() {
  return [...document.querySelectorAll('.cat-checkbox:checked')]
    .map(cb => cb.value);
}

function isVisible(paletteName) {
  // Si palcategories n'est pas chargé, tout est visible
  if (typeof palcategories === 'undefined') return true;

  const active = getActiveCategories();

  // Aucun filtre coché → rien de visible
  if (active.length === 0) return false;

  const cats = palcategories[paletteName] ?? [];

  // La palette est visible si elle appartient à au moins une catégorie cochée
  return cats.some(c => active.includes(c));
}

// ─── Construction de la barre de catégories ───────────────────────────────────

function buildCategoryBar() {
  const bar = document.getElementById('categoryBar');
  if (!bar) return;

  if (typeof palcategories === 'undefined') {
    bar.style.display = 'none';
    return;
  }

  // Collecter toutes les catégories présentes dans le dictionnaire
  const allCats = [
    ...new Set(Object.values(palcategories).flat())
  ].sort();

  // Bouton "Tout"
  const allBtn = document.createElement('button');
  allBtn.className = 'cat-all-btn';
  allBtn.textContent = 'Tout';
  allBtn.onclick = () => {
    bar.querySelectorAll('.cat-checkbox').forEach(cb => cb.checked = true);
    refreshScrollZone();
  };
  bar.appendChild(allBtn);

  // Bouton "Aucun"
  const noneBtn = document.createElement('button');
  noneBtn.className = 'cat-all-btn';
  noneBtn.textContent = 'Aucun';
  noneBtn.onclick = () => {
    bar.querySelectorAll('.cat-checkbox').forEach(cb => cb.checked = false);
    refreshScrollZone();
  };
  bar.appendChild(noneBtn);

  // Séparateur visuel
  const sep = document.createElement('span');
  sep.className = 'cat-sep';
  bar.appendChild(sep);

  // Un checkbox par catégorie
  allCats.forEach(cat => {
    const label = document.createElement('label');
    label.className = 'cat-label';

    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.className = 'cat-checkbox';
    cb.value = cat;
    cb.checked = true; // tout coché par défaut
    cb.onchange = refreshScrollZone;

    label.appendChild(cb);
    label.append(' ' + cat);
    bar.appendChild(label);
  });
}

// ─── Rafraîchit la scroll zone selon la lettre active et les catégories ───────

function refreshScrollZone() {
  const activeBtn = document.querySelector('.letter-btn.active');
  if (!activeBtn) return;
  filterByLetter(activeBtn.textContent, activeBtn, null);
}

// ─── Interface principale ─────────────────────────────────────────────────────

function initInterface() {
  const alphaBar = document.getElementById('alphabetBar');

  if (typeof palsize === 'undefined') return;

  buildCategoryBar();

  const availableLetters = [
    ...new Set(
      Object.keys(palsize)
        .map(name => name[0].toUpperCase())
    )
  ];

  "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    .split('')
    .forEach(L => {
      const btn = document.createElement('button');

      btn.className = `letter-btn ${availableLetters.includes(L) ? '' : 'disabled'}`;
      btn.id = `btn-letter-${L}`;
      btn.textContent = L;

      if (!btn.classList.contains('disabled')) btn.onclick = () => filterByLetter(L, btn);

      alphaBar.appendChild(btn);
    });

  const first = document.querySelector('.letter-btn:not(.disabled)');
  if (first) first.click();
}

function filterByLetter(letter, btn, targetPalette = null) {
  document.querySelectorAll('.letter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  const scrollZone = document.getElementById('scrollZone');
  scrollZone.innerHTML = '';

  const matches = Object
    .keys(palsize)
    .filter(name => name[0].toUpperCase() === letter)
    .filter(name => isVisible(name))           // ← filtre catégories
    .sort();

  if (matches.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'scroll-empty';
    empty.textContent = 'Aucune palette pour cette lettre et ces catégories.';
    scrollZone.appendChild(empty);
    return;
  }

  matches.forEach(name => {
    const pBtn = document.createElement('button');

    pBtn.className = `palette-choice ${targetPalette === name ? 'selected' : ''}`;
    pBtn.innerHTML = `<strong>${name}</strong><small>${palsize[name]} tons</small>`;
    pBtn.onclick = () => selectPalette(name, palsize[name], pBtn);

    scrollZone.appendChild(pBtn);

    if (targetPalette === name) setTimeout(() => pBtn.scrollIntoView({ block: 'nearest' }), 50);
  });
}

function pickRandom() {
  // Pool = toutes les palettes visibles selon les catégories actives
  const pool = Object.keys(palsize).filter(name => isVisible(name));

  if (pool.length === 0) return; // rien à piocher

  const key = pool[Math.floor(Math.random() * pool.length)];

  const letterBtn = document.getElementById(`btn-letter-${key[0].toUpperCase()}`);

  filterByLetter(key[0].toUpperCase(), letterBtn, key);
  selectPalette(key, palsize[key]);
}

function selectPalette(nom, taille, btnElement = null) {
  const cssPath = `../palettes-hf/${nom}.css`;
  const linkTag = document.getElementById('dynamic-palette-css');

  if (linkTag.getAttribute('href') !== cssPath) {
    linkTag.href = cssPath;
  }

  document.querySelectorAll('.palette-choice').forEach(b => b.classList.remove('selected'));
  if (btnElement) btnElement.classList.add('selected');

  document.getElementById('currentTitle').textContent = nom;
  document.getElementById('colorCount').textContent = `${taille} colors`;
  document.getElementById('resultArea').style.display = 'block';

  // Boutons de téléchargement
  const dlBar = document.getElementById('downloadBar');
  if (dlBar) {
    dlBar.innerHTML = formats.map(ext =>
      `<a class="btn-tool btn-download"
          href="../palettes-hf/${nom}.${ext}"
          download="${nom}.${ext}">
        ⬇ ${ext.toUpperCase()}
       </a>`
    ).join('');
  }

  draw(nom, taille);
}

// ─── Rendu SVG ────────────────────────────────────────────────────────────────

const seed = 20260201;

let currentSeed = seed;
const getNextRandom = () => {
  currentSeed = (currentSeed * 1664525 + 1013904223) % 4294967296;
  return currentSeed / 4294967296;
};

function draw(name, size) {
  const colors = [];
  for (let i = 1; i <= size; i++) colors.push(`var(--pal${name}-${i})`);

  // Palette swatches
  if (size > 40) {
    document.getElementById('palette-label').style.display = "none";
    document.getElementById('palette-preview').style.display = "none";
  } else {
    document.getElementById('palette-label').style.display = "flex";
    document.getElementById('palette-preview').style.display = "flex";
    document.getElementById('palette-preview').innerHTML = colors.map(
      c => `<div class="swatch" style="background:${c}"></div>`
    ).join('');
  }

  // Spectrum
  document.getElementById('spectrum-preview').style.background =
    `linear-gradient(90deg, ${colors.join(', ')})`;

  const svg = document.getElementById('canvas');
  svg.innerHTML = '';

  const centerY = 125;
  const circleX = 130;
  const waveStartX = 280;
  const maxR = 100;

  // Cercles concentriques
  colors.forEach((c, i) => {
    const circ = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circ.setAttribute("cx", circleX);
    circ.setAttribute("cy", centerY);
    circ.setAttribute("r", maxR - (i * (maxR / size)));
    circ.setAttribute("fill", c);
    svg.appendChild(circ);
  });

  // Vagues (petite palette ≤ 40 couleurs)
  if (size <= 40) {
    colors.forEach((c, i) => {
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      const yBase = centerY + (i * 7) - (size * 3.5);

      let d = `M ${waveStartX} ${yBase + Math.sin(i) * 40}`;
      for (let x = 1; x <= 440; x += 2) {
        d += ` L ${waveStartX + x} ${yBase + Math.sin(x * 0.04 + i) * 40}`;
      }

      path.setAttribute("d", d);
      path.setAttribute("stroke", c);
      path.setAttribute("fill", "none");
      path.setAttribute("stroke-width", "4");
      path.setAttribute("stroke-linecap", "round");
      svg.appendChild(path);
    });

  // Triangles (grande palette > 40 couleurs)
  } else {
    const svgW = 800;
    const svgH = 400;
    const splitX = 400;
    const count = colors.length;

    // Générateur local isolé (n'interfère pas avec le générateur global)
    let localSeed = 42;
    const localRandom = () => {
      localSeed = (localSeed * 1664525 + 1013904223) % 4294967296;
      return localSeed / 4294967296;
    };

    const shuffledColors = [...colors];
    for (let i = shuffledColors.length - 1; i > 0; i--) {
      const j = Math.floor(localRandom() * (i + 1));
      [shuffledColors[i], shuffledColors[j]] = [shuffledColors[j], shuffledColors[i]];
    }

    const cols = Math.ceil(Math.sqrt(count / 2));
    const rows = Math.ceil(count / (cols * 2));
    const cellW = (svgW - splitX) / cols;
    const cellH = svgH / rows;
    const jitter = 0.5;

    const points = [];
    for (let r = 0; r <= rows; r++) {
      points[r] = [];
      for (let c = 0; c <= cols; c++) {
        let x = splitX + c * cellW;
        let y = r * cellH;
        if (c > 0 && c < cols) x += (localRandom() - 0.5) * cellW * jitter;
        if (r > 0 && r < rows) y += (localRandom() - 0.5) * cellH * jitter;
        points[r][c] = { x, y };
      }
    }

    let colorIndex = 0;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const triangles = [
          [points[r][c],     points[r][c + 1],     points[r + 1][c]],
          [points[r][c + 1], points[r + 1][c + 1], points[r + 1][c]]
        ];

        triangles.forEach(tPoints => {
          if (colorIndex < count) {
            const poly = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
            const pts = tPoints.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");

            poly.setAttribute("points", pts);
            poly.setAttribute("fill", shuffledColors[colorIndex]);
            poly.setAttribute("stroke", shuffledColors[colorIndex]);
            poly.setAttribute("stroke-width", "1");
            svg.appendChild(poly);
            colorIndex++;
          }
        });
      }
    }
  }
}

window.onload = initInterface;
