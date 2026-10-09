"""Stage D arithmetic only; no fitting, quantile roots or model selection."""
from __future__ import annotations
import math
import numpy as np

IDS=list(range(1,101))

def parse_labels(payload:bytes, ids=IDS):
    if list(ids)!=IDS:raise ValueError("Ambiguous/duplicate/unmatched official IDs")
    lines=payload.decode("ascii").splitlines()
    if len(lines)!=100 or any(len(s.split())!=1 for s in lines):
        raise ValueError("Official schema requires exactly 100 one-value rows")
    y=np.array([float(s) for s in lines],dtype=np.float64)
    if not np.all(np.isfinite(y)) or np.any(y<=0):
        raise ValueError("Labels must be finite positive uncapped RUL")
    return y

def valid_predictions(pred, ids):
    if list(ids)!=IDS:raise ValueError("Complete ordered IDs 1..100 required")
    if set(pred)!={"lower","median","upper"}:raise ValueError("Prediction schema")
    a={k:np.asarray(v,dtype=np.float64) for k,v in pred.items()}
    if any(v.shape!=(100,) or not np.all(np.isfinite(v)) for v in a.values()):
        raise ValueError("Complete finite prediction vectors required; primary UNAVAILABLE")
    if np.any(a["lower"]<0) or np.any(a["lower"]>a["upper"]):
        raise ValueError("Frozen nonnegative ordered interval required")
    # CQR median is not projected; retain a negative frozen value if present.
    return a

def evaluate(y, bayes, cqr, ids=IDS):
    y=np.asarray(y,dtype=np.float64)
    if y.shape!=(100,) or not np.all(np.isfinite(y)) or np.any(y<=0):
        raise ValueError("Complete finite positive labels required; primary UNAVAILABLE")
    a={m:valid_predictions(p,ids) for m,p in (("Bayesian",bayes),("CQR",cqr))}
    components={};metrics={}
    for method,p in a.items():
        with np.errstate(over="ignore",invalid="ignore"):
            width=p["upper"]-p["lower"]
            below=20.0*np.maximum(p["lower"]-y,0.0)
            above=20.0*np.maximum(y-p["upper"],0.0)
            score=width+below+above
            errors=p["median"]-y
        if not all(np.all(np.isfinite(v)) for v in (width,below,above,score,errors)):
            raise ValueError("Nonfinite primary score/component; primary UNAVAILABLE")
        inside=(y>=p["lower"])&(y<=p["upper"])
        components[method]=dict(width=width,below_penalty=below,above_penalty=above,score=score,
            median_error=errors,covered=inside,below=y<p["lower"],above=y>p["upper"])
        mse=math.fsum(float(e)*float(e) for e in errors)/100
        metrics[method]=dict(mean_interval_score_cycles=math.fsum(map(float,score))/100,
            coverage_count=int(inside.sum()),coverage_denominator=100,coverage_fraction=int(inside.sum())/100,
            below_count=int((y<p["lower"]).sum()),above_count=int((y>p["upper"]).sum()),
            median_MAE_cycles=math.fsum(abs(float(e)) for e in errors)/100,
            median_RMSE_cycles=math.sqrt(mse),median_bias_cycles=math.fsum(map(float,errors))/100,
            negative_median_count=int((p["median"]<0).sum()))
        if not all(math.isfinite(v) for v in metrics[method].values()):
            raise ValueError("Nonfinite complete score/error summary; primary UNAVAILABLE")
    paired={k:components["Bayesian"][k]-components["CQR"][k] for k in ("width","below_penalty","above_penalty","score")}
    if any(not np.all(np.isfinite(v)) for v in paired.values()):
        raise ValueError("Nonfinite paired contrast; primary UNAVAILABLE")
    difference=math.fsum(map(float,paired["score"]))/100
    if not math.isfinite(difference):raise ValueError("Nonfinite primary compensated sum")
    denominator=metrics["CQR"]["mean_interval_score_cycles"]
    return dict(primary_status="AVAILABLE",engine_count=100,engine_ids=IDS,metrics=metrics,
        paired_difference_cycles=difference,
        mean_score_ratio=metrics["Bayesian"]["mean_interval_score_cycles"]/denominator if denominator>0 else None,
        paired_component_means={k:math.fsum(map(float,v))/100 for k,v in paired.items()},
        components=components,paired=paired,
        estimand="Exact complete finite benchmark of accepted stored predictions; no population inference",
        summation="math.fsum of float64 per-engine paired scores / 100")

def qualification(result):
    upper=[g["approximate_upper_quantile_score_mcse_cycles"] for g in result["batch_size_results"]]
    reasons=[]
    if any(x is None or not math.isfinite(x) for x in upper):reasons.append("undefined_or_nonfinite_score_upper_MCSE")
    elif max(upper)>.5:reasons.append("score_upper_MCSE_above_0.5_cycles")
    if result["label_kink"]["any"]:reasons.append("label_within_three_endpoint_upper_MCSE")
    return dict(status="NUMERICALLY_QUALIFIED" if reasons else "PASS",reasons=reasons,
        maximum_score_upper_MCSE_cycles=max(upper) if all(x is not None and math.isfinite(x) for x in upper) else None,
        stored_complete_score_retained=True,threshold_cycles=.5,
        ideal_posterior_ranking_certified=False,
        scope="Approximate conditional computational uncertainty; no population/pipeline interval")
