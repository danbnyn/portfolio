#!/usr/bin/env python3
"""Render the integrated Markdown article to plain, deployable HTML.

Optional authoring utility; the deployed site needs no Python or build step.
Requires markdown-it-py and, for static mathematics, the optional npm dependency. Raw HTML is allowed because the sources are trusted,
author-maintained files, not user input. LaTeX is preserved for MathJax.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
import re
import subprocess
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://danbnyn.github.io/portfolio/'
MD = MarkdownIt('commonmark', {'html': True}).enable('table')


def figures() -> dict[str, str]:
    return {name: (ROOT/'templates'/'figures'/f'{name}.html').read_text(encoding='utf-8')
            for name in ('scene', 'profiles', 'response')}

FIGURES = figures()
CONFIG = {
    'measuring-a-galaxy-cluster': {
        'title': 'Measuring a galaxy cluster in a crowded Universe',
        'description': 'From photometric overdensity to joint inference: a primary halo, a conditional environment, and the uncertainty between them.',
        'eyebrow': 'Astrophysics · A probabilistic cluster-refinement model',
        'prefix': '',
        'footer': '<p>Model, derivations and diagnostics form one article. See the data section for reproducibility and the validation section for claims not yet established.</p>',
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
    contents = ('<details class="contents"><summary>In this article</summary>'
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
    scene_script = '<script defer src="../js/cluster-loader.js"></script>'
    context = ('<p class="article-context">An article on my <a href="../work.html#cluster-refinement">cluster-refinement work at the Institut d’Astrophysique de Paris</a>.</p>'
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
  <link rel="stylesheet" href="../css/cluster-viz.css">
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
          <p class="entry-meta">Dan Benayoun · <time datetime="2026-09-23">23 September 2026</time></p>
        </header>
        <p class="equation-help">Three linked figure groups · Full-PDZ illustrations · Reproducible mock diagnostics</p>
        <noscript><p>Interactive controls require JavaScript. Equations, static figures, data links and the complete article remain available without it.</p></noscript>
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
    for slug, config in CONFIG.items():
        build(slug, config)
    subprocess.run(['node', str(ROOT/'tools/typeset_math.cjs'),
        *[str(ROOT/'writing'/f'{slug}.html') for slug in CONFIG]], check=True)
