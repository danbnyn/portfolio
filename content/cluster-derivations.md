# Cluster refinement: derivations and assumptions

This is the mathematical companion to [Measuring a galaxy cluster in a crowded Universe](measuring-a-galaxy-cluster.html). It separates identities derived from an assumed probability law from approximations used to describe the astrophysics, and from conventions specific to the model design.

The point-process and Palm framework follows Coeurjolly, Møller and Waagepetersen.[^palm][^lgcp] The finite-dimensional calculations below are explicit consequences of the stated assumptions. Halo-model terminology and exclusion context follow Asgari, Mead and Heymans.[^halo] None of these calculations is a numerical validation of the refinement pipeline.

<aside class="article-note"><p><strong>Status of the specification.</strong> This note describes the model and the conventions recorded in the project’s design notes. It is not an independent verification of inference code, calibration products, or saved posterior samples. Generic teaching constructions are identified as such; in particular, the truncation law and the literal survey covariance calculation are not reconstructed here.</p></aside>

## A. From intensities to a point-process likelihood {#point-process}

Let \(W\) be a fixed bounded observation region with a non-atomic coordinate measure \(dx\). Assume \(\Lambda(x)\geq0\) and \(\mu_W=\int_W\Lambda(x)\,dx<\infty\). A Poisson point process specifies independent counts in disjoint measurable regions:

\[
N(A_j)\mid\Lambda\sim\operatorname{Poisson}(\mu_j),
\qquad \mu_j=\int_{A_j}\Lambda(x)\,dx.
\label{eq:a-counts}
\]

For a finite partition, multiply the probabilities:

\[
P(\{N_j\}\mid\Lambda)=
\exp\!\left(-\sum_j\mu_j\right)
\prod_j\frac{\mu_j^{N_j}}{N_j!}.
\label{eq:a-partition}
\]

Under the usual simple-process and local regularity assumptions, cells can be made small enough to isolate the finite set of realized points almost surely. For a cell containing \(x_i\), \(\mu_j\simeq\Lambda(x_i)|A_j|\). The cell-volume and ordering factors are independent of the parameters. Relative to a fixed reference measure on point configurations, the likelihood is therefore

\[
L(\Lambda;D)\propto
\exp\!\left[-\int_W\Lambda(x)\,dx\right]
\prod_{i=1}^{N}\Lambda(x_i).
\label{eq:a-ppp}
\]

Equivalently, draw \(N\sim\operatorname{Poisson}(\mu_W)\), then, conditional on \(N\), draw positions independently with density \(\Lambda/\mu_W\). Multiplying the count probability and position densities gives the same result, up to the convention for labeling the points. This second argument makes clear what would be lost by conditioning away the total count.

### Random intensity, not merely nonuniform intensity

A deterministic inhomogeneous intensity remains Poisson. If the intensity is random and the catalogue is Poisson conditional on it, the marginal process is Cox. Assume the required second moments exist. For \(\mu_A=\int_A\Lambda\),

\[
\begin{aligned}
\mathbb E[N(A)]&=\mathbb E[\mu_A],\\
\operatorname{Var}[N(A)]&=\mathbb E[\mu_A]+\operatorname{Var}[\mu_A].
\end{aligned}
\label{eq:a-total-variance}
\]

For disjoint \(A,B\), total covariance gives

\[
\begin{aligned}
\operatorname{Cov}[N(A),N(B)]
&=\mathbb E[\operatorname{Cov}(N(A),N(B)\mid\Lambda)]\\
&\quad+\operatorname{Cov}[\mu_A,\mu_B]\\
&=\operatorname{Cov}[\mu_A,\mu_B].
\end{aligned}
\label{eq:a-total-covariance}
\]

More generally, the first term is \(\mathbb E[\mu_{A\cap B}]\). Thus for cells \(j,k\), a fixed primary contribution \(p_j\), and external contribution \(c_jF_j\),

\[
\begin{gathered}
N_j\mid F\sim\operatorname{Poisson}(p_j+c_jF_j),\\
\mathbb E[F_j]=1,\qquad \operatorname{Cov}(F_j,F_k)=K_{jk},\\
\mathbb E[N_j]=p_j+c_j,\\
\operatorname{Cov}(N_j,N_k)
=\delta_{jk}(p_j+c_j)+c_jc_kK_{jk}.
\end{gathered}
\label{eq:a-finite-counts}
\]

The Kronecker-delta term is discrete Poisson sampling. It should not also be inserted into the covariance of the random intensity as another copy of the same shot noise. A spectrum estimated from counts needs the appropriate separation before being used as a latent-intensity covariance.

These are generative statements, not an assertion that true-distance cell counts are observed in a photometric survey. Random primary parameters introduce additional total-variance contributions. Also, although the external component can be log-Gaussian Cox, the sum of a fixed primary intensity and a lognormal external intensity is not generally lognormal. The total is a Cox construction, not in general one LGCP.

## B. The halo-conditioned mean {#palm-mean}

In an ideal stationary mixed process, let halo centres have intensity \(\rho_h\), and let a tracer population have intensity \(\rho_g\). If \(\rho_{hg}^{(2)}(0,x)\) is their mixed product density, the tracer mean under halo Palm conditioning is

\[
m_h(x)=\frac{\rho_{hg}^{(2)}(0,x)}{\rho_h}.
\label{eq:b-palm-ratio}
\]

One way to interpret this is to count halo–tracer pairs with the halo in a tiny test volume, then divide by the expected number of halos in that volume. The shrinking-volume limit gives the distribution seen from a typical halo point. It is not ordinary conditioning on a positive-probability event that a specified continuous coordinate contains a point.[^palm]

Defining \(\rho_{hg}^{(2)}(0,x)=\rho_h\rho_g[1+\xi_{hg}(x)]\) gives

\[
m_h(x)=\rho_g[1+\xi_{hg}(x)].
\label{eq:b-palm-mean}
\]

For the application, the tracer moments must exclude the tagged host’s own galaxies. Host subtraction is an additional modeling operation. *Reduced* Palm conditioning removes the tagged point from its own point configuration; it does not remove every galaxy belonging to that halo. A single-population galaxy Palm formula also cannot simply be relabeled as halo conditioning.

The practical external mean in the main article is a prescribed \(\rho_R H\). Its effective exclusion multiplies the full reference-plus-excess factor. Besides \(0\leq E\leq1\), its use requires a nonnegative complete \(H\) on the retained domain. Exclusion cannot repair a negative bracket by itself, except where the product is exactly zero. Biases, growth, fiducial mass, exclusion scale and distance convention are calibration inputs to this prescription.

## C. Why a general conditional covariance needs more {#conditional-covariance}

At distinct tracer positions \(x,y\), halo conditioning gives the conditional pair intensity

\[
\rho_{gg\mid h_0}^{(2)}(x,y)=
\frac{\rho_{hgg}^{(3)}(0,x,y)}{\rho_h}.
\label{eq:c-third-moment}
\]

For an illustrative stationary halo–tracer process, define its connected three-point correlation \(\zeta_{hgg}\) by

\[
\begin{aligned}
\rho_{hgg}^{(3)}(0,x,y)=\rho_h\rho_g^2\bigl[
 &1+\xi_{hg}(x)+\xi_{hg}(y)\\
 &+\xi_{gg}(x-y)+\zeta_{hgg}(0,x,y)\bigr].
\end{aligned}
\label{eq:c-correlation-expansion}
\]

The product of the conditional means is

\[
m_h(x)m_h(y)=\rho_g^2[1+\xi_{hg}(x)][1+\xi_{hg}(y)].
\label{eq:c-mean-product}
\]

Divide the conditional pair intensity by this product and subtract one. Wherever both conditional means are nonzero,

\[
K_h(x,y)=
\frac{\xi_{gg}(x-y)+\zeta_{hgg}(0,x,y)-\xi_{hg}(x)\xi_{hg}(y)}
{[1+\xi_{hg}(x)][1+\xi_{hg}(y)]}.
\label{eq:c-conditional-excess}
\]

Under a suitable conditional Cox representation, this fractional pair excess is also the fractional covariance of the random intensity at distinct positions. Poisson sampling contributes the separate diagonal term to count covariance.

The ordinary galaxy or matter two-point spectrum does not determine \(\zeta_{hgg}\). It therefore does not determine this general halo-conditioned covariance. For external-only galaxies, every mixed moment must consistently exclude primary-host contributions. Selection and redshift evolution bring additional dependence absent from this stationary teaching expression. Where an adopted exclusion makes the mean zero, the fractional ratio is undefined; use the absolute intensity moments there rather than divide by zero.

## D. The exact Gaussian-tilt calculation {#gaussian-tilt}

Assume a finite jointly Gaussian vector \(Y\sim\mathcal N(0,C)\), containing a halo log-field value \(Y_h(0)\) and external-tracer log-field values \(Y_E(x)\). Define the intensities

\[
\begin{aligned}
\Lambda_h(0)&=\rho_h\exp[Y_h(0)-C_{hh}(0,0)/2],\\
\Lambda_E(x)&=\rho_E\exp[Y_E(x)-C_{EE}(x,x)/2].
\end{aligned}
\label{eq:d-joint-intensities}
\]

Assume the two point processes are conditionally Poisson under this joint intensity law. Halo Palm conditioning reweights the field by \(\Lambda_h(0)/\rho_h\), so

\[
p^*(Y)=\exp[Y_h(0)-C_{hh}(0,0)/2]p(Y).
\label{eq:d-tilted-law}
\]

The reweighting integrates to one by the Gaussian exponential-moment identity. For positive-definite \(C\), complete the square for a general tilt \(t\):

\[
-\tfrac12Y^TC^{-1}Y+t^TY-\tfrac12t^TCt
=-\tfrac12(Y-Ct)^TC^{-1}(Y-Ct).
\label{eq:d-square}
\]

Thus the tilted law is \(\mathcal N(Ct,C)\). A singular covariance can be treated on its Gaussian support, or through its moment-generating function. Taking \(t\) to select the halo component gives

\[
\begin{aligned}
\mathbb E^*[Y_E(x)]&=C_{Eh}(x,0),\\
\operatorname{Cov}^*[Y_E(x),Y_E(y)]&=C_{EE}(x,y).
\end{aligned}
\label{eq:d-shift}
\]

Write the tilted external log-field as \(C_{Eh}(x,0)+G_E(x)\), where \(G_E\) retains the zero-mean covariance \(C_{EE}\). Then the conditional intensity has the distribution

\[
\Lambda_E^{\mid h_0}(x)=
\underbrace{\rho_Ee^{C_{Eh}(x,0)}}_{m_h(x)}
\underbrace{e^{G_E(x)-C_{EE}(x,x)/2}}_{F(x),\ \mathbb E[F(x)]=1}.
\label{eq:d-factorization}
\]

This finite-dimensional multitype argument states its extra assumptions explicitly. The rigorous single-process reduced-Palm LGCP result is Theorem 1 of Coeurjolly, Møller and Waagepetersen.[^lgcp]

What remains unchanged is the Gaussian covariance, hence the fractional intensity covariance. The absolute intensity covariance is

\[
\operatorname{Cov}^*[\Lambda_E(x),\Lambda_E(y)]
=m_h(x)m_h(y)[e^{C_{EE}(x,y)}-1],
\label{eq:d-absolute-covariance}
\]

which changes when the mean changes.

### The boundary of the result

The theorem produces \(H=e^{C_{Eh}}\). The practical model instead prescribes an excluded-linear \(H\) and a residual covariance from a separate nonlinear-power calculation. It does not exhibit a complete jointly valid halo–external Gaussian covariance from which both follow.

Moreover, \(e^{C_{Eh}}>0\) for finite \(C_{Eh}\); it cannot produce hard-zero exclusion. Multiplying an intensity by a nonnegative deterministic exclusion factor still defines a legitimate nonnegative intensity, subject to integrability. It simply is an additional prescription, not the unmodified Gaussian-tilt theorem.

Calling the model a *theory-informed conditional closure* makes this boundary explicit: selected conditional moments approximate a much more complicated environment distribution. A complete finder-selection law and false-positive model are separate requirements. Conditioning on a candidate selected from a catalogue is not the same as Palm conditioning on a typical halo.

## E. From finite-cell moments to a positive field {#finite-field}

For an equal-time Cartesian teaching calculation, choose real normalized windows \(\int W_j(x)\,dx=1\), and define

\[
\delta_j=b_j\int W_j(x)\delta_m(x)\,dx.
\label{eq:e-cell-average}
\]

Use \(\widetilde f(k)=\int f(x)e^{-ik\cdot x}\,dx\) and \(f(x)=\int\widetilde f(k)e^{ik\cdot x}\,d^3k/(2\pi)^3\). Statistical homogeneity and the power-spectrum definition imply

\[
\mathbb E[\widetilde\delta_m(k)\widetilde\delta_m(k')^*]
=(2\pi)^3\delta_D^{(3)}(k-k')P_m(k).
\label{eq:e-spectrum}
\]

Substitution into the two cell averages gives, equivalently for real windows and an even spectrum,

\[
K_{jk}=b_jb_k\int\frac{d^3k}{(2\pi)^3}
P_m(k)\widetilde W_j(k)\widetilde W_k(k)^*.
\label{eq:e-window-covariance}
\]

In particular, for real coefficients \(a_j\),

\[
a^TKa=\int\frac{d^3k}{(2\pi)^3}P_m(k)
\left|\sum_j a_jb_j\widetilde W_j(k)\right|^2\geq0.
\label{eq:e-psd}
\]

The finite-cell covariance is positive semidefinite when the spectrum is nonnegative and the integrals exist. The literal survey design instead uses selected radial windows, angular pixel windows, redshift-dependent features built from square roots of nonlinear power, and finite numerical representations. This Cartesian calculation explains the role of windows; it does not replace that construction.

### Lognormal moment matching

For \(G\sim\mathcal N(0,C)\), its moment-generating function is \(\mathbb E[e^{t^TG}]=e^{t^TCt/2}\). Set \(F_j=e^{G_j-C_{jj}/2}\). Then

\[
\begin{aligned}
\mathbb E[F_j]&=1,\\
\mathbb E[F_jF_k]
&=e^{-(C_{jj}+C_{kk})/2}
  e^{(C_{jj}+2C_{jk}+C_{kk})/2}\\
&=e^{C_{jk}}.
\end{aligned}
\label{eq:e-lognormal-moments}
\]

Consequently a target fractional intensity covariance \(K\) suggests \(C_{jk}=\log(1+K_{jk})\), entrywise. Every \(1+K_{jk}\) must be positive, and the resulting \(C\) must be a valid Gaussian covariance. The second requirement does not follow from the first, or even from \(K\succeq0\).

For a concrete two-cell counterexample, take

\[
K=\begin{pmatrix}1&2\\2&4\end{pmatrix}\succeq0,
\qquad
C=\begin{pmatrix}\log2&\log3\\\log3&\log5\end{pmatrix}.
\label{eq:e-counterexample}
\]

The first matrix is a rank-one outer product. But

\[
\det C=(\log2)(\log5)-(\log3)^2\simeq-0.0914<0.
\label{eq:e-counterexample-determinant}
\]

So the candidate log-covariance is indefinite. No Gaussian vector has that covariance. Projecting it onto a valid covariance would change the represented moments; such a modification must be documented, not treated as exact matching.

An average of correlated lognormal variables is generally not itself lognormal. Moment matching after finite averaging is therefore a finite-dimensional modeling choice, not an identity obtained by averaging a continuous log-field. If a retained loading matrix \(B\) defines \(G=B\epsilon\), \(\epsilon\sim\mathcal N(0,I)\), the compensation must use the actual represented variance \((BB^T)_{jj}/2\), including any retained-mode approximation or numerical adjustment.

The field factor is constant within each retained cell, but \(\rho_R\) and \(H\) need not be. Their integrals over the cell should not silently become midpoint values. Exponentiation, averaging, finite representation and quadrature are distinct operations.

### Several populations and mode penalties

For population \(a\), a shared-driver construction \(G^{(a)}=B^{(a)}\epsilon\) gives

\[
\operatorname{Cov}(G_j^{(a)},G_k^{(b)})
=[B^{(a)}B^{(b)T}]_{jk}.
\label{eq:e-shared-drivers}
\]

After the appropriate diagonal compensation for each field,

\[
\operatorname{Cov}(F_j^{(a)},F_k^{(b)})
=\exp\!\left([B^{(a)}B^{(b)T}]_{jk}\right)-1.
\label{eq:e-cross-population}
\]

This supplies a specific joint law rather than a freely inferred general cross-population covariance. In a covariance eigenmode with positive variance \(\kappa\), the Gaussian negative log density contributes \(g^2/(2\kappa)\). A zero-variance mode is confined to its support. A positive, smooth field is not automatically prevented from resembling the primary; its loading and covariance determine the available competition.

## F. The observation and selection operator {#observation-operator}

Let \(\rho(x)\) be a parent latent intensity. Given the intensity, assume independent measurements from a normalized kernel \(k(y\mid x)\), and independent admission with probability \(s(y)\in[0,1]\). Here \(y\) can include a catalogue’s photometric measurements and other observed marks; hard cuts are included by indicator-valued \(s\).

The expected number admitted to a measurable observation-space set \(B\) is

\[
\mathbb E[N_{\rm sel}(B)\mid\rho]
=\int \rho(x)\int_B s(y)k(y\mid x)\,dy\,dx.
\label{eq:f-observed-count}
\]

Nonnegativity permits interchange of the integrals. The selected observation-space intensity is

\[
\nu(y)=s(y)\int k(y\mid x)\rho(x)\,dx.
\label{eq:f-observed-intensity}
\]

Independent marking, displacement and thinning preserve the conditional Poisson structure. Conditional on a random field, the same construction therefore also preserves the Cox interpretation. Selection depending jointly on the whole catalogue, or dependent measurements, requires a different argument; it is not covered by these independence assumptions.

Integrating over all admitted measurements gives the expected-count term, also called the compensator:

\[
\begin{aligned}
\mu_{\rm sel}&=\int\nu(y)\,dy
=\int\alpha(x)\rho(x)\,dx,\\
\alpha(x)&=\int s(y)k(y\mid x)\,dy.
\end{aligned}
\label{eq:f-admission}
\]

The likelihood is consequently

\[
\log L=\sum_i\log\nu(y_i)-\mu_{\rm sel}+\mathrm{const}.
\label{eq:f-likelihood}
\]

### Two consistent arrangements of selection

One arrangement uses the parent \(\rho\), ordinary measurement kernel \(k\), and explicit admission \(s\). Alternatively, define the selected latent intensity and admission-conditioned kernel by

\[
\rho_R(x)=\alpha(x)\rho(x),
\qquad k_R(y\mid x)=\frac{s(y)k(y\mid x)}{\alpha(x)}
\quad\text{where }\alpha(x)>0.
\label{eq:f-selected-kernel}
\]

Then \(\int k_R(y\mid x)\,dy=1\), and

\[
\nu(y)=\int k_R(y\mid x)\rho_R(x)\,dx,
\qquad \mu_{\rm sel}=\int\rho_R(x)\,dx.
\label{eq:f-equivalence}
\]

Where \(\alpha=0\), the selected intensity vanishes and the kernel need not be defined. Applying the full admission probability again to \(\rho_R\) would double-select the population. This textbook identity explains the bookkeeping principle; it does not replace the design’s empirical reference products.

### A posterior is not a likelihood

For a source photo-z procedure,

\[
p_{\rm src}(z\mid y_i)
=\frac{p_{\rm src}(y_i\mid z)\,\pi_{\rm src}(z)}{p_{\rm src}(y_i)}.
\label{eq:f-source-posterior}
\]

Thus \(p_{\rm src}(y_i\mid z)\propto p_{\rm src}(z\mid y_i)/\pi_{\rm src}(z)\) on the appropriate prior support. This conversion assumes the same treatment of any marginalized nuisance variables. Lost support, unknown source priors, or inconsistent selection cannot be repaired by calling the posterior a likelihood.

The design records the following empirical-reference convention, in redshift coordinates:

\[
\begin{aligned}
Z_i&=\int\hat n_0(z)\ell_i(z)\,dz,\\
q_i(z)&=\frac{\hat n_0(z)\ell_i(z)}{Z_i},\\
\hat n_R(z)&=\hat n_0(z)S(z).
\end{aligned}
\label{eq:f-reference}
\]

Here \(\ell_i\) is the native redshift likelihood, \(\hat n_0\) is the empirical parent reference in its declared measure, and \(S\) supplies the selected-reference factor. The reference-weighted law \(q_i\) is not automatically the source photo-z posterior. Algebra gives, where the terms are defined,

\[
\frac{q_i(z_*)}{\hat n_R(z_*)}
=\frac{\ell_i(z_*)}{Z_i S(z_*)}.
\label{eq:f-primary-reference-ratio}
\]

This identity explains the native-likelihood primary response. The external response integrates \(q_i\) against its represented mean and line-of-sight shell factors. Reproducing all response weights and the compensator requires the declared reference products and selection convention; the identity alone does not specify a full implementation.

The design also records a state-independent finite-domain capture factor applied to both additive event responses. If a positive factor \(c_i\) independent of every inferred parameter divides both responses for object \(i\), then

\[
\log\!\left(\frac{\nu_i^P}{c_i}+\frac{\nu_i^E}{c_i}\right)
=\log(\nu_i^P+\nu_i^E)-\log c_i.
\label{eq:f-capture-factor}
\]

For the fixed observed catalogue, this changes the likelihood only by a parameter-independent constant. It does not rescale the expected-count term, and it does not alter the primary allocation ratio. This is an equivalence of likelihood expressions, not a claim that an arbitrarily reweighted observation-space intensity has the same integral. A state-dependent factor, or a factor applied to only one population, cannot be discarded in this way.

## G. The selected primary and external model {#selected-model}

Suppressing population indices, the design’s conceptual selected intensity per \(d\omega\,d\chi\) is

\[
\Lambda_R(\omega,\chi)=w(\omega)\left[
\lambda U(\omega;\theta)\delta_D(\chi-\chi_*)
+\rho_R(\chi)H(\omega,\chi;\theta)F(\omega,\chi)\right].
\label{eq:g-selected-intensity}
\]

The coverage \(w\) and footprint \(\Omega\) are fixed. For an unnormalized angular shape \(\widetilde U\), define

\[
A(\theta)=\int_\Omega w(\omega)\widetilde U(\omega;\theta)\,d\omega,
\qquad U(\omega;\theta)=\frac{\widetilde U(\omega;\theta)}{A(\theta)},
\label{eq:g-normalization}
\]

assuming \(0<A(\theta)<\infty\) on the prior support. Provided the retained radial domain contains \(\chi_*\),

\[
\mu_P=\lambda\int_\Omega wU\,d\omega
\int\delta_D(\chi-\chi_*)\,d\chi=\lambda.
\label{eq:g-primary-count}
\]

Thus \(\lambda\) is an expected selected primary count inside the fixed covered footprint. Moving the centre changes \(A(\theta)\), not the footprint. A moving aperture would instead change the experiment.

The primary’s delta is a thin latent-depth approximation. It can produce broad measured redshifts through the observation kernel. If one changes variables from \(\chi\) to \(z\), the densities and delta function must be transformed in that coordinate measure. The supplied \(\rho_R(\chi)\) is already per solid angle per comoving distance, so another volume Jacobian \(\chi^2\) would double-count a measure conversion.

The expected external count is

\[
\mu_E(\theta,F)=
\int_\Omega d\omega\int d\chi\,
 w(\omega)\rho_R(\chi)H(\omega,\chi;\theta)F(\omega,\chi).
\label{eq:g-external-count}
\]

If \(F_j\) is constant in represented cell \(V_j\), this can be written \(\sum_j c_j(\theta)F_j\), where \(c_j(\theta)=\int_{V_j}w\rho_RH\,d\omega\,d\chi\). The reference and mean are integrated inside \(c_j\); they need not be constant within the cell.

### Generic projection of a truncated profile

For intuition, a spherical truncated NFW-type galaxy profile can be written generically as

\[
n_{\rm tr}(r)=\frac{a}{(r/r_s)(1+r/r_s)^2}\,T(r;r_t),
\label{eq:g-generic-nfw}
\]

where \(T\) is a nonnegative truncation function with sufficient decay and \(a\) is an amplitude. Integrating along the line of sight, with \(r^2=R^2+l^2\), gives

\[
\begin{aligned}
\Sigma(R)&=\int_{-\infty}^{\infty}n_{\rm tr}(\sqrt{R^2+l^2})\,dl\\
&=2\int_R^\infty n_{\rm tr}(r)\frac{r\,dr}{\sqrt{r^2-R^2}}.
\end{aligned}
\label{eq:g-projection}
\]

Convert the projected density to an angular shape with the appropriate distance and area measure, then apply the covered normalization above. Comoving and physical scales must not be mixed. This is the generic spherical projection, **not a specification of the project’s truncation function**. The original design identifies the default family as `trunc_nfw`; its exact law and implementation are not reproduced here. In particular, the fitted galaxy scale need not equal a mock halo’s supplied virial or scale radius.

## H. Joint inference, allocation, and identifiability {#joint-inference}

For a fixed supplied covariance and calibration, the joint posterior is

\[
p(\theta,G\mid D)\propto
\exp\!\left[\sum_i\log(\nu_i^P+\nu_i^E)-\lambda-\mu_E\right]
\pi(\theta)\,p_C(G).
\label{eq:h-posterior}
\]

All responses and count terms are evaluated at the same joint state. The Gaussian law \(p_C\) is understood on its support; it can equivalently be represented with white drivers. The object-level posterior integrates out the field rather than fixing a fitted map:

\[
p(\theta\mid D)=\int p(\theta,G\mid D)\,dG.
\label{eq:h-marginal}
\]

### Membership is an allocation probability

Introduce latent labels \(Z_i\in\{0,1\}\), with 1 denoting the primary. Conditional on the joint state, superposition of independent primary and external Poisson processes gives label weights

\[
p(\{Z_i\}\mid D,\theta,G)
\propto\prod_i(\nu_i^P)^{Z_i}(\nu_i^E)^{1-Z_i}.
\label{eq:h-label-law}
\]

Normalization factorizes over objects. Hence

\[
a_i(\theta,G)=P(Z_i=1\mid D,\theta,G)
=\frac{\nu_i^P}{\nu_i^P+\nu_i^E},
\quad p_i^P=\mathbb E[a_i(\theta,G)\mid D].
\label{eq:h-allocation}
\]

One must average the ratio, not form the ratio of separately averaged responses. For the assigned primary count in this fixed observed catalogue, \(N_P^{\rm assign}=\sum_i Z_i\),

\[
\begin{aligned}
\mathbb E[N_P^{\rm assign}\mid D]&=\sum_i p_i^P,\\
\operatorname{Var}[N_P^{\rm assign}\mid D]
&=\mathbb E\!\left[\sum_i a_i(1-a_i)\mid D\right]
+\operatorname{Var}\!\left[\sum_i a_i\mid D\right].
\end{aligned}
\label{eq:h-assignment-count}
\]

The first term is conditional allocation uncertainty. The second is shared uncertainty about the state, which can couple the allocations after marginalization.

A new primary catalogue drawn in the same selected footprint instead has \(N_P^{\rm rep}\mid\lambda\sim\operatorname{Poisson}(\lambda)\), and therefore

\[
\mathbb E[N_P^{\rm rep}\mid D]=\mathbb E[\lambda\mid D],
\quad \operatorname{Var}[N_P^{\rm rep}\mid D]
=\mathbb E[\lambda\mid D]+\operatorname{Var}[\lambda\mid D].
\label{eq:h-replicated-count}
\]

Expected richness, allocation of existing observations, and a replicated count are different estimands.

### A count penalty does not guarantee attribution

For \(I(x)=\lambda u(x)+B(x)\), consider an admissible change

\[
\lambda'=\lambda-\Delta,
\qquad B'(x)=B(x)+\Delta u(x).
\label{eq:h-exchange}
\]

Then \(I'=I\) pointwise and \(\int I'=\int I\). Both the event term and the count term are unchanged. The likelihood cannot resolve the exchange. The allowed field family and its prior restrict whether such an exchange is available and probable; they do not prove that every patch is identifiable.

Candidate redshift information may enter a prior while candidate information also defines a fixed selection window. Reusing the underlying observations is not automatically equivalent to adding independent evidence. Assessing that reuse, false detections, population selection and calibration uncertainty requires additional modeling or sensitivity studies. The current positive-richness construction is not, by itself, a calibrated halo-existence probability.

## I. What is exact, assumed, or still to test {#status}

| Statement | Status |
| --- | --- |
| Poisson likelihood; total count variance; allocation ratios | Derived under the stated conditional sampling assumptions |
| Halo Palm mean from a mixed product density | Exact identity for the specified populations |
| Unchanged Gaussian covariance after a Gaussian tilt | Exact under the stated jointly log-Gaussian, multitype Cox law |
| Excluded-linear mean plus separately specified residual moments | Conditional astrophysical approximation |
| Thin primary, profile family, references, field cells and loadings | Model-design choices and calibration conventions |
| Better richness recovery or calibrated posterior intervals | Requires inference runs and compatible truth; not demonstrated here |

The [figure script](../tools/make_figures.py) and [mathematical checks](../tools/check_math.py) reproduce the illustrative calculations. These checks test algebraic identities and numerical constructions, not the scientific adequacy of the approximation. The [main article’s data section](measuring-a-galaxy-cluster.html#data) records the mock selection, provenance and acknowledgements.

[^palm]: J.-F. Coeurjolly, J. Møller & R. Waagepetersen. *A tutorial on Palm distributions for spatial point processes*. [arXiv:1512.05871v2](https://arxiv.org/abs/1512.05871v2). Definitions of Poisson/Cox processes, product densities and Palm conditioning.
[^lgcp]: J.-F. Coeurjolly, J. Møller & R. Waagepetersen. *Palm distributions for log Gaussian Cox processes*. [arXiv:1506.04576v4](https://arxiv.org/abs/1506.04576v4), Theorem 1. The joint halo–external Gaussian-tilt construction here states additional multitype assumptions.
[^halo]: M. Asgari, A. J. Mead & C. Heymans. *The halo model for cosmology: a pedagogical review*. [arXiv:2303.08752v2](https://arxiv.org/abs/2303.08752v2). Halo-model language, profile and exclusion context.
