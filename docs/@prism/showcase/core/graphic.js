/* ------------- *
 * -- CATEGOS -- *
 * ------------- */

function getActiveCategos() {
  return [
    ...document.querySelectorAll('.cat-checkbox:checked')
  ].map(
    cb => cb.value
  );
}


function isVisible(pal_name) {
  if (typeof PAL_CATEGO === 'undefined') {
    return true;
  }

  const active_categos = getActiveCategos();

  if (active_categos.length === 0) {
    return false;
  }

  const all_categos = PAL_CATEGO[pal_name] ?? [];

  return all_categos.some(
    c => active_categos.includes(c)
  );
}


function buildCategoBar() {
  const bar = document.getElementById('category-bar');

  if (!bar) {
    return;
  }

  if (typeof PAL_CATEGO === 'undefined') {
    bar.style.display = 'none';

    return;
  }

  const all_categos = [
    ...new Set(
      Object.values(PAL_CATEGO).flat()
    )
  ].sort();

  const all_btn = document.createElement('button');

  all_btn.className   = 'cat-all-btn';
  all_btn.textContent = 'All';
  all_btn.onclick     = () => {
    bar.querySelectorAll('.cat-checkbox').forEach(
      cb => cb.checked = true
    );

    refreshScrollZone();
  };

  bar.appendChild(all_btn);

  const none_btn = document.createElement('button');

  none_btn.className   = 'cat-all-btn';
  none_btn.textContent = 'None';
  none_btn.onclick     = () => {
    bar.querySelectorAll('.cat-checkbox').forEach(
      cb => cb.checked = false
    );

    refreshScrollZone();
  };

  bar.appendChild(none_btn);

  const sep = document.createElement('span');

  sep.className = 'cat-sep';

  bar.appendChild(sep);

  all_categos.forEach(
    cat => {
      const label = document.createElement('label');

      label.className = 'cat-label';

      const cb = document.createElement('input');

      cb.type      = 'checkbox';
      cb.className = 'cat-checkbox';
      cb.value     = cat;
      cb.checked   = true;
      cb.onchange  = refreshScrollZone;

      label.appendChild(cb);
      label.append(' ' + cat);

      bar.appendChild(label);
    }
  );
}


/* ------------------------- *
 * -- PALETTE SCROLL ZONE -- *
 * ------------------------- */

function filterByLetter(
  letter,
  btn,
  targetPalette = null
) {
  document.querySelectorAll('.letter-btn').forEach(
    b => b.classList.remove('active')
  );

  btn.classList.add('active');

  const scroll_zone = document.getElementById('scroll-zone');

  scroll_zone.innerHTML = '';

  const matches = Object
    .keys(PAL_SIZE)
    .filter(name => name[0].toUpperCase() === letter)
    .filter(name => isVisible(name))
    .sort();

  if (matches.length === 0) {
    const message = document.createElement('p');

    message.className   = 'scroll-empty';
    message.textContent = 'No palette for this letter and these categories.';

    scroll_zone.appendChild(message);

    return;
  }

  matches.forEach(
    name => {
      const btn = document.createElement('button');

      btn.className = `palette-choice ${targetPalette === name ? 'selected' : ''}`;
      btn.innerHTML = `<strong>${name}</strong><small>${PAL_SIZE[name]} tons</small>`;
      btn.onclick   = () => selectPal(
        name,
        PAL_SIZE[name],
        btn
      );

      scroll_zone.appendChild(btn);

      if (targetPalette === name) {
        setTimeout(
          () => btn.scrollIntoView({block: 'nearest'}),
          50
        );
      }
    }
  );
}


function refreshScrollZone() {
  const active_btn = document.querySelector('.letter-btn.active');

  if (!active_btn) {
    return;
  }

  filterByLetter(
    active_btn.textContent,
    active_btn,
    null
  );
}


function selectPal(
  name,
  size,
  btn = null
) {
  const css_path = `../../../@prism/products//css/palettes-hf/${name}.css`;

  const link_tag = document.getElementById('dynamic-palette-css');

  if (link_tag.getAttribute('href') !== css_path) {
    link_tag.href = css_path;
  }

  document.querySelectorAll('.palette-choice').forEach(
    b => b.classList.remove('selected')
  );

  if (btn) {
    btn.classList.add('selected');
  }

  document.getElementById('current-title').textContent = name;

  document.getElementById('color-count').textContent = `${size} colors`;

  document.getElementById('result-area').style.display = 'block';

  const dl_bar = document.getElementById('download-bar');

  if (dl_bar) {
    dl_bar.innerHTML = Object.entries(PAL_FORMAT).map(
      ([folder, ext]) =>
      `<a class="btn-tool btn-download"
          href="../../../@prism/products//${folder}/palettes-hf/${name}.${ext}"
          download="${name}.${ext}">
        ⬇ ${ext.toUpperCase()} (${folder})
       </a>`
    ).join('');
  }

  draw(name, size);
}


/* --------------------- *
 * -- RANDOM SHOWCASE -- *
 * --------------------- */

function pickRandom() {
  const pool = Object.keys(PAL_SIZE).filter(
    name => isVisible(name)
  );

  if (pool.length === 0) {
    return;
  }

  const key = pool[Math.floor(Math.random() * pool.length)];

  const letter_btn = document.getElementById(`btn-letter-${key[0].toUpperCase()}`);

  filterByLetter(
    key[0].toUpperCase(),
    letter_btn,
    key
  );

  selectPal(
    key,
    PAL_SIZE[key]
  );
}


/* -------------- *
 * -- SVG DRAW -- *
 * -------------- */

function draw(name, size) {
  const colors = [];

  for (let i = 1; i <= size; i++) {
    colors.push(`var(--pal${name}-${i})`);
  }

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

  document.getElementById('spectrum-preview').style.background =
    `linear-gradient(90deg, ${colors.join(', ')})`;

  const svg = document.getElementById('canvas');

  svg.innerHTML = '';

  const x_center     = 130;
  const y_center     = 125;
  const x_wave_start = 280;
  const R_max        = 100;

  colors.forEach(
    (c, i) => {
      const circ = document.createElementNS("http://www.w3.org/2000/svg", "circle");

      circ.setAttribute("cx", x_center);
      circ.setAttribute("cy", y_center);
      circ.setAttribute("r", R_max - (i * (R_max / size)));
      circ.setAttribute("fill", c);

      svg.appendChild(circ);
    }
  );

  if (size <= 40) {
    colors.forEach(
      (c, i) => {
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");

        const y_base = y_center + (i * 7) - (size * 3.5);

        let d = `M ${x_wave_start} ${y_base + Math.sin(i) * 40}`;

        for (let x = 1; x <= 440; x += 2) {
          d += ` L ${x_wave_start + x} ${y_base + Math.sin(x * 0.04 + i) * 40}`;
        }

        path.setAttribute("d", d);
        path.setAttribute("stroke", c);
        path.setAttribute("fill", "none");
        path.setAttribute("stroke-width", "4");
        path.setAttribute("stroke-linecap", "round");

        svg.appendChild(path);
    });

  } else {
    const svg_width  = 800;
    const svg_height = 400;
    const x_split    = 400;
    const nb_colors  = colors.length;

    let local_seed = 42;

    const localRandom = () => {
      local_seed = (local_seed * 1664525 + 1013904223) % 4294967296;

      return local_seed / 4294967296;
    };

    const shuffled_colors = [...colors];

    for (let i = shuffled_colors.length - 1; i > 0; i--) {
      const j = Math.floor(localRandom() * (i + 1));

      [shuffled_colors[i], shuffled_colors[j]] = [shuffled_colors[j], shuffled_colors[i]];
    }

    const cols        = Math.ceil(Math.sqrt(nb_colors / 2));
    const rows        = Math.ceil(nb_colors / (cols * 2));
    const cell_width  = (svg_width - x_split) / cols;
    const cell_height = svg_height / rows;
    const jitter      = 0.5;

    const points = [];

    for (let r = 0; r <= rows; r++) {
      points[r] = [];

      for (let c = 0; c <= cols; c++) {
        let x = x_split + c * cell_width;
        let y = r * cell_height;

        if (c > 0 && c < cols) {
          x += (localRandom() - 0.5) * cell_width * jitter;
        }

        if (r > 0 && r < rows) {
          y += (localRandom() - 0.5) * cell_height * jitter;
        }

        points[r][c] = { x, y };
      }
    }

    let color_index = 0;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const triangles = [
          [points[r][c],     points[r][c + 1],     points[r + 1][c]],
          [points[r][c + 1], points[r + 1][c + 1], points[r + 1][c]]
        ];

        triangles.forEach(
          vertices => {
            if (color_index < nb_colors) {
              const polygon = document.createElementNS(
                "http://www.w3.org/2000/svg",
                "polygon"
              );

              const pts  = vertices.map(
                p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`
              ).join(" ");

              polygon.setAttribute("points", pts);
              polygon.setAttribute("fill", shuffled_colors[color_index]);
              polygon.setAttribute("stroke", shuffled_colors[color_index]);
              polygon.setAttribute("stroke-width", "1");

              svg.appendChild(polygon);

              color_index++;
            }
          }
        );
      }
    }
  }
}


/* -------------------- *
 * -- INIT INTERFACE -- *
 * -------------------- */

function initInterface() {
  const alpha_bar = document.getElementById('alphabet-bar');

  if (typeof PAL_SIZE === 'undefined') {
    return;
  }

  buildCategoBar();

  const available_letters = [
    ...new Set(
      Object.keys(PAL_SIZE).map(
        name => name[0].toUpperCase()
      )
    )
  ];

  "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    .split('')
    .forEach(
      L => {
        const btn = document.createElement('button');

        btn.className = `letter-btn ${available_letters.includes(L) ? '' : 'disabled'}`;
        btn.id = `btn-letter-${L}`;
        btn.textContent = L;

        if (!btn.classList.contains('disabled')) {
          btn.onclick = () => filterByLetter(L, btn);
        }

        alpha_bar.appendChild(btn);
      }
    );

  const first = document.querySelector('.letter-btn:not(.disabled)');

  if (first) {
    first.click();
  }
}


window.onload = initInterface;
