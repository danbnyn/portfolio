#!/usr/bin/env python3
"""Reproduce the Flagship catalogue diagnostics, not a cluster-refinement fit.

python tools/analyse_flagship.py /path/to/flagship_hp4x2.csv.gz --cache /path/to/cache

The input unit header and completeness mask were not supplied. This implementation
adopts the explicit conventions in the article and records them in provenance.
A north-polar-cap HEALPix helper is intentionally limited to this two-pixel input.
RAM and scratch requirements are a few GB; no network or astropy/healpy is needed.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,tempfile
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import PchipInterpolator
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter1d

ROOT=Path(__file__).resolve().parents[1]
def read_catalogue(source:Path,cache:Path):
    cache.mkdir(parents=True,exist_ok=True)
    with source.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    audit_file=cache/'catalogue_audit.json'
    if audit_file.exists():
        audit=json.loads(audit_file.read_text())
        if audit.get('sha256')==digest and all((cache/p).exists() for p in ['selected.pkl','centres.pkl']):
            print('Reusing checksum-matched local cache.',flush=True)
            return pd.read_pickle(cache/'selected.pkl'),pd.read_pickle(cache/'centres.pkl'),audit
    cols=['halo_id','galaxy_id','kind','ra_gal','dec_gal','observed_redshift_gal','euclid_nisp_h','lm_halo','true_redshift_halo','conc_vir_halo','rs_halo','rvir_halo','hpix_29_nest']
    header=pd.read_csv(source,nrows=0).columns
    if set(cols)-set(header):raise ValueError('Required catalogue columns are missing.')
    parts=[];centres=[];n=0;bad=0;bounds={};kinds={}
    for d in pd.read_csv(source,usecols=cols,chunksize=300000):
        d.insert(0,'source_row',np.arange(n,n+len(d),dtype=np.int64));n+=len(d)
        for k,v in d.kind.value_counts().items():kinds[str(k)]=kinds.get(str(k),0)+int(v)
        for key in ['ra_gal','dec_gal','observed_redshift_gal','true_redshift_halo','euclid_nisp_h','lm_halo','rvir_halo']:
            lo,hi=bounds.get(key,[float('inf'),float('-inf')]);bounds[key]=[min(lo,float(d[key].min())),max(hi,float(d[key].max()))]
        h=-2.5*np.log10(d.euclid_nisp_h.where(d.euclid_nisp_h>0))-48.6
        bad+=int((~np.isfinite(h)).sum());d['h_ab']=h
        centres.append(d.loc[(d.kind==0)&(h<24)].copy());parts.append(d.loc[h<24].copy())
        print(f'Read {n:,} rows.',flush=True)
    s=pd.concat(parts,ignore_index=True);c=pd.concat(centres,ignore_index=True)
    if c.halo_id.duplicated().any():raise ValueError('Multiple selected central rows for one halo.')
    audit={'source':source.name,'sha256':digest,'rows':n,'columns':len(header),'h24_rows':len(s),'centres_all':kinds.get('0',0),'centres_h24':len(c),'kind_counts':kinds,'bounds':bounds,'nonpositive_or_invalid_h_flux':bad,'massive_centres_lm14':int((c.lm_halo>=14).sum()),'h_flux_units_status':'Inherited cgs f_nu convention; source unit metadata not supplied.'}
    s.to_pickle(cache/'selected.pkl');c.to_pickle(cache/'centres.pkl');audit_file.write_text(json.dumps(audit,indent=2))
    return s,c,audit

H=.67; OM=.319; C=299792.458
zz=np.linspace(0,3.2,32001); cc=cumulative_trapezoid(C/100/np.sqrt(OM*(1+zz)**3+1-OM),zz,initial=0); chi=PchipInterpolator(zz,cc)
def unit(ra,dec):
 a=np.deg2rad(ra);d=np.deg2rad(dec)
 return np.column_stack([np.cos(d)*np.cos(a),np.cos(d)*np.sin(a),np.sin(d)])
def hp4(ra,dec):
 # North polar-cap ang2pix, nested nside=16; valid for this footprint.
 z=np.sin(np.deg2rad(dec)); tt=np.mod(np.asarray(ra)/90.,4.)
 if np.any(z<=2/3): raise ValueError('Only northern polar cap is supported by this footprint helper.')
 nt=np.floor(tt).astype(int);tp=tt-nt;tmp=16*np.sqrt(3*(1-z))
 jp=np.minimum(np.floor(tp*tmp).astype(int),15); jm=np.minimum(np.floor((1-tp)*tmp).astype(int),15)
 ix=15-jm;iy=15-jp;id=np.zeros_like(ix)
 for b in range(4):id|=((ix>>b)&1)<<(2*b);id|=((iy>>b)&1)<<(2*b+1)
 return nt*256+id
def inside_aperture(ra,dec,radius):
 # Great-circle circle at 1% extra radius, densely sampled: conservative boundary check.
 a=np.deg2rad(ra);d=np.deg2rad(dec); r=np.asarray(radius)*1.01
 t=np.linspace(0,2*np.pi,2048,endpoint=False)
 ds=np.arcsin(np.sin(d)*np.cos(r)+np.cos(d)*np.sin(r)*np.cos(t))
 aa=a+np.arctan2(np.sin(t)*np.sin(r)*np.cos(d),np.cos(r)-np.sin(d)*np.sin(ds))
 return bool(np.isin(hp4(np.rad2deg(aa),np.rad2deg(ds)),[702,703]).all())

def measure(source:Path,cache:Path,O:Path):
    O.mkdir(parents=True,exist_ok=True)
    s,c,audit=read_catalogue(source,cache)
    assert np.array_equal(hp4(s.ra_gal.values[::101],s.dec_gal.values[::101]),s.hpix_29_nest.values[::101]>>(2*(29-4)))
    cv=unit(c.ra_gal.values,c.dec_gal.values);sv=unit(s.ra_gal.values,s.dec_gal.values)
    st=cKDTree(sv);cm=c[c.lm_halo>=np.log10(1e14*H)].copy()
    cm['m_msun']=10**cm.lm_halo/H;cm['chi_mpc_h']=chi(cm.true_redshift_halo);cm['rvir_cmpc_h']=cm.rvir_halo/1000;cm['theta_vir']=cm.rvir_cmpc_h/cm.chi_mpc_h
    cm['interior']=[inside_aperture(a,d,5*t) if z>.08 else False for a,d,t,z in zip(cm.ra_gal,cm.dec_gal,cm.theta_vir,cm.true_redshift_halo)]
    print('centres >=1e14Msun',len(cm),'interior',cm.interior.sum(),flush=True)
    # Stack retained halos with fixed equal-halo weighting, 0.4<z<1; focus selectors later.
    halos=cm[cm.interior & cm.true_redshift_halo.between(.4,1.,inclusive='left')].copy().sort_values('halo_id').reset_index(drop=True)
    edges=np.geomspace(.1,5,19);mid=np.sqrt(edges[:-1]*edges[1:]);n=len(halos);nb=len(mid)
    cnt=np.zeros((n,3,nb),int);rand=np.zeros((n,nb));envvar=[]
    sz=s.observed_redshift_gal.to_numpy();sh=s.halo_id.to_numpy();sr=s.ra_gal.to_numpy();sd=s.dec_gal.to_numpy();rng=np.random.default_rng(260923)
    schi=chi(sz); depth=20.0
    # Real-space halo CENTRE positions, not fabricated true galaxy coordinates.
    hxyz=cv*chi(c.true_redshift_halo.to_numpy())[:,None];ht=cKDTree(hxyz); hc=np.zeros((n,nb),int)
    for i,row in enumerate(halos.itertuples()):
     vv=unit([row.ra_gal],[row.dec_gal])[0];r=row.rvir_cmpc_h;ch=row.chi_mpc_h
     ids=np.array(st.query_ball_point(vv,2*np.sin(5*r/ch/2)),dtype=int)
     angle=2*np.arcsin(np.minimum(np.linalg.norm(sv[ids]-vv,axis=1)/2,1));x=ch*angle/r
     # Redshift-space cylinder around observed central redshift (preserves velocity zero-point).
     keep=np.abs(schi[ids]-chi(row.observed_redshift_gal))<depth
     idx=ids[keep];xx=x[keep];prim=sh[idx]==row.halo_id
     cnt[i,0]=np.histogram(xx,edges)[0];cnt[i,1]=np.histogram(xx[prim],edges)[0];cnt[i,2]=np.histogram(xx[~prim],edges)[0]
     # 12 uniform-solid-angle reference apertures, matched z and radius. Can overlap.
     rr=[];nt=0
     while len(rr)<12 and nt<10000:
      nt+=1;ra=rng.uniform(180,190);dec=np.rad2deg(np.arcsin(rng.uniform(np.sin(np.deg2rad(57.3)),np.sin(np.deg2rad(66.5)))))
      if int(hp4(np.array([ra]),np.array([dec]))[0]) not in [702,703]:continue
      if not inside_aperture(ra,dec,5*r/ch):continue
      v=unit([ra],[dec])[0];ii=np.array(st.query_ball_point(v,2*np.sin(5*r/ch/2)),dtype=int)
      k=np.abs(schi[ii]-chi(row.observed_redshift_gal))<depth;ii=ii[k]
      xxr=ch*2*np.arcsin(np.minimum(np.linalg.norm(sv[ii]-v,axis=1)/2,1))/r
      rr.append(np.histogram(xxr,edges)[0])
     if len(rr)!=12:raise RuntimeError('Reference sampling failed')
     rand[i]=np.mean(rr,axis=0)
     # Remove the conditioning centre only here; all other observable centres remain.
     pos=vv*ch;ii=np.array(ht.query_ball_point(pos,5*r),dtype=int);xxh=np.linalg.norm(hxyz[ii]-pos,axis=1)/r
     hc[i]=np.histogram(xxh[xxh>1e-6],edges)[0]
     if i%25==0:print('stack',i,'/',n,flush=True)
    area=np.pi*(edges[1:]**2-edges[:-1]**2)[None,:]*halos.rvir_cmpc_h.values[:,None]**2
    vol=4*np.pi/3*(edges[1:]**3-edges[:-1]**3)[None,:]*halos.rvir_cmpc_h.values[:,None]**3
    # Reference halo-centre number density in redshift slabs in the adopted 2-pixel footprint.
    solid=2*4*np.pi/(12*16**2);zcent=c.true_redshift_halo.to_numpy();dens=[]
    for z in halos.true_redshift_halo:
     lo=max(0,z-.025);hi=z+.025; vv=solid/3*(chi(hi)**3-chi(lo)**3);dens.append(np.count_nonzero((zcent>=lo)&(zcent<hi))/vv)
    dens=np.array(dens); hratio=hc/vol/dens[:,None]
    # flatten tidy data for complete reproducibility, keep integer halo ids as strings in JSON.
    records=[]
    for i,row in enumerate(halos.itertuples()):
     for j in range(nb):
      records.append({'halo_id':str(row.halo_id),'mass_msun':row.m_msun,'z_halo':row.true_redshift_halo,'rvir_cmpc_h':row.rvir_cmpc_h,'r_lo_rvir':edges[j],'r_hi_rvir':edges[j+1],'r_mid_rvir':mid[j],'total_n':int(cnt[i,0,j]),'primary_n':int(cnt[i,1,j]),'environment_n':int(cnt[i,2,j]),'annulus_area_cmpc2_h2':area[i,j],'random_mean_n':rand[i,j],'other_central_n':int(hc[i,j]),'shell_volume_cmpc3_h3':vol[i,j],'central_reference_density':dens[i]})
    pd.DataFrame(records).to_csv(O/'profiles-per-halo.csv',index=False,float_format='%.9g')
    halos.to_csv(O/'profile-centres.csv',index=False,float_format='%.9g')
    np.savez_compressed(O/'profiles.npz',edges=edges,mid=mid,counts=cnt,random=rand,area=area,volume=vol,hcent=hc,hcentre_ratio=hratio,mass=halos.m_msun.values,z=halos.true_redshift_halo.values,rvir=halos.rvir_cmpc_h.values)
    # Default narrow slice limits both mass and redshift mixing; broad alternatives are exploratory.
    sel=(halos.m_msun.values<3e14)&(halos.true_redshift_halo.values>=.5)&(halos.true_redshift_halo.values<.8)
    print('DEFAULT HALOS',sel.sum(),flush=True)
    # Select scene now; use no redshift cut for the actual figure subset.
    pid=4039480311176;nid=4039470670730
    p=c[c.halo_id==pid].iloc[0];q=c[c.halo_id==nid].iloc[0]
    pz=p.true_redshift_halo;nz=q.true_redshift_halo
    sep=float(np.hypot(60*(q.ra_gal-p.ra_gal)*np.cos(np.deg2rad(p.dec_gal)),60*(q.dec_gal-p.dec_gal)))
    ra0=p.ra_gal;dec0=p.dec_gal
    xx=60*(s.ra_gal-ra0)*np.cos(np.deg2rad(dec0));yy=60*(s.dec_gal-dec0)
    mask=(abs(xx)<6)&(abs(yy)<6);scene=s.loc[mask].copy();scene['x_arcmin']=xx[mask];scene['y_arcmin']=yy[mask]
    # Stable local RNG creates noisy measurements in s=ln(1+z), including rare aliases.
    rng=np.random.default_rng(271828);ns=len(scene);sigma=.015+.035*np.clip((scene.h_ab.values-20)/4,0,1);a=rng.choice([-1,0,1],ns,p=[.04,.92,.04]);noise=rng.normal(size=ns);scale=np.where(a==0,1,1.5)
    scene['pdz_sigma_log1pz']=sigma;scene['synthetic_t']=np.log1p(scene.observed_redshift_gal.values)+a*.25+scale*sigma*noise
    scene['synthetic_error_alias']=a;scene['population']=np.where(scene.halo_id==pid,'Primary',np.where(scene.halo_id==nid,'Aligned halo','Other hosts'))
    scene.to_csv(O/'scene.csv',index=False,float_format='%.10g')
    meta=audit.copy();meta.update({'area_deg2':solid*(180/np.pi)**2,'adopted_hp_order':4,'adopted_hp_nested_ids':[702,703],'cosmology':{'h':H,'Omega_m':OM,'Omega_lambda':1-OM,'distance_approximation':'flat matter+Lambda; ignore small separate radiation/neutrino expansion terms for illustration'},'radius_convention':'rvir_halo /1000 interpreted as comoving Mpc/h; supported by internal spherical-overdensity consistency, no export unit header supplied','mass_convention':'lm_halo=log10(M/(Msun/h)); physical mass=10**lm_halo/h; inherited Flagship/ROCKSTAR convention','h_flux_convention':'cgs f_nu, H_AB=-2.5log10(flux)-48.6; inherited from draft and consistent with exact H<24 limit','mass_cut_physical_msun':1e14,'massive_centres':len(cm),'massive_interior_centres':int(cm.interior.sum()),'profile_halos':n,'profile_z_limits':[.4,1.0],'profile_default_halos':int(sel.sum()),'profile_default_mass_limits_msun':[1e14,3e14],'profile_default_z_limits':[.5,.8],'radial_edges_rvir':edges.tolist(),'los_half_depth_cmpc_h':depth,'random_apertures_per_halo':12,'profile_seed':260923,'halo_centre_reference':'central galaxies selected H<24; true halo redshift; density reference in z+-0.025 slice; no real-space galaxy positions inferred','profile_uncertainty':'between-halo spread, not standard error or inferred latent covariance; overlapping apertures and varying mass/z remain','scene':{'primary_id':str(pid),'aligned_id':str(nid),'primary_z':float(pz),'aligned_z':float(nz),'angular_separation_arcmin':float(sep),'ra0_deg':float(ra0),'dec0_deg':float(dec0),'half_width_arcmin':6,'rows':ns,'primary_rows':int((scene.halo_id==pid).sum()),'aligned_rows':int((scene.halo_id==nid).sum()),'selection':'H<24; abs(x)<6arcmin, abs(y)<6arcmin; no redshift selection','synthetic_pdz':{'seed':271828,'variable':'s=ln(1+z)','sigma_formula':'.015+.035*clip((H-20)/4,0,1)','weights':[.04,.92,.04],'alias_shifts':[-.25,0,.25],'scale_factors':[1.5,1,1.5],'source_prior':'uniform in s on 0<z<3.2, density in z proportional to 1/(1+z)','status':'new illustrative full PDZ distributions, not supplied or validated Euclid photo-zs'}},'figure_status':'empirical mock diagnostics and explicitly synthetic PDZ illustrations; no pipeline inference or performance results'})
    
    meta['scene']['choice']='Deliberately chosen aligned halo pair after inspecting the catalogue, not a representative validation sample.'
    zedges=np.linspace(0,3.2,801);ct=np.histogram(s.observed_redshift_gal,zedges)[0];zmid=(zedges[:-1]+zedges[1:])/2
    reference=gaussian_filter1d(ct.astype(float),3);reference=np.maximum(reference,1e-8);reference/=np.trapezoid(reference,zmid)
    pd.DataFrame({'z':zmid,'pi_reference':reference}).to_csv(O/'reference-redshift.csv',index=False,float_format='%.10g')
    meta['reference_visualization']={'source':'entire supplied H<24 catalogue, observed_redshift_gal','grid_edges':[0,3.2],'bins':800,'gaussian_smoothing_bins':3,'normalization':'unit integral over midpoint grid','status':'mock-derived fixed teaching reference, not independently calibrated survey n(z)'}
    # Independent consistency check, not a substitute for missing export unit metadata.
    a=c[c.lm_halo>=14];z=a.true_redshift_halo.to_numpy();ez2=OM*(1+z)**3+1-OM;delta=18*np.pi**2+82*(OM*(1+z)**3/ez2-1)-39*(OM*(1+z)**3/ez2-1)**2
    r_expected=(3*10**a.lm_halo.to_numpy()/(4*np.pi*delta*2.77536627e11*ez2))**(1/3)*(1+z)
    ratio=r_expected/(a.rvir_halo.to_numpy()/1000)
    meta['radius_units_status']='Adopted comoving h^-1 kpc; internally consistent, export metadata not supplied.'
    meta['radius_consistency_check']={'method':'Bryan-Norman spherical-collapse overdensity relative to critical density; expected comoving radius divided by exported radius/1000','halo_lm_min':14,'n':len(a),'median_ratio':float(np.median(ratio)),'p10_ratio':float(np.quantile(ratio,.1)),'p90_ratio':float(np.quantile(ratio,.9)),'status':'Internal cross-check only; cannot independently authenticate export units.'}
    meta['pdz_display']={'map':'exact truncated-mixture CDF differences; no display-window renormalization','cloud':'25 deterministic equal-probability nodes per highlighted galaxy, weight 1/25; finite visualization, full analytic PDZ is retained','inference_status':'No posterior fit or validation result.'}
    (O/'provenance.json').write_text(json.dumps(meta,indent=2))
    print(json.dumps({'profile_halos':n,'default_halos':int(sel.sum()),'scene_rows':ns,'radius_check':meta['radius_consistency_check']},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'assets/cluster')
    parser.add_argument('--cache',type=Path,help='Trusted local pickle cache; validated against the input SHA256.')
    args=parser.parse_args()
    if not args.source.is_file():parser.error('Input catalogue not found.')
    if args.cache:measure(args.source,args.cache,args.output)
    else:
        with tempfile.TemporaryDirectory(prefix='flagship-') as tmp:measure(args.source,Path(tmp),args.output)
