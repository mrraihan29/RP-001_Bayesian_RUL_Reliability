import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np
from scipy.special import logsumexp
from scipy.stats import norm
from rp001.data import load_training,manifest,fit_preprocessor,transform_prefix
def test_preprocessor_and_features_are_future_blind():
    raw=load_training()
    ids=[r["engine"] for r in manifest() if r["eligible_alive"] and r["role"]=="fit"]
    cuts={r["engine"]:r["proposed_cutoff"] for r in manifest()}
    original=fit_preprocessor(raw,ids)
    altered={i:rows.copy() for i,rows in raw.items()}
    for i in ids:altered[i][altered[i][:,1]>cuts[i],5:]+=1e6
    changed=fit_preprocessor(altered,ids)
    for key in original:np.testing.assert_array_equal(original[key],changed[key])
    for i in ids:np.testing.assert_array_equal(transform_prefix(raw[i],cuts[i],original),transform_prefix(altered[i],cuts[i],changed))
def test_global_sensor_only_update_matches_conjugate_gaussian():
    rng=np.random.default_rng(511)
    theta=rng.normal(.2,.6,200000)
    z,a,noise=1.1,1.2,.7
    logw=norm.logpdf(z,loc=a*theta,scale=noise)
    weights=np.exp(logw-logsumexp(logw))
    var=1/(1/.6**2+a*a/noise**2)
    mean=var*(.2/.6**2+a*z/noise**2)
    estimate=np.dot(weights,theta)
    variance=np.dot(weights,(theta-estimate)**2)
    np.testing.assert_allclose(estimate,mean,atol=.005)
    np.testing.assert_allclose(variance,var,atol=.005)
    assert abs(estimate-.2)>.1

import hashlib
from collections import Counter
from scipy.stats import spearmanr
from rp001.data import ROOT
def test_lead_independent_cutoff_and_survival_audit():
    raw=load_training();records=manifest();seed="RP001-20261008-v0.2"
    ordered=sorted(range(1,101),key=lambda i:hashlib.sha256(f"{seed}|split|{i}".encode()).hexdigest())
    roles={i:"fit" if j<55 else "tune" if j<70 else "calibration" for j,i in enumerate(ordered)}
    counts=Counter();all_c=[];all_t=[];surv_c=[];surv_t=[]
    for r in records:
        i=r["engine"];c=30+int(hashlib.sha256(f"{seed}|cutoff|{i}".encode()).hexdigest(),16)%221
        T=int(raw[i][-1,1])
        assert r["role"]==roles[i] and r["proposed_cutoff"]==c and r["eligible_alive"]==(c<T)
        all_c.append(c);all_t.append(T)
        if c<T:counts[r["role"]]+=1;surv_c.append(c);surv_t.append(T)
    assert counts=={"fit":43,"tune":13,"calibration":25}
    result={"counts":dict(counts),"all_pearson":float(np.corrcoef(all_c,all_t)[0,1]),
            "survivor_pearson":float(np.corrcoef(surv_c,surv_t)[0,1]),
            "all_spearman":float(spearmanr(all_c,all_t).statistic),
            "survivor_spearman":float(spearmanr(surv_c,surv_t).statistic),
            "interpretation":"Descriptive association; fixed hash does not prove stochastic independence.",
            "verifier":"lead independent reimplementation","official_test_access":False}
    import json
    (ROOT/"logs/lead_cutoff_verification.json").write_text(json.dumps(result,indent=2)+"\n")
