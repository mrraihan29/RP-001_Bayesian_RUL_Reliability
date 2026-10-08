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
def predict_engine(draws,data,error="normal",reweight=True,chains=4):
    assert len(data.ids)==1 and data.y is None
    terms=[numpy_terms(data,p,error) for p in draws]
    lz=np.array([t[0][0] for t in terms])
    mu=np.array([t[2][0] for t in terms]); var=np.array([t[3][0] for t in terms])
    sr=np.array([p["sigma_r"] for p in draws])
    weights=np.exp(lz-logsumexp(lz)) if reweight else np.full(len(draws),1/len(draws))
    quantiles=[mixture_quantile(mu,var,weights,q,error,sr) for q in (.05,.5,.95)]
    chain_q=[]
    if len(draws)%chains==0:
        for indices in np.array_split(np.arange(len(draws)),chains):
            lw=lz[indices]
            cw=np.exp(lw-logsumexp(lw)) if reweight else np.full(len(indices),1/len(indices))
            chain_q.append([mixture_quantile(mu[indices],var[indices],cw,q,error,sr[indices]) for q in (.05,.5,.95)])
    mcse=np.std(chain_q,axis=0,ddof=1)/np.sqrt(chains) if chain_q else np.full(3,np.nan)
    return {"lower":quantiles[0],"median":quantiles[1],"upper":quantiles[2],
            "weight_ess":float(1/np.sum(weights**2)),"max_weight":float(np.max(weights)),
            "chain_quantiles":chain_q,"between_chain_quantile_mcse_approx":mcse.tolist(),
            "conditioning":"full sensor-only importance update" if reweight else "modular fixed theta",
            "mcse_limitation":"Between-chain quantile variability is an approximate MC diagnostic, not a bound."}
def predict_data(draws,data,error="normal",reweight=True,chains=4):
    return [dict(engine=int(data.ids[i]),**predict_engine(draws,replace(data,a=data.a[i:i+1],z=data.z[i:i+1],
               y=None,ids=data.ids[i:i+1]),error,reweight,chains)) for i in range(len(data.ids))]
