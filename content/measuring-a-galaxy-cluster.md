# Measuring a galaxy cluster in a crowded Universe

A cluster candidate is an excess of galaxies in a patch of sky. It is not yet a set of galaxies whose physical association has been settled. A concentration on one side might belong to the cluster’s outskirts, to a neighbouring group, or to a foreground structure that happens to lie in the same direction.

That ambiguity matters before we ask how a cluster’s galaxy population changes with radius. Where is the population centred? How extended is it? How many of the galaxies we could observe does it contribute? An answer to any one of these questions can depend on the answer to the others—and on what we allow the surroundings to explain.

The aim of this refinement model is to carry that competition into the measurement itself. Starting from a supplied candidate, we infer the primary cluster’s galaxy distribution and its environment together. **The target is the primary galaxy population, not a direct dark-matter mass measurement.** The environment is a nuisance in the statistical sense: it is not the quantity we ultimately want, but its uncertainty is part of our uncertainty about that quantity.

This is a difference of emphasis, not a claim that existing finders merely detect. AMICO, for example, already estimates amplitudes and membership probabilities and treats local-background variation.[^amico] The question here is how to construct a local, joint probability model for an individual candidate.

We will build it in stages. A homogeneous background is a useful baseline. Conditioning on a halo changes the expected environment. A random field then describes how this particular environment can depart from that expectation. Finally, the whole model must pass through the same selection and measurement process as the data.

<aside class="article-note"><p><strong>Reading this note.</strong> The main text develops the model and its motivation. The <a href="cluster-derivations.html">derivation companion</a> gives the probability calculations, conditioning assumptions, and selection bookkeeping in full. The figures explain the construction; none is a reported recovery result from the refinement pipeline.</p></aside>

## One scene, different information {#one-scene}

The following views contain exactly the same **2,737 mock galaxies**. They come from a fixed, deliberately chosen neighbourhood in the public Euclid Flagship 2 galaxy mock.[^flagship] On the sky, the populations overlap. Reveal their simulation host labels and the problem becomes easier to see: a primary, another host at a similar redshift, and a foreground host all contribute near the apparent centre.

<!-- FIGURE:scene -->

The redshift-space view supplies information that an image alone does not. It is still not a map of true three-dimensional positions: the exported galaxy redshift includes peculiar-velocity effects.[^flagship] More importantly, this export contains no individual photometric-redshift likelihoods. We should not mistake its simulated redshifts for the noisy distance information of an imaging survey.

In that survey, angular positions and distances play very different observational roles. A galaxy can be well located on the sky while its photometry supports a broad range of redshifts, or several separate ranges. Spectroscopic studies of optically selected clusters demonstrate the resulting projection contamination.[^projection] The anisotropy is in our information, not a preferred direction in the underlying Universe.

Choosing a single best redshift would choose one explanation before the cluster model has compared the alternatives. Instead, each galaxy carries evidence about an unknown distance. A broad likelihood still belongs to **one observed galaxy**. It is not a collection of independent fractional galaxies spread along a line of sight.

There is also a boundary to the experiment. We explain the galaxies admitted by a fixed selection rule in a fixed angular footprint, including its coverage and mask. That catalogue and footprint do not change when the fitted centre or redshift moves. Otherwise, a change in the model would quietly change the data being explained.

## A baseline that knows how to count {#poisson}

Set the observational complications aside for a moment. Suppose the galaxies’ true positions are known in a fixed, completely observed region \(W\). Write

\[
\Lambda_0(x;\theta)=\lambda u(x;\theta)+\bar n_g,
\qquad \int_W u(x;\theta)\,dx=1.
\label{eq:baseline}
\]

Here \(u\) is the primary’s spatial profile, \(\theta\) collects the primary parameters, and \(\bar n_g\) is a homogeneous external number density. The normalization makes \(\lambda\) the expected primary count in this idealized region. The first term is the *one-halo* component: galaxies associated with the primary host.

An intensity \(\Lambda\) is an expected number per unit coordinate volume, not a probability density for one galaxy. Its integral is an expected count and need not be one. Nor does an intensity alone specify a random catalogue. We need a rule for drawing points from it.

The baseline rule is a Poisson point process. Conditional on its intensity, counts in disjoint regions are independent, and

\[
N(A)\mid\Lambda\sim\operatorname{Poisson}(\mu_A),
\qquad \mu_A=\int_A\Lambda(x)\,dx.
\label{eq:counts}
\]

Poisson does not mean spatially uniform: the primary already makes this intensity inhomogeneous. It is a sampling law, not a dynamical model of galaxy formation.[^palm]

To derive the likelihood, divide \(W\) into small cells \(A_j\), with expected counts \(\mu_j\) and observed counts \(N_j\). Independence gives

\[
L=\prod_j\frac{e^{-\mu_j}\mu_j^{N_j}}{N_j!}.
\label{eq:cell-product}
\]

As the cells shrink, a cell containing the observed point \(x_i\) contributes \(\Lambda(x_i)\) times a cell-volume factor. Those volume factors do not depend on the parameters. All the exponential factors combine, leaving

\[
\log L=\sum_i\log\Lambda(x_i)-\int_W\Lambda(x)\,dx+\mathrm{const}.
\label{eq:poisson-likelihood}
\]

The two terms ask different questions. Does the model put intensity where galaxies were observed? Does it predict a plausible total count in the observed region? Empty regions contribute through the integral. This is an unbinned likelihood; the small cells are a derivation device, not a requirement to bin the observations. The [companion gives the limiting argument and its assumptions](cluster-derivations.html#point-process).

This baseline accounts for a concentrated primary and discrete sampling. But changing one background number cannot represent a coherent gradient or an external group. Some of that structure could instead be explained by changing the primary’s amplitude, scale, or centre. That need not happen in every patch; it is the failure mode the next extension addresses.

## A halo does not live at a random location {#conditional-mean}

Imagine placing many apertures at random locations, then placing many on halo centres. These are different sampling experiments. The second selects environments associated with halos. Its expected galaxy density is related to a halo–galaxy cross-correlation, not just to the global mean.[^halo]

The mathematical language for the distribution seen from a typical point of a point process is a *Palm distribution*.[^palm] Here the conditioning point is a halo centre, while the surrounding points are galaxies. We must keep the two populations distinct.

Let \(\bar n_h\) be the halo intensity and let \(\rho^{(2)}_{hE}(0,x)\) be the mixed joint intensity of a halo at the origin and an **external** galaxy at \(x\). The definition of the cross-correlation gives

\[
\begin{aligned}
\rho^{(2)}_{hE}(0,x)&=\bar n_h\bar n_g[1+\xi_{hE}(x)],\\
\overline\Lambda_E(x\mid h_0)
&=\frac{\rho^{(2)}_{hE}(0,x)}{\bar n_h}
=\bar n_g[1+\xi_{hE}(x)].
\end{aligned}
\label{eq:palm-mean}
\]

The subscript \(E\) matters. A full halo–galaxy cross-correlation includes the primary’s own galaxies. Adding a separate primary to that mean would count its population twice. External-only moments must consistently omit contributions from the tagged host. Reduced Palm conditioning alone does not perform that host subtraction; it removes the conditioning point from the point process to which that point belongs.

In halo-model language, the contribution associated with other halos is the *two-halo contribution*. It is not a fit to one particular second halo. On sufficiently large scales, a bias approximation relates its correlated excess to the matter correlation.[^halo]

The design used here prescribes the following environmental factor:

\[
\begin{aligned}
H(r;\theta)&=E(r/R_*)\,[1+A_*\xi_L(r,0)],\\
A_*&=b_h(M_{\rm fid},z_*)\,b_g(z_*)\,D^2(z_*).
\end{aligned}
\label{eq:environment-factor}
\]

The halo and galaxy biases \(b_h\) and \(b_g\) describe their large-scale clustering response relative to matter. The linear growth factor is normalized by \(D(0)=1\); \(\xi_L(r,0)\) is the present-day linear matter correlation. Distances and the exclusion scale \(R_*\) must use a consistent convention.

The factor \(E\) introduces effective exclusion near the primary in three dimensions. It multiplies the **whole bracket**, not just its correlated excess. Otherwise a baseline external population would remain inside the nominally excluded core. Its scale and transition are modeling choices, not a complete calculation of neighbouring halos. The fiducial mass \(M_{\rm fid}\) is a calibration input, not a mass measured by this fit. The chosen prescription must keep \(H\geq0\) over its domain.

<!-- FIGURE:mean -->

Exclusion is not a hole cut out of the image. A foreground galaxy can project directly onto the primary’s centre and still be far outside its excluded three-dimensional neighbourhood. In the opening scene, the foreground host should remain a possible explanation for projected central galaxies.

Our second model is therefore

\[
\Lambda_1(x;\theta)=\lambda u(x;\theta)+\bar n_g H(x;\theta).
\label{eq:conditioned-poisson}
\]

We have changed what we expect around a halo. But an average neighbourhood is not the actual neighbourhood of this halo.

## A mean environment is not this environment {#cox}

A fixed mean can produce chance concentrations through Poisson sampling. It cannot make the underlying expected density itself vary coherently between two otherwise similar patches. A neighbouring group, for example, changes the local intensity from which galaxies are drawn, not just the outcome of one draw.

Change the generative experiment: first draw an external intensity field, then draw the galaxies conditional on that field and the primary. A Poisson process driven by a random intensity is a *Cox process*.[^palm] We write

\[
\begin{aligned}
\Lambda_2(x;\theta,F)&=\lambda u(x;\theta)+\bar n_gH(x;\theta)F(x),\\
F(x)&>0,\qquad \mathbb E[F(x)]=1.
\end{aligned}
\label{eq:cox-model}
\]

There are still two additive populations: primary and external. The multiplier \(F\) modulates the external population; it is not a third population added on top.

The distinction between the two kinds of randomness can be derived without spatial machinery. The expected count \(\mu_A\) is now random. Conditional on it, the Poisson mean and variance are both \(\mu_A\). Total variance gives

\[
\begin{aligned}
\operatorname{Var}[N(A)]
&=\mathbb E[\operatorname{Var}(N(A)\mid F)]
 +\operatorname{Var}(\mathbb E[N(A)\mid F])\\
&=\underbrace{\mathbb E[\mu_A]}_{\text{discrete sampling}}
 +\underbrace{\operatorname{Var}(\mu_A)}_{\text{environmental variation}}.
\end{aligned}
\label{eq:total-variance}
\]

For fixed primary parameters, the second term comes from variation in the environment. It vanishes when the intensity is fixed. Counts in disjoint cells can also become correlated after averaging over the field: their covariance is the covariance of their random expected counts.

<!-- FIGURE:counts -->

Conditional Poisson independence is therefore compatible with a correlated marginal catalogue. Nor is the latent field just a smoothed map of the observed points: it is one of the unobserved objects that could have generated them. The [companion derives both the count variance and cross-cell covariance](cluster-derivations.html#point-process).

This freedom addresses object-to-object environmental variation. It also creates a new problem: what stops the external field from explaining away the primary?

## Give the field freedom—with a cost {#field}

The attribution problem is exact in the simplified expression \(I(x)=\lambda u(x)+B(x)\). Decrease \(\lambda\) by \(\Delta\) and add \(\Delta u(x)\) to \(B(x)\). Whenever both allocations are allowed, the total intensity and its integral are unchanged. **The likelihood cannot distinguish them.** Even the expected-count term cannot resolve an exchange that preserves the total intensity.

A model must restrict which external explanations are available and how probable they are. Too little freedom can force contamination into the primary. Unrestricted freedom can remove the primary. The objective is not to forbid competition, but to make its probability law explicit.

Start with positivity. An additive Gaussian fluctuation can make an intensity negative. Instead, define a finite jointly Gaussian vector over retained field cells and exponentiate it:

\[
G\sim\mathcal N(0,C),
\qquad F_j=\exp\!\left(G_j-\frac{C_{jj}}2\right).
\label{eq:lognormal}
\]

The covariance \(C\) specifies how the log-field values vary together. The exponential guarantees a positive multiplier. Lognormal–Poisson inference has precedent in large-scale-structure analysis; here the lognormal component describes residual external variation around a separately prescribed mean.[^jasche]

The subtraction is essential. A zero-mean Gaussian variable obeys \(\mathbb E[e^{G_j}]=e^{C_{jj}/2}\), so \(\mathbb E[F_j]=1\). Adding fluctuations does not silently increase the mean external density. This is an **ensemble** normalization, not a rule forcing every realized patch to average to one.

The same Gaussian moment identity yields

\[
\mathbb E[F_jF_k]=e^{C_{jk}},
\qquad \operatorname{Cov}(F_j,F_k)=e^{C_{jk}}-1.
\label{eq:lognormal-moments}
\]

If \(K\) is the desired fractional covariance of the external intensity, moment matching suggests

\[
C_{jk}=\log(1+K_{jk}).
\label{eq:moment-match}
\]

This logarithm is entrywise, not a matrix logarithm. The entries must exist, and the resulting matrix must be positive semidefinite: every linear combination must have nonnegative variance. Even a positive-semidefinite \(K\) does not guarantee this. The [companion gives a two-cell counterexample](cluster-derivations.html#finite-field).

### Connect the freedom to represented scales

Positivity alone does not protect the primary. The decisive choice is which spatial patterns receive substantial prior probability.

A power spectrum distributes fluctuation variance across spatial scales. Long-wavelength modes vary slowly across a patch; shorter wavelengths can represent more localized structure. In an equal-time Cartesian teaching example, define a cell-averaged fluctuation by \(\delta_j=b_j\int W_j(x)\delta_m(x)\,dx\), with \(\int W_j=1\). Then

\[
K_{jk}=b_jb_k\int\frac{d^3k}{(2\pi)^3}\,
P_m(k)\,\widetilde W_j(\mathbf k)\,
\widetilde W_k(\mathbf k)^*.
\label{eq:windows}
\]

The power supplies each mode’s variance; the windows determine what survives averaging in each cell. This is a teaching identity, not the literal survey calculation. The design calls for angular pixels, selected radial windows, population bias, and redshift-dependent nonlinear matter power. A power spectrum supplies second-order statistics; it does not specify the complete environment of a halo.[^halo]

Finite averaging matters. We first construct moments on the represented cells, then match a lognormal law on those cells. Averaging a continuous Gaussian log-field and exponentiating would generally give different moments. Averaging and nonlinear transformation do not commute, and an average of lognormal variables is not generally lognormal.

<!-- FIGURE:prior -->

The Gaussian prior makes the cost of a competing pattern explicit. In an eigenmode of \(C\) with variance \(\kappa>0\), an amplitude \(g\) costs \(g^2/(2\kappa)\) in the negative log density. Patterns with little prior variance are expensive to excite. This is more informative than counting field coordinates or calling a field “smooth”. A zero-variance mode is fixed rather than assigned a finite quadratic penalty.

Still, the lognormal field is unbounded above, and its patterns need not be orthogonal to the primary. A physically plausible external structure should be allowed to compete. Conversely, overly restrictive covariance or coarse cells can force real external structure back into the primary. Resolution and prior calibration are scientific sensitivity questions, not merely numerical settings.

## What Palm conditioning does—and does not—prove {#palm-boundary}

We changed the environmental mean using halo conditioning. Should conditioning also change the residual covariance?

There is an instructive exact case. Suppose the halo-centre and external-tracer intensities are driven by **jointly Gaussian log-fields**, with conditional Poisson sampling for both types. Seeing a halo at the origin reweights each possible field by the halo intensity it places there. For a zero-mean Gaussian vector \(Y\), exponential tilting gives

\[
Y\sim\mathcal N(0,C)
\quad\Longrightarrow\quad
 e^{t^TY-\frac12t^TCt}p(Y)
 \text{ is the density of }\mathcal N(Ct,C).
\label{eq:gaussian-tilt}
\]

Completing the square shifts the Gaussian mean and leaves its covariance unchanged. Taking \(t\) to select the halo component shifts the external log-field mean by its cross-covariance with the halo log-field at the origin. Thus the conditioned external intensity factors into a changed mean and a unit-mean lognormal residual. The corresponding single-process reduced-Palm LGCP theorem is established by Coeurjolly, Møller and Waagepetersen.[^lgcp] The [companion works through the multitype calculation](cluster-derivations.html#gaussian-tilt).

In this ideal joint model, the mean factor is \(H(x)=\exp[C_{Eh}(x,0)]\). The Gaussian covariance—and the *fractional* intensity covariance—remains unchanged. The absolute intensity covariance changes with the mean.

Our practical prescription is **not an exact application of that theorem**. It uses an excluded-linear environmental mean and residual moments built from a separate power-spectrum calculation. A finite Gaussian cross-covariance cannot produce an exactly zero mean, since its exponential is strictly positive. More generally, the covariance of the environment seen from a halo depends on mixed halo–galaxy three-point information, not only an ordinary matter two-point spectrum.

The construction is therefore a conditional approximation: a specified mean and physically motivated residual moments stand in for the full joint distribution of a halo and its environment. Using linear correlation for the mean and nonlinear power for residual variation reflects their different jobs. It does not establish the accuracy of their combination, particularly near the primary. That combination needs testing.

There is a second boundary. A *known halo* and a *candidate selected by a finder* are not the same conditioning event. The finder may select on the very observations used again in the local fit. Palm reasoning does not, by itself, model false positives, finder selection, or the reuse of data. A positive-richness refinement model is not automatically a calibrated probability that a halo exists.

## Forward through the observation {#observation}

So far we have described possible latent galaxy distributions. The data are observations of those galaxies. The bridge must be a forward model, not an assignment of every object to a best-fit distance.

Let \(x\) denote a latent coordinate, \(y\) a measurement, \(k(y\mid x)\) a normalized measurement kernel, and \(s(y)\) the probability that the measurement is admitted. Given independent measurements and selection conditional on the latent intensity, the observed intensity is

\[
\begin{aligned}
\nu(y)&=s(y)\int k(y\mid x)\Lambda(x)\,dx,\\
\mu_{\rm obs}&=\int\nu(y)\,dy
=\int\alpha(x)\Lambda(x)\,dx,\\
\alpha(x)&=\int s(y)k(y\mid x)\,dy.
\end{aligned}
\label{eq:observation}
\]

Every latent galaxy contributes according to the probability of the measurements it could produce. **Both populations pass through this operation.** The same admission rule must also determine the expected observed count. The likelihood still has its event term and its expected-count term, now in observation space.

A redshift likelihood \(\ell_i(z)\) describes the information in one galaxy’s measurement about \(z\). It can remain broad or multimodal throughout inference. A supplied posterior is not automatically that likelihood: Bayes’ rule includes the source prior. Dividing out a known prior, with appropriate support and consistent nuisance-variable treatment, is not optional bookkeeping.

<!-- FIGURE:likelihood -->

Selection can be organized in two equivalent ways: a parent intensity with explicit admission, or a selected latent intensity with a measurement kernel normalized conditional on admission. Mixing the two would apply selection twice. The [companion derives this equivalence](cluster-derivations.html#observation-operator) and separately records the empirical-reference convention used in the design.

### What the richness actually means

The primary is approximated as thin in latent redshift, at \(z_*\). This is motivated by a compact primary viewed through broad photometric-distance uncertainty, not by an assertion that all its observed redshifts are identical. More informative distance measurements would require revisiting the approximation.

Let \(U(\omega;\theta)\) be the primary angular profile and \(w(\omega)\) the fixed coverage. Normalize it over the fixed footprint \(\Omega\):

\[
\int_\Omega w(\omega)U(\omega;\theta)\,d\omega=1.
\label{eq:covered-normalization}
\]

Now \(\lambda\) has its scientific meaning: **the expected selected primary count in the fixed covered footprint**. It is not an intrinsic three-dimensional richness. If the centre moves, the covered normalization of its profile changes; the footprint and catalogue do not.

The design uses a projected, truncated NFW family for the galaxy profile. This is an interpretable shape choice, not a claim that every galaxy population follows the dark-matter profile. A scale of that fitted galaxy profile is not automatically a simulated halo radius. The [companion gives the generic projection and normalization](cluster-derivations.html#selected-model), without choosing an undocumented truncation function.

Writing \(\chi\) for comoving distance, the selected latent intensity per solid angle and distance is

\[
\begin{aligned}
\Lambda_R(\omega,\chi)=w(\omega)\bigl[
 &\lambda U(\omega;\theta)\delta_D(\chi-\chi_*)\\
 &+\rho_R(\chi)H(\omega,\chi;\theta)F(\omega,\chi)\bigr].
\end{aligned}
\label{eq:selected-intensity}
\]

The selected reference \(\rho_R\) already has units per solid angle and comoving distance; an extra \(\chi^2\) volume factor would be incorrect. It can vary with distance even in the homogeneous-external model. Thus “homogeneous background” ultimately means no additional angular environmental structure, not a flat redshift distribution.

Individual redshift likelihoods belong in this observation calculation. They are not one universal extra smoothing kernel to insert into the prior covariance. The uncertainty of a particular distance and the prior variation of an intensity field describe different things.

## Infer the cluster and the ambiguity together {#inference}

Let \(\nu_i^P\) and \(\nu_i^E\) denote the primary and external responses for observation \(i\), including the observation and selection conventions. The likelihood becomes

\[
\log L(\theta,G)=
\sum_i\log[\nu_i^P(\theta)+\nu_i^E(\theta,G)]
-\lambda-\mu_E(\theta,G)+\mathrm{const}.
\label{eq:joint-likelihood}
\]

The external field contributes at the observed galaxies **and** to its expected count \(\mu_E\). The environmental mean depends on the primary state, so moving the primary can change the external explanation. Both components must be evaluated at the same joint state.

Priors complete the posterior. To learn about the primary, integrate over the field:

\[
p(\theta\mid D)=\int p(\theta,G\mid D)\,dG.
\label{eq:marginal}
\]

This is not generally equivalent to fitting one external map, subtracting it, and analyzing the remainder. A single subtraction treats one environmental explanation as settled. Marginalization retains the possibility that different environments support different richnesses, scales, or centres.

Membership follows from the same competition. Conditional on a joint state, an observed galaxy’s primary allocation probability is its primary response divided by the total. The reported membership is

\[
p_i^P=\mathbb E_{\theta,G\mid D}
\left[\frac{\nu_i^P}{\nu_i^P+\nu_i^E}\right].
\label{eq:membership}
\]

The ratio is formed **before** averaging. Membership is an output of the model, not a clean input catalogue available beforehand. The [companion derives the allocation law from Poisson superposition](cluster-derivations.html#joint-inference).

Three quantities should remain distinct: \(\lambda\), an expected selected intensity; \(\sum_i p_i^P\), an allocation of existing observations; and the primary count in a new replicated catalogue, which includes another Poisson draw. Their uncertainties answer different questions.

Population labels, or *marks*, can extend the construction to several galaxy populations. The design allows population-specific references, biases and primary parameters, with shared latent drivers for the external fields. That specifies a particular cross-population dependence; it does not infer an arbitrary cross-covariance. The central question remains the same: how much of the admitted catalogue is supported as primary rather than external?

## What would count as a successful refinement? {#validation}

A plausible-looking environmental map is not the test. The model is useful if its treatment of the environment improves inference about the primary, including the interpretation of uncertainty.

The progression above suggests a controlled comparison:

| Model | Environmental mean | Residual field |
| --- | --- | --- |
| Homogeneous baseline | \(H=1\) | \(F=1\) |
| Conditioned mean | Prescribed \(H\) | \(F=1\) |
| Stochastic, unconditioned ablation | \(H=1\) | Random \(F\) |
| Full conditional model | Prescribed \(H\) | Random \(F\) |

All four must use the same admitted galaxies, footprint, primary family, references, priors, and target quantity. Otherwise an apparent improvement could simply reflect a different question.

In controlled mocks, we can test recovery of the *generating* selected richness, centre, redshift and profile parameters. Across a specified ensemble, we can check whether credible intervals contain compatible truth at the rates we expect. A realized number of labeled mock members is not automatically the generating expected richness. The 160 labeled primary galaxies in our illustrative cut, for example, are a count in that cut—not a supplied generating value of \(\lambda\).

In-model mocks test recovery under the assumptions. Deliberately different environments, primary shapes, redshift errors, and calibration choices test the consequences of misspecification. Posterior predictions should also confront raw observed counts. A membership-weighted profile already depends on the model’s attribution and cannot independently confirm that attribution.

This article does not report those validation runs. The Flagship scene motivates the inference problem; the other figures demonstrate mathematical properties or explicitly specified toy models. Recovery plots, coverage curves, and posterior tradeoffs require actual inference outputs and compatible truth definitions.

Cosmology, fiducial mass, bias calibration, empirical references, and field settings remain supplied inputs here. Candidate selection and potential data reuse remain separate concerns. Population conclusions from a refined catalogue would still need a suitable selection and population model.

A more flexible environment need not make a primary posterior narrower. An ambiguous object should be allowed to remain ambiguous. A broader interval can be the more faithful result when the alternative is precision obtained by treating the surroundings as known.

The progression is therefore not simply from a small model to a larger one. Halo conditioning changes what we expect. The random field describes how one environment can differ. Its covariance gives those departures structure. Joint inference carries the resulting competition into the measurement of the primary.

**We do not need to pretend a cluster’s surroundings are simple. We need to keep track of which conclusions about the cluster survive uncertainty about them.**

## Data, code and acknowledgements {#data}

The opening scene uses the public Euclid Flagship 2 galaxy mock. The modern catalogue paper describes the four-trillion-particle simulation and its galaxy-population construction.[^flagship] Potter, Stadel and Teyssier (2017) describe PKDGRAV3 and an earlier two-trillion-particle run; they should not be used alone to document the later four-trillion-particle catalogue.[^pkdgrav]

The original CosmoHub export, `27277.csv.bz2`, contains **530,570 rows and 21 columns**, selected from `euclid_fs2_mock_dr_v1_1_phz`. Its SQL selects positive H-band flux and \(H_{\rm AB}<26\) in the nested order-6 HEALPix pixel containing \((190^\circ,60^\circ)\). These are the export’s cuts, not a claim about the refinement pipeline’s selection.

For the figure, the origin is the central galaxy of host `4040470062983`, at \((\alpha_0,\delta_0)=(189.68779^\circ,59.70510^\circ)\). Its supplied halo redshift is \(0.7255272\). The additional illustration cuts are \(|x|<6\) arcmin, \(|y|<6\) arcmin, and \(H_{\rm AB}<22.5\), with \(x=60(\alpha-\alpha_0)\cos\delta_0\), \(y=60(\delta-\delta_0)\), and angular coordinates in degrees. The offsets use a small-angle approximation. No redshift cut or random downsampling is applied.

The resulting 2,737 rows include 160 galaxies of the primary host, 35 of highlighted host `4040470064477`, and 33 of highlighted foreground host `3838420219862`. These are simulation labels. The scene was deliberately chosen for explanation; it is not a representative sample or a validation ensemble. The export lacks individual galaxy true-redshift coordinates and photo-z likelihood arrays; the redshift panel uses `observed_redshift_gal`, not `true_redshift_halo` copied onto every satellite as though it supplied its true distance.

The [fixed figure subset](../assets/cluster/scene.csv), [provenance and raw-file checksum](../assets/cluster/provenance.json), [toy-model specifications](../assets/cluster/illustration-models.json), and [figure-generation script](../tools/make_figures.py) make the illustrations reproducible. The large raw catalogue is not needed to display the article. The [derivation companion](cluster-derivations.html) and [article source](../content/measuring-a-galaxy-cluster.md) are available separately.

<details class="disclosure"><summary>CosmoHub acknowledgement</summary><p>This work has made use of CosmoHub (Tallada et al. 2020; Carretero et al. 2018), developed by PIC (maintained by IFAE and CIEMAT) in collaboration with ICE-CSIC. It received funding from the Spanish government (grant EQC2021-007479-P funded by MCIN/AEI/10.13039/501100011033), the EU NextGeneration/PRTR (PRTR-C17.I1), and the Generalitat de Catalunya.</p></details>

The acknowledgement above reproduces the requirement in the export header. The associated CosmoHub and SciPIC publications are included below.[^cosmohub][^scipic]

[^amico]: F. Bellagamba, M. Roncarelli, M. Maturi & L. Moscardini (2018). *AMICO: optimised detection of galaxy clusters in photometric surveys*. MNRAS 473, 5221–5236. [arXiv:1705.03029v2](https://arxiv.org/abs/1705.03029v2), especially §§2.6 and 3.1.
[^flagship]: Euclid Collaboration, F. J. Castander et al. (2025). *Euclid. V. The Flagship galaxy mock catalogue: a comprehensive simulation for the Euclid mission*. A&A 697, A5. [arXiv:2405.13495](https://arxiv.org/abs/2405.13495). Galaxy-mock and simulation provenance, not evidence for this refinement method’s performance.
[^projection]: J. Myles et al. (2025). *Spectroscopic Characterization of redMaPPer Galaxy Clusters with DESI*. [arXiv:2506.06249v3](https://arxiv.org/abs/2506.06249v3). Evidence for projection contamination in optically selected clusters, not a direct validation of the present model.
[^palm]: J.-F. Coeurjolly, J. Møller & R. Waagepetersen (2017). *A tutorial on Palm distributions for spatial point processes*. International Statistical Review 85, 404–420. [arXiv:1512.05871v2](https://arxiv.org/abs/1512.05871v2). Point-process and Palm definitions.
[^halo]: M. Asgari, A. J. Mead & C. Heymans (2023). *The halo model for cosmology: a pedagogical review*. [arXiv:2303.08752v2](https://arxiv.org/abs/2303.08752v2), especially §§2–3 and 5.6. Halo-model terminology, bias and exclusion context; it does not establish the conditional closure used here.
[^jasche]: J. Jasche, F. S. Kitaura, B. D. Wandelt & S. Gottlöber (2010). *Bayesian non-linear large scale structure inference of the Sloan Digital Sky Survey data release 7*. [arXiv:0911.2498](https://arxiv.org/abs/0911.2498). Precedent for lognormal–Poisson field inference, not the origin of the present conditional construction.
[^lgcp]: J.-F. Coeurjolly, J. Møller & R. Waagepetersen (2017). *Palm distributions for log Gaussian Cox processes*. Scandinavian Journal of Statistics 44, 192–203. [arXiv:1506.04576v4](https://arxiv.org/abs/1506.04576v4), Theorem 1. The multitype illustration here additionally assumes jointly Gaussian halo and tracer log-intensities.
[^pkdgrav]: D. Potter, J. Stadel & R. Teyssier (2017). *PKDGRAV3: beyond trillion particle cosmological simulations for the next era of galaxy surveys*. Computational Astrophysics and Cosmology 4, 2. [Published article](https://link.springer.com/article/10.1186/s40668-017-0021-1).
[^cosmohub]: P. Tallada et al. (2020). *CosmoHub: Interactive exploration and distribution of astronomical data on Hadoop*. Astronomy and Computing 32, 100391. [arXiv:2003.03217](https://arxiv.org/abs/2003.03217).
[^scipic]: J. Carretero et al. (2018). *CosmoHub and SciPIC: Massive cosmological data analysis, distribution and generation using a Big Data platform*. PoS(EPS-HEP2017) 488. [Published proceedings](https://pos.sissa.it/314/488/).
