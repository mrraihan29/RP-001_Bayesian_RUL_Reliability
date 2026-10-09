import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts/stage_D"))
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
import math
import numpy as np
import pytest
from core import parse_labels,evaluate,qualification
from oracles import verify_evaluation,scalar_mcse,verify_mcse
from rp001.v05_score_numerics import endpoint_cycle_quantile_influence,estimate_joint_interval_score_mcse

def fixture():
    y=np.tile([5.,10.,15.,20.,25.],20)
    b=dict(lower=np.full(100,10.),median=np.full(100,15.),upper=np.full(100,20.))
    c=dict(lower=np.zeros(100),median=np.full(100,-2.),upper=np.full(100,15.))
    return y,b,c

def test_complete_score_width_misses_coverage_and_decimal_oracle():
    y,b,c=fixture();r=evaluate(y,b,c)
    np.testing.assert_array_equal(r["components"]["Bayesian"]["score"],np.tile([110,10,10,10,110],20))
    assert r["metrics"]["Bayesian"]["coverage_count"]==60
    assert r["metrics"]["CQR"]["coverage_count"]==60
    assert r["metrics"]["CQR"]["negative_median_count"]==100
    assert r["paired_difference_cycles"]==math.fsum(r["paired"]["score"])/100
    assert verify_evaluation(y,b,c,r)["status"]=="PASS"

@pytest.mark.parametrize("bad",[float("nan"),float("inf"),-1,0])
def test_invalid_label_rejects_whole_cohort(bad):
    y,b,c=fixture();y[73]=bad
    with pytest.raises(ValueError):evaluate(y,b,c)

@pytest.mark.parametrize("method,key",[("b","lower"),("b","upper"),("c","lower"),("c","median")])
def test_single_missing_prediction_never_subset(method,key):
    y,b,c=fixture();p=b if method=="b" else c;p[key][31]=np.nan
    with pytest.raises(ValueError):evaluate(y,b,c)

def test_overflow_and_missing_engine_rejected():
    y,b,c=fixture()
    with pytest.raises(ValueError):evaluate(y[:-1],b,c)
    with pytest.raises(ValueError):evaluate(y,b,c,ids=list(range(1,100))+[99])
    b["upper"][0]=np.finfo(float).max;y[0]=1
    b["lower"][0]=np.finfo(float).max/2
    with pytest.raises(ValueError):evaluate(y,b,c)

def test_label_schema_order_positive_complete():
    payload=b"\n".join(str(i).encode() for i in range(1,101))+b"\n"
    np.testing.assert_array_equal(parse_labels(payload),range(1,101))
    for wrong in (payload+b"1\n",payload.replace(b"25\n",b"25 26\n"),payload.replace(b"25\n",b"\n"),
        payload.replace(b"25\n",b"nan\n"),payload.replace(b"25\n",b"0\n")):
        with pytest.raises(ValueError):parse_labels(wrong)
    with pytest.raises(ValueError):parse_labels(payload,[1]*100)

def test_compensated_contrast_preserves_cancellation():
    assert math.fsum([1e16,1.,-1e16])==1.
    y=np.ones(100)
    b=dict(lower=np.ones(100),median=np.ones(100),upper=np.ones(100))
    c={k:v.copy() for k,v in b.items()}
    b["upper"][0]=1e16+1
    b["upper"][1]=2
    c["upper"][2]=1e16+1
    r=evaluate(y,b,c)
    assert r["paired_difference_cycles"]==.01

def test_influence_covariance_scalar_projection_and_cross_engine_dependence():
    t=np.arange(24,dtype=float)
    w=np.array([1.,2.,3.,4.]*6)[None,:,None]
    w=np.broadcast_to(w,(2,24,2)).copy();w[1]*=1.7
    cdf=np.broadcast_to((.2+.4*(t%4)/4)[None,:,None],w.shape).copy()
    a=endpoint_cycle_quantile_influence(np.log(w),cdf,.05,[10,20],[.5,.7])["influence_cycles"]
    expected=-np.array([10,20])*w/w.mean(axis=(0,1))*(cdf-.05)/np.array([.5,.7])
    np.testing.assert_allclose(a,expected,rtol=1e-14,atol=1e-13)
    # Strong shared dependence; endpoint signs/scales deliberately retain covariance.
    b=.3*a+np.sin(t)[None,:,None]
    r=estimate_joint_interval_score_mcse(a,b,[15,25],[10,20],[20,30],[.1,.1],[.1,.1],
        tail_probability=.025,batch_sizes=(3,6))
    H=np.empty((2,24))
    for c in range(2):
        for d in range(24):H[c,d]=math.fsum([-a[c,d,0],-a[c,d,1],b[c,d,0],b[c,d,1]])/2
    np.testing.assert_allclose(H,r["score_influence"],rtol=1e-13,atol=1e-12)
    for o,g in zip(scalar_mcse(H,(3,6)),r["batch_size_results"]):
        np.testing.assert_allclose(o["variance"],g["score_variance_cycles_squared"],rtol=1e-12)
        np.testing.assert_allclose(o["upper_mcse"],g["approximate_upper_quantile_score_mcse_cycles"],rtol=1e-12)
        cov=g["joint_endpoint_mc_error_covariance_cycles_squared"];contrast=r["score_contrast"]
        diagonal_only=float(np.sum(contrast*contrast*np.diag(cov)))
        assert abs(diagonal_only-g["score_variance_cycles_squared"])>1e-3

def test_qualification_undefined_nonfinite_threshold_and_kink():
    def item(u,k=False):
        return dict(batch_size_results=[dict(approximate_upper_quantile_score_mcse_cycles=x) for x in u],
            label_kink=dict(any=k))
    assert qualification(item([.1,.5]))["status"]=="PASS"
    for v in ([None,.1],[np.nan,.1],[np.inf,.1],[.500001,.1]):
        assert qualification(item(v))["status"]=="NUMERICALLY_QUALIFIED"
    assert qualification(item([.1,.1],True))["status"]=="NUMERICALLY_QUALIFIED"

def test_exact_boundary_kink_and_zero_variance_undefined_upper():
    a=np.zeros((2,1000,2))
    r=estimate_joint_interval_score_mcse(a,a,[10,30],[10,20],[20,30],[0,0],[0,0],tail_probability=.025)
    assert r["label_kink"]["any"]
    assert all(g["approximate_upper_quantile_score_mcse_cycles"] is None for g in r["batch_size_results"])
    assert qualification(r)["status"]=="NUMERICALLY_QUALIFIED"
