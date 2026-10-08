import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dataclasses import replace
import numpy as np
import pytest
import pytensor
import pytensor.tensor as pt
from scipy.stats import multivariate_normal, norm
from scipy.special import logsumexp
from rp001.data import generate_synthetic, LandmarkData
from rp001.model import symbolic_terms,numpy_terms,covariance,prior_draws
from rp001.metrics import correction,conformal_rank,interval_score,apply_correction
from rp001.prediction import mixture_quantile
def pack(p):
    return np.r_[p["beta"],p["gamma"],p["Gamma"].ravel(),p["tau"],p["r_g"],p["sigma_z"],p["sigma_r"],p["rho"]]
def unpack(v):
    return {"beta":v[:2],"gamma":v[2:4],"Gamma":v[4:8].reshape((2,2)),
            "tau":v[8:10],"r_g":v[10],"sigma_z":v[11],"sigma_r":v[12],"rho":v[13]}
def dense_joint_logp(d,p,error="normal"):
    S=covariance(p); B=d.B; w=len(B)
    K=p["rho"]**np.abs(np.arange(w)[:,None]-np.arange(w)[None,:])
    Czz=B@S@B.T+p["sigma_z"]**2*K
    czy=B@S@p["gamma"]
    m0=d.a@p["Gamma"].T
    means=np.column_stack((m0@B.T,d.a@p["beta"]+m0@p["gamma"]))
    def component(multiplier):
        cyy=p["gamma"]@S@p["gamma"]+multiplier*p["sigma_r"]**2
        C=np.block([[Czz,czy[:,None]],[czy[None,:],np.array([[cyy]])]])
        return np.array([multivariate_normal.logpdf(np.r_[d.z[i],d.y[i]],mean=means[i],cov=C) for i in range(len(d.ids))])
    if error=="contamination":
        return logsumexp(np.stack((np.log(.95)+component(1),np.log(.05)+component(9))),axis=0)
    return component(1)
@pytest.mark.parametrize("w,rho",[(1,0),(2,-.5),(30,0),(30,.5),(30,.9),(30,.99)])
@pytest.mark.parametrize("error",["normal","contamination"])
def test_joint_likelihood_against_dense_scipy(w,rho,error):
    d,p=generate_synthetic(5,123+int(rho*10),rho,w=w)
    v=pt.dvector("theta")
    symbolic=symbolic_terms(d,unpack(v),error)
    f=pytensor.function([v],symbolic[:2],mode="FAST_COMPILE")
    lz,ly=f(pack(p))
    nz,ny,*_=numpy_terms(d,p,error)
    oracle=dense_joint_logp(d,p,error)
    np.testing.assert_allclose(lz+ly,oracle,atol=1e-8,rtol=1e-10)
    np.testing.assert_allclose(nz+ny,oracle,atol=1e-8,rtol=1e-10)
@pytest.mark.parametrize("rho",[0,.5,.9])
def test_autodiff_likelihood_gradient(rho):
    d,p=generate_synthetic(8,9101,rho)
    v=pt.dvector("theta")
    lz,ly,*_=symbolic_terms(d,unpack(v))
    f=pytensor.function([v],pt.grad(pt.sum(lz+ly),v),mode="FAST_COMPILE")
    x=pack(p); h=1e-5
    finite=[]
    for j in range(len(x)):
        plus=x.copy(); minus=x.copy()
        plus[j]+=h;minus[j]-=h
        finite.append((dense_joint_logp(d,unpack(plus)).sum()-dense_joint_logp(d,unpack(minus)).sum())/(2*h))
    np.testing.assert_allclose(f(x),finite,rtol=1e-4,atol=1e-4)
def test_conditional_density_does_not_use_outcome():
    d,p=generate_synthetic(5,321)
    a=numpy_terms(d,p)
    b=numpy_terms(replace(d,y=None),p)
    np.testing.assert_array_equal(a[0],b[0])
    np.testing.assert_array_equal(a[2],b[2])
    np.testing.assert_array_equal(a[3],b[3])
def test_calibration_rank_ties_and_nonshrinking():
    assert conformal_rank(25)==24 and conformal_rank(9)==9 and conformal_rank(8)==9
    assert correction(np.arange(25.))==23.
    assert correction(np.full(25,-2.))==0.
    assert np.isinf(correction(np.arange(8.)))
    assert correction(np.ones(25))==1.
    assert conformal_rank(19)==18 and conformal_rank(99)==90
def test_interval_score_asymmetric_misses():
    np.testing.assert_array_equal(interval_score(np.array([15,5,25]),np.full(3,10),np.full(3,20)),[10,110,110])
def test_support_clipping_membership():
    for q in [0,2,10]:
        L,U=apply_correction(np.array([-5.,10]),np.array([5.,20]),q)
        y=np.arange(0,31)
        for j in range(2):
            assert np.array_equal((np.array([-5.,10])[j]-q<=y)&(y<=np.array([5.,20])[j]+q),(L[j]<=y)&(y<=U[j]))
def test_single_component_quantiles_are_lognormal():
    for q in [.05,.5,.95]:
        result=mixture_quantile(np.array([4.]),np.array([.25]),np.array([1.]),q)
        np.testing.assert_allclose(result,np.exp(4+.5*norm.ppf(q)),rtol=1e-9)
def test_lkj_two_dimensional_prior_variance():
    r=np.array([p["r_g"] for p in prior_draws(20000,111)])
    assert abs(r.mean())<.02 and abs(r.var()-.2)<.015
