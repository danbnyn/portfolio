# Checks performed — 22 September 2026

## Passed

`python tools/check.py`: 8 HTML pages, 214 links/assets; local paths and section
anchors, metadata, landmarks, unique IDs and the six-page public sitemap.

`python tools/check_math.py`: seven deterministic test groups covering Gaussian
tilting, lognormal moments / Poisson-mixture variance, entrywise-log admissibility,
selection factorization, allocation and intensity exchange, actual prior-loading
compensation, and the fixed scene’s row identities and counts.

Article compilation: 20 numbered displays in the narrative and 50 in the
companion, with inline notation additionally rendered. SVG and assistive MathML
are embedded; no TeX error nodes were found.

Browser checks used Chromium 144.0.7559.96 and the actual local documents with
assets inlined into a preview, because network navigation is restricted in the
editing environment. Runs at 320, 390, 768 and 1280 pixels found no page-wide
overflow, clipped display-equation starts or JavaScript errors. The keyboard skip
link, three scene controls, reference anchors and print all-view fallback passed.
With JavaScript disabled, all scene panels, native contents disclosures and all
70 numbered equations remained available. Desktop/mobile screenshots were
inspected during preparation.

## Not claimed

These checks do not validate the astrophysical model, test posterior recovery or
coverage, or verify unpublished implementation documents. They do not test HTTP
status handling, live external links/CDN availability, deployment, every browser,
or every screen-reader combination. Assistive MathML is present, but that is not
a full assistive-technology audit. No live website was deployed or modified.

## Re-run

See the root README. The browser check can be split into:

```sh
python tools/browser_check.py --widths 320 390
python tools/browser_check.py --widths 768 1280
```
