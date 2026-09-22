# Dan Benayoun — scientific notes

A small, writing-first static website. The published pages are already built:
**no framework, server application, CMS, or build step is needed to publish them.**
The visual language of the original site is retained: system fonts, serif headings,
a single restrained accent, and a narrow reading column.

## Read / preview

Open `index.html` in a browser, or serve this directory locally:

```sh
python -m http.server 8000
```

Then open `http://localhost:8000`. The article is under
`writing/measuring-a-galaxy-cluster.html`; its technical companion is
`writing/cluster-derivations.html`.

The published articles contain pre-rendered SVG equations with assistive MathML.
There is **no browser MathJax download**, no web-font request, and no network call
for the figures. The only article JavaScript is the small optional scene-view
switcher. Without JavaScript, all three scene views appear in sequence, the
contents disclosure still works, and all equations remain typeset.

The underlying image assets remain SVG; PNG files are convenient previews, not
additional downloads made by the pages. The site does not send analytics.

## What belongs where

- `index.html`: a short introduction and the latest article, not a second CV.
- `about.html`: background and education, including the incoming Oxford programme.
- `work.html`: selected IAP and RODEO work; no exhaustive project inventory.
- `writing.html`: the article index, with the companion attached to its main note.
- `content/`: editable Markdown sources, including LaTeX and references.
- `assets/cluster/`: the fixed illustration subset, provenance, and generated figures.
- `tools/`: optional authoring and checking utilities.
- `notes/editorial-review.md`: editorial decisions and scientific follow-through.
- `notes/check-results.md`: the checks performed and their boundaries.

## Edit an article

The ready-to-publish HTML is committed so that editing does not need a new site
framework. The optional authoring path keeps prose in Markdown and generates
numbered mathematics, footnotes, contents links, figure modules and page metadata.

One-time authoring setup (Python 3.11+ and Node.js are needed only for rebuilding):

```sh
python -m pip install -r requirements-articles.txt
npm install --ignore-scripts
```

Then edit `content/*.md` and run:

```sh
python tools/build_articles.py
python tools/check.py
```

`tools/build_articles.py` renders the two Markdown sources and invokes the small
build-time MathJax script. `package.json` pins the authoring dependency; it does
not introduce browser dependencies or a JavaScript application. No font files are
bundled with the site. SVG glyph paths and assistive MathML are embedded in HTML.
Figure captions and HTML modules are in `tools/build_articles.py`. Headings may
use `{#stable-anchor}`. References use `[^key]` and single-line definitions.

For a deliberately client-typeset alternative, `--client-math` skips static
mathematics and retains the original MathJax 4.1.2 CDN loader. That alternative
requires JavaScript and network access; it is **not** how the supplied articles
are built. `templates/article.html` retains the original noindex client-math
template as a small manual authoring example.

## Reproduce the figures

The raw 530,570-row catalogue is intentionally not in this repository. Displaying
the page never loads the CSV. The committed 2,737-row subset is sufficient to
reproduce the figures:

```sh
python -m pip install -r requirements-figures.txt
python tools/make_figures.py
python tools/check_math.py
```

To reproduce the subset from the original attachment instead:

```sh
python tools/make_figures.py --catalogue /path/to/27277.csv.bz2
```

The selected host, magnitude and footprint cuts, row identities and raw-file
checksum are recorded in `assets/cluster/provenance.json`. The original export’s
private contact information is not reproduced. The exact required CosmoHub
acknowledgement is in the article and the asset README.

The sky and redshift views use the supplied simulation. All remaining figures
are explicitly specified teaching calculations. **None is a fitted posterior,
recovery result, or test of the actual refinement pipeline.** The export has no
per-galaxy photo-z likelihood arrays; the likelihood illustration is synthetic.

## Checks

```sh
python tools/check.py              # standard library only: pages, paths, anchors, metadata
python tools/check_math.py         # mathematical identities and fixed-subset checks
python -m pip install playwright==1.57.0
python -m playwright install chromium
python tools/browser_check.py      # optional local Chromium rendering checks
```

The browser checker uses inline previews of the actual local pages and assets.
It checks 320, 390, 768 and 1280 px layouts, equation starts, scene controls,
keyboard access, and no-JavaScript reading. It does not claim to test a live
website, HTTP responses, or a CDN. Screenshots and JSON reports go to the ignored
`artifacts/` directory. For a shorter run, use `--widths 320 390` or `--widths 768 1280`.
The checks are evidence about the article and website—not scientific validation
of the inference method.

## Publish

Copy this directory’s contents into the existing site repository. The pages keep
the original canonical base `https://danbnyn.github.io/portfolio/` and relative
asset links. GitHub Pages can serve the files directly; `.nojekyll` is included.
Choose the relevant branch/root in the existing repository’s Pages settings if
it is not already configured. No deployment or repository write has been done as
part of this revision.

For a different repository name or custom domain, update the canonical and Open
Graph URLs in root pages and `tools/build_articles.py`, the `BASE` in
`tools/check.py`, `sitemap.xml`, and the `/portfolio/` fallback paths in `404.html`.
Then rebuild and re-run the local-link checker.
