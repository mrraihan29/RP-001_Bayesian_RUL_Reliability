from dataclasses import asdict
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
import joblib
from .data import ROOT,load_training,manifest,fit_preprocessor,make_dataset,features
from .comparators import candidate_specs,fit_candidate,predict_endpoints,select_candidate,fit_median_candidate,fit_gaussian_logr_reference,predict_gaussian_logr_reference,predict_median_candidate,mean90_interval_score
from .metrics import calibrate,correction,conformal_rank
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.write_text(json.dumps(o,indent=2)+"\n")
def main():
    root=ROOT/"results/pilot"
    out=root/"comparator_calibration.json"
    if out.exists():raise FileExistsError("Preserve comparator pilot results")
    start=time.perf_counter();cpu=time.process_time()
    git=r"C:\Program Files\Git\cmd\git.exe"
    commit=subprocess.check_output([git,"-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
    dirty=bool(subprocess.check_output([git,"-C",str(ROOT),"status","--porcelain"],text=True).strip())
    env=json.loads((ROOT/"logs/pilot_environment.json").read_text())
    eng=load_training();man=manifest()
    fit_ids=[r["engine"] for r in man if r["eligible_alive"] and r["role"]=="fit"]
    pre=fit_preprocessor(eng,fit_ids)
    fit=make_dataset(eng,pre,("fit",));tune=make_dataset(eng,pre,("tune",))
    fs,ff=features(fit),features(fit,True);ts,tf=features(tune),features(tune,True)
    records=[];scores={};failures={}
    for spec in candidate_specs():
        begin=time.perf_counter()
        candidate=fit_candidate(fs,ff,np.exp(fit.y),spec)
        score=None
        if candidate.status=="completed":
            lower,upper=predict_endpoints(candidate,ts,tf)
            score=mean90_interval_score(np.exp(tune.y),lower,upper)
        else:failures[spec.candidate_id]=str(candidate.failure_message)
        scores[spec.candidate_id]=score
        config=asdict(spec)
        cfg=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
        records.append({"candidate_id":spec.candidate_id,"config":config,"status":candidate.status,
                        "tuning_mean90_interval_score":score,"elapsed_seconds":time.perf_counter()-begin,
                        "failure":candidate.failure_message,"config_hash":cfg})
        registry={"run_id":"cqr_"+spec.candidate_id,"phase":"tuning","method":"CQR endpoint regressor",
                  "code_commit":commit,"code_dirty":dirty,"config_hash":cfg,"status":candidate.status,
                  "metrics_file":"results/pilot/cqr_search.json","seed":20261008,
                  "data_fingerprint":"963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8",
                  "environment_fingerprint":env["fingerprint"],"protected_test_access":False}
        with (ROOT/"research/experiment_registry.jsonl").open("a") as f:f.write(json.dumps(registry)+"\n")
    decision=select_candidate(scores,failure_reasons=failures)
    write(root/"cqr_search.json",{"records":records,"selection":asdict(decision),"calibration_accessed":False,
                                "phase":"tuning","code_commit":commit,"code_dirty":dirty})
    refit_ids=[r["engine"] for r in man if r["eligible_alive"] and r["role"] in ("fit","tune")]
    pre=fit_preprocessor(eng,refit_ids)
    combined=make_dataset(eng,pre,("fit","tune"))
    Xs,Xf=features(combined),features(combined,True)
    selected=fit_candidate(Xs,Xf,np.exp(combined.y),decision.candidate)
    median=fit_median_candidate(Xs,Xf,np.exp(combined.y),decision.candidate)
    reference=fit_gaussian_logr_reference(Xs,np.exp(combined.y))
    assert selected.status=="completed" and median.status=="completed"
    np.savez(root/"refit_preprocessor.npz",**pre)
    freeze={"frozen":True,"version":"pilot-v0.3","selected_cqr":decision.candidate.candidate_id,
            "selection_source_sha256":sha(root/"cqr_search.json"),"source_code_commit":commit,"code_dirty":dirty,
            "fit_ids":refit_ids,"calibration_access_before_freeze":False,
            "bayesian_policy":"Base fixed priors, no winner selection from sensitivities; refit56 after sampler diagnostics",
            "primary_endpoint_changed":False,"final_protocol_locked":False,"official_test_access":False}
    freeze_path=ROOT/"configs/pilot_selection_freeze.json"
    if freeze_path.exists():raise FileExistsError("Existing selection freeze")
    write(freeze_path,freeze)
    # Calibration outcomes first enter this module only after the immutable selection record above.
    cal=make_dataset(eng,pre,("calibration",),allow_calibration=True)
    cs,cf=features(cal),features(cal,True);R=np.exp(cal.y)
    lo,up=predict_endpoints(selected,cs,cf)
    q=calibrate(R,lo,up)
    rawscores=np.maximum(lo-R,R-up)
    rng=np.random.default_rng(8103304)
    sensitivity=[]
    for n in (9,19,24,25):
        vals=[correction(rawscores[rng.choice(len(R),size=n,replace=False)]) for _ in range(500)]
        sensitivity.append({"n":n,"rank":conformal_rank(n),"correction_range95":np.quantile(vals,[.025,.5,.975]).tolist(),
                            "scope":"Without-replacement subset sensitivity within fixed25; not a confidence interval"})
    boot=[correction(rawscores[rng.integers(0,25,size=25)]) for _ in range(2000)]
    leave=[correction(np.delete(rawscores,i)) for i in range(25)]
    rp=predict_gaussian_logr_reference(reference,cs)
    med=predict_median_candidate(median,cs,cf)
    joblib.dump({"preprocessor":pre,"selected":selected,"median":median,"reference":reference},root/"selected_comparator.joblib")
    result={"phase":"exploratory_calibration_feasibility","selected_cqr":decision.candidate.candidate_id,
            "n_refit":len(combined.ids),"n_calibration":len(cal.ids),"rank":24,"q_raw":float(np.partition(rawscores,23)[23]),
            "nonshrinking_correction":q,"calibration_engine_ids":cal.ids.tolist(),"raw_engine_scores":rawscores.tolist(),
            "uncalibrated_endpoints":{"lower":lo.tolist(),"upper":up.tolist(),"median":med.tolist()},
            "reference_endpoints":{"lower":rp.lower.tolist(),"upper":rp.upper.tolist(),"median":rp.median.tolist()},
            "subset_sensitivity":sensitivity,"bootstrap25_correction_range95":np.quantile(boot,[.025,.5,.975]).tolist(),
            "leave_one_out_corrections":leave,"negative_median_count":int((med<0).sum()),
            "calibration_score_use":"Feasibility/influence only; no independent performance claim on calibration engines",
            "bootstrap_interpretation":"Fixed selected/refitted model and representation; excludes training and selection variation",
            "official_test_access":False,"confirmatory":False,"practical_threshold":None,
            "code_commit":commit,"code_dirty":dirty,"environment_fingerprint":env["fingerprint"],
            "wall_seconds":time.perf_counter()-start,"process_cpu_seconds":time.process_time()-cpu,
            "preprocessor_sha256":sha(root/"refit_preprocessor.npz"),"selection_freeze_sha256":sha(freeze_path)}
    write(out,result)
    with (ROOT/"research/experiment_registry.jsonl").open("a") as f:f.write(json.dumps({
        "run_id":"cqr_refit_calibration_feasibility","phase":"exploratory","method":"Frozen CQR+calibration",
        "code_commit":commit,"code_dirty":dirty,"config_hash":sha(freeze_path),"status":"completed",
        "metrics_file":str(out.relative_to(ROOT)),"environment_fingerprint":env["fingerprint"],"seed":8103304,
        "protected_test_access":False,"wall_seconds":result["wall_seconds"],"cpu_seconds":result["process_cpu_seconds"]})+"\n")
    print(json.dumps({k:result[k] for k in ("selected_cqr","n_refit","n_calibration","q_raw","nonshrinking_correction","bootstrap25_correction_range95","wall_seconds")}))
if __name__=="__main__":main()
