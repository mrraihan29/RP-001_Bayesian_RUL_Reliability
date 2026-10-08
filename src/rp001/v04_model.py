"""v0.4 priors and joint-data generator; all policies frozen in remediation_plan."""
import numpy as np
import pymc as pm
import pytensor.tensor as pt
from .model import symbolic_terms, covariance
from .data import LandmarkData, truth_parameters

def build_model(data, prior, scale=1., error='normal', rho_zero=False, extra_sensor=None):
    with pm.Model() as model:
        beta=pm.Normal('beta', prior['beta_mu'],np.asarray(prior['beta_sd'])*scale,shape=2)
        gamma=pm.Normal('gamma',0,prior['gamma_sd']*scale,shape=2)
        Gamma=pm.Normal('Gamma',0,np.tile(prior['Gamma_sd'],(2,1))*scale,shape=(2,2))
        tau=pm.HalfNormal('tau',prior['tau_sd']*scale,shape=2)
        rg=pm.Deterministic('r_g',2*pm.Beta('gcor_u',prior['lkj_eta'],prior['lkj_eta'])-1)
        sz=pm.HalfNormal('sigma_z',prior['sigma_z_sd']*scale)
        sr=pm.HalfNormal('sigma_r',prior['sigma_r_sd']*scale)
        # Broadening changes scale priors only; the correlation policies remain fixed.
        rho=pm.Deterministic('rho',pt.as_tensor_variable(0.) if rho_zero else pt.tanh(pm.Normal('eta_rho',0,prior['eta_rho_sd'])))
        p=dict(beta=beta,gamma=gamma,Gamma=Gamma,tau=tau,r_g=rg,sigma_z=sz,sigma_r=sr,rho=rho)
        lz,ly,*_=symbolic_terms(data,p,error)
        pm.Potential('engine_likelihood',pt.sum(lz+ly))
        if extra_sensor is not None:
            if extra_sensor.y is not None: raise ValueError('Oracle extra data must be sensor-only')
            lz,*_=symbolic_terms(extra_sensor,p,error)
            pm.Potential('new_engine_sensor_only',pt.sum(lz))
    return model

def draw_prior(n,seed,p,scale=1.):
    rng=np.random.default_rng(seed)
    return [dict(beta=rng.normal(p['beta_mu'],np.asarray(p['beta_sd'])*scale),
        gamma=rng.normal(0,p['gamma_sd']*scale,2),Gamma=rng.normal(0,np.tile(p['Gamma_sd'],(2,1))*scale),
        tau=np.abs(rng.normal(0,p['tau_sd']*scale,2)),r_g=2*rng.beta(p['lkj_eta'],p['lkj_eta'])-1,
        sigma_z=abs(rng.normal(0,p['sigma_z_sd']*scale)),sigma_r=abs(rng.normal(0,p['sigma_r_sd']*scale)),
        rho=np.tanh(rng.normal(0,p['eta_rho_sd']))) for _ in range(n)]

def generate(n,seed,regime):
    theta=truth_parameters(regime['rho'],regime.get('weak',False))
    for key in ('gamma','Gamma','sigma_z','sigma_r'):
        if key in regime: theta[key]=np.asarray(regime[key]) if key in ('gamma','Gamma') else regime[key]
    rng=np.random.default_rng(seed);c=rng.integers(30,251,n)
    a=np.column_stack((np.ones(n),np.log(c/100)))
    B=np.column_stack((np.ones(30),np.arange(-29,1)/30))
    g=rng.multivariate_normal(np.zeros(2),covariance(theta),n)+a@theta['Gamma'].T
    K=theta['rho']**np.abs(np.arange(30)[:,None]-np.arange(30)[None,:])
    z=g@B.T+rng.multivariate_normal(np.zeros(30),theta['sigma_z']**2*K,n)
    y=a@theta['beta']+g@theta['gamma']+rng.normal(0,theta['sigma_r'],n)
    return LandmarkData(a,z,y,np.arange(n),B,f'v04 synthetic seed{seed}'),theta