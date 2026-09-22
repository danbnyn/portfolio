/* Opt in per article with data-math and <script defer src="../js/math.js">. */
(() => {
  'use strict';
  const article = document.querySelector('[data-math]');
  if (!article || window.MathJax) return;
  const notice = article.querySelector('[data-math-status]');
  const failed = () => {
    document.documentElement.dataset.math = 'unavailable';
    if (notice) {
      notice.textContent = 'Maths could not be typeset. The original LaTeX is still shown; reloading the page may help.';
      notice.hidden = false;
    }
  };
  const timeout = window.setTimeout(failed, 20000);
  window.MathJax = {
    loader: { failed },
    tex: {
      inlineMath: [['\\(', '\\)']],
      displayMath: [['\\[', '\\]'], ['$$', '$$']],
      processEscapes: true,
      tags: 'ams'
    },
    svg: { fontCache: 'global', displayOverflow: 'scroll', displayAlign: 'left' },
    startup: {
      elements: [article],
      pageReady() {
        return MathJax.startup.defaultPageReady().then(() => {
          window.clearTimeout(timeout);
          document.documentElement.dataset.math = 'ready';
          if (notice) notice.hidden = true;
        }).catch(() => {
          window.clearTimeout(timeout);
          failed();
        });
      }
    }
  };
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/mathjax@4.1.2/tex-svg.js';
  script.async = true;
  script.onerror = () => { window.clearTimeout(timeout); failed(); };
  document.head.appendChild(script);
})();
