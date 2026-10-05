/* Optional article figures. Native SVG/canvas; data is loaded on first use. */
(() => {
  'use strict';
  const dataURL = document.currentScript.src ? new URL('../assets/cluster/figure-data.json', document.currentScript.src) : null;
  const ns = 'http://www.w3.org/2000/svg';
  const palette = {primary: '#963d31', external: '#526d82', ink: '#22231f', muted: '#62645e', rule: '#e2e5dc'};
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const diagnostics = window.CLUSTER_FIGURES = {};
  let pending, chartNumber = 0;

  function readData() {
    if (!pending) {
      const embedded = document.getElementById('figure-data');
      pending = embedded ? Promise.resolve(JSON.parse(embedded.textContent)) :
        fetch(dataURL).then(response => {
          if (!response.ok) throw new Error('Figure data unavailable');
          return response.json();
        });
      pending = pending.catch(error => { pending = null; throw error; });
    }
    return pending;
  }
  const byId = id => document.getElementById(id);
  const pressed = (buttons, key, value) => buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset[key] === value)));
  const sum = values => values.reduce((a, b) => a + b, 0);
  function element(tag, attrs = {}, text) {
    const node = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, value));
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function observe(figure, render) {
    let frame;
    new ResizeObserver(() => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(render);
    }).observe(figure);
  }
  function canvasContext(canvas, width, height) {
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    const context = canvas.getContext('2d');
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);
    context.fillStyle = '#fff';
    context.fillRect(0, 0, width, height);
    return context;
  }
  function ticks(low, high, count = 5) {
    const rough = (high - low) / count;
    const power = 10 ** Math.floor(Math.log10(rough));
    const step = [1, 2, 5, 10].map(v => v * power).find(v => v >= rough);
    const result = [];
    for (let v = Math.ceil(low / step) * step; v <= high + step * 1e-8; v += step) result.push(Number(v.toPrecision(9)));
    return result;
  }
  function axisPlot(host, options) {
    const width = Math.max(host.clientWidth, 260), height = width < 450 ? 325 : 365;
    const margin = {left: 58, right: 15, top: 17, bottom: 54};
    const innerWidth = width - margin.left - margin.right, innerHeight = height - margin.top - margin.bottom;
    const transformX = options.logX ? Math.log10 : v => v;
    const transformY = options.logY ? Math.log10 : v => v;
    const [xmin, xmax] = options.x.map(transformX), [ymin, ymax] = options.y.map(transformY);
    const x = v => margin.left + (transformX(v) - xmin) / (xmax - xmin) * innerWidth;
    const y = v => margin.top + (ymax - transformY(v)) / (ymax - ymin) * innerHeight;
    const svg = element('svg', {viewBox: '0 0 ' + width + ' ' + height, 'aria-hidden': 'true'});
    const clipId = 'plot-clip-' + (++chartNumber);
    const defs = element('defs'), clip = element('clipPath', {id: clipId});
    clip.append(element('rect', {x: margin.left, y: margin.top, width: innerWidth, height: innerHeight}));
    defs.append(clip); svg.append(defs);
    const plot = element('g', {'clip-path': 'url(#' + clipId + ')'});
    const label = (px, py, text, attrs = {}) => svg.append(element('text', {x: px, y: py, fill: palette.muted, 'font-size': 11, 'font-family': 'system-ui, sans-serif', ...attrs}, text));
    const line = (x1, y1, x2, y2, color = palette.rule) => svg.append(element('line', {x1, y1, x2, y2, stroke: color, 'stroke-width': 1}));
    const yticks = options.logY ? Array.from({length: Math.floor(ymax) - Math.ceil(ymin) + 1}, (_, i) => 10 ** (Math.ceil(ymin) + i)) : ticks(...options.y);
    yticks.forEach(v => {
      line(margin.left, y(v), width - margin.right, y(v));
      const text = options.logY && (v < .01 || v >= 1000) ? '10^' + Math.round(Math.log10(v)) : String(Number(v.toPrecision(3)));
      label(margin.left - 9, y(v) + 4, text, {'text-anchor': 'end'});
    });
    const xticks = options.logX ? [.1, .2, .5, 1, 2, 5].filter(v => v >= options.x[0] && v <= options.x[1]) : ticks(...options.x);
    xticks.forEach(v => {
      line(x(v), height - margin.bottom, x(v), height - margin.bottom + 5, palette.muted);
      label(x(v), height - margin.bottom + 21, v, {'text-anchor': 'middle'});
    });
    line(margin.left, margin.top, margin.left, height - margin.bottom, '#aeb2a8');
    line(margin.left, height - margin.bottom, width - margin.right, height - margin.bottom, '#aeb2a8');
    label(margin.left + innerWidth / 2, height - 9, options.xlabel, {'text-anchor': 'middle', 'font-size': 12});
    const midY = margin.top + innerHeight / 2;
    label(13, midY, options.ylabel, {transform: 'rotate(-90 13 ' + midY + ')', 'text-anchor': 'middle', 'font-size': 11});
    svg.append(plot);
    host.replaceChildren(svg);
    function path(xs, ys, color, dash = '', thickness = 1.8) {
      let d = '', active = false;
      xs.forEach((v, i) => {
        const py = y(ys[i]), px = x(v);
        if (!Number.isFinite(px) || !Number.isFinite(py) || (options.logY && ys[i] <= 0)) { active = false; return; }
        d += (active ? 'L' : 'M') + px.toFixed(3) + ',' + py.toFixed(3) + ' ';
        active = true;
      });
      plot.append(element('path', {d, fill: 'none', stroke: color, 'stroke-width': thickness, 'stroke-dasharray': dash, 'stroke-linejoin': 'round'}));
    }
    function band(xs, lower, upper, color) {
      let run = [];
      const flush = () => {
        if (run.length > 1) {
          const a = run.map(i => x(xs[i]) + ',' + y(upper[i])).join(' L');
          const b = [...run].reverse().map(i => x(xs[i]) + ',' + y(lower[i])).join(' L');
          plot.append(element('path', {d: 'M' + a + ' L' + b + ' Z', fill: color, 'fill-opacity': .14, stroke: 'none'}));
        }
        run = [];
      };
      xs.forEach((_, i) => {
        if (Number.isFinite(y(lower[i])) && Number.isFinite(y(upper[i]))) run.push(i); else flush();
      });
      flush();
    }
    function vertical(v, color, dash = '3 4') {
      plot.append(element('line', {x1: x(v), y1: margin.top, x2: x(v), y2: height - margin.bottom, stroke: color, 'stroke-width': 1, 'stroke-dasharray': dash}));
    }
    function horizontal(v, color, dash = '4 4') {
      plot.append(element('line', {x1: margin.left, y1: y(v), x2: width - margin.right, y2: y(v), stroke: color, 'stroke-width': 1, 'stroke-dasharray': dash}));
    }
    return {path, band, vertical, horizontal};
  }

  function projection(figure, data) {
    const scene = data.scene, canvas = byId('projection-canvas');
    const buttons = [...figure.querySelectorAll('[data-stage]')];
    const slider = byId('projection-angle'), output = byId('projection-angle-out'), play = byId('projection-play');
    const status = byId('projection-status'), camera = figure.querySelector('.projection-camera');
    let stage = 'sky', angle = 0, animation = 0, positions = [];
    const N = scene.x.length;
    function stop() { cancelAnimationFrame(animation); animation = 0; play.textContent = 'Animate projection'; }
    function render(updateStatus = true) {
      const width = canvas.clientWidth, height = canvas.clientHeight;
      if (!width || !height) return;
      const ctx = canvasContext(canvas, width, height);
      ctx.font = '12px system-ui, sans-serif';
      ctx.fillStyle = palette.muted;
      if (stage === 'pdf') {
        const left = 49, right = 18, top = 27, bottom = 46;
        const pw = width - left - right, ph = height - top - bottom;
        const rows = scene.maps[0].length, cols = scene.maps[0][0].length;
        let max = 0, retained = 0;
        for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
          const total = scene.maps[0][j][i] + scene.maps[1][j][i];
          max = Math.max(max, total); retained += total;
        }
        for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
          const a = scene.maps[0][j][i], b = scene.maps[1][j][i], total = a + b;
          if (total === 0) continue;
          const alpha = .88 * Math.sqrt(total / max);
          const rgb = [150 * a + 82 * b, 61 * a + 109 * b, 49 * a + 130 * b].map(v => Math.round(255 * (1 - alpha) + v / total * alpha));
          ctx.fillStyle = 'rgb(' + rgb.join(',') + ')';
          ctx.fillRect(left + i * pw / cols, top + (rows - j - 1) * ph / rows, pw / cols + .5, ph / rows + .5);
        }
        ctx.fillStyle = palette.muted; ctx.textAlign = 'center';
        [-6, -3, 0, 3, 6].forEach(v => ctx.fillText(v, left + (v + 6) / 12 * pw, height - bottom + 18));
        ctx.fillText('East [arcmin]', left + pw / 2, height - 8);
        ctx.textAlign = 'right';
        [.6, .7, .8, .9].forEach(v => ctx.fillText(v.toFixed(1), left - 9, top + (.94 - v) / .36 * ph + 4));
        ctx.save(); ctx.translate(13, top + ph / 2); ctx.rotate(-Math.PI / 2); ctx.textAlign = 'center'; ctx.fillText('Redshift', 0, 0); ctx.restore();
        ctx.strokeStyle = '#aeb2a8'; ctx.strokeRect(left, top, pw, ph);
        ctx.textAlign = 'left'; ctx.fillText('Full-PDF mass / bin (square-root scale)', left, 14);
        positions = [];
        if (updateStatus) status.textContent = N + ' galaxies; ' + (100 * retained / N).toFixed(1) + '% of their total PDF mass lies in the displayed 0.58–0.94 window. Off-screen probability is retained; no PDF is renormalized.';
        diagnostics.projection = {stage, angle, galaxies: N, retainedMass: retained, fullMass: N};
      } else {
        const radians = angle * Math.PI / 180, co = Math.cos(radians), si = Math.sin(radians);
        const scale = Math.min((width - 86) / (12 * Math.abs(co) + 16.2 * Math.abs(si)), (height - 86) / 12);
        const project = (x, y, z) => [width / 2 + scale * (co * x + si * (z - .76) * 45), height / 2 - scale * y];
        const stroke = (a, b, color, label) => {
          const p = project(...a), q = project(...b);
          ctx.beginPath(); ctx.moveTo(...p); ctx.lineTo(...q); ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke();
          if (label) { ctx.fillStyle = palette.muted; ctx.textAlign = 'center'; ctx.fillText(label, (p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 27); }
        };
        stroke([-6, -6, .58], [6, -6, .58], '#afb3a9', 'East [arcmin]');
        stroke([-6, -6, .58], [-6, 6, .58], '#afb3a9');
        if (angle > 8) {
          stroke([-6, -6, .58], [-6, -6, .94], '#9db0bb', 'Simulation z');
          stroke([-6, 6, .58], [-6, 6, .94], palette.rule);
          stroke([6, 6, .58], [6, 6, .94], palette.rule);
          stroke([6, -6, .58], [6, -6, .94], palette.rule);
          stroke([-6, 6, .94], [6, 6, .94], palette.rule);
        }
        ctx.fillStyle = palette.muted; ctx.textAlign = 'left';
        ctx.fillText('North [arcmin]', 8, 16);
        [-6, 0, 6].forEach(v => { const p = project(-6, v, .58); ctx.textAlign = 'right'; ctx.fillText(v, p[0] - 6, p[1] + 4); });
        if (angle > 8) [.58, .76, .94].forEach(v => { const p = project(-6, -6, v); ctx.textAlign = 'center'; ctx.fillText(v.toFixed(2), p[0], p[1] + 13); });
        else [-6, 0, 6].forEach(v => { const p = project(v, -6, .58); ctx.textAlign = 'center'; ctx.fillText(v, p[0], p[1] + 13); });
        positions = scene.x.map((x, i) => ({p: project(x, scene.y[i], scene.z[i]), i, depth: -si * x + co * (scene.z[i] - .76) * 45}));
        [...positions].sort((a, b) => a.depth - b.depth).forEach(({p, i}) => {
          ctx.fillStyle = scene.population[i] === 0 ? palette.primary : palette.external;
          ctx.globalAlpha = .73; ctx.beginPath();
          if (scene.population[i] === 0) ctx.arc(p[0], p[1], 2.5, 0, 2 * Math.PI);
          else { ctx.moveTo(p[0], p[1] - 3.4); ctx.lineTo(p[0] - 3, p[1] + 2.5); ctx.lineTo(p[0] + 3, p[1] + 2.5); ctx.closePath(); }
          ctx.fill();
        });
        ctx.globalAlpha = 1;
        if (updateStatus) status.textContent = angle === 0 ?
          N + ' galaxies projected onto two sky coordinates. Rotate the view to reveal simulation redshift space.' :
          N + ' galaxies at the same fixed positions and simulation redshifts. The redshift direction is scaled independently for visibility; the view does not depict physical aspect ratios.';
        diagnostics.projection = {stage, angle, galaxies: N};
      }
      output.value = Math.round(angle) + '°'; slider.value = angle;
    }
    function select(next) {
      stop(); stage = next; angle = next === 'sky' ? 0 : 70;
      pressed(buttons, 'stage', stage); camera.hidden = stage === 'pdf'; render();
    }
    buttons.forEach(button => button.addEventListener('click', () => select(button.dataset.stage)));
    slider.addEventListener('input', () => {
      stop(); angle = Number(slider.value); stage = angle === 0 ? 'sky' : 'depth';
      pressed(buttons, 'stage', stage); render();
    });
    canvas.addEventListener('keydown', event => {
      if (stage === 'pdf' || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      event.preventDefault(); stop(); angle = Math.min(70, Math.max(0, angle + (event.key === 'ArrowRight' ? 5 : -5)));
      stage = angle === 0 ? 'sky' : 'depth'; pressed(buttons, 'stage', stage); render();
    });
    canvas.addEventListener('mousemove', event => {
      const rect = canvas.getBoundingClientRect(), px = event.clientX - rect.left, py = event.clientY - rect.top;
      const nearest = positions.reduce((best, point) => {
        const d = Math.hypot(point.p[0] - px, point.p[1] - py);
        return d < best.distance ? {distance: d, point} : best;
      }, {distance: 9, point: null});
      const i = nearest.point ? nearest.point.i : null;
      canvas.title = i !== null ? (scene.population[i] ? 'Aligned' : 'Primary') + ' host · galaxy ' + scene.ids[i] + ' · simulation z = ' + scene.z[i].toFixed(4) : '';
    });
    play.addEventListener('click', () => {
      if (animation) { stop(); render(); return; }
      stage = 'depth'; angle = 0; pressed(buttons, 'stage', stage);
      if (reducedMotion.matches) { angle = 70; render(); return; }
      play.textContent = 'Pause animation';
      const start = performance.now();
      const frame = time => {
        const t = Math.min((time - start) / 1800, 1);
        angle = 70 * (t * t * (3 - 2 * t)); render(false);
        if (t < 1) animation = requestAnimationFrame(frame); else { stop(); render(); }
      };
      animation = requestAnimationFrame(frame);
    });
    new IntersectionObserver(entries => { if (!entries[0].isIntersecting && animation) { stop(); render(); } }).observe(figure);
    document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
    reducedMotion.addEventListener('change', () => { if (reducedMotion.matches && animation) { stop(); angle = 70; render(); } });
    observe(figure, () => render()); render();
  }

  function profiles(figure, data) {
    const host = byId('profile-plot'), selector = byId('profile-sample');
    const buttons = [...figure.querySelectorAll('[data-profile]')];
    const legend = document.createElement('p'); legend.className = 'viz-legend'; host.after(legend);
    let mode = 'projected';
    function render() {
      const sample = data.profiles[selector.value], x = sample.radius;
      if (mode === 'projected') {
        const positive = ['total', 'primary', 'external', 'random'].flatMap(key => sample[key].mean).concat(sample.external.lo, sample.external.hi).filter(v => v > 0);
        const plot = axisPlot(host, {x: [.1, 5], y: [10 ** Math.floor(Math.log10(Math.min(...positive))), 10 ** Math.ceil(Math.log10(Math.max(...positive)))],
          logX: true, logY: true, xlabel: 'Projected radius / virial radius', ylabel: 'Surface density [(Mpc/h)⁻²]'});
        plot.band(x, sample.external.lo, sample.external.hi, palette.external);
        plot.vertical(1, '#bfc3b9');
        [['total', palette.ink, ''], ['primary', palette.primary, '5 3'], ['external', palette.external, ''], ['random', palette.muted, '2 4']].forEach(([key, color, dash]) => plot.path(x, sample[key].mean, color, dash));
        legend.textContent = '';
        [['Total', palette.ink], ['– – Same host', palette.primary], ['Other hosts', palette.external], ['··· Matched random', palette.muted]].forEach(([label, color]) => {
          const span = document.createElement('span'); span.style.color = color; span.textContent = label; legend.append(span);
        });
        byId('profile-status').textContent = sample.n + ' halos; equal-halo means in a ±20 Mpc/h redshift-space cylinder. Band: other-host 16–84% spread across halos. Zero densities are omitted on this logarithmic axis.';
      } else {
        const c = sample.centres;
        const plot = axisPlot(host, {x: [.1, 5], y: [0, Math.max(...c.mean, ...c.hi) * 1.1], logX: true,
          xlabel: 'True separation / virial radius', ylabel: 'Centre density / reference'});
        plot.band(x, c.lo, c.hi, palette.external); plot.horizontal(1, palette.muted); plot.vertical(1, '#bfc3b9');
        plot.path(x, c.mean, palette.external);
        legend.textContent = 'Other selected centrals · dashed line: reference density';
        byId('profile-status').textContent = sample.n + ' conditioning halos; other selected centrals at true host distances. Inner zeros remain visible. Band: 16–84% spread across halos, not an error on the mean.';
      }
      diagnostics.profiles = {mode, sample: selector.value, halos: sample.n};
    }
    buttons.forEach(button => button.addEventListener('click', () => { mode = button.dataset.profile; pressed(buttons, 'profile', mode); render(); }));
    selector.addEventListener('change', render); observe(figure, render); render();
  }

  function random(seed) {
    let a = seed >>> 0;
    return () => { a += 0x6D2B79F5; let t = a; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  }
  function poisson(mu, rng) {
    const limit = Math.exp(-mu);
    let product = 1, k = 0;
    do { k++; product *= rng(); } while (product > limit);
    return k - 1;
  }
  function field(figure, data) {
    const specification = data.field, size = specification.size;
    const slider = byId('field-scatter'), output = byId('field-scatter-out');
    const buttons = [...figure.querySelectorAll('[data-field-view]')];
    let draw = 0, view = 'intensity';
    function renderMap(canvas, values, counts, seed) {
      const width = canvas.clientWidth || 300, ctx = canvasContext(canvas, width, width);
      const rng = random(seed);
      values.forEach((value, index) => {
        const i = index % size, j = Math.floor(index / size), cell = width / size;
        if (counts) {
          ctx.fillStyle = '#f5f6f2'; ctx.fillRect(i * cell, (size - j - 1) * cell, cell + .5, cell + .5);
          ctx.fillStyle = palette.ink;
          for (let k = 0; k < counts[index]; k++) {
            ctx.beginPath(); ctx.arc((i + rng()) * cell, (size - j - rng()) * cell, Math.max(.9, width / 250), 0, Math.PI * 2); ctx.fill();
          }
        } else {
          const stops = [[245, 246, 242], [200, 210, 211], [82, 109, 130], [40, 63, 77]];
          const t = Math.min(Math.max(value / 8, 0), 1) * 3, n = Math.min(Math.floor(t), 2), f = t - n;
          const rgb = stops[n].map((v, channel) => Math.round(v * (1 - f) + stops[n + 1][channel] * f));
          ctx.fillStyle = 'rgb(' + rgb.join(',') + ')'; ctx.fillRect(i * cell, (size - j - 1) * cell, cell + .5, cell + .5);
        }
      });
    }
    function render() {
      const scatter = Number(slider.value), coefficients = specification.coefficients[draw];
      const mean = [], multiplier = [], intensity = [], counts = [];
      const rng = random(specification.poisson_seed + draw);
      for (let j = 0; j < size; j++) for (let i = 0; i < size; i++) {
        const x = (i + .5) / size, y = (j + .5) / size;
        let g = 0;
        specification.modes.forEach(([kx, ky], m) => {
          const phase = 2 * Math.PI * (kx * x + ky * y);
          g += specification.weights[m] * (coefficients[m][0] * Math.cos(phase) + coefficients[m][1] * Math.sin(phase));
        });
        const h = specification.mean[j * size + i];
        const f = Math.exp(scatter * g - .5 * scatter ** 2);
        mean.push(h); multiplier.push(f); intensity.push(h * f);
        counts.push(draw === 0 && scatter === specification.scatter ? specification.initial_counts[j * size + i] : poisson(specification.base * h * f, rng));
      }
      renderMap(byId('field-mean'), mean);
      renderMap(byId('field-current'), intensity, view === 'counts' ? counts : null, specification.poisson_seed + draw + 100);
      const expected = specification.base * sum(intensity), sampled = sum(counts), variance = Math.expm1(scatter ** 2);
      output.value = scatter.toFixed(2);
      byId('field-expected').textContent = expected.toFixed(1); byId('field-count').textContent = sampled;
      byId('field-variance').textContent = variance.toFixed(3);
      byId('field-current-label').textContent = view === 'counts' ? 'Poisson galaxies in this environment' : 'This environment H × F';
      byId('field-status').textContent = 'Realization ' + (draw + 1) + ' of ' + specification.coefficients.length + ' · fixed ' + size + ' × ' + size + ' cell scale. Ensemble expected count: ' + (specification.base * sum(mean)).toFixed(1) + '. Each realization keeps its own total; increasing scatter leaves the ensemble mean unchanged.';
      diagnostics.field = {draw, scatter, view, expected, sampled, variance, ensembleExpected: specification.base * sum(mean), multiplier};
    }
    slider.addEventListener('input', render);
    byId('field-draw').addEventListener('click', () => { draw = (draw + 1) % specification.coefficients.length; render(); });
    buttons.forEach(button => button.addEventListener('click', () => { view = button.dataset.fieldView; pressed(buttons, 'fieldView', view); render(); }));
    observe(figure, render); render();
  }

  function interpolate(x, xs, ys) {
    if (x <= xs[0]) return ys[0];
    if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
    let low = 0, high = xs.length - 1;
    while (high - low > 1) { const middle = (low + high) >> 1; if (xs[middle] > x) high = middle; else low = middle; }
    const t = (x - xs[low]) / (xs[high] - xs[low]);
    return ys[low] * (1 - t) + ys[high] * t;
  }
  function integrate(xs, ys) {
    let total = 0;
    for (let i = 1; i < xs.length; i++) total += (xs[i] - xs[i - 1]) * (ys[i] + ys[i - 1]) / 2;
    return total;
  }
  function response(figure, data) {
    const selector = byId('response-object'), sliderZ = byId('response-z'), sliderA = byId('response-amplitude'), windowSelector = byId('response-window');
    data.examples.forEach((example, index) => {
      const option = document.createElement('option'); option.value = index; option.textContent = example.label; selector.append(option);
    });
    selector.value = '0';
    function render() {
      const z = data.reference.z, ref = data.reference.pdf, example = data.examples[Number(selector.value)];
      const pdf = example.pdf, haloZ = Number(sliderZ.value), amplitude = Number(sliderA.value);
      const weighted = z.map((v, i) => pdf[i] * (1 + amplitude * Math.exp(-.5 * ((v - data.meta.scene.aligned_z) / .018) ** 2)));
      const primary = .15 * interpolate(haloZ, z, pdf) / interpolate(haloZ, z, ref);
      const external = integrate(z, weighted), allocation = primary / (primary + external);
      const limits = windowSelector.value === 'full' ? [0, 3.2] : [.3, 1.4];
      const visible = z.map((v, i) => v >= limits[0] && v <= limits[1] ? Math.max(pdf[i], weighted[i], ref[i]) : 0);
      const plot = axisPlot(byId('response-plot'), {x: limits, y: [0, Math.max(...visible) * 1.12],
        xlabel: 'Redshift', ylabel: 'Density per unit redshift'});
      plot.vertical(haloZ, palette.primary, '');
      plot.path(z, ref, palette.muted, '2 4', 1.2);
      plot.path(z, weighted, palette.external, '6 4'); plot.path(z, pdf, palette.primary);
      byId('response-z-out').value = haloZ.toFixed(3); byId('response-amplitude-out').value = amplitude.toFixed(1);
      byId('response-primary').textContent = primary.toFixed(3); byId('response-external').textContent = external.toFixed(3);
      byId('response-allocation').textContent = (allocation * 100).toFixed(1) + '%';
      byId('response-status').textContent = 'Galaxy ' + example.id + ' · H = ' + example.h_ab.toFixed(2) + ' · simulation label: ' + example.population + '. The PDF and empirical reference stay fixed. P samples the chosen redshift; E integrates the full 0–3.2 support.';
      diagnostics.response = {example: Number(selector.value), haloZ, amplitude, primary, external, allocation,
        pdfIntegral: integrate(z, pdf), referenceIntegral: integrate(z, ref), window: windowSelector.value};
    }
    [selector, windowSelector].forEach(control => control.addEventListener('change', render));
    [sliderZ, sliderA].forEach(control => control.addEventListener('input', render));
    observe(figure, render); render();
  }

  const initialize = {projection, profiles, field, response};
  document.querySelectorAll('[data-figure]').forEach(figure => {
    const panel = figure.querySelector('.interactive-panel'), fallback = figure.querySelector('.static-fallback');
    const button = document.createElement('button');
    panel.id = figure.id + '-interactive'; button.type = 'button'; button.className = 'figure-explore';
    button.textContent = 'Explore this figure'; button.setAttribute('aria-controls', panel.id); button.setAttribute('aria-expanded', 'false');
    figure.querySelector('h3').after(button);
    let ready = false;
    button.addEventListener('click', async () => {
      if (ready) {
        const show = panel.hidden; panel.hidden = !show; fallback.hidden = show;
        button.textContent = show ? 'Show static figure' : 'Explore this figure'; button.setAttribute('aria-expanded', String(show));
        return;
      }
      button.disabled = true; button.textContent = 'Loading figure…';
      try {
        const data = await readData();
        panel.hidden = false; initialize[figure.dataset.figure](figure, data);
        fallback.hidden = true; ready = true; figure.dataset.ready = 'true';
        figure.querySelector('.figure-error')?.remove();
        button.textContent = 'Show static figure'; button.setAttribute('aria-expanded', 'true');
      } catch (error) {
        panel.hidden = true; fallback.hidden = false; button.textContent = 'Retry interactive figure';
        let message = figure.querySelector('.figure-error');
        if (!message) { message = document.createElement('p'); message.className = 'viz-status figure-error'; message.setAttribute('role', 'status'); button.after(message); }
        message.textContent = 'The interactive data could not load. The complete static figure is available below.';
      } finally { button.disabled = false; }
    });
  });
})();
