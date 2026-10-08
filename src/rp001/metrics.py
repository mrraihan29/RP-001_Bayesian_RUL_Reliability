import math
from decimal import Decimal, ROUND_CEILING
import numpy as np
from scipy.stats import norm
def interval_score(y,lower,upper,alpha=.1):
    y,lower,upper=np.asarray(y),np.asarray(lower),np.asarray(upper)
    if np.any(lower>upper) or not np.isfinite(np.r_[y.ravel(),lower.ravel(),upper.ravel()]).all():
        raise ValueError("Invalid endpoints/outcomes")
    return upper-lower+2/alpha*np.maximum(lower-y,0)+2/alpha*np.maximum(y-upper,0)
def conformal_rank(n,alpha=.1):
    return int((Decimal(n+1)*(Decimal(1)-Decimal(str(alpha)))).to_integral_value(rounding=ROUND_CEILING))
def correction(scores,alpha=.1,nonshrinking=True):
    scores=np.asarray(scores,dtype=float)
    if scores.ndim!=1 or not np.isfinite(scores).all(): raise ValueError("Engine scores must be finite")
    k=conformal_rank(len(scores),alpha)
    if k>len(scores): return math.inf
    q=float(np.partition(scores,k-1)[k-1])
    return max(0.,q) if nonshrinking else q
def calibrate(y,lower,upper,alpha=.1):
    lo,up=np.minimum(lower,upper),np.maximum(lower,upper)
    return correction(np.maximum(lo-y,y-up),alpha)
def apply_correction(lower,upper,q):
    lo,up=np.minimum(lower,upper),np.maximum(lower,upper)
    return np.maximum(0.,lo-q),np.maximum(0.,up+q)
def summarize(y,lower,upper,median=None):
    score=interval_score(y,lower,upper)
    out={"mean_interval_score":float(np.mean(score)),
         "coverage":float(np.mean((lower<=y)&(y<=upper))),
         "mean_width":float(np.mean(upper-lower)),
         "lower_miss_fraction":float(np.mean(y<lower)),
         "upper_miss_fraction":float(np.mean(y>upper)),"n_engines":len(y)}
    if median is not None:
        out.update({"mae":float(np.mean(abs(y-median))),"rmse":float(np.sqrt(np.mean((y-median)**2)))})
    return out
