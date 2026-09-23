# Verification results — 23 September 2026

`tools/check_math.py`: **14 / 14 pass**. Tests cover selected sample/flux counts,
full PDZ mass and density/CDF consistency, prior removal, native/reference
likelihood equivalence, exact profile decomposition, the distinction between
centres and projected galaxies, adopted mass/radius consistency, the entrywise
log PSD counterexample, lognormal/Cox moments, Gaussian tilting, allocation
averaging order and integration before taking the log.

`tools/check.py`: **pass**. Seven portfolio/reading/redirect pages checked;
30 numbered equations; 14 references; local links and anchors; static image
alt text; no runtime remote dependencies in the article; no companion article.

Diagnostic reproduction: **byte-identical** `scene.csv`,
`profiles-per-halo.csv`, `profile-centres.csv` and `reference-redshift.csv`
after rerunning the portable analysis on the SHA256-matched cache of the supplied
catalogue. Raw-input audit and checksum are recorded in provenance.

`tools/browser_check.py`: **pass** at desktop width 1440 and mobile width 390,
with all runtime network requests blocked. No page overflow or script errors.
The full analytic PDZ map has total displayed full-domain probability mass
7340.999999030074 after serialization, versus 7,341 expected. Source and
reference-weighted example PDFs integrate to one numerically. The environmental
amplitude changes the external response and allocation while leaving the primary
response unchanged. Three-dimensional rotation works with the CPU canvas
renderer, without WebGL. With JavaScript disabled, the 30 typeset equations and
all three static figure groups remain visible.

These checks do **not** establish parameter recovery, posterior coverage,
membership calibration, selection completeness/purity or a mass calibration.
