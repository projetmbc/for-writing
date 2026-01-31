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

        btn.className   = `letter-btn ${availableLetters.includes(L) ? '' : 'disabled'}`;
        btn.id          = `btn-letter-${L}`;
        btn.textContent = L;

        if (!btn.classList.contains('disabled')) btn.onclick = () => filterByLetter(L, btn);

        alphaBar.appendChild(btn);
      }
    );

  const first = document.querySelector('.letter-btn:not(.disabled)');

  if (first) first.click();
}

function filterByLetter(letter, btn, targetPalette = null) {
  document
    .querySelectorAll('.letter-btn')
    .forEach(
      b => b.classList.remove('active')
    );

  btn.classList.add('active');

  const scrollZone = document.getElementById('scrollZone');

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
      pBtn.onclick   = () => selectPalette(name, palsize[name], pBtn);

      scrollZone.appendChild(pBtn);

      if(targetPalette === name) setTimeout(() => pBtn.scrollIntoView({ block: 'nearest' }), 50);
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
  document
    .querySelectorAll('.palette-choice')
    .forEach(b => b.classList.remove('selected'));

  if(btnElement) btnElement.classList.add('selected');

  document.getElementById('currentTitle').textContent = nom;
  document.getElementById('colorCount').textContent   = `${taille} colors`;
  document.getElementById('resultArea').style.display = 'block';

  draw(nom, taille);
}

function draw(name, size) {
  const colors = [];

  for (let i = 1; i <= size; i++) colors.push(`var(--pal${name}-${i})`);

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

  document.getElementById('spectrum-preview').style.background = `linear-gradient(90deg, ${colors.join(', ')})`;

  const svg = document.getElementById('canvas');

  svg.innerHTML = '';

  const centerY = 125;
  const circleX = 130;
  const waveStartX = 280;
  const maxR = 100;

// Cercles
  colors.forEach((c, i) => {
    const circ = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "circle"
    );

    circ.setAttribute("cx", circleX);
    circ.setAttribute("cy", centerY);
    circ.setAttribute("r", maxR - (i * (maxR/size)));
    circ.setAttribute("fill", c);

    svg.appendChild(circ);
  })

// Ondes
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

// Diagonales
  } else {
    colors.forEach((c, i) => {
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");

      const offset = (i * 5) - (size * 2.5);
      const xStart = waveStartX;
      const xEnd = waveStartX + 440;

      const yStart = centerY + 80 + offset;
      const yEnd = centerY - 80 + offset;

      const d = `M ${xStart} ${yStart} L ${xEnd} ${yEnd}`;

      path.setAttribute("d", d);
      path.setAttribute("stroke", c);
      path.setAttribute("fill", "none");
      path.setAttribute("stroke-width", "2.5");
      path.setAttribute("stroke-linecap", "round");

      svg.appendChild(path);
    });
  }
}

window.onload = initInterface;
