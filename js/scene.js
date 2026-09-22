/* Optional enhancement: all three views are present without JavaScript. */
(() => {
  'use strict';
  const figure = document.querySelector('[data-scene]');
  if (!figure) return;
  const controls = figure.querySelector('.figure-controls');
  const buttons = [...figure.querySelectorAll('[data-view]')];
  const panels = [...figure.querySelectorAll('[data-scene-panel]')];
  if (!controls || !buttons.length || buttons.length !== panels.length) return;
  const show = (id) => {
    if (!panels.some(panel => panel.id === id)) return;
    panels.forEach(panel => { panel.hidden = panel.id !== id; });
    buttons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.view === id));
    });
  };
  buttons.forEach(button => button.addEventListener('click', () => show(button.dataset.view)));
  show(buttons[0].dataset.view);
  controls.hidden = false;
})();
