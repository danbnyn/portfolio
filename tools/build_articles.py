#!/usr/bin/env python3
"""Render the two committed Markdown articles to plain, deployable HTML.

Optional authoring utility; the deployed site needs no Python or build step.
Requires markdown-it-py and, for static mathematics, the optional npm dependency. Raw HTML is allowed because the sources are trusted,
author-maintained files, not user input. LaTeX is preserved for MathJax.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
import re
import argparse
import subprocess
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://danbnyn.github.io/portfolio/'
MD = MarkdownIt('commonmark', {'html': True}).enable('table')


def image(name: str, alt: str, *, height: int = 440, eager: bool = False) -> str:
    return (f'<a class="figure-image" href="../assets/cluster/{name}.svg" aria-label="Open {name.replace(chr(45), chr(32))} at full size">'
            f'<img src="../assets/cluster/{name}.svg" alt="{escape(alt, quote=True)}" '
            f'width="740" height="{height}" loading="{"eager" if eager else "lazy"}" decoding="async"></a>')


def figures() -> dict[str, str]:
    scene = f'''<figure id="fig-scene" class="scene-figure" data-scene>
  <p class="figure-kind">Figure 1 · Supplied simulation</p>
  <div class="figure-controls" role="group" aria-label="Choose a view of the same mock galaxies" hidden>
    <button type="button" aria-pressed="true" aria-controls="scene-sky" data-view="scene-sky">On the sky</button>
    <button type="button" aria-pressed="false" aria-controls="scene-hosts" data-view="scene-hosts">Reveal host labels</button>
    <button type="button" aria-pressed="false" aria-controls="scene-redshift" data-view="scene-redshift">Redshift space</button>
  </div>
  <div id="scene-sky" class="scene-panel" data-scene-panel>
    <p class="panel-label">A · Angular positions only</p>
    {image('scene-sky', 'The fixed sky patch contains 2,737 mock galaxies, with a central concentration and other overlapping concentrations. Host identities are not distinguished in this view.', height=620, eager=True)}
  </div>
  <div id="scene-hosts" class="scene-panel" data-scene-panel>
    <p class="panel-label">B · The same points, with simulation host labels</p>
    {image('scene-hosts', 'The same sky positions, now distinguishing 160 primary-host galaxies with circles, 35 nearby-host galaxies with triangles, and 33 foreground-host galaxies with squares. All other hosts remain small dots. The populations overlap in projection.', height=620)}
  </div>
  <div id="scene-redshift" class="scene-panel" data-scene-panel>
    <p class="panel-label">C · The same points, with simulated redshifts</p>
    {image('scene-redshift', 'Angular x-offset versus simulated galaxy redshift for all 2,737 rows. The primary and nearby host are near redshift 0.73; the highlighted foreground host is near 0.43. Their shared sky region does not imply shared distance.', height=620)}
  </div>
  <figcaption><strong>Projection does not establish association.</strong> All three views use exactly the same rows, with no redshift cut or subsampling. Host labels reveal simulation information, not inferred memberships. The redshift coordinate is <code>observed_redshift_gal</code>, not a photometric-redshift estimate or a true-distance coordinate. The fixed selection is a 12 × 12 arcmin square with H-band magnitude below 22.5. <a href="#data">Full provenance and selection</a>.</figcaption>
</figure>'''
    mean = f'''<figure id="fig-mean">
  <p class="figure-kind">Figure 2 · Schematic mean, not a calibration</p>
  {image('conditional-mean', 'Mean external density relative to the reference: a flat reference at one, a correlated mean elevated near the origin, and an excluded mean that is zero in the core, rises through a smooth transition, and tends toward the correlated mean.', height=440)}
  <figcaption><strong>Conditioning changes the expectation; exclusion changes its core.</strong> For this illustration only, let \\(q=r/R_*\\) and use the correlated factor \\(1+2/(1+q^2)\\). The exclusion is \\(E=t^2(3-2t)\\), where \\(t=\\operatorname{{clip}}((q-1)/0.6,0,1)\\). The final curve multiplies the entire correlated factor by \\(E\\). These are explanatory curves, not the model’s calibrated matter correlation or exclusion function.</figcaption>
</figure>'''
    counts = f'''<figure id="fig-counts">
  <p class="figure-kind">Figure 3 · Calculated toy probability laws</p>
  {image('poisson-cox', 'Two count distributions with the same expected count of 20. The Poisson distribution has variance 20. A Poisson mixture with a random external intensity has a much broader distribution with variance 76.25.')}
  <figcaption><strong>The same mean need not imply the same uncertainty.</strong> In one illustrative cell, fix the primary expectation at 5 and the external expectation at 15. The second model uses \\(N\\mid F\\sim\\operatorname{{Poisson}}(5+15F)\\), with \\(\\mathbb E F=1\\) and \\(\\operatorname{{Var}}F=0.25\\). Its variance is \\(20+15^2(0.25)=76.25\\). The mixture probabilities are evaluated by Gaussian quadrature; the displayed range is not renormalized. No fitted counts or recovery results are shown.</figcaption>
</figure>'''
    prior = f'''<figure id="fig-prior">
  <p class="figure-kind">Figure 4 · Explicit finite-cell prior illustrations</p>
  {image('prior-short', 'Three stepwise positive multiplier draws on 64 cells with correlation length 0.35. Local peaks and troughs vary over relatively short distances.', height=365)}
  {image('prior-long', 'Three multiplier draws using the same white drivers but correlation length 1.4. The departures are broader and more coherent, with the same pointwise Gaussian variance.', height=365)}
  <details class="disclosure"><summary>See the Gaussian mode variances</summary>
    {image('prior-modes', 'Sorted covariance eigenvalues for the two illustrative correlation lengths. The longer length concentrates variance in fewer leading modes. Both include the same small numerical diagonal term.', height=400)}
  </details>
  <figcaption><strong>The covariance decides which alternatives are plausible.</strong> These teaching priors use 64 cells of width 0.125 in arbitrary units, with \\(C_{{jk}}=0.49\\exp[-(x_j-x_k)^2/(2\\ell^2)]+10^{{-10}}\\delta_{{jk}}\\), for \\(\\ell=0.35\\) and \\(1.4\\). The same three white drivers are used for both lengths. Each plotted field is \\(F_j=\\exp(G_j-C_{{jj}}/2)\\): its <em>ensemble</em> mean is one, not necessarily its average across this patch. These covariances are not the project’s power-spectrum calibration. <a href="../assets/cluster/illustration-models.json">Parameters and seed</a>.</figcaption>
</figure>'''
    likelihood = f'''<figure id="fig-likelihood">
  <p class="figure-kind">Figure 5 · Synthetic measurement illustration</p>
  {image('redshift-likelihoods', 'Three illustrative relative redshift likelihoods: a narrow peak near the candidate, a broad foreground peak with a tail toward the candidate, and a two-peaked ambiguous curve. A vertical line marks the candidate redshift 0.7255.')}
  <figcaption><strong>One curve belongs to one observation.</strong> These deliberately constructed likelihoods illustrate distance ambiguity; they are not measurements from the supplied mock and are not attached to its individual rows. Each curve is scaled to a peak of one, solely for comparison. The primary samples a likelihood near its latent redshift; the external response integrates competing intensity along the line of sight. A curve’s area in this plot is not a number of galaxies.</figcaption>
</figure>'''
    return {'scene': scene, 'mean': mean, 'counts': counts, 'prior': prior, 'likelihood': likelihood}


FIGURES = figures()
CONFIG = {
    'measuring-a-galaxy-cluster': {
        'title': 'Measuring a galaxy cluster in a crowded Universe',
        'description': 'From a detected overdensity to joint inference of one halo and the galaxies around it.',
        'eyebrow': 'Research note · Astrophysics & statistical inference',
        'prefix': '',
        'footer': '<a href="cluster-derivations.html">Continue to the derivations →</a>',
    },
    'cluster-derivations': {
        'title': 'Cluster refinement: the derivations',
        'description': 'Point processes, halo conditioning, positive fields, selection, and joint inference—under explicit assumptions.',
        'eyebrow': 'Technical companion · Cluster refinement',
        'prefix': 'A',
        'footer': '<a href="measuring-a-galaxy-cluster.html">← Return to the narrative</a>',
    }
}


def render_source(source: str, prefix: str) -> tuple[str, int]:
    source = re.sub(r'^# .+\n', '', source, count=1)
    definitions = dict(re.findall(r'^\[\^([\w-]+)\]: (.+)$', source, re.M))
    source = re.sub(r'^\[\^[\w-]+\]: .+\n?', '', source, flags=re.M)
    for name, figure in FIGURES.items():
        source = source.replace(f'<!-- FIGURE:{name} -->', '\n'+figure+'\n')
    if '<!-- FIGURE:' in source:
        raise ValueError('Unresolved figure marker')

    # Protect LaTeX before Markdown sees backslashes, underscores, or ampersands.
    protected: dict[str, str] = {}
    equation_count = 0
    def protect(match):
        nonlocal equation_count
        token = f'MATHPLACEHOLDER{len(protected):04d}END'
        if match.group(1) is not None:
            equation_count += 1
            number = f'{prefix}{equation_count}'
            tex = '\\begin{equation}\n'+match.group(1).strip()+f'\n\\tag{{{number}}}\n\\end{{equation}}'
            # The HTML id makes a useful anchor before MathJax runs as well.
            protected[token] = (f'<div class="equation" id="equation-{number}" tabindex="0" '
                f'role="group" aria-label="Equation {number}">{escape(tex)}</div>')
            return f'\n\n{token}\n\n'
        protected[token] = escape('\\('+match.group(2)+'\\)')
        return token
    source = re.sub(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', protect, source, flags=re.S)

    refs: list[str] = []
    occurrences: dict[str, int] = {}
    def reference(match):
        key = match.group(1)
        if key not in definitions:
            raise ValueError(f'Undefined reference: {key}')
        if key not in refs:
            refs.append(key)
        occurrences[key] = occurrences.get(key, 0)+1
        index = refs.index(key)+1
        return (f'<sup class="citation"><a id="cite-{key}-{occurrences[key]}" href="#ref-{key}" '
                f'role="doc-noteref" aria-label="Reference {index}">{index}</a></sup>')
    source = re.sub(r'\[\^([\w-]+)\]', reference, source)

    headings = []
    def heading(match):
        marks, label, ident = match.groups()
        if not ident:
            ident = re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')
        if len(marks) == 2:
            headings.append((ident, label))
        return f'<h{len(marks)} id="{ident}">{MD.renderInline(label)}</h{len(marks)}>'
    source = re.sub(r'^(#{2,3}) (.+?)(?: \{#([\w-]+)\})?$', heading, source, flags=re.M)
    body = MD.render(source)
    contents = ('<details class="contents"><summary>In this note</summary>'
                '<nav aria-label="Article contents">'+''.join(
                    f'<a href="#{ident}">{escape(label)}</a>' for ident,label in headings
                )+'<a href="#references">References</a></nav></details>')
    first_h2 = body.index('<h2 ')
    body = body[:first_h2]+contents+'\n'+body[first_h2:]
    for token, value in protected.items():
        if value.startswith('<div'):
            body = body.replace('<p>'+token+'</p>', value)
        body = body.replace(token, value)
    # Wide tables scroll inside their own container, never the whole page.
    body = body.replace('<table>', '<div class="table-scroll" tabindex="0" role="region" aria-label="Comparison table"><table>')
    body = body.replace('</table>', '</table></div>')
    if refs:
        body += '<section class="references" role="doc-bibliography" aria-labelledby="references"><h2 id="references">References</h2><ol>\n'
        for key in refs:
            backlinks = ' '.join(f'<a class="reference-back" href="#cite-{key}-{i}" aria-label="Return to citation {i} of reference {refs.index(key)+1}">↩{i if occurrences[key]>1 else ""}</a>'
                for i in range(1, occurrences[key]+1))
            body += f'<li id="ref-{key}">{MD.renderInline(definitions[key])} {backlinks}</li>\n'
        body += '</ol></section>\n'
    if 'MATHPLACEHOLDER' in body:
        raise ValueError('Unresolved math marker')
    return body, equation_count


def build(slug: str, config: dict) -> None:
    source = (ROOT/'content'/f'{slug}.md').read_text(encoding='utf-8')
    body, count = render_source(source, config['prefix'])
    canonical = BASE+'writing/'+slug+'.html'
    title = escape(config['title'])
    description = escape(config['description'], quote=True)
    scene_script = '<script defer src="../js/scene.js"></script>' if slug == 'measuring-a-galaxy-cluster' else ''
    context = ('<p class="article-context">A note on my <a href="../work.html#cluster-refinement">cluster-refinement work at the Institut d’Astrophysique de Paris</a>.</p>'
               if slug == 'measuring-a-galaxy-cluster' else '')
    output = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <meta name="theme-color" content="#ffffff">
  <title>{title} — Dan Benayoun</title>
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="Dan Benayoun">
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../css/styles.css">
  <script defer src="../js/math.js"></script>
  {scene_script}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="site-shell">
    <header class="site-header">
      <a class="brand" href="../index.html">Dan Benayoun<span aria-hidden="true">.</span></a>
      <nav class="nav" aria-label="Primary navigation">
        <a href="../index.html">Home</a>
        <a href="../work.html">Work</a>
        <a href="../writing.html" aria-current="page">Writing</a>
        <a href="../about.html">About</a>
      </nav>
    </header>
    <main id="main" tabindex="-1">
      <article class="article" data-math aria-labelledby="article-title">
        <header class="article-header">
          <p class="eyebrow">{escape(config['eyebrow'])}</p>
          <h1 id="article-title">{title}</h1>
          <p class="lede">{description}</p>
          {context}
          <p class="entry-meta">Dan Benayoun · <time datetime="2026-09-22">22 September 2026</time></p>
        </header>
        <p class="math-status" data-math-status role="status" hidden></p>
        <noscript><p class="math-status">JavaScript is needed to typeset equations. Their LaTeX source remains visible. Every figure and the full text remain available.</p></noscript>
        <p class="equation-help">Wide equations scroll sideways. Select a plot to open it at full size.</p>
        <div class="prose">
{body}
        </div>
        <footer class="article-footer">
          {config['footer']}
          <p><a href="../writing.html">All writing</a> · <a href="../content/{slug}.md">Markdown source</a></p>
        </footer>
      </article>
    </main>
    <footer class="site-footer">
      <span>© 2026 Dan Benayoun</span>
      <a href="https://github.com/danbnyn">GitHub <span aria-hidden="true">↗</span></a>
    </footer>
  </div>
</body>
</html>
'''
    path = ROOT/'writing'/f'{slug}.html'
    path.parent.mkdir(exist_ok=True)
    path.write_text(output, encoding='utf-8')
    print(f'Built {path.relative_to(ROOT)}: {count} numbered equations')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-math', action='store_true',
        help='Keep browser MathJax instead of embedding mathematics at build time.')
    args = parser.parse_args()
    for slug, config in CONFIG.items():
        build(slug, config)
    if not args.client_math:
        subprocess.run(['node', str(ROOT/'tools/typeset_math.cjs'),
            *[str(ROOT/'writing'/f'{slug}.html') for slug in CONFIG]], check=True)

