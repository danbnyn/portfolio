#!/usr/bin/env python3
"""Deterministic checks of the article's algebra and illustrative data.

These are NOT inference-pipeline tests, recovery experiments, or coverage tests.
Requires NumPy, pandas and SciPy. Run: python tools/check_math.py
"""
from __future__ import annotations
import json
from pathlib import Path
import unittest
import numpy as np
import pandas as pd
from numpy.polynomial.hermite import hermgauss
from numpy.testing import assert_allclose
from scipy.stats import multivariate_normal

ROOT = Path(__file__).resolve().parents[1]


class ArticleChecks(unittest.TestCase):
    def test_gaussian_exponential_tilt(self):
        C = np.array([[.6, .2, -.1], [.2, .8, .3], [-.1, .3, .9]])
        t = np.array([1., 0., 0.])
        y = np.array([.4, -.1, .2])
        tilted_log = multivariate_normal.logpdf(y, cov=C)+t@y-.5*t@C@t
        assert_allclose(tilted_log, multivariate_normal.logpdf(y, mean=C@t, cov=C))
        # The shifted mean changes absolute intensity covariance, not fractional covariance.
        m = np.exp(C[1:, 0])
        K = np.expm1(C[1:, 1:])
        self.assertFalse(np.allclose(m[:, None]*m[None, :]*K, K))

    def test_lognormal_moments_and_cox_variance(self):
        nodes, weights = hermgauss(100)
        v = np.log1p(.25)
        F = np.exp(np.sqrt(2*v)*nodes-v/2)
        w = weights/np.sqrt(np.pi)
        assert_allclose(w@F, 1, rtol=1e-12)
        assert_allclose(w@(F**2)-(w@F)**2, .25, rtol=1e-12)
        mu = 5+15*F
        assert_allclose(w@mu, 20)
        assert_allclose(w@mu+w@(mu**2)-(w@mu)**2, 76.25)
        C = np.array([[.49, .15], [.15, .64]])
        for j in range(2):
            for k in range(2):
                a = np.eye(2)[j]+np.eye(2)[k]
                moment = np.exp(.5*a@C@a-.5*C[j,j]-.5*C[k,k])
                assert_allclose(moment, np.exp(C[j,k]))

    def test_entrywise_log_is_not_psd_preserving(self):
        K = np.array([[1., 2.], [2., 4.]])
        self.assertGreaterEqual(np.linalg.eigvalsh(K).min(), -1e-12)
        C = np.log1p(K)
        self.assertLess(np.linalg.eigvalsh(C).min(), 0)
        assert_allclose(np.linalg.det(C), np.log(2)*np.log(5)-np.log(3)**2, atol=1e-12)
        assert_allclose(np.linalg.det(C), -.0914, atol=5e-5)

    def test_selection_bookkeeping(self):
        # k[x,y] is a normalized discrete measurement kernel.
        parent = np.array([2., 5., 3.])
        k = np.array([[.6,.3,.1], [.1,.5,.4], [.2,.2,.6]])
        s = np.array([0., .5, 1.])
        alpha = k@s
        selected = parent*alpha
        k_R = k*s[None, :]/alpha[:, None]
        assert_allclose(k.sum(axis=1), 1)
        assert_allclose(k_R.sum(axis=1), 1)
        observed_parent = s*(parent@k)
        observed_selected = selected@k_R
        assert_allclose(observed_parent, observed_selected)
        assert_allclose(observed_parent.sum(), selected.sum())
        # A second alpha changes the experiment rather than merely its notation.
        self.assertFalse(np.allclose((selected*alpha)@k_R, observed_parent))

    def test_joint_membership_and_exchange(self):
        P = np.array([2., 3., 1.])
        E = np.array([6., 1., 4.])
        c = np.array([.3, 2., 7.])
        assert_allclose(P/(P+E), (c*P)/(c*P+c*E))
        delta_logL = np.log(c*(P+E)).sum()-np.log(P+E).sum()
        assert_allclose(delta_logL, np.log(c).sum())
        p = np.array([1., 8.]); e = np.array([1., 2.])
        self.assertNotAlmostEqual(np.mean(p/(p+e)), np.mean(p)/(np.mean(p)+np.mean(e)))
        # Exchange keeps total intensity and total expected count fixed.
        u = np.array([.1,.3,.6]); background = np.array([2.,3.,1.])
        richness, exchange = 10., 2.
        assert_allclose(richness*u+background, (richness-exchange)*u+background+exchange*u)

    def test_actual_retained_prior_loading(self):
        x = (np.arange(64)+.5)*.125
        for ell in (.35,1.4):
            C = .49*np.exp(-.5*((x[:,None]-x[None,:])/ell)**2)+1e-10*np.eye(64)
            B = np.linalg.cholesky(C)
            assert_allclose(B@B.T, C, atol=1e-14)
            assert_allclose(np.sum(B**2,axis=1), np.diag(C), atol=1e-14)
            self.assertGreater(np.linalg.eigvalsh(C).min(), 0)

    def test_fixed_scene_and_provenance(self):
        d = pd.read_csv(ROOT/'assets/cluster/scene.csv')
        meta = json.loads((ROOT/'assets/cluster/provenance.json').read_text())
        self.assertEqual(len(d), meta['selected_rows'])
        self.assertEqual(len(d), 2737)
        self.assertTrue(d.source_row.is_unique)
        self.assertTrue((d.x_arcmin.abs()<6).all())
        self.assertTrue((d.y_arcmin.abs()<6).all())
        self.assertTrue((d.h_ab<22.5).all())
        for name, key, expected in [('illustrative','selected_primary_rows',160),
                                    ('nearby','selected_nearby_rows',35),
                                    ('foreground','selected_foreground_rows',33)]:
            self.assertEqual((d.halo_id==int(meta[f'{name}_halo_id'])).sum(), expected)
            self.assertEqual(meta[key], expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
