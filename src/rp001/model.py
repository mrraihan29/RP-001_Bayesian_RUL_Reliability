from __future__ import annotations
import numpy as np
import pymc as pm
import pytensor.tensor as pt
from scipy.special import logsumexp
def covariance(p):
    t=np.asarray(p["tau"])
    return np.diag(t)@np.array([[1.,float(p["r_g"])],[float(p["r_g"]),1.]])@np.diag(t)
def numpy_terms(data,p,error="normal"):
    S=covariance(p)
    B=data.B
    w=len(B)
    rho=float(p["rho"])
    K=rho**np.abs(np.arange(w)[:,None]-np.arange(w)[None,:])
    C=B@S@B.T+float(p["sigma_z"])**2*K
    sign,ld=np.linalg.slogdet(C)
    assert sign>0
    mu0=data.a@np.asarray(p["Gamma"]).T
    u=data.z-mu0@B.T
    invu=np.linalg.solve(C,u.T).T
    cross=S@B.T
    latent_mu=mu0+invu@cross.T
    V=S-cross@np.linalg.solve(C,cross.T)
    mean=data.a@np.asarray(p["beta"])+latent_mu@np.asarray(p["gamma"])
    vg=float(np.asarray(p["gamma"])@V@np.asarray(p["gamma"]))
    variance=float(p["sigma_r"])**2+vg
    lz=-.5*(w*np.log(2*np.pi)+ld+np.sum(u*invu,axis=1))
    if data.y is None:
        ly=np.zeros(len(data.z))
    else:
        diff=data.y-mean
        ln=-.5*(np.log(2*np.pi*variance)+diff**2/variance)
        if error=="contamination":
            broad=9*float(p["sigma_r"])**2+vg
            lb=-.5*(np.log(2*np.pi*broad)+diff**2/broad)
            ly=logsumexp(np.stack((np.log(.95)+ln,np.log(.05)+lb)),axis=0)
        else: ly=ln
    return lz,ly,mean,np.full(len(mean),variance),V
def symbolic_terms(data,p,error="normal"):
    B=pt.as_tensor_variable(np.asarray(data.B,dtype="float64"))
    a=pt.as_tensor_variable(np.asarray(data.a,dtype="float64"))
    z=pt.as_tensor_variable(np.asarray(data.z,dtype="float64"))
    w=data.z.shape[1]
    tau=p["tau"]; rg=p["r_g"]; rho=p["rho"]
    s00=tau[0]**2; s11=tau[1]**2; s01=tau[0]*tau[1]*rg
    ds=s00*s11-s01**2
    inv00=s11/ds; inv11=s00/ds; inv01=-s01/ds
    mu0=pt.dot(a,p["Gamma"].T)
    u=z-pt.dot(mu0,B.T)
    if w>1:
        WB=pt.concatenate([B[:1],(B[1:]-rho*B[:-1])/pt.sqrt(1-rho**2)],axis=0)
        WU=pt.concatenate([u[:,:1],(u[:,1:]-rho*u[:,:-1])/pt.sqrt(1-rho**2)],axis=1)
    else: WB,WU=B,u
    precision_scale=1/p["sigma_z"]**2
    J=pt.dot(WB.T,WB)*precision_scale
    A00=inv00+J[0,0]; A11=inv11+J[1,1]; A01=inv01+J[0,1]
    da=A00*A11-A01**2
    V=pt.stack([pt.stack([A11/da,-A01/da]),pt.stack([-A01/da,A00/da])])
    b=pt.dot(WU,WB)*precision_scale
    delta=pt.dot(b,V)
    mu=mu0+delta
    q=pt.sum(WU**2,axis=1)*precision_scale-pt.sum(b*delta,axis=1)
    ld=w*pt.log(p["sigma_z"]**2)+(w-1)*pt.log(1-rho**2)+pt.log(ds)+pt.log(da)
    lz=-.5*(w*np.log(2*np.pi)+ld+q)
    mean=pt.dot(a,p["beta"])+pt.dot(mu,p["gamma"])
    vg=pt.dot(p["gamma"],pt.dot(V,p["gamma"]))
    variance=p["sigma_r"]**2+vg
    if data.y is None: ly=pt.zeros_like(mean)
    else:
        diff=pt.as_tensor_variable(data.y)-mean
        ln=-.5*(pt.log(2*np.pi*variance)+diff**2/variance)
        if error=="contamination":
            broad=9*p["sigma_r"]**2+vg
            lb=-.5*(pt.log(2*np.pi*broad)+diff**2/broad)
            ly=pt.logaddexp(np.log(.95)+ln,np.log(.05)+lb)
        else: ly=ln
    return lz,ly,mean,variance,V
def build_model(data,prior_scale=1.,error="normal",rho_zero=False,extra_sensor=None):
    with pm.Model() as model:
        beta=pm.Normal("beta",mu=[np.log(100),0],sigma=np.array([1.,.75])*prior_scale,shape=2)
        gamma=pm.Normal("gamma",mu=0,sigma=.5*prior_scale,shape=2)
        Gamma=pm.Normal("Gamma",mu=0,sigma=np.tile([1.,.5],(2,1))*prior_scale,shape=(2,2))
        tau=pm.HalfNormal("tau",sigma=.5*prior_scale,shape=2)
        # For dimension 2, LKJ(eta=2) correlation is r=2*Beta(2,2)-1.
        rg=pm.Deterministic("r_g",2*pm.Beta("gcor_u",2,2)-1)
        sz=pm.HalfNormal("sigma_z",sigma=.5*prior_scale)
        sr=pm.HalfNormal("sigma_r",sigma=.5*prior_scale)
        if rho_zero: rho=pm.Deterministic("rho",pt.as_tensor_variable(0.))
        else: rho=pm.Deterministic("rho",pt.tanh(pm.Normal("eta_rho",0,.75*prior_scale)))
        p={"beta":beta,"gamma":gamma,"Gamma":Gamma,"tau":tau,"r_g":rg,"sigma_z":sz,"sigma_r":sr,"rho":rho}
        lz,ly,_,_,_=symbolic_terms(data,p,error)
        pm.Potential("engine_likelihood",pt.sum(lz+ly))
        if extra_sensor is not None:
            assert extra_sensor.y is None
            elz,*_=symbolic_terms(extra_sensor,p,error)
            pm.Potential("new_engine_sensor_only",pt.sum(elz))
    return model
def prior_draws(n,seed,scale=1.,rho_zero=False):
    rng=np.random.default_rng(seed)
    return [{"beta":rng.normal([np.log(100),0],np.array([1.,.75])*scale),
             "gamma":rng.normal(0,.5*scale,size=2),
             "Gamma":rng.normal(0,np.tile([1.,.5],(2,1))*scale),
             "tau":np.abs(rng.normal(0,.5*scale,size=2)),
             "r_g":2*rng.beta(2,2)-1,"sigma_z":abs(rng.normal(0,.5*scale)),
             "sigma_r":abs(rng.normal(0,.5*scale)),
             "rho":0. if rho_zero else np.tanh(rng.normal(0,.75*scale))}
            for _ in range(n)]
def flatten_parameters(idata):
    post=idata.posterior
    names=["beta","gamma","Gamma","tau","r_g","sigma_z","sigma_r","rho"]
    arrays={n:post[n].values.reshape((-1,)+post[n].values.shape[2:]) for n in names}
    return [{n:arrays[n][i] for n in names} for i in range(len(arrays["rho"]))]
