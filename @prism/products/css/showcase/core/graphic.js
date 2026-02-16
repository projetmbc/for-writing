function initInterface() {
  const alphaBar = document.getElementById('alphabetBar');

  if (typeof palsize === 'undefined') return;

  const availableLetters = [
    ...new Set(
      Object.keys(palsize)
        .map(name => name[0].toUpperCase())
    )
  ];

  "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    .split('')
    .forEach(
      L => {
        const btn = document.createElement('button');

        btn.className = `letter-btn ${availableLetters.includes(L) ? '' : 'disabled'}`;
        btn.id = `btn-letter-${L}`;
        btn.textContent = L;

        if (!btn.classList.contains('disabled')) btn.onclick = () => filterByLetter(L, btn);

        alphaBar.appendChild(btn);
      }
    );

  const first = document.querySelector('.letter-btn:not(.disabled)');

  if (first) first.click();
}

function filterByLetter(letter, btn, targetPalette = null) {
  document.querySelectorAll('.letter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  const scrollZone = document.getElementById('scrollZone');
  scrollZone.innerHTML = '';


  document
    .querySelectorAll('.letter-btn')
    .forEach(
      b => b.classList.remove('active')
    );

  btn.classList.add('active');


  scrollZone.innerHTML = '';

  const matches = Object
    .keys(palsize)
    .filter(name => name[0].toUpperCase() === letter)
    .sort();

  matches.forEach(
    name => {
      const pBtn = document.createElement('button');

      pBtn.className = `palette-choice ${targetPalette === name ? 'selected' : ''}`;
      pBtn.innerHTML = `<strong>${name}</strong><small>${palsize[name]} tons</small>`;
      pBtn.onclick = () => selectPalette(name, palsize[name], pBtn);

      scrollZone.appendChild(pBtn);

      if (targetPalette === name) setTimeout(() => pBtn.scrollIntoView({ block: 'nearest' }), 50);
    }
  );
}

function pickRandom() {
  const keys = Object.keys(palsize);

  const key = keys[Math.floor(Math.random() * keys.length)];

  const letterBtn = document.getElementById(`btn-letter-${key[0].toUpperCase()}`);

  filterByLetter(key[0].toUpperCase(), letterBtn, key);

  selectPalette(key, palsize[key]);
}

function selectPalette(nom, taille, btnElement = null) {
  const cssPath = `../palettes-hf/${nom}.css`;
  const linkTag = document.getElementById('dynamic-palette-css');

  // On ne recharge le CSS que si c'est une nouvelle lettre
  if (linkTag.getAttribute('href') !== cssPath) {
    linkTag.href = cssPath;
  }


  document
    .querySelectorAll('.palette-choice')
    .forEach(b => b.classList.remove('selected'));

  if (btnElement) btnElement.classList.add('selected');

  document.getElementById('currentTitle').textContent = nom;
  document.getElementById('colorCount').textContent = `${taille} colors`;
  document.getElementById('resultArea').style.display = 'block';

  draw(nom, taille);
}

const seed = 20260201; // Change cette valeur pour générer une nouvelle variante
const srandom = (s) => {
  let t = s + 0x6D2B79F5;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

let currentSeed = seed;
const getNextRandom = () => {
  currentSeed = (currentSeed * 1664525 + 1013904223) % 4294967296;
  return currentSeed / 4294967296;
};

function draw(name, size) {
  const colors = [];

  for (let i = 1; i <= size; i++) colors.push(`var(--pal${name}-${i})`);

  // Palettes.
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

  // Spectrum.
  document.getElementById('spectrum-preview').style.background = `linear-gradient(90deg, ${colors.join(', ')})`;

  const svg = document.getElementById('canvas');

  svg.innerHTML = '';

  const centerY = 125;
  const circleX = 130;
  const waveStartX = 280;
  const maxR = 100;

  // Circles
  colors.forEach((c, i) => {
    const circ = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "circle"
    );

    circ.setAttribute("cx", circleX);
    circ.setAttribute("cy", centerY);
    circ.setAttribute("r", maxR - (i * (maxR / size)));
    circ.setAttribute("fill", c);

    svg.appendChild(circ);
  })

  // Waves (small size).
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

// Random triangles (big size).
  } else {
    const width = 800;
    const height = 400;
    const splitX = 400;
    const size = colors.length;


    let seed = 42;
    const getNextRandom = () => {
      seed = (seed * 1664525 + 1013904223) % 4294967296;
      return seed / 4294967296;
    };

    const shuffledColors = [...colors];
    for (let i = shuffledColors.length - 1; i > 0; i--) {
      const j = Math.floor(getNextRandom() * (i + 1));
      [shuffledColors[i], shuffledColors[j]] = [shuffledColors[j], shuffledColors[i]];
    }

    const cols = Math.ceil(Math.sqrt(size / 2));
    const rows = Math.ceil(size / (cols * 2));
    const cellW = (width - splitX) / cols;
    const cellH = height / rows;

    const points = [];
    const jitter = 0.5;

    for (let r = 0; r <= rows; r++) {
      points[r] = [];
      for (let c = 0; c <= cols; c++) {
        let x = splitX + c * cellW;
        let y = r * cellH;
        if (c > 0 && c < cols) x += (getNextRandom() - 0.5) * cellW * jitter;
        if (r > 0 && r < rows) y += (getNextRandom() - 0.5) * cellH * jitter;
        points[r][c] = { x, y };
      }
    }

    let colorIndex = 0;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const triangles = [
          [points[r][c], points[r][c + 1], points[r + 1][c]],
          [points[r][c + 1], points[r + 1][c + 1], points[r + 1][c]]
        ];

        triangles.forEach(tPoints => {
          if (colorIndex < size) {
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
