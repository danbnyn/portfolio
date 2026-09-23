#!/usr/bin/env python3
"""Numerical regression checks for the article's explicit finite models.

These tests validate identities and retained data products; they do not establish
cluster-parameter recovery or calibrated membership probabilities.
"""
from pathlib import Path
import json,unittest
import numpy as np
import pandas as pd
from scipy.special import ndtr
from make_figures import pdz,SHIFTS,SCALES,WEIGHTS

ROOT=Path(__file__).resolve().parents[1];A=ROOT/'assets/cluster'
class ScientificChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene=pd.read_csv(A/'scene.csv',dtype={'halo_id':str})
        cls.profiles=pd.read_csv(A/'profiles-per-halo.csv',dtype={'halo_id':str})
        cls.meta=json.loads((A/'provenance.json').read_text())
    def test_selection_and_counts(self):
        s=self.scene
        self.assertEqual(len(s),7341)
        self.assertTrue((s.h_ab<24).all())
        self.assertTrue((abs(s.x_arcmin)<6).all() and (abs(s.y_arcmin)<6).all())
        self.assertEqual(s.population.value_counts().to_dict(),{'Other hosts':7062,'Primary':183,'Aligned halo':96})
        self.assertEqual(s.source_row.nunique(),len(s))
    def test_flux_magnitude(self):
        np.testing.assert_allclose(self.scene.h_ab,-2.5*np.log10(self.scene.euclid_nisp_h)-48.6,rtol=0,atol=6e-9)
    def test_full_pdz_mass_and_positive_bins(self):
        s=self.scene
        mass=np.diff(pdz(np.linspace(0,3.2,321),s.synthetic_t,s.pdz_sigma_log1pz,True),axis=1)
        self.assertGreaterEqual(mass.min(),-1e-14)
        np.testing.assert_allclose(mass.sum(axis=1),1,atol=2e-13)
        near=np.diff(pdz(np.array([.58,.94]),s.synthetic_t,s.pdz_sigma_log1pz,True),axis=1)[:,0]
        self.assertTrue(np.any((near>0)&(near<.9)))
    def test_pdf_is_derivative_of_cdf(self):
        s=self.scene.iloc[::137];z=np.linspace(.001,3.199,1500);eps=1e-5
        d=(pdz(z+eps,s.synthetic_t,s.pdz_sigma_log1pz,True)-pdz(z-eps,s.synthetic_t,s.pdz_sigma_log1pz,True))/(2*eps)
        np.testing.assert_allclose(d,pdz(z,s.synthetic_t,s.pdz_sigma_log1pz),atol=2e-6,rtol=2e-6)
    def test_source_prior_removal(self):
        s=self.scene.iloc[::137];z=np.linspace(0,3.2,400)
        mu=s.synthetic_t.values[:,None]-SHIFTS;sd=s.pdz_sigma_log1pz.values[:,None]*SCALES
        norm=np.sum(WEIGHTS*(ndtr((np.log1p(3.2)-mu)/sd)-ndtr(-mu/sd)),axis=1)
        native=np.sum(WEIGHTS*np.exp(-.5*((np.log1p(z)[None,:,None]-mu[:,None,:])/sd[:,None,:])**2)/(np.sqrt(2*np.pi)*sd[:,None,:]),axis=2)
        np.testing.assert_allclose(pdz(z,s.synthetic_t,s.pdz_sigma_log1pz)*(1+z)*norm[:,None],native,atol=1e-13)
    def test_reference_compression_preserves_likelihood(self):
        s=self.scene.iloc[::211];z=np.linspace(0,3.2,16001);ref=pd.read_csv(A/'reference-redshift.csv')
        rho=140*np.interp(z,ref.z,ref.pi_reference)
        ell=pdz(z,s.synthetic_t,s.pdz_sigma_log1pz)*(1+z)
        Z=np.trapezoid(ell*rho,z,axis=1);q=ell*rho/Z[:,None]
        np.testing.assert_allclose(np.trapezoid(q,z,axis=1),1,atol=1e-13)
        j=np.argmin(abs(z-.768));enhance=1+4*np.exp(-.5*((z-.739677)/.018)**2);amp=21
        raw=amp*ell[:,j]+np.trapezoid(ell*rho*enhance,z,axis=1)
        compressed=amp*q[:,j]/rho[j]+np.trapezoid(q*enhance,z,axis=1)
        np.testing.assert_allclose(raw/Z,compressed,rtol=2e-13,atol=2e-13)
    def test_profiles_have_exact_decomposition(self):
        p=self.profiles
        np.testing.assert_array_equal(p.total_n,p.primary_n+p.environment_n)
        self.assertEqual(p.halo_id.nunique(),339)
        narrow=p[(p.mass_msun<3e14)&(p.z_halo>=.5)&(p.z_halo<.8)]
        self.assertEqual(narrow.halo_id.nunique(),162)
        self.assertEqual(len(p),339*18)
        self.assertTrue((p.mass_msun>=1e14).all())
        self.assertTrue((p.r_lo_rvir>=.1-1e-12).all() and (p.r_hi_rvir<=5).all())
        np.testing.assert_allclose(p.annulus_area_cmpc2_h2,np.pi*p.rvir_cmpc_h**2*(p.r_hi_rvir**2-p.r_lo_rvir**2),rtol=8e-8)
    def test_galaxies_are_not_halo_centres(self):
        p=self.profiles;inner=p[p.r_hi_rvir<.8]
        self.assertEqual(int(inner.other_central_n.sum()),0)
        self.assertGreater(int(inner.environment_n.sum()),0)
        self.assertGreater(int(p.loc[p.r_lo_rvir>1,'primary_n'].sum()),0)
    def test_mass_and_radius_conventions(self):
        self.assertAlmostEqual(np.log10(.67*1e14),13.826074802700826)
        self.assertEqual(self.meta['massive_centres'],715)
        r=self.meta['radius_consistency_check'];self.assertLess(abs(r['median_ratio']-1),.001)
        self.assertTrue(r['p10_ratio']>.99 and r['p90_ratio']<1.01)
    def test_entrywise_log_need_not_be_psd(self):
        K=np.array([[1.,2.],[2.,4.]])
        self.assertGreaterEqual(np.linalg.eigvalsh(K).min(),-1e-14)
        self.assertLess(np.linalg.det(np.log1p(K)),0)
    def test_lognormal_compensation_and_cox_variance(self):
        rng=np.random.default_rng(73129);variance=np.log1p(.25)
        F=np.exp(rng.normal(0,np.sqrt(variance),400000)-variance/2)
        self.assertLess(abs(F.mean()-1),.004)
        self.assertLess(abs(F.var()-.25),.004)
        n=rng.poisson(5+15*F)
        self.assertLess(abs(n.mean()-20),.06)
        self.assertLess(abs(n.var()-76.25),1.4)
    def test_gaussian_tilt(self):
        C=np.array([[.4,.13],[.13,.6]]);t=np.array([1.,0.]);x=np.array([[.2,-.1],[-.4,.8],[1.2,-.5]])
        inv=np.linalg.inv(C);shift=C@t
        lhs=-.5*np.einsum('ni,ij,nj->n',x,inv,x)+x@t-.5*t@C@t
        rhs=-.5*np.einsum('ni,ij,nj->n',x-shift,inv,x-shift)
        np.testing.assert_allclose(lhs,rhs,atol=1e-14)
    def test_allocation_average_order(self):
        primary=np.array([.1,10.]);external=np.array([.9,1.])
        posterior_average=np.mean(primary/(primary+external))
        ratio_of_means=primary.mean()/(primary.mean()+external.mean())
        self.assertGreater(abs(posterior_average-ratio_of_means),.3)
    def test_integrate_before_log(self):
        intensity=np.array([1.,9.]);weights=np.array([.5,.5])
        self.assertGreater(np.log(weights@intensity),weights@np.log(intensity))
if __name__=='__main__':unittest.main(verbosity=2)
