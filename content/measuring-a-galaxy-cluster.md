# Measuring a galaxy cluster in a crowded Universe

Galaxy clusters connect two very different scales of cosmology. Their internal galaxy populations occupy compact regions, but the abundance and clustering of the dark-matter halos that host them reflect the growth of structure across the Universe. Massive halos lie on the rare tail of the halo population: changing the fluctuation amplitude or growth history changes how many form. Their redshift distribution also depends on cosmological volume. This makes clusters valuable cosmological probes—and makes the route from an observed concentration of galaxies to a well-defined cluster observable consequential.[^cosmology]

Schematically, the expected number of halo-associated detections whose measured properties fall in a bin \(B\) is

\[
\begin{aligned}
\mathbb E[N_{\rm det}(B)]={}&\int d\Omega\,dz\,
\frac{dV}{d\Omega\,dz}(z;\varphi)
\int d\ln M\,\frac{dn}{d\ln M}(M,z;\varphi)\\
&\times P(\mathrm{det},\widehat O\in B\mid M,z;\psi).
\end{aligned}
\label{eq:cosmological-counts}
\]

This form assumes a unique primary-halo association; false detections require an additional contribution. Here \(\varphi\) denotes cosmological parameters and \(\psi\) the galaxy–halo relation, observing conditions, and analysis choices. The last factor is a **joint detection-and-measurement response**, not necessarily a product of an independent completeness function and an independent measurement error. A line-of-sight structure can both promote a candidate into the catalogue and increase its measured richness. Scatter and selection then matter together, especially where the mass function is steep.[^projection]

This article concerns one part of that response: **refining the primary galaxy population around an already supplied candidate while retaining uncertainty about its environment**. The outputs are a centre, redshift, galaxy-profile parameters, a selected richness, and probabilistic memberships. They are not a direct dark-matter mass measurement. Connecting them to the first equation still requires mass calibration and a survey-level selection model.

### From finding an overdensity to interpreting it

Optical cluster finding already has a substantial probabilistic literature. redMaPPer combines a red-sequence model with spatial and luminosity information, probabilistic membership, and uncertain centring.[^redmapper] AMICO uses an optimal filter, assigns membership probabilities, and includes a local-background correction.[^amico] PZWav searches photometric-redshift slices with a wavelet-style filter and distributes each galaxy across slices using its full redshift probability distribution. AMICO and PZWav were selected in the published Euclid Cluster Finder Challenge.[^cfc]

The distinction here is therefore not “existing algorithms detect; this model measures.” Detection, membership, and measurement already overlap. The more specific question is whether a **local, joint generative model of the primary and a fluctuating external population** can carry environmental ambiguity into the primary posterior. A PDZ-weighted map is a useful detection statistic; it is not automatically a likelihood for independent counts in those redshift slices.

The argument will proceed from what is actually observed to what generates it. First we keep the catalogue selection and distance uncertainty explicit. Then we ask what a halo’s surroundings should look like on average, what is lost by replacing a particular environment with that average, and how a positive random field supplies controlled alternatives. These pieces lead to one joint likelihood rather than a background subtraction followed by a separate cluster fit.

## The same galaxies, different distance information {#one-scene}

Consider a fixed \(12\times12\) arcmin patch in the Flagship catalogue used here. With \(H_{\rm AB}<24\), it contains **7,341 galaxies**, including 183 assigned to one halo at \(z_h=0.7681\) and 96 to an aligned halo at \(z_h=0.7397\). Their centres are only about 2.12 arcmin apart. The neighbourhood was deliberately chosen to expose an ambiguity, not to represent an average cluster.

<!-- FIGURE:scene -->

The redshift-space view separates structures that overlap in angle. But the exported `observed_redshift_gal` is a simulation redshift that includes peculiar-velocity effects; it is neither a photometric estimate nor a true real-space radial coordinate. This catalogue export contains **no individual PDZ arrays**. The full-PDZ view therefore adds a declared synthetic measurement model to exactly the same galaxies. It does not claim to reproduce Euclid’s calibrated photo-z performance.

For this illustration, put \(s=\ln(1+z)\) and generate a noisy measurement \(t_i\) from a three-component Gaussian mixture around the galaxy’s simulated redshift. The dominant component has width \(\sigma_{s,i}=0.015+0.035\,\mathrm{clip}[(H_i-20)/4,0,1]\); the two alias components are displaced by \(\pm0.25\) in \(s\), have widths \(1.5\sigma_{s,i}\), and each carry probability 0.04. A prior uniform in \(s\) over \(0<z<3.2\) produces a normalized, generally multimodal PDZ for every galaxy. Thus \(\sigma_z/(1+z)\) is approximately 0.015–0.05 for the dominant component, **by construction**, not by measurement.

The important visual operation is not to give every galaxy one displaced point. It is to replace one known radial coordinate with a distribution of possible coordinates. In the PDZ map, a galaxy contributes a total probability of one across the full redshift domain. The interactive view can reveal the other hosts and inspect individual distributions; zooming does not renormalize probability into the displayed interval.

The uncertainty is highly anisotropic: sky positions are precise while distance information is broad. The cluster model should exploit the angular information without prematurely resolving the distance ambiguity. A broad PDZ still belongs to **one observed object**.

## A likelihood that explains positions and counts {#point-process}

An intensity \(\Lambda(x)\) specifies an expected number per unit coordinate measure. Its integral is an expected count, not necessarily one. To obtain a probability law for a catalogue, we also need a sampling model.

As a baseline, assume conditional Poisson sampling in a fixed region \(W\). Divide it into small cells with means \(\mu_j=\int_{A_j}\Lambda(x)\,dx\). Independent cell counts have likelihood

\[
L=\prod_j \frac{e^{-\mu_j}\mu_j^{N_j}}{N_j!}
\quad\Longrightarrow\quad
\log L=\sum_i\log\Lambda(x_i)-\int_W\Lambda(x)\,dx+\mathrm{const}.
\label{eq:poisson}
\]

In the shrinking-cell limit, each occupied cell contributes its local intensity times a parameter-independent cell volume; the exponential factors combine into the integral. Equivalently, draw the total count from a Poisson distribution and then draw locations from the intensity normalized by its integral. This is an unbinned likelihood: the cells explain the derivation, not a required representation of the data.[^palm]

The first term rewards intensity at observed events. The second—the expected-count term, or compensator—penalizes predicting too many events over the observed region. Empty regions therefore carry information. Poisson sampling does not require a uniform intensity: a centrally concentrated cluster already makes it inhomogeneous.

### Selection is part of the observation model

The latent galaxies are not the catalogue. Let \(x\) include the true quantities needed to predict an observation \(y\), let \(k(y\mid x)\) be a normalized measurement kernel, and let \(s(y)\) be the admission probability. Independent marking and selection, conditional on the latent intensity, give

\[
\begin{aligned}
\nu(y)&=s(y)\int k(y\mid x)\Lambda(x)\,dx,\\
\mu_{\rm obs}&=\int\nu(y)\,dy
=\int\alpha(x)\Lambda(x)\,dx,\\
\alpha(x)&=\int s(y)k(y\mid x)\,dy.
\end{aligned}
\label{eq:observation}
\]

The same observing rule enters both the event responses and the expected count. Neither the primary nor the external population can bypass it. Catalogue-dependent deblending or correlated photometric errors would require extensions to the independent-measurement assumption.

It is often simpler to model the **selected latent population** directly. Define

\[
\Lambda_R(x)=\alpha(x)\Lambda(x),\qquad
k_R(y\mid x)=\frac{s(y)k(y\mid x)}{\alpha(x)}.
\label{eq:selected-kernel}
\]

Where \(\alpha>0\), \(k_R\) integrates to one and \(\nu(y)=\int k_R(y\mid x)\Lambda_R(x)\,dx\). Consequently \(\mu_{\rm obs}=\int\Lambda_R\). This is the convention used below: flux admission is already absorbed into the selected population and its compatible measurement kernel. Applying that admission probability again would select the population twice.

The angular footprint, mask, and admitted catalogue remain **fixed throughout a fit**. Changing the fitted centre must not add or remove observations. A finder may define the initial patch, but a trial parameter value does not redefine the experiment.

## A compact primary seen through broad PDZs {#primary-pdz}

Let \(\omega\) denote sky position, \(z\) latent cosmological redshift, and \(w(\omega)\) fixed angular coverage. Write the selected intensity per \(d\omega\,dz\) as

\[
\Lambda_R(\omega,z)=w(\omega)
\left[\lambda U(\omega;\theta)g_P(z;\theta)+B(\omega,z)\right],
\label{eq:primary-external}
\]

where \(B\) is the external intensity before angular coverage, \(\int g_P\,dz=1\), and

\[
U(\omega;\theta)=
\frac{\widetilde U(\omega;\theta)}
{\int_\Omega w(\omega')\widetilde U(\omega';\theta)\,d\omega'},
\qquad \int_\Omega wU\,d\omega=1.
\label{eq:primary-normalization}
\]

This defines \(\lambda\) precisely: **the expected number of admitted primary galaxies in the fixed covered footprint**. If the centre or scale changes, the denominator changes; the footprint does not. Richness in a standardized physical aperture, or above a standardized luminosity threshold, would be a different observable requiring an explicit conversion and its uncertainty.

The primary’s angular shape can be obtained by projecting an NFW-like galaxy number-density profile with an integrable outer truncation.[^nfw] For comoving radius \(r\), projected comoving separation \(R\), and comoving distance \(\chi_*\),

\[
\begin{aligned}
n_P(r)&\propto
\frac{T(r)}{(r/r_s)(1+r/r_s)^2},\\
\Sigma_P(R)&=2\int_R^\infty
\frac{n_P(r)r}{\sqrt{r^2-R^2}}\,dr,\\
\widetilde U(\omega;\theta)&\propto
\chi_*^2\Sigma_P\!\left(\chi_*\vartheta(\omega,\omega_*)\right).
\end{aligned}
\label{eq:projection}
\]

The factor \(\chi_*^2\) converts projected comoving area into solid angle; normalization then removes the arbitrary profile amplitude. Here \(r_s\) and the truncation describe **galaxies**, not a measured dark-matter profile. 

A compact primary is thin compared with broad photometric-distance errors, suggesting \(g_P(z;\theta)\simeq\delta_D(z-z_*)\). This is a latent-depth approximation, not a claim that all measured redshifts coincide. Peculiar velocities belong in the observation kernel: in a more complete treatment, a native likelihood is averaged over \(z_{\rm spec}\simeq z+(1+z)v_\parallel/c\). Neglecting that convolution is justified only when the relevant PDZ features are broad compared with both the primary’s depth and velocity-induced redshift spread. It must be revisited for spectroscopy or unusually narrow PDZ modes.

### A PDZ is not automatically a likelihood

For one galaxy with photometric data \(d_i\), write \(\mathcal S\) for catalogue admission. A source photo-z posterior obeys

\[
p_{{\rm src},i}(z\mid d_i,\mathcal S)
=\frac{\ell_i(z)\,\pi_{{\rm src},i}(z\mid\mathcal S)}{Z_{{\rm src},i}},
\qquad
\ell_i(z)\propto
\frac{p_{{\rm src},i}(z\mid d_i,\mathcal S)}{\pi_{{\rm src},i}(z\mid\mathcal S)}.
\label{eq:pdz-likelihood}
\]

The source prior may depend on magnitude, type, or other conditioning information. Dividing it out recovers a usable likelihood only with matching support, selection, and nuisance-variable marginalization. An implicit or unknown prior, clipped tails, or an incompatible spectral-type mixture cannot be repaired by relabelling a PDF “the likelihood.” This is the same issue that arises when combining individual photo-z posteriors into a population-level redshift inference.[^pdz]

For clarity, the equations below assume that \(\ell_i(z)\) represents a calibrated, admission-conditioned measurement likelihood usable for both populations, up to a factor independent of all fitted quantities. That is a substantive compression assumption. A red primary population and a mixed external population may require explicit luminosity/type marks or different marginalized kernels. Photometry already used in a PDZ must not be multiplied in again as independent colour evidence.

Under these assumptions, the event responses are

\[
\begin{aligned}
\nu_i^P&=w_i\lambda U_i\int g_P(z;\theta)\ell_i(z)\,dz
\simeq w_i\lambda U_i\ell_i(z_*),\\
\nu_i^E&=w_i\int B(\omega_i,z)\ell_i(z)\,dz.
\end{aligned}
\label{eq:event-responses}
\]

This expresses the asymmetry directly. The thin primary tests the evidence near one common redshift. The environment integrates its competing intensity along the entire uncertain sightline. A secondary PDZ mode can support an external structure even when the highest PDZ peak lies near the candidate.

Most importantly, the likelihood contribution of this object is \(\log(\nu_i^P+\nu_i^E)\): **integrate over its unknown distance, add the possible origins, then take one logarithm**. It is not \(\int p_i(z)\log\Lambda_R(\omega_i,z)\,dz\), and it is not a product of independent fractional observations. Those alternatives perform different statistical operations.

We now have a meaningful primary and a correct place for its PDZs. What remains is to specify \(B\).

## A halo is not a random place in the Universe {#conditional-mean}

A homogeneous external reference is a useful baseline: \(B(\omega,z)=\rho_R(z)\), where \(\rho_R\) is the selected number per unit solid angle and redshift, before angular coverage. “Homogeneous” here means no extra angular structure, not a flat redshift distribution. If instead the reference were supplied per comoving volume, the conversion would be \(\rho_R(z)=\bar n_R(z)\chi^2(z)c/H_{\rm cos}(z)\) in a flat geometry. A reference already expressed per \(d\omega\,dz\) must not receive that Jacobian twice.

However, a halo-centred aperture is not a randomly centred aperture. Halos trace large-scale structure, and finite halo sizes affect which neighbouring centres can occur nearby. The catalogue lets us inspect these two statements without first running the refinement model.

<!-- FIGURE:profiles -->

The projected galaxy census uses 339 interior centres with adopted physical mass \(M\geq10^{14}M_\odot\) and \(0.4\leq z_h<1\); the default view restricts this to **162 halos** with \(M<3\times10^{14}M_\odot\) and \(0.5\leq z_h<0.8\). For each centre, logarithmic annuli extend from \(0.1\) to \(5r_{\rm vir}\). Galaxies lie in a redshift-space cylinder with half-depth \(20\,h^{-1}\) comoving Mpc around the central galaxy’s observed redshift. For population \(a\),

\[
\Sigma_{h,j}^{a}=
\frac{N_{h,j}^{a}}
{\pi r_{{\rm vir},h}^{\,2}(x_{j+1}^2-x_j^2)},
\qquad
\overline\Sigma_j^{a}=\frac{1}{N_h}\sum_h\Sigma_{h,j}^{a},
\quad x=R/r_{{\rm vir},h}.
\label{eq:profile-estimator}
\]

Total, primary-host, and other-host counts use exactly the same cylinder and annulus; hence their decomposition is exact for these selected rows. The reference uses twelve random angular centres per halo with the same radius, redshift, and boundary requirement. Curves are equal-halo means, not a pooled count divided by a pooled area. The external band is the 16th–84th percentile spread **across halos**, not an error on the mean.

The external surface density is not zero in the projected core. In the default sample it remains elevated relative to matched random sightlines, and that excess persists toward \(5r_{\rm vir}\). There is substantial variation between environments. Both are directly relevant to modelling a primary against a non-uniform external population.

The second view uses a different observable: **other central galaxies placed at their host’s true redshift**, giving a three-dimensional halo-centre proxy. It reveals a strongly depleted inner region and an enhanced surrounding population. This does not manufacture real-space satellite coordinates: those are absent from the export. The centre diagnostic and the projected galaxy diagnostic are deliberately not presented as the same profile.

The distinction matters physically. Halo-centre exclusion concerns separations of finite hosts; external galaxies are those hosts’ spatially extended tracers. Projection then includes foreground and background galaxies even at zero projected separation. Moreover, Flagship assigns some satellites beyond their host’s virial radius, so a radial cut is not equivalent to a host label.[^flagship] Neither a central hole in the image nor a sharp galaxy boundary at \(r_{\rm vir}\) follows from halo exclusion.

### The conditional mean

The appropriate ensemble is the environment seen from a halo of the relevant class. In point-process language this is halo Palm conditioning. Let \(\bar n_h\) be the density of conditioning halos, and let \(\rho_{hE}^{(2)}(0,x)\) count halo–galaxy pairs **only when the galaxy belongs to another host**. Then

\[
\overline\Lambda_E(x\mid h_0)
=\frac{\rho_{hE}^{(2)}(0,x)}{\bar n_h}
=\bar n_g[1+\xi_{hE}(x)].
\label{eq:palm-mean}
\]

The ratio follows by counting pairs with the halo in an infinitesimal volume and dividing by the expected number of halos there. Crucially, a full halo–galaxy correlation also contains the primary’s own galaxies. Adding a separate primary profile to that full mean would double-count them. Reduced Palm removal of the conditioning point is not a substitute for removing its host’s galaxy population.[^palm]

On large scales, the correlated external excess admits a bias approximation. A tractable prescription is

\[
\begin{aligned}
B_{\rm mean}(\omega,z;\theta)&=\rho_R(z)H(r;\theta),\\
H(r;\theta)&=E_{\rm eff}(r;\theta)
\left[1+b_h(M_{\rm fid},z_*)b_g(z_*)D^2(z_*)\xi_L(r,0)\right],\\
r^2&=\chi^2(z)+\chi_*^2-2\chi(z)\chi_*\cos\vartheta.
\end{aligned}
\label{eq:environment-mean}
\]

Distances are comoving, \(D(0)=1\), and \(\xi_L\) is the linear matter correlation. The contribution from galaxies in other halos is commonly called the two-halo contribution; it is an ensemble term, not a literal fit to one second halo.[^halo]

Here \(E_{\rm eff}\) is an **effective galaxy-level suppression**, not the halo-centre exclusion curve pasted into a galaxy model. It should approach one far from the primary and be calibrated with consistent host definitions, tracer selection, and distance coordinates. Multiplying the full bracket suppresses the reference density as well as the excess. But setting it exactly to zero is a strong modelling restriction: no subsequent multiplier can restore external intensity there. The complete \(H\) must remain nonnegative and integrable on the fitted domain.

The fiducial mass controls a calibration of the environment, not a mass inferred by the galaxy-profile fit. Its uncertainty, the bias calibration, and the suppression scale warrant sensitivity tests or explicit nuisance parameters. The linear-bias expression is asymptotic; continuing it through the nonlinear halo boundary with an effective suppression is an approximation to be tested, not a derivation of the transition.

## The average environment is not this environment {#cox}

Replacing a constant background with a conditional mean solves one problem: the mean is now associated with a halo. It leaves another untouched. A particular halo can have a neighbouring group or filament where the ensemble mean has only a smooth enhancement.

Instead of treating the intensity as fixed, draw a positive external field and then draw the galaxies conditional on it:

\[
B(\omega,z;\theta,F)=\rho_R(z)H(\omega,z;\theta)F(\omega,z),
\qquad F>0,\qquad \mathbb E[F\mid\theta]=1.
\label{eq:cox-field}
\]

This is a Cox construction. The multiplier modulates the external population; it is not a third galaxy population added to primary and environment. Conditional Poisson sampling remains possible even though the marginal catalogue is correlated.

For cells with fixed primary expectations \(p_j\) and mean external expectations \(c_j\), suppose the retained field factor is constant within each cell. Then

\[
\begin{aligned}
N_j\mid F&\sim\operatorname{Poisson}(p_j+c_jF_j),\\
\mathbb E[N_j]&=p_j+c_j,\\
\operatorname{Cov}(N_j,N_k)
&=\delta_{jk}(p_j+c_j)+c_jc_kK_{jk},
\qquad K_{jk}=\operatorname{Cov}(F_j,F_k).
\end{aligned}
\label{eq:count-covariance}
\]

This follows from total covariance: average the conditional Poisson covariance, then add the covariance of the conditional means. In one cell, \(\operatorname{Var}N=\mathbb E\mu+\operatorname{Var}\mu\). The first term is discrete sampling; the second is variation of the underlying intensity. Shared field modes also correlate disjoint cells.

The environmental spread in the stack motivates asking for this second contribution, but does **not** directly estimate \(K\). The stack still mixes mass and redshift within bins, includes Poisson noise, and contains overlapping neighbourhoods in one limited sky region. A calibrated conditional covariance must separate those contributions and account for the chosen windows. In particular, shot noise estimated from galaxy counts must not be inserted into the field covariance and then counted a second time in the Poisson likelihood.

The added freedom is useful only if it has a meaningful probability law. Otherwise the environment could absorb the primary itself.

## Restrict competing explanations, not just negative densities {#field-prior}

The attribution ambiguity is already visible in \(I=\lambda u+B\). Wherever the model allows the exchange

\[
\lambda' = \lambda-\Delta,\qquad B'=B+\Delta u,
\qquad I'=I,
\label{eq:attribution}
\]

the complete likelihood—including its expected-count term—is unchanged. The data distinguish total intensity, not automatically its decomposition. Exclusion, profile geometry, distance information, and the field prior must constrain which competing decompositions are possible and plausible.

A lognormal multiplier provides positivity without imposing an artificial upper bound. On a finite set of represented cells, take

\[
G\sim\mathcal N(0,C),\qquad
F_j=\exp\!\left(G_j-\tfrac12 C_{jj}\right).
\label{eq:lognormal}
\]

The Gaussian moment identity \(\mathbb E[e^{t^TG}]=e^{t^TCt/2}\) immediately gives

\[
\mathbb E[F_j]=1,\qquad
\mathbb E[F_jF_k]=e^{C_{jk}},\qquad
K_{jk}=e^{C_{jk}}-1.
\label{eq:lognormal-moments}
\]

Subtracting half the variance prevents fluctuations from silently increasing the mean environment. It normalizes an **ensemble**, not each realized patch. Forcing every patch’s average multiplier to one would define a different prior and remove some genuine large-scale count variation. Lognormal–Poisson inference has established applications to large-scale structure; here it represents residual external variation around a separately specified conditional mean.[^jasche]

### Which spatial patterns should be cheap?

The covariance determines which departures from the mean are plausible. In an eigenmode of \(C\) with positive variance \(\kappa\), a log-field amplitude \(g\) contributes \(g^2/(2\kappa)\) to the negative log prior. Large prior variance makes a competing pattern inexpensive; zero variance removes the mode from the support. “Smooth” is therefore not a complete specification of the field, and positivity alone provides no protection against attributing a cluster-like feature to the environment.

To relate the represented freedom to physical scales, choose normalized real-space windows \(W_j\), including the intended angular and radial averaging. A spectrum-informed candidate covariance—not yet a halo-conditioned calibration—comes from an equal-time matter field and cell-dependent tracer biases:

\[
\begin{aligned}
\delta_j&=b_j\int W_j(x)\delta_m(x)\,d^3x,\qquad \int W_j\,d^3x=1,\\
K^{\rm spec}_{jk}&=b_jb_k\int\frac{d^3k}{(2\pi)^3}
P_m(k)\widetilde W_j(\mathbf k)\widetilde W_k(\mathbf k)^*.
\end{aligned}
\label{eq:cell-covariance}
\]

The power spectrum sets mode amplitudes; the windows specify which modes the finite representation retains. For any real vector \(a\), the quadratic form is the integral of \(P_m\left|\sum_j a_jb_j\widetilde W_j\right|^2\), and is nonnegative when \(P_m\geq0\). Thus this construction gives a positive-semidefinite covariance when the integrals exist.

A lightcone additionally requires redshift evolution. One practical approximation replaces the unequal-time spectrum by \(P(k;z,z')\simeq\sqrt{P_{\rm NL}(k,z)P_{\rm NL}(k,z')}\). It leads to a Gram representation

\[
\begin{aligned}
\Psi_j(\mathbf k)&=\int d^3x\,W_j(x)b_g(z)
\sqrt{P_{\rm NL}(k,z)}e^{-i\mathbf k\cdot x},\\
K^{\rm spec}_{jk}&\simeq\int\frac{d^3k}{(2\pi)^3}
\Psi_j(\mathbf k)\Psi_k(\mathbf k)^*.
\end{aligned}
\label{eq:lightcone-covariance}
\]

This preserves positive semidefiniteness, but assumes perfect unequal-time coherence at fixed mode and uses an approximate relation between galaxy and matter fluctuations. It is not a measured halo-conditioned covariance. Angular pixels, selected radial windows, bias, and resolution belong in its calibration. Individual galaxies’ PDZs belong in the observation likelihood, not as a universal extra smoothing of this latent prior. Convolving the prior too would change the model and can double-count distance uncertainty.

### Moment matching is a model choice, not an identity

If \(K\) is the desired finite-cell fractional covariance, the lognormal moments suggest the **entrywise** transformation

\[
C_{jk}=\log(1+K_{jk}).
\label{eq:moment-match}
\]

Every entry must exist and the resulting \(C\) must be positive semidefinite. The latter does not follow from \(K\succeq0\): for \(K=\left(\begin{smallmatrix}1&2\\2&4\end{smallmatrix}\right)\), the transformed determinant is \((\log2)(\log5)-(\log3)^2<0\). A covariance adjustment or mode truncation therefore changes the requested moments and must be recorded and tested. Alternatively, start from a valid parametric \(C\) and calibrate the implied \(e^C-1\), rather than claiming exact moment matching.

An average of lognormal variables is generally not lognormal. The consistent interpretation is a finite-cell approximation to selected moments, not “average a continuous field and exponentiate” as an exact operation. With a retained loading \(G=L\epsilon\), \(\epsilon\sim\mathcal N(0,I)\), the variance subtraction must use \((LL^T)_{jj}/2\), the variance actually represented.

Coarse cells or a restrictive covariance can force external structure into the primary; excessive small-scale freedom can support the reverse attribution. Resolution and prior calibration are therefore scientific sensitivity questions. A prior is not made identifiable merely by being physically motivated.

## How much does halo conditioning actually establish? {#conditioning-limits}

The conditional mean has an exact Palm interpretation. It does not follow that an unconditional matter spectrum supplies the correct conditional residual covariance.

For distinct external galaxies at \(x\) and \(y\), their pair intensity around a halo depends on a mixed three-point product density, \(\rho_{hEE}^{(3)}(0,x,y)/\bar n_h\). Expanding its connected correlations gives the fractional conditional pair excess

\[
K_h(x,y)=
\frac{\xi_{EE}(x-y)+\zeta_{hEE}(0,x,y)-\xi_{hE}(x)\xi_{hE}(y)}
{[1+\xi_{hE}(x)][1+\xi_{hE}(y)]}.
\label{eq:conditional-covariance}
\]

The expression follows by subtracting the product of the two conditional means from the conditional pair intensity, then dividing by that product. Every moment must use the same primary-host exclusion. Under a suitable conditional Cox representation this is the fractional intensity covariance at distinct points; Poisson sampling contributes a separate diagonal term to count covariance. Where the conditional mean vanishes, use absolute moments instead of dividing by it.

The mixed three-point function \(\zeta_{hEE}\) is not determined by an ordinary two-point matter spectrum. This is why prescribing an excluded mean and a spectrum-informed residual field is a **conditional closure**: a tractable approximation to a more complicated joint distribution.

There is an exact special case that explains why the factorization is attractive. Suppose halo centres and external tracers are conditionally Poisson processes driven by jointly Gaussian log-fields \(Y\sim\mathcal N(0,C)\). Observing a halo reweights the field law by its halo intensity. Completing the square shows that

\[
e^{t^TY-\frac12t^TCt}\,p(Y)
=\mathcal N(Y;Ct,C).
\label{eq:gaussian-tilt}
\]

Choosing \(t\) to select the halo log-field shifts the external log-field mean by \(C_{Eh}(x,0)\) while leaving its Gaussian covariance unchanged. The conditional intensity consequently factors into

\[
\Lambda_E(x\mid h_0)\ \overset{d}{=}
\bar n_g e^{C_{Eh}(x,0)}
\exp\!\left(G_E(x)-\tfrac12 C_{EE}(x,x)\right).
\label{eq:tilted-intensity}
\]

The reduced-Palm theorem for a single log-Gaussian Cox process establishes the corresponding result rigorously; the expression here uses the stated multitype extension.[^lgcp] The unchanged quantity is the Gaussian covariance, hence the **fractional** intensity covariance. The absolute covariance still scales with the changed conditional means.

Our practical \(H\) is not \(e^{C_{Eh}}\) derived from a jointly calibrated Gaussian system. In particular, finite Gaussian cross-covariance cannot produce a hard-zero mean. Neither halo exclusion nor the full galaxy occupation law is established by this theorem. The model retains the useful mean-times-residual structure while explicitly giving up an exact joint halo–galaxy construction.

## One joint refinement pipeline {#joint-inference}

We can now collect the pieces without changing the experiment:

\[
\Lambda_R(\omega,z;\theta,G)=w(\omega)
\left[\lambda U(\omega;\theta)\delta_D(z-z_*)
+\rho_R(z)H(\omega,z;\theta)e^{G(\omega,z)-\frac12\operatorname{Var}G(\omega,z)}\right].
\label{eq:final-intensity}
\]

The primary contributes exactly \(\lambda\) to the selected expected count. If the multiplier is constant in field cell \(V_j\), define

\[
c_j(\theta)=\int_{V_j}w(\omega)\rho_R(z)H(\omega,z;\theta)\,d\omega\,dz,
\qquad
\mu_E(\theta,G)=\sum_j c_j(\theta)F_j.
\label{eq:compensator}
\]

The reference and mean remain inside the cell integral; a constant multiplier does not make either of them constant. All primary, environmental, and count terms are evaluated at the same joint state. Moving the primary changes its normalized profile and can also change the mean external explanation.

### A direct interpretation of reference-weighted PDZs

The event integrals become especially transparent after a fixed reference normalization. From the compatible native likelihood define

\[
Z_i=\int\rho_R(z)\ell_i(z)\,dz,
\qquad
q_i(z)=\frac{\rho_R(z)\ell_i(z)}{Z_i}.
\label{eq:reference-pdz}
\]

Thus \(q_i\) is a normalized redshift distribution **under the selected reference population**. It is not automatically the source PDZ. It is obtained by removing the source prior and applying the chosen reference, not by applying two priors to the same photometry.

Dividing both event responses by the same fixed \(w_iZ_i\) gives

\[
\begin{aligned}
a_i^P(\theta)&=\lambda U_i\,
\frac{q_i(z_*)}{\rho_R(z_*)},\\
a_i^E(\theta,G)&=\int q_i(z)H(\omega_i,z;\theta)F(\omega_i,z)\,dz,\\
\log L(\theta,G)&=\sum_i\log(a_i^P+a_i^E)-\lambda-\mu_E(\theta,G)+\mathrm{const}.
\end{aligned}
\label{eq:reference-likelihood}
\]

The thin primary response requires \(\rho_R(z_*)>0\) on its prior support. Its finite-depth replacement is \(\lambda U_i\int g_P(z)q_i(z)/\rho_R(z)\,dz\). In a homogeneous external model, \(H=F=1\) and \(a_i^E=1\); the primary is an excess relative to that reference. With structure, the external response is the **PDZ expectation of the environmental enhancement**. These expressions preserve every PDZ mode without assigning an object to a best redshift.

<!-- FIGURE:response -->

The dropped factors are independent of every inferred quantity. They change the event log likelihood only by a constant and cancel in allocation ratios; they do **not** rescale the physical expected-count term. If the reference or PDZ calibration is itself inferred, that dependence must instead be retained consistently.

A local field grid need not cover all PDZ support, but the remaining support needs an explicit external explanation—for example, a fixed reference outside the active grid, with both its event response and count integral included. Renormalizing each PDZ into a narrow candidate window would artificially turn distant probability into evidence for the candidate. A real redshift-dependent admission cut must likewise be represented in the selection model, not introduced by a trial fit.

Priors on the primary and Gaussian field complete the posterior,

\[
p(\theta,G\mid D)\propto L(\theta,G)p(\theta)p(G\mid\theta),
\qquad
p(\theta\mid D)=\int p(\theta,G\mid D)\,dG.
\label{eq:posterior}
\]

A covariance that depends on fitted parameters carries its normalization with it; in a white-driver representation that dependence belongs in the loading and the generative transformation. The inferential objective is marginalization over plausible environments, not optimization of one external map followed by treating that map as known.

### Membership and richness answer different questions

Superposition of the primary and external Poisson processes gives, at a fixed joint state, the primary allocation probability

\[
a_i(\theta,G)=\frac{a_i^P}{a_i^P+a_i^E},
\qquad
p_i^P=\mathbb E_{\theta,G\mid D}[a_i(\theta,G)].
\label{eq:membership}
\]

The ratio is formed **before** posterior averaging. A ratio of separately averaged intensities generally gives a different answer. Membership is therefore an inference output, not a clean list supplied to the fit. Probabilistic membership itself has established observational validation in existing cluster catalogues; the calibration of these particular probabilities would need its own tests.[^membership]

For the assigned primary count in this observed catalogue,

\[
\begin{aligned}
\mathbb E[N_P^{\rm assign}\mid D]&=\sum_i p_i^P,\\
\operatorname{Var}(N_P^{\rm assign}\mid D)
&=\mathbb E\!\left[\sum_i a_i(1-a_i)\mid D\right]
+\operatorname{Var}\!\left(\sum_i a_i\mid D\right).
\end{aligned}
\label{eq:assigned-count}
\]

The first term is conditional label uncertainty; the second is shared uncertainty in the cluster and environment. A **new** primary catalogue instead has \(N_P^{\rm rep}\mid\lambda\sim\operatorname{Poisson}(\lambda)\), with posterior predictive variance \(\mathbb E[\lambda\mid D]+\operatorname{Var}(\lambda\mid D)\). The generating selected richness, an allocation of existing observations, and a replicated count are not interchangeable truth targets.

The same construction can retain galaxy populations as marks. Population-specific primary profiles, references, and measurement kernels then enter additively. Shared Gaussian drivers provide explicit cross-population environmental covariance; assuming shared drivers is a particular dependence model, not an estimate of an arbitrary cross-covariance.

In operational terms, the pipeline is:

| Stage | Quantity that must remain explicit |
| --- | --- |
| Propose candidates | Finder outputs and the observations used to select them; no claim of confirmed membership. |
| Freeze the local experiment | Footprint, mask, flux admission, PDZ support, and target richness definition. |
| Construct the forward model | Primary projection and normalization, selected reference, conditional mean, residual covariance, and compatible PDZ likelihoods. |
| Infer jointly | Primary parameters and external field, with all event and expected-count terms evaluated together. |
| Report and calibrate | Marginal primary posteriors, allocation probabilities, predictive diagnostics, and the survey-level detection-and-measurement response. |

## What the model still has to earn {#validation}

The catalogue diagnostics support the need to distinguish a primary, a conditional mean environment, and environmental variation. They do not establish that this particular closure improves parameter recovery or produces calibrated uncertainties. **This article presents a model derivation and empirical mock diagnostics, not a completed validation of the refinement pipeline.** Establishing improved recovery and calibrated uncertainty requires repeated-fit experiments with compatible truth targets.

The cleanest test is a factorial comparison on exactly the same selected data and target observable:

| Model | Environmental mean | Residual multiplier |
| --- | --- | --- |
| Homogeneous baseline | \(H=1\) | \(F=1\) |
| Conditional mean only | Calibrated \(H\) | \(F=1\) |
| Stochastic, unconditioned | \(H=1\) | Random \(F\) |
| Full conditional model | Calibrated \(H\) | Random \(F\) |

Hold the primary family, catalogue, mask, reference, priors, and estimand fixed. In-model simulations can test recovery of generating parameters and numerical inference. Misspecified mocks should vary the primary’s shape, centre, environment, field resolution, photo-z tails and aliases, source-prior calibration, and selection. Coverage tests require repeated datasets with compatible truth. The 183 labelled primary galaxies in the scene are a realized count in a cut, not a supplied generating value of \(\lambda\).

For real-mock membership tests, host labels provide a useful allocation truth. Reliability curves, contamination versus projected radius and PDZ ambiguity, and joint centre–richness errors address different failure modes. Posterior predictive checks should confront **raw observed** angular counts and measurement distributions; a membership-weighted profile already depends on the fitted attribution and is not an independent validation of it. The conditional Poisson law should itself be tested: an explicit central-plus-satellite occupation model need not have Poisson counts even at fixed environment. The mock’s built-in galaxy placement also means that agreement with an NFW-like profile is not independent evidence that real galaxies follow that family.[^flagship]

### A known halo is not a finder-selected candidate

Halo Palm conditioning assumes a halo. A finder conditions on an observed pattern, possibly including a false detection. In particular, setting \(\lambda=0\) while retaining a halo-conditioned \(H\) is not a genuine no-halo model: the environment still assumes the halo. Calibrated existence probabilities require a distinct null model and the appropriate selection treatment.

Data reuse also needs care. A finder’s redshift summary, computed from these same PDZs, is not an independent prior measurement. Using it to initialize a fit is different from multiplying its likelihood into the fit again. If selection is a deterministic function of the **fully retained** data, conditioning on that selection adds no information to an already conditioned object posterior. Truncating the data to a local patch, or modelling a selected population, changes the bookkeeping. One cannot insert or omit a detection-efficiency factor indiscriminately; the likelihood and population prior must refer to the same selection experiment.

This returns us to cosmology. A refined richness is valuable only with a calibrated relation to mass and a response that includes how objects entered the catalogue. Environmental flexibility may make an individual posterior wider rather than narrower. That is not necessarily a loss of information: it can be the removal of unjustified certainty.

**The objective is not to make every overdensity look like a clean cluster. It is to identify which conclusions about the primary survive plausible explanations of the galaxies around it.**

## Data and reproducibility {#data}

The working catalogue, `flagship_hp4x2.csv.gz`, contains **4,997,763 rows and 21 columns**. With the adopted cgs flux convention, every row satisfies \(H_{\rm AB}=-2.5\log_{10}f_\nu-48.6<24\). Its nested order-29 HEALPix identifiers map to order-4 pixels 702 and 703, an adopted footprint of 26.8574 square degrees. The analysis assumes these pixels are complete and have no internal mask; the export does not include its selection query or a survey completeness model. The magnitude cut is Euclid-Wide-like, not a full Euclid observing simulation.

We adopt \(h=0.67\), \(\Omega_m=0.319\), and a flat matter-plus-\(\Lambda\) distance calculation for the illustrations, omitting the small separate radiation/neutrino terms in the published simulation cosmology.[^flagship] The catalogue’s usual mass convention is taken to be \(\log_{10}[M/(h^{-1}M_\odot)]\), so the physical mass cut is \(\mathrm{lm\_halo}\geq\log_{10}(0.67\times10^{14})\), not simply 14. We interpret `rvir_halo` as comoving \(h^{-1}\) kpc. The export has no unit header: this radius convention is supported by an internal virial mass–radius–redshift consistency check, not asserted to be independently verified metadata. These adopted conventions and their checks are recorded with the data products.

All profile apertures pass a conservative boundary check at \(5.05r_{\rm vir}\). The galaxy profiles use projected annular areas, not spherical shell volumes; the separate halo-centre diagnostic uses shell volumes and a central-galaxy density reference measured in \(z_h\pm0.025\). Neither its reference uncertainty nor the dependence of overlapping apertures is included in an error on the mean. No such error is claimed.

The interactive scene stores the fixed angular sample, host labels, and synthetic measurement parameters; it does not replace a missing PDZ catalogue with undocumented point estimates. The response explorer uses a smoothed redshift reference from this mock and an explicitly illustrative external enhancement, not a fitted environment or posterior membership. Full selections, seeds, checksums, per-halo counts, and figure specifications accompany the article.

[Article source](../content/measuring-a-galaxy-cluster.md) · [Data provenance](../assets/cluster/provenance.json) · [Per-halo profile measurements](../assets/cluster/profiles-per-halo.csv) · [Fixed scene](../assets/cluster/scene.csv) · [Analysis code](../tools/analyse_flagship.py) · [Figure generator](../tools/make_figures.py)

The Flagship mock and the CosmoHub infrastructure should be credited when reusing these illustrations.[^flagship][^cosmohub] This work has made use of CosmoHub, developed by PIC (maintained by IFAE and CIEMAT) in collaboration with ICE-CSIC, with support from the Spanish government, the EU NextGeneration/PRTR programme, and the Generalitat de Catalunya.

[^cosmology]: S. W. Allen, A. E. Evrard & A. B. Mantz (2011). *Cosmological Parameters from Observations of Galaxy Clusters*. Annual Review of Astronomy and Astrophysics 49, 409–470. [arXiv:1103.4829](https://arxiv.org/abs/1103.4829). Cosmological motivation, mass calibration, and selection.
[^projection]: M. Costanzi et al. (2019). *Modelling projection effects in optically selected cluster catalogues*. MNRAS 482, 490–505. [doi:10.1093/mnras/sty2665](https://academic.oup.com/mnras/article/482/1/490/5114581). Projection effects in the richness response.
[^redmapper]: E. S. Rykoff et al. (2014). *redMaPPer. I. Algorithm and SDSS DR8 Catalog*. ApJ 785, 104. [arXiv:1303.3562](https://arxiv.org/abs/1303.3562).
[^amico]: F. Bellagamba, M. Roncarelli, M. Maturi & L. Moscardini (2018). *AMICO: optimised detection of galaxy clusters in photometric surveys*. MNRAS 473, 5221–5236. [arXiv:1705.03029v2](https://arxiv.org/html/1705.03029v2), especially the local-background and membership sections.
[^cfc]: Euclid Collaboration, R. Adam et al. (2019). *Euclid preparation. III. Galaxy cluster detection in the wide photometric survey, performance and algorithm selection*. A&A 627, A23. [arXiv:1906.04707v3](https://arxiv.org/html/1906.04707v3). Published comparison of detection approaches, including PZWav’s use of full PDZs.
[^palm]: J.-F. Coeurjolly, J. Møller & R. Waagepetersen (2017). *A tutorial on Palm distributions for spatial point processes*. International Statistical Review 85, 404–420. [arXiv:1512.05871](https://arxiv.org/abs/1512.05871).
[^nfw]: J. F. Navarro, C. S. Frenk & S. D. M. White (1997). *A Universal Density Profile from Hierarchical Clustering*. ApJ 490, 493–508. [arXiv:astro-ph/9611107](https://arxiv.org/abs/astro-ph/9611107). Origin of the dark-matter profile family; using it for galaxies is a separate modelling assumption.
[^pdz]: A. I. Malz & D. W. Hogg (2022; preprint 2020). *How to obtain the redshift distribution from probabilistic redshift estimates*. ApJ 928, 127. [arXiv:2007.12178](https://arxiv.org/abs/2007.12178). The source-prior issue in downstream inference from photo-z PDFs.
[^flagship]: Euclid Collaboration, F. J. Castander et al. (2025). *Euclid. V. The Flagship galaxy mock catalogue: a comprehensive simulation for the Euclid mission*. A&A 697, A5. [arXiv:2405.13495](https://arxiv.org/html/2405.13495v1). Simulation cosmology, host-centred galaxy placement, and mock construction; not evidence of refinement-pipeline performance.
[^halo]: M. Asgari, A. J. Mead & C. Heymans (2023). *The halo model for cosmology: a pedagogical review*. The Open Journal of Astrophysics 6. [arXiv:2303.08752v2](https://arxiv.org/html/2303.08752v2), especially halo bias and exclusion.
[^jasche]: J. Jasche, F. S. Kitaura, C. Li & T. A. Enßlin (2010). *Bayesian non-linear large scale structure inference of the Sloan Digital Sky Survey data release 7*. MNRAS 409, 355–370. [arXiv:0911.2498](https://arxiv.org/abs/0911.2498).
[^lgcp]: J.-F. Coeurjolly, J. Møller & R. Waagepetersen (2017). *Palm distributions for log Gaussian Cox processes*. Scandinavian Journal of Statistics 44, 192–203. [arXiv:1506.04576v4](https://arxiv.org/html/1506.04576v4), Theorem 1.
[^membership]: E. Rozo, E. S. Rykoff, M. Becker, R. M. Reddick & R. H. Wechsler (2015). *redMaPPer IV: Photometric Membership Identification of Cluster Galaxies with 1% Precision*. MNRAS 453, 38–52. [arXiv:1410.1193](https://arxiv.org/abs/1410.1193).
[^cosmohub]: P. Tallada et al. (2020). *CosmoHub: Interactive exploration and distribution of astronomical data on Hadoop*. Astronomy and Computing 32, 100391. [doi:10.1016/j.ascom.2020.100391](https://doi.org/10.1016/j.ascom.2020.100391).
