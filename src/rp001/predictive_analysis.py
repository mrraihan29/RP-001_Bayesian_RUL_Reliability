from dataclasses import replace
from pathlib import Path
import hashlib,json,subprocess,time
import arviz as az
import numpy as np
from .data import ROOT,load_training,manifest,fit_preprocessor,make_dataset
from .model import flatten_parameters
from .prediction import predict_data
from .metrics import calibrate
def write(p,obj):p.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n")
def load_result(name):return json.loads((ROOT/f"results/pilot/{name}.json").read_text())
def correlation_summary(idata):
    columns=[];names=[]
    for name in ("beta","gamma","Gamma","tau","r_g","sigma_z","sigma_r","rho"):
        vals=idata.posterior[name].values;flat=vals.reshape((-1,)+vals.shape[2:])
        if flat.ndim==1:flat=flat[:,None]
        else:flat=flat.reshape((len(flat),-1))
        for j in range(flat.shape[1]):
            if np.std(flat[:,j])>1e-12:
                columns.append(flat[:,j]);names.append(f"{name}[{j}]")
    corr=np.corrcoef(columns)
    pairs=[]
    for i in range(len(names)):
        for j in range(i):
            pairs.append({"first":names[i],"second":names[j],"correlation":float(corr[i,j])})
    return sorted(pairs,key=lambda x:abs(x["correlation"]),reverse=True)[:10]
def main():
    path=ROOT/"results/pilot/predictive_integration.json"
    if path.exists():raise FileExistsError("Preserve predictive integration result")
    start=time.perf_counter();cpu=time.process_time()
    git=r"C:\Program Files\Git\cmd\git.exe"
    commit=subprocess.check_output([git,"-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    dirty=bool(subprocess.check_output([git,"-C",str(ROOT),"status","--porcelain"],text=True).strip())
    eng=load_training();man=manifest()
    fitids=[r["engine"] for r in man if r["eligible_alive"] and r["role"]=="fit"]
    pre=fit_preprocessor(eng,fitids);tune=make_dataset(eng,pre,("tune",))
    sensitivities={}
    correlations={}
    for name in ("base","prior_half","prior_double","rho_zero","contamination"):
        idata=az.from_netcdf(ROOT/f"results/pilot/{name}.nc")
        assert load_result(name)["diagnostics"]["acceptance"]=="PASS"
        draws=flatten_parameters(idata)
        sensitivities[name]=predict_data(draws,replace(tune,y=None),error="contamination" if name=="contamination" else "normal")
        correlations[name]=correlation_summary(idata)
    base=np.array([[p[k] for k in ("lower","median","upper")] for p in sensitivities["base"]])
    delta=[]
    for name,rows in sensitivities.items():
        current=np.array([[p[k] for k in ("lower","median","upper")] for p in rows])
        delta.append({"variant":name,"max_absolute_quantile_delta_cycles":np.max(abs(current-base),axis=0).tolist(),
                      "mean_absolute_quantile_delta_cycles":np.mean(abs(current-base),axis=0).tolist(),
                      "weight_ess_min":min(r["weight_ess"] for r in rows),
                      "max_between_chain_quantile_mcse_approx":np.max([r["between_chain_quantile_mcse_approx"] for r in rows],axis=0).tolist()})
    refitids=[r["engine"] for r in man if r["eligible_alive"] and r["role"] in ("fit","tune")]
    pre=fit_preprocessor(eng,refitids)
    cal=make_dataset(eng,pre,("calibration",),allow_calibration=True)
    idata=az.from_netcdf(ROOT/"results/pilot/refit.nc")
    draws=flatten_parameters(idata)
    predictions=predict_data(draws,replace(cal,y=None))
    R=np.exp(cal.y)
    correction=calibrate(R,np.array([p["lower"] for p in predictions]),np.array([p["upper"] for p in predictions]))
    oracle_idata=az.from_netcdf(ROOT/"results/pilot/sensor_oracle.nc")
    oracle_draws=flatten_parameters(oracle_idata)
    one=replace(cal,a=cal.a[:1],z=cal.z[:1],y=None,ids=cal.ids[:1])
    oracle=predict_data(oracle_draws,one,reweight=False)[0]
    oracle["conditioning"]="Exact global posterior was updated with this engine's sensors; conditional latent prediction; no second weighting"
    approximate=predictions[0]
    keys=("lower","median","upper")
    diffs=np.array([approximate[k]-oracle[k] for k in keys])
    am=np.array(approximate["between_chain_quantile_mcse_approx"]);om=np.array(oracle["between_chain_quantile_mcse_approx"])
    tolerance=np.maximum(1.,3*np.sqrt(am**2+om**2))
    failures=[]
    ess=min(p["weight_ess"] for p in predictions)
    mc=np.array([p["between_chain_quantile_mcse_approx"] for p in predictions])
    if ess<1000:failures.append("At least one new-engine importance ESS below1000")
    if np.max(mc)>.5:failures.append("At least one predictive quantile approximate MCSE above0.5cycle")
    if not np.all(abs(diffs)<=tolerance):failures.append("Exact sensor-update oracle disagreement")
    output={"scope":"Training-only numerical prediction and sensitivity diagnostics; not independent performance evidence",
            "tuning_engine_predictions":sensitivities,"sensitivity_deltas":delta,"top_posterior_correlations":correlations,
            "refit_calibration_engine_predictions":predictions,"importance_weight_ess_min":ess,
            "quantile_mcse_max_approx":float(np.max(mc)),
            "prediction_acceptance":"PASS" if not failures else "FAIL","failure_reasons":failures,
            "bayesian_calibration_ablation":{"n_calibration":25,"rank":24,"nonshrinking_correction_cycles":correction,
                "accepted_for_inference":not failures,"scope":"Secondary development calibration feasibility; no performance claim"},
            "sensor_update_oracle":{"engine":int(cal.ids[0]),"importance_prediction":approximate,"exact_update_prediction":oracle,
                "differences_cycles":diffs.tolist(),"agreement_tolerances":tolerance.tolist(),
                "agreement":bool(np.all(abs(diffs)<=tolerance)),
                "scope":"One deterministic held-out training engine; no universal importance-sampling validation"},
            "code_commit":commit,"code_dirty":dirty,"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "environment_fingerprint":json.loads((ROOT/"logs/pilot_environment.json").read_text())["fingerprint"],
            "wall_seconds":time.perf_counter()-start,"process_cpu_seconds":time.process_time()-cpu,
            "official_test_access":False,"confirmatory":False,"practical_threshold":None}
    write(path,output)
    with (ROOT/"research/experiment_registry.jsonl").open("a") as f:f.write(json.dumps({
         "run_id":"predictive_integration_pilot","phase":"exploratory","method":"Sensor-only joint predictive integration",
         "code_commit":commit,"code_dirty":dirty,"config_hash":output["script_sha256"],"status":"completed",
         "metrics_file":str(path.relative_to(ROOT)),"seed":None,"environment_fingerprint":output["environment_fingerprint"],
         "protected_test_access":False,"wall_seconds":output["wall_seconds"],"cpu_seconds":output["process_cpu_seconds"]})+"\n")
    print(json.dumps({k:output[k] for k in ("prediction_acceptance","failure_reasons","importance_weight_ess_min","quantile_mcse_max_approx","bayesian_calibration_ablation","sensor_update_oracle","sensitivity_deltas","wall_seconds")}))
if __name__=="__main__":main()
