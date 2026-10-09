"""Separate arithmetic oracles. No source scoring helpers used."""
import math
from decimal import Decimal, localcontext
import numpy as np
from scipy.stats import chi2

def scalar_scores(y,pred):
    rows=[]
    with localcontext() as c:
        c.prec=60
        decimal_residuals=[]
        for v,l,m,u in zip(y,pred["lower"],pred["median"],pred["upper"],strict=True):
            v,l,m,u=map(float,(v,l,m,u))
            width=u-l;below=20*max(l-v,0);above=20*max(v-u,0)
            s=width+below+above
            rows.append((width,below,above,s,l<=v<=u,m-v))
            dy,dl,du=map(Decimal.from_float,(v,l,u))
            exact=du-dl+20*max(dl-dy,Decimal(0))+20*max(dy-du,Decimal(0))
            decimal_residuals.append(float(abs(Decimal.from_float(s)-exact)))
    return rows, max(decimal_residuals)

def verify_evaluation(y,bayes,cqr,result):
    tables={}
    for method,p in (("Bayesian",bayes),("CQR",cqr)):
        rows,res=scalar_scores(y,p)
        for j,k in enumerate(("width","below_penalty","above_penalty","score","covered","median_error")):
            np.testing.assert_array_equal([r[j] for r in rows],result["components"][method][k])
        count=sum(int(r[4]) for r in rows)
        assert count==result["metrics"][method]["coverage_count"]
        assert count/100==result["metrics"][method]["coverage_fraction"]
        np.testing.assert_allclose(res,0,atol=1e-9,rtol=0)
        errors=[r[5] for r in rows]
        for key,value in (
            ("mean_interval_score_cycles",math.fsum(r[3] for r in rows)/100),
            ("median_MAE_cycles",math.fsum(abs(e) for e in errors)/100),
            ("median_RMSE_cycles",math.sqrt(math.fsum(e*e for e in errors)/100)),
            ("median_bias_cycles",math.fsum(errors)/100)):
            assert value==result["metrics"][method][key]
        tables[method]=rows
    delta=[a[3]-b[3] for a,b in zip(tables["Bayesian"],tables["CQR"],strict=True)]
    np.testing.assert_array_equal(delta,result["paired"]["score"])
    assert math.fsum(delta)/100==result["paired_difference_cycles"]
    for i in range(100):
        parts=math.fsum(float(result["paired"][k][i]) for k in ("width","below_penalty","above_penalty"))
        np.testing.assert_allclose(parts,delta[i],rtol=1e-12,atol=1e-10)
    return {"status":"PASS","engines":100,"all_scores_and_components_exact_float64":True,
        "coverage_and_compensated_contrast_exact":True,"Decimal_arithmetic_residual_limit_cycles":1e-9,
        "method":"Separate stdlib scalar and 60-digit Decimal oracle; internal verification"}

def scalar_mcse(H,batch_sizes=(250,500),tail=.025):
    H=np.asarray(H,dtype=np.float64);chains,draws=H.shape;total=chains*draws
    out=[]
    for b in batch_sizes:
        parts=[];counts=[]
        for c in range(chains):
            batches=[math.fsum(map(float,H[c,j:j+b]))/b for j in range(0,(draws//b)*b,b)]
            center=math.fsum(batches)/len(batches)
            variance=math.fsum((x-center)**2 for x in batches)/(len(batches)-1)
            parts.append(draws*b*variance/(total*total));counts.append(len(batches)-1)
        v=math.fsum(parts);den=math.fsum(x*x/d for x,d in zip(parts,counts))
        df=v*v/den if den>0 else None
        upper=math.sqrt(v*df/float(chi2.ppf(tail,df))) if df is not None else None
        out.append(dict(batch_size=b,variance=v,ordinary_mcse=math.sqrt(v),upper_mcse=upper,
            satterthwaite_df=df,variance_components=parts))
    return out

def verify_mcse(H,result):
    checks=scalar_mcse(H)
    for a,b in zip(checks,result["batch_size_results"],strict=True):
        np.testing.assert_allclose(a["variance"],b["score_variance_cycles_squared"],rtol=1e-10,atol=1e-11)
        np.testing.assert_allclose(a["variance"],b["score_variance_from_joint_covariance_cycles_squared"],rtol=1e-10,atol=1e-11)
        np.testing.assert_allclose(a["ordinary_mcse"],b["quantile_score_mcse_cycles"],rtol=1e-10,atol=1e-11)
        if a["upper_mcse"] is None:assert b["approximate_upper_quantile_score_mcse_cycles"] is None
        else:np.testing.assert_allclose(a["upper_mcse"],b["approximate_upper_quantile_score_mcse_cycles"],rtol=1e-10,atol=1e-11)
    return checks
