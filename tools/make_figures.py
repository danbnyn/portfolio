#!/usr/bin/env python3
"""Rebuild article figure assets from the retained, non-inference data products.

Requires numpy, scipy, pandas, matplotlib and plotly. No network or input mock
is needed. All PDZs are explicit synthetic measurement illustrations.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.special import ndtr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from plotly.offline import get_plotlyjs

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'cluster'
ZMAX = 3.2
SHIFTS = np.array([-.25, 0., .25])
WEIGHTS = np.array([.04, .92, .04])
SCALES = np.array([1.5, 1., 1.5])

def pdz(z: np.ndarray, t: np.ndarray, sigma: np.ndarray, cdf: bool = False) -> np.ndarray:
    """Source PDZ in z (or its CDF), normalized on 0 <= z <= 3.2.

    The source prior is uniform in s=log(1+z). No truncated-view
    renormalization is performed. Output shape is (objects, redshifts).
    """
    z = np.atleast_1d(z).astype(float)
    t = np.atleast_1d(t).astype(float)
    sigma = np.atleast_1d(sigma).astype(float)
    mu = t[:, None] - SHIFTS[None, :]
    sd = sigma[:, None] * SCALES[None, :]
    low = ndtr(-mu / sd)
    norm = np.sum(WEIGHTS * (ndtr((np.log1p(ZMAX)-mu)/sd)-low), axis=1)
    u = (np.log1p(np.clip(z, 0, ZMAX))[None, :, None] - mu[:, None, :]) / sd[:, None, :]
    if cdf:
        result = np.sum(WEIGHTS * (ndtr(u)-low[:, None, :]), axis=2) / norm[:, None]
        return np.clip(result, 0, 1)
    result = np.sum(WEIGHTS * np.exp(-.5*u*u) / (np.sqrt(2*np.pi)*sd[:, None, :]), axis=2)
    result /= norm[:, None]*(1+z[None, :])
    return np.where((z[None, :] >= 0)&(z[None, :] <= ZMAX), result, 0.)

def save(fig, name):
    fig.tight_layout(pad=1.5)
    fig.savefig(OUT/f'{name}.svg', bbox_inches='tight', metadata={'Date':None})
    plt.close(fig)

def chart(title, subtitle, xlabel, ylabel, figsize=(9.4, 5.5)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(title + '\n' + subtitle, loc='left', fontsize=14, pad=18)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(labelsize=10)
    return fig,ax

def roundlist(a, digits=7):
    return np.round(np.asarray(a, dtype=float), digits).tolist()

def main():
    scene = pd.read_csv(OUT/'scene.csv', dtype={'galaxy_id':str,'halo_id':str})
    meta = json.loads((OUT/'provenance.json').read_text())
    prof = pd.read_csv(OUT/'profiles-per-halo.csv', dtype={'halo_id':str})
    groups = ['Primary','Aligned halo','Other hosts']
    pop = scene.population.map(dict(zip(groups,range(3)))).to_numpy()
    pair = pop < 2
    for name, sky in [('scene-rsd',False),('scene-angular',True)]:
        fig,ax = chart('One angular overlap, two host populations',
            '279 highlighted galaxies from the same 7,341-object H < 24 sightline',
            'Eastward offset [arcmin]', 'Northward offset [arcmin]' if sky else 'Galaxy redshift (simulation redshift space)')
        for p, marker in [(0,'o'),(1,'^')]:
            m = pop==p
            ax.scatter(scene.x_arcmin[m], scene.y_arcmin[m] if sky else scene.observed_redshift_gal[m],
                       s=21, marker=marker, alpha=.70, label=f'{groups[p]} ({m.sum()})')
        ax.set_xlim(-6,6); ax.set_ylim((-6,6) if sky else (.58,.94))
        ax.legend(frameon=False, loc='upper left', fontsize=10)
        save(fig,name)

    # These maps use exact analytic CDF differences. A cell is probability mass,
    # not an independent Poisson count; only display density divides by cell area.
    xe = np.linspace(-6,6,61)
    histograms={}
    for view,ze in [('near',np.linspace(.58,.94,181)),('full',np.linspace(0,3.2,321))]:
        probs=np.diff(pdz(ze,scene.synthetic_t,scene.pdz_sigma_log1pz,cdf=True),axis=1)
        assert np.min(probs)>-1e-12
        if view=='full': assert np.allclose(probs.sum(axis=1),1,atol=2e-13)
        xi=np.clip(np.searchsorted(xe,scene.x_arcmin,side='right')-1,0,len(xe)-2)
        cube=np.zeros((3,len(ze)-1,len(xe)-1))
        for j in range(3):
            ids=np.flatnonzero(pop==j)
            np.add.at(cube[j].T,xi[ids],probs[ids])
        histograms[view]={'x':roundlist((xe[:-1]+xe[1:])/2),
                          'z':roundlist((ze[:-1]+ze[1:])/2),
                          'dx':float(np.diff(xe)[0]), 'dz':float(np.diff(ze)[0]),
                          'mass':roundlist(cube,8)}
        if view=='near':
            fig,ax=chart('Full PDZs blur the separation—not the angular positions',
                'Synthetic, magnitude-dependent distributions; all tails retained on 0 < z < 3.2',
                'Eastward offset [arcmin]', 'Possible redshift')
            density=cube[:2].sum(axis=0)/(np.diff(xe)[0]*np.diff(ze)[0])
            im=ax.pcolormesh(xe,ze,density,shading='flat',rasterized=True)
            fig.colorbar(im,ax=ax,pad=.025,label='Summed PDZ density / (arcmin × redshift)')
            ax.set_xlim(-6,6);ax.set_ylim(.58,.94)
            save(fig,'scene-full-pdz')

    profiles={}
    for key,mask in [('narrow',(prof.mass_msun<3e14)&(prof.z_halo>=.5)&(prof.z_halo<.8)),('broad',np.ones(len(prof),bool))]:
        a=prof[mask];nh=a.halo_id.nunique(); grouped=a.groupby('r_mid_rvir',sort=True)
        r=np.array(sorted(a.r_mid_rvir.unique()))
        def vals(col, denominator):
            tmp=a.copy();tmp['v']=tmp[col]/tmp[denominator]
            return tmp.groupby('r_mid_rvir').v
        total=vals('total_n','annulus_area_cmpc2_h2').mean().values
        primary=vals('primary_n','annulus_area_cmpc2_h2').mean().values
        ev=vals('environment_n','annulus_area_cmpc2_h2')
        env=ev.mean().values;lo=ev.quantile(.16).values;hi=ev.quantile(.84).values
        random=vals('random_mean_n','annulus_area_cmpc2_h2').mean().values
        tmp=a.copy();tmp['centre_ratio']=tmp.other_central_n/tmp.shell_volume_cmpc3_h3/tmp.central_reference_density
        cr=tmp.groupby('r_mid_rvir').centre_ratio
        assert np.allclose(total,primary+env)
        profiles[key]={'n':nh,'r':roundlist(r),'total':roundlist(total),'primary':roundlist(primary),
           'env':roundlist(env),'env_lo':roundlist(lo),'env_hi':roundlist(hi),'random':roundlist(random),
           'centre':roundlist(cr.mean().values),'centre_lo':roundlist(cr.quantile(.16).values),'centre_hi':roundlist(cr.quantile(.84).values)}
        if key=='narrow':
            fig,ax=chart('A halo is not surrounded by an average sightline',
                f'{nh} halos · 0.5 ≤ z < 0.8 · 10¹⁴ ≤ M < 3 × 10¹⁴ M☉ · H < 24',
                'Projected radius R / rᵥᵢᵣ', 'Surface density [galaxies / (h⁻¹ Mpc)²]')
            for arr,label,ls in [(total,'Total','-'),(primary,'Primary host','--'),(env,'Complementary / external','-.'),(random,'Matched random sightlines',':')]:
                ax.plot(r,np.where(arr>0,arr,np.nan),ls,label=label,lw=2)
            ax.fill_between(r,np.where(lo>0,lo,np.nan),hi,alpha=.16,label='External: 16–84% across halos')
            ax.set_xscale('log');ax.set_yscale('log');ax.set_xlim(.1,5)
            ax.set_xticks([.1,.2,.5,1,2,5],labels=['0.1','0.2','0.5','1','2','5'])
            ax.axvline(1,ls=':',alpha=.45); ax.legend(frameon=False,fontsize=9,loc='upper right')
            save(fig,'profiles-projected')
            fig,ax=chart('Exclusion is clearest in the centres—not projected galaxies',
                f'Same {nh} conditioning halos; other H < 24 centrals placed at host true redshifts',
                'Real-space centre separation r / rᵥᵢᵣ', 'Other-centre density / redshift-slice reference')
            ax.plot(r,cr.mean().values,'o-',lw=2,label='Equal-halo mean')
            ax.fill_between(r,cr.quantile(.16).values,cr.quantile(.84).values,alpha=.18,label='16–84% across halos')
            ax.axhline(1,ls='--',label='Reference = 1');ax.axvline(1,ls=':',alpha=.45)
            ax.set_xscale('log');ax.set_xlim(.1,5);ax.set_ylim(bottom=0)
            ax.set_xticks([.1,.2,.5,1,2,5],labels=['0.1','0.2','0.5','1','2','5'])
            ax.legend(frameon=False,fontsize=10,loc='upper left')
            save(fig,'profiles-centres')

    # Accessible object choices plus a linked on-click single-object inspector.
    pids=np.flatnonzero(pop==0); aids=np.flatnonzero(pop==1)
    normal=pids[np.argmin(abs(scene.synthetic_t.iloc[pids].values-np.log1p(meta['scene']['primary_z'])))]
    aligned=aids[np.argmin(abs(scene.synthetic_t.iloc[aids].values-np.log1p(meta['scene']['aligned_z'])))]
    aliasids=pids[scene.synthetic_error_alias.iloc[pids].values!=0]
    aliased=aliasids[np.argmin(abs(scene.synthetic_t.iloc[aliasids].values-np.log1p(meta['scene']['primary_z'])-.25))]
    examples=[{'index':int(normal),'label':'Primary-host galaxy: main peak'},
              {'index':int(aligned),'label':'Aligned-host galaxy: main peak'},
              {'index':int(aliased),'label':'Primary-host galaxy: alias-dominated measurement'}]
    ref=pd.read_csv(OUT/'reference-redshift.csv')
    z=np.linspace(0,3.2,1601); pref=np.interp(z,ref.z,ref.pi_reference);pref/=np.trapezoid(pref,z)
    row=scene.iloc[normal];qs=pdz(z,[row.synthetic_t],[row.pdz_sigma_log1pz])[0]
    qr=qs*(1+z)*pref;qr/=np.trapezoid(qr,z)
    external=1+4*np.exp(-.5*((z-meta['scene']['aligned_z'])/.018)**2)
    aext=np.trapezoid(qr*external,z)
    zstar=round(meta['scene']['primary_z'],3); ap=.15*np.interp(zstar,z,qr)/np.interp(zstar,z,pref)
    allocation=float(ap/(ap+aext))
    fig,ax=chart('One PDZ, two competing intensity responses',
        f'Illustrative state: aP = {ap:.2f}, aE = {aext:.2f}, conditional allocation = {allocation:.2f}',
        'Possible redshift','Probability density / response integrand')
    ax.plot(z,qs,':',label='Source PDZ',lw=2)
    ax.plot(z,qr,'-',label='Reference-weighted response qᵢ',lw=2)
    ax.plot(z,qr*external,'--',label='External integrand qᵢ × H F',lw=2)
    ax.axvline(zstar,ls='-.',label='Candidate redshift');ax.set_xlim(.3,1.4);ax.set_ylim(bottom=0)
    ax.legend(frameon=False,fontsize=9,loc='upper right')
    save(fig,'pdz-response')

    # A deterministic quadrature cloud is a view of each full PDZ, not 25 galaxies.
    # Equal-probability nodes use the exact truncated mixture CDF, via bisection.
    qq=(np.arange(25)+.5)/25
    ids=np.flatnonzero(pair); tt=scene.synthetic_t.values[ids];ss=scene.pdz_sigma_log1pz.values[ids]
    cloud=np.zeros((len(ids),25))
    for j,target in enumerate(qq):
        low=np.zeros(len(ids));high=np.full(len(ids),3.2)
        mu=tt[:,None]-SHIFTS;sd=ss[:,None]*SCALES; base=ndtr(-mu/sd)
        norm=np.sum(WEIGHTS*(ndtr((np.log1p(3.2)-mu)/sd)-base),axis=1)
        for it in range(40):
            mid=(low+high)/2
            cf=np.sum(WEIGHTS*(ndtr((np.log1p(mid)[:,None]-mu)/sd)-base),axis=1)/norm
            low=np.where(cf<target,mid,low);high=np.where(cf>=target,mid,high)
        cloud[:,j]=(low+high)/2
    data={'schema':1,'meta':meta['scene'], 'groups':groups,
        'scene':{'id':scene.galaxy_id.tolist(),'row':scene.source_row.astype(int).tolist(),'x':roundlist(scene.x_arcmin,6),'y':roundlist(scene.y_arcmin,6),
                 'z':roundlist(scene.observed_redshift_gal,8),'h':roundlist(scene.h_ab,4),'p':pop.tolist(),
                 't':roundlist(scene.synthetic_t,9),'sigma':roundlist(scene.pdz_sigma_log1pz,9)},
        'maps':histograms,'profiles':profiles,'examples':examples,
        'cloud':{'indices':ids.tolist(),'z':roundlist(cloud,7),'nodes_per_galaxy':25,'weight_per_node':1/25},
        'reference':{'z':roundlist(z,5),'p':roundlist(pref,10)},
        'checks':{'full_map_mass':float(sum(np.sum(np.array(histograms['full']['mass'])[p]) for p in range(3))),
                  'objects':len(scene),'default_allocation':allocation,'profile_identity':True}}
    (OUT/'interactive-data.js').write_text('window.CLUSTER_DATA='+json.dumps(data,separators=(',',':'),ensure_ascii=False)+';\n')
    vendor=ROOT/'js/vendor';vendor.mkdir(exist_ok=True)
    (vendor/'plotly.min.js').write_text(get_plotlyjs())
    print(f'Built 6 static views, 3 interactive data groups, {len(scene):,} full synthetic PDZs.')
    print(f'Full map probability mass: {data["checks"]["full_map_mass"]:.6f}; expected {len(scene)}.')
    print(f'Default example aP={ap:.6f}, aE={aext:.6f}, allocation={allocation:.6f}.')

if __name__=='__main__':main()
