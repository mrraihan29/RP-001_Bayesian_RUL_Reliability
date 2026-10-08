from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np
import xarray as xr
import arviz as az
from rp001.pilot import convert_trace
def test_nested_backend_attrs_roundtrip_without_sample_changes(tmp_path):
    posterior=xr.Dataset({"beta":(("chain","draw"),np.array([[1.,2.],[3.,4.]]))},attrs={"settings":{"target_accept":.95}})
    stats=xr.Dataset({"energy":(("chain","draw"),np.array([[2.,3.],[4.,5.]]))},attrs={"settings":{"sampler":"nuts"}})
    trace=xr.DataTree.from_dict({"posterior":posterior,"sample_stats":stats})
    idata=convert_trace(trace)
    idata.to_netcdf(tmp_path/"roundtrip.nc")
    restored=az.from_netcdf(tmp_path/"roundtrip.nc")
    np.testing.assert_array_equal(restored.posterior.beta,idata.posterior.beta)

def test_legacy_inferencedata_nested_root_attrs(tmp_path):
    posterior=xr.Dataset({"beta":(("chain","draw"),np.array([[1.,2.],[3.,4.]]))})
    trace=az.InferenceData(posterior=posterior,attrs={"sample_stats":{"backend":"nutpie"}})
    fixed=convert_trace(trace)
    fixed.to_netcdf(tmp_path/"legacy.nc")
    restored=az.from_netcdf(tmp_path/"legacy.nc")
    np.testing.assert_array_equal(restored.posterior.beta,posterior.beta)
