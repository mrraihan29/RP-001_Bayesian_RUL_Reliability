import numpy as np
from dataclasses import replace
from rp001.data import generate_synthetic,truth_parameters
from rp001.model import numpy_terms,covariance
from rp001.v04_predict import sensor_terms
from rp001.metrics import conformal_rank,interval_score
from rp001.v04_precision import estimate_mixture_quantile_mcse
from scipy.stats import norm

def test_vector_predict_against_dense_scipy():
    data,_=generate_synthetic(7,170);data=replace(data,y=None)
    pars=[truth_parameters(rho) for rho in (-.5,0,.5,.95,.99)]
    p={k:np.asarray([x[k] for x in pars]) for k in pars[0]}
    lz,mu,var=sensor_terms(p,data,batch=2)
    for j,param in enumerate(pars):
        a,b,c,d,v=numpy_terms(data,param)
        np.testing.assert_allclose(lz[j],a,rtol=1e-8,atol=1e-8)
        np.testing.assert_allclose(mu[j],c,rtol=1e-8,atol=1e-8)
        np.testing.assert_allclose(var[j],d,rtol=1e-8,atol=1e-8)

def test_generic_covariance_inversion_identifiability():
    for rho in (-.5,0,.5,.9,.95,.99):
        p=truth_parameters(rho);w=30;B=np.column_stack((np.ones(w),np.arange(-29,1)/30))
        D=np.diff(np.eye(w),n=2,axis=0);S=covariance(p);K=rho**np.abs(np.arange(w)[:,None]-np.arange(w)[None,:])
        C=B@S@B.T+p['sigma_z']**2*K;DC=D@C@D.T
        c2=DC[0,2];c3=DC[0,3];rhat=c3/c2
        np.testing.assert_allclose(rhat,rho,atol=2e-6)
        sz2=c2/(1-rhat)**4
        np.testing.assert_allclose(sz2,p['sigma_z']**2,rtol=1e-3)
        pinv=np.linalg.pinv(B);recovered=pinv@(C-p['sigma_z']**2*K)@pinv.T
        np.testing.assert_allclose(recovered,S,atol=1e-9)
        cross=B@S@p['gamma'];gamma=np.linalg.solve(recovered,pinv@cross)
        np.testing.assert_allclose(gamma,p['gamma'],atol=1e-9)
        cYY=p['gamma']@S@p['gamma']+p['sigma_r']**2
        np.testing.assert_allclose(cYY-gamma@recovered@gamma,p['sigma_r']**2)

def test_ratio_influence_density_delta_independent_formula():
    rng=np.random.default_rng(987);theta=rng.normal(size=(4,2000));mu=np.log(100)+.2*theta;var=np.full_like(mu,.09);lw=-.5*(1-theta)**2
    res=estimate_mixture_quantile_mcse(mu,var,lw,.95,tail_probability=.000333333333,batch_sizes=(250,500))
    w=np.exp(lw-lw.max());q=res['quantile_log_rul'];F=norm.cdf((q-mu)/.3);h=w*(F-.95);f=np.sum(w*norm.pdf((q-mu)/.3)/.3)/w.sum()
    for r in res['batch_size_results']:
        b=r['batch_size'];means=h.reshape(4,-1,b).mean(axis=2)
        lrv=b*means.var(axis=1,ddof=1)
        direct=np.exp(q)*np.sqrt(lrv.sum()*2000)/(8000*w.mean()*f)
        np.testing.assert_allclose(r['quantile_rul_mcse'],direct,rtol=1e-12)
    eps=1e-5;density_fd=(np.sum(w*norm.cdf((q+eps-mu)/.3))-np.sum(w*norm.cdf((q-eps-mu)/.3)))/(2*eps*w.sum())
    np.testing.assert_allclose(f,density_fd,rtol=1e-8)

def test_cqr_rank_and_interval_score_lipschitz():
    assert conformal_rank(25)==24
    rng=np.random.default_rng(897)
    y=rng.uniform(0,500,1000);lo=rng.uniform(0,200,1000);hi=lo+rng.uniform(1,100,1000)
    dl=rng.uniform(-.4,.4,1000);du=rng.uniform(-.4,.4,1000)
    delta=np.abs(interval_score(y,lo+dl,hi+du)-interval_score(y,lo,hi))
    assert np.all(delta<=19*(abs(dl)+abs(du))+1e-9)