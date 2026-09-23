# Dan Benayoun — portfolio and scientific notes

The published site is at https://danbnyn.github.io/portfolio/. Its main article,
**Measuring a galaxy cluster in a crowded Universe**, contains the derivations,
literature context and three interactive figure groups. The former technical
companion URL redirects to the integrated article.

## Read and publish

Open `writing/measuring-a-galaxy-cluster.html`, or serve the directory:

```sh
python -m http.server 8000
```

The site is already built. GitHub Pages serves the repository's `master` branch
from its root. Publishing requires no Python, Node, server-side application or
build service. Equations are pre-rendered SVG with assistive
MathML. Figures use a bundled Plotly distribution and a small CPU-projected 3D
canvas renderer; **WebGL is not required**. There are no runtime requests for
fonts, data, plotting libraries or equation rendering, and no analytics.

Without JavaScript, the entire article, equations, static SVG views and data
links remain available. Static views also appear when printing. Keyboard users
can use the figure selectors, native sliders and 3D arrow-key controls; every
figure includes a text description and equivalent static views.

## What is evidence, and what is illustration?

The retained mock diagnostics are measurements from `flagship_hp4x2.csv.gz`:
4,997,763 selected rows; 339 interior massive conditioning halos; a 162-halo
narrower default stack; and a fixed 7,341-galaxy scene. Per-halo counts preserve
an exact total = primary + complementary identity for the same selection.

The PDZs are **synthetic full distributions**, generated from a documented
magnitude-dependent, three-component likelihood in `s = log(1+z)`, using real
mock sky positions and simulation redshift-space coordinates. They are not
supplied Euclid PDZs or a calibration of Euclid performance. Probability-density
maps integrate the full distributions analytically. The 3D probability cloud is
a finite quadrature display, not a collection of independently observed galaxies.

The response explorer evaluates one chosen illustrative state. No refinement
engine, posterior samples, inference results or performance validation are
included or claimed. The article specifies the tests needed to establish those
claims; the numerical checks below test identities and data integrity only.

## Rebuild the retained figures and article

Versions used are pinned in `requirements-articles.txt`,
`requirements-figures.txt` and `package.json`. The numerical tools use Python
3.11 or newer (`hashlib.file_digest` is used by the optional raw-data analysis).

```sh
python -m pip install -r requirements-articles.txt -r requirements-figures.txt
npm install --ignore-scripts
python tools/make_figures.py
python tools/build_articles.py
python tools/check_math.py
python tools/check.py
python tools/export_standalone.py artifacts/cluster-refinement.html
```

`make_figures.py` needs only the compact retained CSVs, not the full input mock.
`build_articles.py` renders the Markdown and the three figure templates, then
runs MathJax **at build time**. `export_standalone.py` optionally embeds all
scripts, styles, figures and linked data files into a single HTML file. It also
removes portfolio navigation that would otherwise become a broken local link.

Optional browser regression checks use Playwright and an installed Chromium:

```sh
python -m pip install playwright
python tools/browser_check.py --chromium /path/to/chromium
```

The browser check loads the self-contained document with networking blocked,
exercises desktop/mobile controls and 3D rotation, and tests a JavaScript-disabled
reading view. It is a functional/accessibility smoke test, not a certification
against every browser or assistive technology.

## Reproduce the diagnostics from the supplied compressed catalogue

The large original catalogue is not duplicated in this package. Supply its path:

```sh
python tools/analyse_flagship.py /path/to/flagship_hp4x2.csv.gz --cache /path/to/local-cache
python tools/make_figures.py
```

The analysis uses a few GB of memory and scratch space. A persistent cache is
optional; it is matched against the raw input SHA256 before reuse. Cache files
are trusted local pickles, not portable source data and not included here.

The analysis is intentionally specific to the supplied two-pixel north-polar
footprint. It checks its order-4 HEALPix mapping against a sample of the actual
order-29 nested IDs. It does not implement a general survey mask or completeness
model. The conservative aperture test samples 2,048 positions around a circle
at 5.05 virial radii. This is a dense numerical boundary check, not an exact
geometric mask proof. Twelve random angular apertures per halo are drawn
uniformly in solid angle and subjected to the same test. Overlaps remain possible.

The recorded source SHA256 is:

```
424f2ca1a5a9e8a46fc5291536899dda1467780c152722371357accb918414e7
```

### Adopted units and geometries

The CSV export contains no unit header or export query. The following conventions
are therefore **adopted and cross-checked, not independently authenticated**:

- H-band flux is cgs f_nu, with `H_AB = -2.5 log10(f_nu) - 48.6`. Every input row
  then satisfies H < 24, including the sharp faint-end limit.
- `lm_halo = log10(M / (h^-1 Msun))`, with h = 0.67. Physical masses are
  `10**lm_halo / 0.67`. The physical 10^14 Msun threshold is not `lm_halo >= 14`.
- `rvir_halo` is interpreted as comoving h^-1 kpc. A spherical-overdensity
  mass–radius–redshift check gives expected/exported radius median 1.000030 and
  10th–90th percentiles 0.996845–1.002755 for 290 halos with `lm_halo >= 14`.
- Distance calculations use flat matter + Lambda, Omega_m = 0.319, neglecting
  small separate radiation/neutrino expansion terms for these illustrations.
- The two order-4 nested pixels, 702 and 703, are assumed complete and unmasked;
  their combined area is 26.85739665 square degrees.

Projected galaxy profiles use a galaxy-redshift-space cylinder of half-depth
20 h^-1 comoving Mpc around the central galaxy's observed redshift, and
logarithmic annuli from 0.1 to 5 rvir. Area normalization is per halo in comoving
(h^-1 Mpc)^2; curves are equal-halo means. The central at R = 0 is below the
first bin. The separate halo-centre diagnostic places selected centrals at host
true redshifts and uses spherical-shell volumes, referenced to the selected
central density within z_h ± 0.025. It does not invent true satellite positions.

Percentile bands show between-halo distributions. They are not uncertainty on
the mean or a calibrated latent-field covariance; shot noise, mass/redshift
mixing and overlapping apertures remain. Zero bounds are not replaced with an
artificial positive number on log-density plots.

## File map

`content/measuring-a-galaxy-cluster.md` is the scientific source. Figure insertion
markers correspond to `templates/figures/{scene,profiles,response}.html`.
`assets/cluster/` contains static views, tidy measurements, provenance, and the
browser's precomputed probability maps. `tools/` contains reproducible analysis,
figure, article and validation utilities. `notes/editorial-review.md` records
revision decisions; it is not an additional scientific appendix.

The original author's biography and unrelated portfolio pages are retained.
Flagship and CosmoHub credits remain in the article. The bundled Plotly source
retains its MIT license notice. No font files are included.

## Publish

Commit the built HTML and its local assets to `master`, then push to `origin`.
GitHub Pages serves the files directly from the repository root; `.nojekyll`
is kept in the repository. The redirect at
`writing/cluster-derivations.html` preserves the former companion URL. The
source archive used for this revision is ignored by Git.
