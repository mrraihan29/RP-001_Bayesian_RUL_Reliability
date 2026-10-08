from __future__ import annotations
import argparse, hashlib, json, os, platform, subprocess, threading, time, traceback
from dataclasses import replace
from pathlib import Path
import arviz as az
import numpy as np
import nutpie, psutil
from .data import ROOT,generate_synthetic,load_training,manifest,fit_preprocessor,make_dataset
from .model import build_model,flatten_parameters,numpy_terms,covariance,prior_draws
PLAN=json.loads((ROOT/"configs/pilot_plan_v0.3.json").read_text())
ENV=json.loads((ROOT/"logs/pilot_environment.json").read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def git_state():
    git=r"C:\Program Files\Git\cmd\git.exe"
    commit=subprocess.check_output([git,"-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    dirty=bool(subprocess.check_output([git,"-C",str(ROOT),"status","--porcelain"],text=True).strip())
    return commit,dirty
def write_json(path,obj):
    path.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n")
def convert_trace(trace):
    if isinstance(trace,az.InferenceData):
        idata=trace
    else:
        groups={}
        for name in ("posterior","sample_stats","warmup_posterior","warmup_sample_stats"):
            if name in trace:
                node=trace[name]
                groups[name]=node.to_dataset()
        idata=az.InferenceData(**groups)
    # Preserve nested backend metadata as JSON attributes without altering any samples.
    def safe(value):
        return json.dumps(value,sort_keys=True,default=str) if isinstance(value,(dict,list,tuple)) else value
    idata.attrs={k:safe(v) for k,v in idata.attrs.items()}
    for group in idata.groups():
        ds=getattr(idata,group)
        ds.attrs={k:safe(v) for k,v in ds.attrs.items()}
        for variable in ds.variables:
            ds[variable].attrs={k:safe(v) for k,v in ds[variable].attrs.items()}
    return idata
def diagnostics(idata,rho_zero=False):
    names=["beta","gamma","Gamma","tau","r_g","sigma_z","sigma_r"]+([] if rho_zero else ["rho"])
    summary=az.summary(idata,var_names=names,round_to="none")
    stats=idata.sample_stats
    divergent=int(stats["diverging"].sum()) if "diverging" in stats else None
    energy_bfmi=az.bfmi(idata).tolist() if "energy" in stats else None
    depth_key=next((k for k in ("depth","tree_depth") if k in stats),None)
    saturation=float((stats[depth_key]>=12).mean()) if depth_key else None
    failures=[]
    rhat=float(summary["r_hat"].max()); bulk=float(summary["ess_bulk"].min());tail=float(summary["ess_tail"].min())
    if not np.isfinite(rhat) or rhat>=1.01: failures.append("Rhat threshold")
    if bulk<400: failures.append("Bulk ESS threshold")
    if tail<400: failures.append("Tail ESS threshold")
    if divergent is None or divergent>0: failures.append("Missing/nonzero divergences")
    if energy_bfmi is None or min(energy_bfmi)<=.3: failures.append("Missing/low BFMI")
    if saturation is None or saturation>.01: failures.append("Missing/excessive tree depth saturation")
    return {"rhat_max":rhat,"bulk_ess_min":bulk,"tail_ess_min":tail,
            "divergences":divergent,"bfmi":energy_bfmi,"maxdepth_fraction":saturation,
            "sample_stat_keys":list(stats.data_vars),"acceptance":"PASS" if not failures else "FAIL",
            "failures":failures},summary
def recovery(idata,truth):
    if truth is None: return None
    out=[]
    for name in ("beta","gamma","Gamma","tau","r_g","sigma_z","sigma_r","rho"):
        values=idata.posterior[name].values
        flat=values.reshape((-1,)+values.shape[2:])
        mean=flat.mean(axis=0);sd=flat.std(axis=0,ddof=1)
        q=np.quantile(flat,[.025,.975],axis=0)
        target=np.asarray(truth[name])
        for index in np.ndindex(target.shape) if target.ndim else [()]:
            m=float(mean[index]);s=float(sd[index]);t=float(target[index])
            out.append({"parameter":name+str(index),"truth":t,"mean":m,"sd":s,
                        "equal_tail95":[float(q[0][index]),float(q[1][index])],
                        "truth_in95":bool(q[0][index]<=t<=q[1][index]),
                        "standardized_mean_error":float((m-t)/s) if s>0 else None})
    maxz=max(abs(r["standardized_mean_error"]) for r in out if r["standardized_mean_error"] is not None)
    return {"parameters":out,"max_abs_standardized_mean_error":maxz,
            "gross_recovery_flag":maxz>3,
            "interpretation":"Four fixed datasets, not SBC or repeated-sampling interval coverage."}
def predictive_checks(data,draws,seed,error="normal"):
    rng=np.random.default_rng(seed)
    indices=np.linspace(0,len(draws)-1,1000,dtype=int)
    conditional=[];joint=[];zstats=[]
    actual_y=[float(data.y.mean()),float(data.y.std()),float(np.quantile(data.y,.9))]
    actual_z=[float(data.z.std()),float(np.mean(data.z[:,-1]-data.z[:,0]))]
    for j in indices:
        p=draws[j]
        _,_,mu,var,_=numpy_terms(data,p,error)
        if error=="contamination":
            var=var+8*float(p["sigma_r"])**2*(rng.random(len(data.ids))<.05)
        y=mu+np.sqrt(var)*rng.normal(size=len(mu))
        conditional.append([y.mean(),y.std(),np.quantile(y,.9)])
        S=covariance(p)
        g=rng.multivariate_normal(np.zeros(2),S,size=len(mu))+data.a@p["Gamma"].T
        rho=float(p["rho"]);w=data.z.shape[1]
        K=rho**np.abs(np.arange(w)[:,None]-np.arange(w)[None,:])
        z=g@data.B.T+rng.multivariate_normal(np.zeros(w),p["sigma_z"]**2*K,size=len(mu))
        yrep=data.a@p["beta"]+g@p["gamma"]+p["sigma_r"]*rng.normal(size=len(mu))
        if error=="contamination":
            extra=(rng.random(len(mu))<.05)
            yrep=data.a@p["beta"]+g@p["gamma"]+p["sigma_r"]*rng.normal(size=len(mu))*np.where(extra,3.,1.)
        joint.append([yrep.mean(),yrep.std(),np.quantile(yrep,.9)])
        zstats.append([z.std(),np.mean(z[:,-1]-z[:,0])])
    return {"conditional_y_statistics":actual_y,"joint_y_statistics":actual_y,
            "observed_z_statistics":actual_z,
            "conditional_y_replica_quantiles":np.quantile(conditional,[.025,.5,.975],axis=0).tolist(),
            "joint_y_replica_quantiles":np.quantile(joint,[.025,.5,.975],axis=0).tolist(),
            "joint_z_replica_quantiles":np.quantile(zstats,[.025,.5,.975],axis=0).tolist(),
            "conditional_tail_areas":np.mean(np.asarray(conditional)>=actual_y,axis=0).tolist(),
            "joint_z_tail_areas":np.mean(np.asarray(zstats)>=actual_z,axis=0).tolist(),
            "n_draws":1000,"scope":"Model fit diagnostics, not out-of-sample performance or calibration."}
def prior_check():
    result=[]
    for scale in (.5,1.,2.):
        draws=prior_draws(4000,7710,scale)
        rng=np.random.default_rng(7711)
        vals=[]
        for p in draws:
            age=np.array([[1.,np.log(c/100)] for c in (30,100,250)])
            g=rng.multivariate_normal(np.zeros(2),covariance(p),size=3)+age@p["Gamma"].T
            y=age@p["beta"]+g@p["gamma"]+rng.normal(0,p["sigma_r"],size=3)
            vals.append(y)
        vals=np.asarray(vals)
        result.append({"prior_scale":scale,"ages":[30,100,250],"rul_quantiles":np.exp(np.quantile(vals,[.01,.05,.5,.95,.99],axis=0)).tolist(),
                       "prob_rul_lt1":np.mean(vals<0,axis=0).tolist(),
                       "prob_rul_gt1000":np.mean(vals>np.log(1000),axis=0).tolist(),
                       "prob_rul_gt5000":np.mean(vals>np.log(5000),axis=0).tolist()})
    write_json(ROOT/"results/pilot/prior_predictive.json",{"seed":7710,"draws_per_scale":4000,"results":result,
              "scope":"Working priors; no domain plausibility threshold or empirical calibration certified."})
def run(run_id):
    outdir=ROOT/"results/pilot";outdir.mkdir(exist_ok=True,parents=True)
    metrics=outdir/(run_id+".json")
    if metrics.exists(): raise FileExistsError("Preserve completed/failed runs; choose a new repair ID.")
    commit,dirty=git_state()
    config={"run_id":run_id,"sampling":PLAN["sampling"],"source_plan":"configs/pilot_plan_v0.3.json"}
    truth=None;scale=1.;error="normal";rho_zero=False;extra_sensor=None
    base_id=run_id.split("_repair")[0]
    syn=next((x for x in PLAN["synthetic_design"] if x["id"]==base_id),None)
    if syn:
        data,truth=generate_synthetic(syn["n"],syn["seed"],syn["rho"],syn["weak"])
        config.update(syn)
        seed=10000+syn["seed"]
    elif base_id in PLAN["training_runs"]:
        engines=load_training()
        roles=("fit","tune") if base_id in ("refit","sensor_oracle") else ("fit",)
        ids=[r["engine"] for r in manifest() if r["role"] in roles and r["eligible_alive"]]
        pre=fit_preprocessor(engines,ids)
        data=make_dataset(engines,pre,roles)
        if base_id=="sensor_oracle":
            calibration=make_dataset(engines,pre,("calibration",),allow_calibration=True)
            extra_sensor=replace(calibration,a=calibration.a[:1],z=calibration.z[:1],ids=calibration.ids[:1],y=None)
            assert int(extra_sensor.ids[0]) not in set(data.ids)
            np.savez(outdir/(run_id+"_extra_sensors.npz"),a=extra_sensor.a,z=extra_sensor.z,B=extra_sensor.B,ids=extra_sensor.ids)
            config["extra_sensor_engine"]=int(extra_sensor.ids[0])
            config["extra_sensor_sha256"]=sha(outdir/(run_id+"_extra_sensors.npz"))
        prepath=outdir/("refit_preprocessor_bayes.npz" if len(ids)==56 else "fit_preprocessor.npz")
        if prepath.exists():
            stored=np.load(prepath)
            for key in pre: np.testing.assert_array_equal(stored[key],pre[key])
        else: np.savez(prepath,**pre)
        config.update({"dataset":f"FD001 training fitting cohort n={len(ids)}","data_sha256":"963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8",
                       "preprocessing_fit_ids":ids,"pc1_explained_ratio":pre["pc1_explained_ratio"]})
        seed=13000+PLAN["training_runs"].index(base_id)
        scale=.5 if base_id=="prior_half" else 2. if base_id=="prior_double" else 1.
        rho_zero=base_id=="rho_zero";error="contamination" if base_id=="contamination" else "normal"
    else: raise ValueError("Unknown prespecified pilot run")
    config.update({"prior_scale":scale,"error":error,"rho_zero":rho_zero,"seed":seed})
    config_hash=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
    write_json(outdir/(run_id+"_config.json"),config)
    np.savez(outdir/(run_id+"_data.npz"),a=data.a,z=data.z,y=data.y,B=data.B,ids=data.ids)
    status="failed";exception=None;peak=[psutil.Process().memory_info().rss]
    stop=threading.Event()
    def monitor():
        while not stop.wait(.5): peak[0]=max(peak[0],psutil.Process().memory_info().rss)
    thread=threading.Thread(target=monitor,daemon=True);thread.start()
    start=time.perf_counter();cpu=time.process_time()
    result={}
    try:
        model=build_model(data,scale,error,rho_zero,extra_sensor=extra_sensor)
        cstart=time.perf_counter()
        compiled=nutpie.compile_pymc_model(model,backend="numba")
        compile_seconds=time.perf_counter()-cstart
        sample_start=time.perf_counter()
        raw=nutpie.sample(compiled,draws=2000,tune=1000,chains=4,cores=2,seed=seed,
                          target_accept=.95,maxdepth=12,progress_bar=False,save_warmup=False)
        idata=convert_trace(raw)
        sampling_seconds=time.perf_counter()-sample_start
        idata.to_netcdf(outdir/(run_id+".nc"))
        diag,summary=diagnostics(idata,rho_zero)
        summary.to_csv(outdir/(run_id+"_summary.csv"))
        draws=flatten_parameters(idata)
        ppc=predictive_checks(data,draws,seed+100,error)
        rec=recovery(idata,truth)
        status="completed"
        result={"diagnostics":diag,"recovery":rec,"posterior_predictive_checks":ppc,
                "compile_seconds":compile_seconds,"sampling_seconds":sampling_seconds,
                "posterior_file":str((outdir/(run_id+".nc")).relative_to(ROOT)),
                "posterior_sha256":sha(outdir/(run_id+".nc"))}
    except Exception as exc:
        exception=traceback.format_exc()
        result={"exception":exception}
    finally:
        stop.set();thread.join()
        result.update({"run_id":run_id,"phase":"exploratory" if syn or run_id=="base" else "robustness",
                       "status":status,"code_commit":commit,"code_dirty":dirty,"config_hash":config_hash,
                       "environment_fingerprint":ENV["fingerprint"],"config":config,
                       "wall_seconds":time.perf_counter()-start,"process_cpu_seconds":time.process_time()-cpu,
                       "peak_process_rss_gib":peak[0]/2**30,"official_test_access":False,
                       "confirmatory":False})
        write_json(metrics,result)
        registry={"run_id":run_id,"phase":result["phase"],"method":"Bayesian joint landmark pilot",
                  "code_commit":commit,"code_dirty":dirty,"config_hash":config_hash,"status":status,
                  "metrics_file":str(metrics.relative_to(ROOT)),"seed":seed,
                  "environment_fingerprint":ENV["fingerprint"],"data_file":f"results/pilot/{run_id}_data.npz",
                  "data_fingerprint":sha(outdir/(run_id+"_data.npz")),
                  "wall_seconds":result["wall_seconds"],"cpu_seconds":result["process_cpu_seconds"],
                  "protected_test_access":False}
        with (ROOT/"research/experiment_registry.jsonl").open("a") as f: f.write(json.dumps(registry)+"\n")
    print(json.dumps({k:result.get(k) for k in ("run_id","status","diagnostics","wall_seconds","process_cpu_seconds","peak_process_rss_gib","exception")}),flush=True)
    if exception: raise RuntimeError(exception)
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--run",required=True);args=parser.parse_args()
    (ROOT/"results/pilot").mkdir(parents=True,exist_ok=True)
    if args.run=="prior": prior_check()
    else: run(args.run)
if __name__=="__main__": main()
