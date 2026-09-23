# Revision record — 23 September 2026

## Result

The draft and its former technical companion have been rewritten as one
scientific article, **Measuring a galaxy cluster in a crowded Universe**.
The argument now runs from cosmological selection and mass calibration to the
observation likelihood, the primary population, halo-conditioned environments,
stochastic residual structure, and joint inference. Thirty numbered equations
sit directly in that argument. Fourteen primary-literature references supply
context and attribution. The old companion URL redirects to the article;
its source, navigation link and obsolete figures have been removed.

The main reading artifact is the self-contained interactive HTML. The portfolio
package also includes the editable Markdown, figure templates, derived data,
analysis/build utilities and verification tools. Unrelated portfolio content
and the author's biography were retained.

## Scientific revisions

**Cosmological motivation and scope.** The opening now distinguishes the halo
mass function from the joint detection-and-measurement response. Projection can
change both entry into a catalogue and the measured observable, so an independent
completeness-times-error factorization is not assumed. A primary galaxy-profile
fit is not labelled a dark-matter mass measurement. False detections and unique
primary matching are acknowledged. redMaPPer, AMICO and PZWav are discussed as
existing probabilistic approaches, not caricatured as finders without measurement
or environmental corrections.

**A consistent selected point-process likelihood.** The Poisson likelihood is
derived from cells, including the expected-count term. Measurement and admission
are made explicit before passing to a selected-latent-population convention.
The footprint stays fixed when trial parameters move. Richness is defined as an
expected admitted primary count in that footprint, not quietly interchanged
with an aperture richness, a host-labelled realized count or mass.

**PDZs as one observation per galaxy.** The explanation proceeds through native
likelihood, source posterior and reference-weighted response. Removing a known
source prior is distinguished from applying a new reference. The assumptions
needed for that compression—support, selection and nuisance-variable
marginalization—are stated. Every object's distance and component origin are
marginalized before one logarithm is taken. Fractional redshift-slice counts,
clipped tails, double use of colours and candidate-window renormalization are
not substituted for the generative likelihood.

**An external-only conditional mean.** Halo Palm conditioning is connected to
halo–galaxy pair counting. The primary's own population is removed explicitly;
removing only the central point would not avoid double counting. Halo-centre
exclusion is separated from effective galaxy-level suppression and from
projection. Linear bias near the nonlinear halo boundary is identified as an
approximation requiring calibration.

**A controlled stochastic closure.** Poisson sampling variance is separated
from intensity variance. The compensated lognormal field is derived, including
its ensemble normalization and covariance. Windowed power-spectrum covariances
are identified as candidates, not automatically calibrated conditional
covariances. The entrywise-log PSD counterexample is retained in the narrative.
The exact Gaussian-tilt special case is distinguished from the practical
excluded-mean model: a two-point spectrum alone does not supply the mixed
three-point information needed for general halo-conditioned covariance.

**Joint inference and honest outputs.** Event terms and the compensator are
collected in one likelihood. Membership ratios are averaged after, not before,
being formed. Generating richness, assignment counts and replicated counts are
separated. A halo-conditioned model at zero primary amplitude is not called a
valid no-halo model. Finder conditioning and reuse of the same PDZ information
are addressed. A four-model factorial comparison specifies what would test the
proposed environmental refinements without claiming those tests were performed.

Minor core prescriptions and obsolete modelling history were removed rather
than allowed to interrupt the argument.

## What the data changed

The supplied compressed catalogue contains 4,997,763 rows, all consistent with
H < 24 under the adopted cgs flux convention. The source contains no actual
per-galaxy PDZ arrays and no individual true real-space satellite coordinates.
Those omissions changed the visualization design rather than being hidden.

A fixed 7,341-object sightline includes 183 galaxies in the primary host and 96
in a closely aligned host. Their angular separation is approximately 2.12
arcmin; their host true redshifts are approximately 0.7681 and 0.7397. The same
rows are shown in angular and simulation redshift-space views. A specified
magnitude-dependent measurement model then generates full multimodal PDZs on
0 < z < 3.2. The example is deliberately selected to expose ambiguity, not to
establish typical blending rates or forecast Euclid performance.

The profiles use 339 interior massive halos, with a default narrower selection
of 162. All projected populations use identical redshift-space cylinders and
annuli out to five virial radii. Total = primary + complementary is therefore
an exact count identity. The external population remains enhanced relative to
matched random sightlines, including at small projected radii. Its spread is
substantial but is not presented as a calibrated latent covariance.

A separate true-distance **halo-centre** diagnostic reveals a depleted inner
region and an enhanced exterior. This is the clearest available exclusion
illustration. It does not manufacture missing true satellite positions or imply
that the projected complementary galaxy density must vanish. Host-assigned
primary galaxies beyond one virial radius also prevent identifying a host label
with a sharp virial-radius cut.

Mass and radius units are adopted with explicit caveats. The physical mass
threshold uses h = 0.67 correctly. The comoving-radius interpretation passes an
internal mass–radius–redshift check, but that is not independent authentication
of the missing export metadata. The two HEALPix pixels are assumed complete;
no internal mask or completeness function was supplied.

## Visual decisions

Three figure groups replace the old collection of separate teaching plots:

1. **One sightline, several possible structures.** Linked sky, redshift-space,
   full-PDZ density, rotatable 3D redshift-space and 3D PDZ-cloud views; an
   all-host toggle; full-support zoom; and individual-PDZ inspection. Cloud
   nodes are deterministic quadrature points with weights, not new galaxies.
2. **Separate halo exclusion from projected contamination.** Projected total,
   primary, complementary and matched-random profiles, an across-halo band,
   and the distinct real-space halo-centre diagnostic, with two sample choices.
3. **Let the same galaxy compete between explanations.** A source-prior-aware
   response explorer with candidate-redshift and environmental-amplitude
   controls. It shows how an external explanation changes the conditional
   allocation without changing the galaxy's photometry or source PDZ.

The 3D renderer works without WebGL. Static SVG counterparts, textual
interpretations, keyboard controls and print/no-JavaScript views are included.
The article makes no runtime network request for code, data, fonts or equations.

## Verification and remaining limits

The diagnostic regeneration reproduced four CSV products byte for byte from a
SHA256-matched catalogue cache: scene, profile measurements, conditioning
centres and redshift reference. Fourteen numerical regression tests pass.
Structural checks verify 30 rendered equations, 14 references, local links and
anchors, image descriptions, and the absence of a separate companion article.
Offline Chromium checks exercise desktop and 390-pixel mobile views, figure
selectors, PDZ inspection, 3D rotation, response integrals and no-JavaScript
fallbacks, with no observed script errors, page overflow or runtime requests.

These are data-integrity and functional checks, not inference validation or
exhaustive accessibility certification. A publication making recovery,
uncertainty-calibration or Euclid-performance claims would still need an actual
refinement implementation and repeated-fit experiments; real survey PDZ and
selection calibration; conditional mean/covariance calibration; and a
mass–observable/selection analysis. The article is framed as a rigorous model
and diagnostic study precisely so that it does not depend on unperformed tests.
