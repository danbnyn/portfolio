#!/usr/bin/env python3
"""Reproduce the article figures; no inference-pipeline results are generated.

python tools/make_figures.py --catalogue /path/to/27277.csv.bz2
python tools/make_figures.py  # uses the committed, fixed illustrative subset

Requires NumPy, pandas, SciPy and Matplotlib. Plot defaults deliberately supply
colours; marker shapes and line styles also distinguish every series.
"""
from __future__ import annotations
import argparse
import bz2
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import gammaln, logsumexp
from numpy.polynomial.hermite import hermgauss

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'cluster'
HALO = 4040470062983
NEAR = 4040470064477
FOREGROUND = 3838420219862
HALF_WIDTH = 6.0
MAG_LIMIT = 22.5


def save(fig, name: str) -> None:
    """Write a vector figure and a raster preview with a fixed canvas."""
    fig.tight_layout(pad=1.3)
    fig.savefig(OUT / f'{name}.svg', metadata={'Date': None})
    fig.savefig(OUT / f'{name}.png', dpi=160, metadata={'Software': 'Matplotlib'})
    plt.close(fig)


def read_catalogue(path: Path) -> tuple[pd.DataFrame, dict]:
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, comment='#')
    df.columns = df.columns.str.removeprefix('t.')
    required = {'halo_id','galaxy_id','kind','ra_gal','dec_gal',
                'observed_redshift_gal','true_redshift_halo','euclid_nisp_h'}
    if missing := required.difference(df.columns):
        raise ValueError(f'Missing columns: {sorted(missing)}')
    central = df.loc[(df.halo_id == HALO) & (df.kind == 0)]
    if len(central) != 1:
        raise ValueError('Expected exactly one central of the demonstration halo.')
    ra0 = float(central.ra_gal.iloc[0])
    dec0 = float(central.dec_gal.iloc[0])
    z0 = float(central.true_redshift_halo.iloc[0])
    if not np.isfinite(df[list(required - {'halo_id','galaxy_id','kind'})].to_numpy()).all():
        raise ValueError('Non-finite inputs; define an explicit exclusion before proceeding.')
    if (df.euclid_nisp_h <= 0).any():
        raise ValueError('H-band flux must be positive for the stated magnitude cut.')
    # Small-angle tangent-plane offsets, not exact spherical coordinates.
    x = 60 * (df.ra_gal - ra0) * np.cos(np.deg2rad(dec0))
    y = 60 * (df.dec_gal - dec0)
    mag = -2.5 * np.log10(df.euclid_nisp_h) - 48.6
    selected = (np.abs(x) < HALF_WIDTH) & (np.abs(y) < HALF_WIDTH) & (mag < MAG_LIMIT)
    d = df.loc[selected, ['halo_id','galaxy_id','kind','ra_gal','dec_gal',
                         'observed_redshift_gal','true_redshift_halo']].copy()
    d.insert(0, 'source_row', df.index[selected].to_numpy(dtype=np.int64))
    d['x_arcmin'] = x[selected]; d['y_arcmin'] = y[selected]; d['h_ab'] = mag[selected]
    # No subsampling and no cut on true/simulated redshift.
    d.to_csv(OUT / 'scene.csv', index=False, float_format='%.9g')
    meta = {
        'source': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'source_rows': len(df), 'source_columns': len(df.columns),
        'source_catalogue': 'euclid_fs2_mock_dr_v1_1_phz',
        'source_query': 'HEALPix NESTED order-6 pixel containing (RA, Dec) = (190 deg, 60 deg); positive euclid_nisp_h; H_AB < 26',
        'export_utc': '2026-09-22T16:06:26+00:00',
        'illustrative_halo_id': str(HALO), 'nearby_halo_id': str(NEAR),
        'foreground_halo_id': str(FOREGROUND),
        'centre_ra_deg': ra0, 'centre_dec_deg': dec0, 'host_true_redshift': z0,
        'half_width_arcmin': HALF_WIDTH, 'h_ab_limit': MAG_LIMIT,
        'selection': 'abs(x_arcmin)<6, abs(y_arcmin)<6, H_AB<22.5; no redshift cut; no random downsampling',
        'selected_rows': len(d), 'selected_primary_rows': int((d.halo_id == HALO).sum()),
        'selected_nearby_rows': int((d.halo_id == NEAR).sum()),
        'selected_foreground_rows': int((d.halo_id == FOREGROUND).sum()),
        'redshift_column': 'observed_redshift_gal (simulation redshift; not a photo-z estimate)',
        'identity': 'source_row is the zero-based data-row index; host labels are simulation truth, not inferred membership',
        'choice': 'A deliberately chosen interior rich halo for explanation, not a random or representative validation target.',
        'raw_source_included': False,
        'toy_seed': 271828,
        'figure_status': 'Scene panels use the supplied mock. All other figures are explicitly specified pedagogical calculations, not fitted results.'
    }
    (OUT / 'provenance.json').write_text(json.dumps(meta, indent=2) + '\n')
    return d, meta


def sky_figures(d: pd.DataFrame, meta: dict) -> None:
    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    ax.scatter(d.x_arcmin, d.y_arcmin, s=6, alpha=.45, linewidths=0)
    ax.set(xlim=(-6,6), ylim=(-6,6), aspect='equal',
           xlabel=r'$(\alpha-\alpha_0)\cos\delta_0$ [arcmin]',
           ylabel=r'$\delta-\delta_0$ [arcmin]', title=f'{len(d):,} galaxies · sky positions only')
    save(fig, 'scene-sky')

    populations = [
        ('Other hosts', ~d.halo_id.isin([HALO,NEAR,FOREGROUND]), '.', 8, .25),
        ('Primary host', d.halo_id == HALO, 'o', 18, .8),
        ('Nearby host', d.halo_id == NEAR, '^', 28, .85),
        ('Foreground host', d.halo_id == FOREGROUND, 's', 22, .85),
    ]
    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    for label, m, marker, size, alpha in populations:
        ax.scatter(d.loc[m,'x_arcmin'], d.loc[m,'y_arcmin'], s=size, alpha=alpha,
                   marker=marker, linewidths=0, label=label)
    ax.set(xlim=(-6,6), ylim=(-6,6), aspect='equal',
           xlabel=r'$(\alpha-\alpha_0)\cos\delta_0$ [arcmin]',
           ylabel=r'$\delta-\delta_0$ [arcmin]', title='The same sky · simulation host labels revealed')
    ax.legend(loc='upper left', fontsize=9, framealpha=.95, markerscale=1.2)
    save(fig, 'scene-hosts')

    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    for label, m, marker, size, alpha in populations:
        ax.scatter(d.loc[m,'x_arcmin'], d.loc[m,'observed_redshift_gal'],
                   s=size, alpha=alpha, marker=marker, linewidths=0, label=label)
    ax.set(xlim=(-6,6), ylim=(0,3.05),
           xlabel=r'$(\alpha-\alpha_0)\cos\delta_0$ [arcmin]',
           ylabel='Simulation redshift (includes peculiar velocities)',
           title='The same galaxies · redshift-space view')
    ax.legend(loc='upper left', fontsize=9, framealpha=.95, markerscale=1.2)
    save(fig, 'scene-redshift')


def mean_figure() -> None:
    r = np.linspace(0, 6, 500)
    correlated = 1 + 2/(1+r*r)
    t = np.clip((r-1)/.6, 0, 1)
    exclusion = t*t*(3-2*t)
    fig, ax = plt.subplots(figsize=(7.4,4.4))
    ax.plot(r, np.ones_like(r), '--', label='Random-location reference')
    ax.plot(r, correlated, ':', label='Correlated mean, no exclusion')
    ax.plot(r, correlated*exclusion, '-', label='Correlated mean × exclusion')
    ax.set(xlim=(0,6), ylim=(0,3.25), xlabel=r'True separation / exclusion scale, $r/R_*$',
           ylabel='External mean / reference density', title='Changing the mean is not drawing a sky mask')
    ax.legend(fontsize=9, loc='upper right')
    save(fig, 'conditional-mean')


def count_figure() -> dict:
    # An exact 1-cell example: primary p=5; external c=15; C=log(1.25).
    # Integrate over the Gaussian driving log field using Gauss-Hermite quadrature.
    p, c, variance_F = 5., 15., .25
    variance_G = np.log1p(variance_F)
    n = np.arange(101)
    mu = p+c
    poisson = np.exp(n*np.log(mu)-mu-gammaln(n+1))
    nodes, weights = hermgauss(120)
    field = np.exp(np.sqrt(2*variance_G)*nodes - variance_G/2)
    means = p+c*field
    logterms = (np.log(weights/np.sqrt(np.pi))[:,None]
                + n[None,:]*np.log(means[:,None])-means[:,None]-gammaln(n[None,:]+1))
    cox = np.exp(logsumexp(logterms,axis=0))
    fig, ax = plt.subplots(figsize=(7.4,4.4))
    ax.plot(n, poisson, 'o-', ms=3, lw=1.5, label='Fixed intensity · variance 20')
    ax.plot(n, cox, 's--', ms=3, lw=1.5, label='Random external intensity · variance 76.25')
    ax.set(xlim=(0,60), ylim=(0,.1), xlabel='Realized galaxy count in one cell',
           ylabel='Probability', title='The same expected count: 20 galaxies')
    ax.legend(fontsize=9)
    save(fig, 'poisson-cox')
    return {'p':p,'c':c,'var_F':variance_F,'mean':mu,'var_poisson':mu,
            'var_cox':mu+c*c*variance_F,'quadrature_nodes':120,
            'probability_above_100':float(1-cox.sum())}


def prior_figures() -> dict:
    # Demonstration covariances only: not the project's cosmological calibration.
    x = (np.arange(64)+.5)*.125
    noise = np.random.default_rng(271828).normal(size=(64,3))
    eigenvalues = []
    for ell, name in [(.35,'prior-short'),(1.4,'prior-long')]:
        C = .49*np.exp(-.5*((x[:,None]-x[None,:])/ell)**2)+1e-10*np.eye(len(x))
        L = np.linalg.cholesky(C)
        G = L @ noise
        F = np.exp(G-.5*np.diag(C)[:,None])
        eigenvalues.append(np.linalg.eigvalsh(C)[::-1])
        fig, ax = plt.subplots(figsize=(7.4,3.65))
        for i, style in enumerate(['-','--',':']):
            ax.step(x, F[:,i], where='mid', linestyle=style, label=f'Draw {i+1}')
        ax.set(xlim=(0,8), ylim=(0,5), xlabel='Position [arbitrary units]',
               ylabel=r'Positive multiplier $F_j$',
               title=f'Correlation length {ell:g} · 64 cells · cell width 0.125')
        ax.legend(fontsize=9, ncols=3)
        save(fig, name)
    fig, ax = plt.subplots(figsize=(7.4,4.0))
    for vals, style, label in zip(eigenvalues, ['-','--'], ['Length 0.35','Length 1.4']):
        ax.semilogy(np.arange(1,65), vals, style, label=label)
    ax.set(xlim=(1,64), ylim=(5e-11,100), xlabel='Gaussian mode rank (largest variance first)',
           ylabel=r'Eigenvalue of $C$', title='Equal pointwise variance, different permitted spatial patterns')
    ax.legend(fontsize=9)
    save(fig, 'prior-modes')
    return {'cells':64,'cell_width':.125,'C_diagonal':.4900000001,
            'correlation_lengths':[.35,1.4], 'jitter':1e-10,
            'seed':271828,'formula':'C_jk = .49 exp[-(x_j-x_k)^2/(2 ell^2)] + 1e-10 delta_jk',
            'same_white_drivers_for_both_lengths':True,
            'not_cosmological_calibration':True}


def likelihood_figure(meta: dict) -> None:
    z = np.linspace(.2,1.25,600)
    z0 = meta['host_true_redshift']
    gaussian = lambda x, m, s: np.exp(-.5*((x-m)/s)**2)
    curves = [gaussian(z,.729,.055), gaussian(z,.431,.13),
              .65*gaussian(z,.903,.07)+.8*gaussian(z,.72,.05)]
    labels = ['Near-primary, unimodal', 'Foreground, broad', 'Background, ambiguous']
    fig, ax = plt.subplots(figsize=(7.4,4.4))
    for curve, label, style in zip(curves,labels,['-','--',':']):
        curve = curve/curve.max()
        ax.plot(z,curve,style,label=label)
    ax.axvline(z0,linestyle='-.',lw=1,label=r'Candidate $z_* = 0.7255$')
    ax.set(xlim=(.2,1.25),ylim=(0,1.12),xlabel='Latent redshift, z',
           ylabel='Relative likelihood (each peak scaled to 1)',
           title='Illustrative likelihoods, not photo-z data from the export')
    ax.legend(fontsize=9,loc='upper left')
    save(fig,'redshift-likelihoods')


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalogue',type=Path)
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if args.catalogue:
        d, meta=read_catalogue(args.catalogue)
    else:
        if not (OUT/'scene.csv').exists():
            parser.error('Supply --catalogue once, or restore the committed scene.csv.')
        d=pd.read_csv(OUT/'scene.csv')
        meta=json.loads((OUT/'provenance.json').read_text())
    # Stable SVG IDs and system-default fonts/colours; no font files are bundled.
    plt.rcParams['svg.hashsalt']='dan-benayoun-cluster-note-v1'
    sky_figures(d,meta)
    mean_figure()
    tests={'count_example':count_figure(),'prior_example':prior_figures()}
    likelihood_figure(meta)
    (OUT/'illustration-models.json').write_text(json.dumps(tests,indent=2)+'\n')
    print(f'Generated 9 SVG figures and PNG previews from {len(d):,} fixed scene rows.')
    print(json.dumps({k:meta[k] for k in ['source_rows','selected_rows','selected_primary_rows','selected_nearby_rows','selected_foreground_rows','host_true_redshift']},indent=2))


if __name__=='__main__':
    main()
