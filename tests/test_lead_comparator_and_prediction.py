import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np
import statsmodels.api as sm
import pytest
from rp001.comparators import fit_gaussian_logr_reference,predict_gaussian_logr_reference
from rp001.data import generate_synthetic,features
from rp001.prediction import predict_data,predict_engine
from dataclasses import replace
def test_reference_prediction_against_statsmodels():
    rng=np.random.default_rng(111)
    X=rng.normal(size=(56,5));y=np.column_stack((np.ones(56),X))@np.array([4,.2,-.1,.3,-.2,.1])+rng.normal(0,.3,56)
    new=rng.normal(size=(8,5))
    fit=fit_gaussian_logr_reference(X,np.exp(y))
    result=predict_gaussian_logr_reference(fit,new)
    oracle=sm.OLS(y,sm.add_constant(X)).fit().get_prediction(sm.add_constant(new)).summary_frame(alpha=.1)
    np.testing.assert_allclose(result.lower,np.exp(oracle.obs_ci_lower),rtol=1e-10)
    np.testing.assert_allclose(result.upper,np.exp(oracle.obs_ci_upper),rtol=1e-10)
def test_reference_rejects_nonestimable_new_contrast():
    rng=np.random.default_rng(112)
    X=rng.normal(size=(56,5));X[:,4]=0
    fit=fit_gaussian_logr_reference(X,np.exp(4+rng.normal(0,.3,56)))
    new=np.ones((1,5))
    with pytest.raises(ValueError,match="nonestimable"):
        predict_gaussian_logr_reference(fit,new)
def test_shared_five_summary_features():
    d,_=generate_synthetic(10,111)
    f=features(d)
    assert f.shape==(10,5)
    np.testing.assert_array_equal(f[:,0],d.a[:,1])
    np.testing.assert_array_equal(f[:,1],d.z[:,-1])
def test_batched_prediction_matches_separate_engine():
    d,p=generate_synthetic(2,112)
    draws=[p]*40
    batch=predict_data(draws,replace(d,y=None))
    single=predict_engine(draws,replace(d,a=d.a[:1],z=d.z[:1],ids=d.ids[:1],y=None))
    for key in ("lower","median","upper","weight_ess"):
        np.testing.assert_allclose(batch[0][key],single[key],rtol=1e-12)
