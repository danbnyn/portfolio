/* Load the interactive figures only when a reader asks for them. */
(() => {
  'use strict';
  const base = new URL('.', document.currentScript.src);
  const figures = [...document.querySelectorAll('.scientific-figure')];
  if (!figures.length) return;

  const scripts = [
    'vendor/plotly.min.js',
    '../assets/cluster/interactive-data.js',
    'cluster-canvas3d.js',
    'cluster-viz.js',
  ];
  const load = path => new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = new URL(path, base).href;
    script.onload = resolve;
    script.onerror = () => reject(new Error(`Could not load ${path}`));
    document.head.append(script);
  });
  let pending;
  const buttons = figures.map(figure => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'figure-load';
    button.textContent = 'Explore interactive figures';
    figure.querySelector('h3').after(button);
    button.addEventListener('click', async () => {
      if (!pending) {
        buttons.forEach(item => {
          item.disabled = true;
          item.textContent = 'Loading interactive figures…';
        });
        pending = scripts.reduce((step, path) => step.then(() => load(path)), Promise.resolve())
          .then(() => {
            if (!window.CLUSTER_VIZ) throw new Error('Interactive figures could not start');
            buttons.forEach(item => item.remove());
          })
          .catch(() => {
            buttons.forEach(item => {
              item.disabled = false;
              item.textContent = 'Retry interactive figures';
            });
            pending = null;
          });
      }
      await pending;
    });
    return button;
  });
})();
