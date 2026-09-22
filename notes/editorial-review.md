# Editorial review and handoff

## Positioning

The site now presents a longstanding interest in mathematical and theoretical
physics, with computation as a way to investigate models. It no longer tells an
“engineering to physics” transition story. The About page retains the formal
engineering qualification while explaining the theoretical course of study in
personal, neutral terms. This follows the supplied CV and the author’s account;
it does not generalize about every French engineering programme.

The homepage is an entrance to the writing, not a compressed repetition of About
and Work. It contains one short introduction and the latest article. Oxford’s
incoming status appears on About, not on every page. The supplied dates place
the programme’s start in October 2026; the copy does not treat it as already
under way on the revision date, 22 September 2026.

The IAP internship context is stated on Work. The article links back to the
project naturally without repeatedly advertising the internship. The dates in
the CV combine “September 2025–Present” with “six-month internship”; rather than
invent an end date or maintain a possibly stale current-status claim, the site
omits that interval. The CV’s paper-in-preparation statement is not promoted to
a current publication or submission claim.

## Curation, not deletion of experience

For this first public selection, keep IAP and the RODEO course project. Together
they give the site a coherent centre in physical questions, probability models,
and computation. The RODEO description retains the task and partnership, but
not the unsupported comparative speed/resource claim from the CV.

The cryptographic suite and industrial radiance-field project are not displayed.
That is an editorial choice, not a judgment about their value. They can return
when there is a specific question, argument or result worth writing about.
Neither appears as an empty “coming soon” card. Projects commented out in the
CV were not revived as if they were selected current work.

## Article architecture

The main article preserves the drafts’ underlying progression:

1. An observed excess is not an already-established member catalogue.
2. A Poisson primary-plus-background model is a useful starting experiment.
3. Halo conditioning changes the expected external environment.
4. A Cox residual accounts for coherent environment-to-environment variation.
5. Finite-cell covariance determines which competing explanations are plausible.
6. Selection and measurement map the latent model to the observed catalogue.
7. Joint inference carries that competition into primary parameters and memberships.
8. Validation has to compare matched estimands and calibrated uncertainties.

The opening is now built around one actual mock neighbourhood rather than a
series of generic mission motivations. The technical companion is a reading
layer of the same article, not an unrelated second blog post. Both have numbered
equations, stable section anchors, references, and downloadable Markdown.

The companion adds explicit intermediate algebra where it improves auditability:
Poisson likelihood and count covariance; mixed Palm product densities;
conditional three-point dependence; completing the square for Gaussian tilting;
finite-window covariance; selection factorization; generic spherical profile
projection; and the distinction between allocation and replicated counts.
The two-cell entrywise-log counterexample is an added pedagogical calculation,
not a pipeline result. These additions are derived from stated assumptions rather
than silently represented as details of uninspected code.

## Scientific boundaries retained or strengthened

The main target is the primary galaxy population, not a direct mass estimate.
Richness is an expected selected primary count in the fixed covered footprint.
The footprint is not moved with the fitted centre. The selected reference is
already expressed in its declared angular/radial measure.

Primary galaxies must not be counted both in a separate one-halo profile and
again in a full halo–galaxy conditional mean. Reduced Palm removal of a tagged
point is not host-member subtraction. The exact multitype Gaussian-tilt example
requires jointly Gaussian log-intensities and conditional Poisson sampling.
The separately prescribed excluded mean and power-spectrum residual covariance
are a conditional approximation, not the exact Palm law of a survey detection.
A general halo-conditioned pair covariance depends on higher-order mixed
statistics. Its absolute covariance is not unchanged by the Gaussian mean shift.

Lognormal positivity does not solve attribution. The entrywise logarithm of
`1 + K` is not guaranteed to be a covariance matrix. A retained loading must use
its actual represented variance in the exponential compensation. A prior with
physical motivation is not automatically orthogonal to the primary.

A source redshift posterior is not automatically a native likelihood. Selection
must not be applied twice. The same observation convention must enter event
responses and the expected-count term. A shared state-independent factor in an
event likelihood is distinct from rescaling a physical observation-space intensity.

Membership is the posterior expectation of an allocation ratio, not a ratio of
posterior means. Generating richness, allocated observed counts and new Poisson
counts have different interpretations. Finder selection, false positives and
reuse of candidate information remain separate concerns.

## What the supplied sources do not establish

The two drafts refer to `model(2).md`, `numerics.md`, `usage(1).md` and
`results(1).md`. Those files and the inference implementation were not included
in the supplied site archive or attachments. Their claims are therefore carried
as descriptions of the design recorded in the drafts, not independently verified
implementation statements. Broken private-document references were removed
from the public bibliography. The exact truncation law, empirical response
products, and literal survey covariance implementation were not reconstructed.

The catalogue is not a set of inference outputs. There are no supplied posterior
samples, calibrated covariance products or compatible generating-richness labels
from which to report refinement recovery or coverage. The article ends with a
substantive validation design, not an invented results figure or an empty slot.

Before attaching empirical performance claims, the most useful next inputs are
one reproducible pipeline configuration, its empirical reference/covariance
products, and posterior samples for a mock with explicitly compatible truth.
Actual per-galaxy likelihood arrays would also allow a genuine measurement-space
illustration. A larger raw sky sample alone would not supply those missing objects.

## Visual provenance

The 2,737-row scene comes from a deliberately chosen interior rich host in the
530,570-row export. All three views use identical rows and simulation host labels.
The plot does not use the halo’s true redshift as the true distance of each
satellite. The exported galaxy redshift includes peculiar velocities; it is not
a photo-z measurement. The supplied mock’s host labels are not inferred memberships.

The other figures are labeled teaching constructions. They show a schematic
excluded mean, a calculable one-cell Poisson mixture, two explicit finite-cell
Gaussian priors, and synthetic redshift-likelihood shapes. No toy recovery plots
or fake posterior samples were generated.

Primary literature was checked for AMICO, point processes/Palm conditioning,
log-Gaussian Cox processes, the halo model, projection, and Flagship provenance.
The modern Flagship catalogue paper supports the later four-trillion-particle
catalogue; Potter et al. (2017) is retained as PKDGRAV3/earlier-run context rather
than treated as the sole source for that later catalogue. Each article reference
states its role. Catalogue cuts and counts come from the attachment, not from a
claim about the full public survey release or the refinement pipeline selection.

## Implementation choices

No framework or runtime build system was added. The four original root pages,
CSS visual language, navigation and GitHub Pages base are retained. The writing
pages are committed HTML; the editable sources and small authoring scripts are
optional. Equations are rendered at authoring time to SVG plus assistive MathML,
so reading them no longer depends on a live CDN or browser JavaScript. The scene
switcher is progressive enhancement, and the static figures remain usable without it.

The full raw catalogue, CV source, private export contact line, font files,
`node_modules`, caches and browser artifacts are not included in the deliverable.
No repository write or deployment has been performed.
