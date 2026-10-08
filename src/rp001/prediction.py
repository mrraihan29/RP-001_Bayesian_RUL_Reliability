from dataclasses import replace
import numpy as np
from scipy.special import logsumexp
from scipy.optimize import brentq
from scipy.stats import norm
from .model import numpy_terms
def mixture_quantile(mu,var,weights,tau,error="normal",sigma_r=None):
    sd=np.sqrt(var)
    if error=="contamination":
        broad=np.sqrt(var+8*np.asarray(sigma_r)**2)
        f=lambda x: np.dot(weights,.95*norm.cdf((x-mu)/sd)+.05*norm.cdf((x-mu)/broad))-tau
        limit=broad
    else:
        f=lambda x: np.dot(weights,norm.cdf((x-mu)/sd))-tau
        limit=sd
    root=brentq(f,float(np.min(mu-12*limit)),float(np.max(mu+12*limit)),xtol=1e-10)
    return float(np.exp(root))
def summarize_mixture(lz,mu,var,sr,reweight=True,chains=4,error="normal"):
    weights=np.exp(lz-logsumexp(lz)) if reweight else np.full(len(lz),1/len(lz))
    quantiles=[mixture_quantile(mu,var,weights,q,error,sr) for q in (.05,.5,.95)]
    chain_q=[]
    if len(lz)%chains==0:
        for indices in np.array_split(np.arange(len(lz)),chains):
            lw=lz[indices]
            cw=np.exp(lw-logsumexp(lw)) if reweight else np.full(len(indices),1/len(indices))
            chain_q.append([mixture_quantile(mu[indices],var[indices],cw,q,error,sr[indices]) for q in (.05,.5,.95)])
    mcse=np.std(chain_q,axis=0,ddof=1)/np.sqrt(chains) if chain_q and chains>1 else np.full(3,np.nan)
    return {"lower":quantiles[0],"median":quantiles[1],"upper":quantiles[2],
            "weight_ess":float(1/np.sum(weights**2)),"max_weight":float(np.max(weights)),
            "chain_quantiles":chain_q,"between_chain_quantile_mcse_approx":mcse.tolist(),
            "conditioning":"full sensor-only importance update" if reweight else "modular fixed theta",
            "mcse_limitation":"Between-chain quantile variability is an approximate MC diagnostic, not a bound."}
def predict_engine(draws,data,error="normal",reweight=True,chains=4):
    assert len(data.ids)==1 and data.y is None
    return predict_data(draws,data,error,reweight,chains)[0]
def predict_data(draws,data,error="normal",reweight=True,chains=4):
    # Reuse each draw's sensor covariance across engines, with separate per-engine theta weights.
    sensor=replace(data,y=None)
    terms=[numpy_terms(sensor,p,error) for p in draws]
    lz=np.array([t[0] for t in terms]);mu=np.array([t[2] for t in terms]);var=np.array([t[3] for t in terms])
    sr=np.array([p["sigma_r"] for p in draws])
    return [dict(engine=int(data.ids[i]),**summarize_mixture(lz[:,i],mu[:,i],var[:,i],sr,reweight,chains,error))
            for i in range(len(data.ids))]
