"""Independent SOL arithmetic verification of sealed Stage B bytes.
No new roots, predictions, fitting, draws, labels or outcome scoring.
"""
from pathlib import Path
import datetime, hashlib, itertools, json, math, subprocess, time
import numpy as np
from scipy.special import ndtr
from scipy.stats import chi2, norm
R=Path(__file__).resolve().parents[2]
P=R/".protected/stage_B/B001"
V=R/".protected/stage_B/B001_verification"
V.mkdir(parents=True,exist_ok=False)
D=R/"docs/stage_B"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding="utf8"))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("xb") as f:f.write((json.dumps(d,indent=2,allow_nan=False)+"\n").encode())
def check(condition, gate, **details):
    if not bool(condition):raise ValueError(json.dumps({"gate":gate,**details},allow_nan=False))
def equal(a,b):
    return np.allclose(a,b,rtol=1e-12,atol=1e-14,equal_nan=False)
began=time.monotonic()
try:
    public=read(D/"STAGE_B_RESULT.json")
    check(sha(P/"PAYLOAD_MANIFEST.json")==public["protected_payload_manifest_sha256"],"manifest_hash")
    manifest=read(P/"PAYLOAD_MANIFEST.json")
    for row in manifest["files"]:
        path=R/row["path"]
        check(path.is_file() and sha(path)==row["sha256"] and path.stat().st_size==row["bytes"],"payload_hash",path=row["path"])
    expected_paths={row["path"] for row in manifest["files"]}
    actual_paths={str(p.relative_to(R)).replace("\\","/") for p in P.rglob("*") if p.is_file() and p.name!="PAYLOAD_MANIFEST.json"}
    check(expected_paths==actual_paths,"payload_complete_inventory")
    sealed=read(R/"logs/protocol_lock/final_G3/lock_payload_manifest.json")
    for row in sealed["files"]:
        check(sha(R/row["path"])==row["sha256"],"G3_unchanged",path=row["path"])
    frozen_code=read(R/"docs/protocol_lock/FROZEN_CODE_AND_ENVIRONMENT_MANIFEST.json")
    for row in frozen_code["scientific_sources"]+frozen_code["scientific_configurations"]:
        check(sha(R/row["path"])==row["sha256"],"science_unchanged",path=row["path"])
    previous=None;events=sorted((P/"events").glob("*.json"))
    for index,path in enumerate(events,1):
        event=read(path)
        check(event["event"]==index and event["previous_sha256"]==previous,"event_chain",event=index)
        previous=sha(path)
    check(previous==public["journal_head_sha256"],"journal_head")
    check([r["kind"] for r in map(read,events[:2])]==["CAMPAIGN_REGISTERED","PREFLIGHT_PASS"],"pre_sensor_registry")
    check(len(read(P/"failure_ledger.json"))==0,"empty_failure_ledger")
    outcome=read(P/"outcome.json")
    check(outcome["status"]=="READY FOR OWNER STAGE C REVIEW" and outcome["labels_accessed"]==False and outcome["new_draws"]==0 and outcome["scoring"]==False,"outcome_boundary")
    ledger=read(P/"engine_ledger_final.json")
    check(len(ledger)==100 and [r["engine"] for r in ledger]==list(range(1,101)) and all(r["Bayesian"]==r["CQR"]=="PASS" and r["failure"] is None for r in ledger),"complete_ledger")
    # Independently check the exact source schema/order and observation history.
    raw=np.loadtxt(R/"data/raw/test_FD001.txt",dtype=np.float64)
    audit=read(P/"input_overlap_audit.json")
    check(sha(R/"data/raw/test_FD001.txt")==audit["sensor_sha256"],"sensor_source")
    check(raw.shape==(13096,26) and np.isfinite(raw).all(),"schema_finite")
    schema=read(R/"data/raw/schema_contract.json")
    check([f["name"] for f in schema["fields"]]==["engine_id","cycle"]+[f"setting_{i}" for i in range(1,4)]+[f"sensor_{i}" for i in range(1,22)],"declared_column_order")
    check(len(np.unique(raw[:,:2],axis=0))==len(raw),"unique_keys")
    check(np.array_equal(np.unique(raw[:,0]),np.arange(1,101)),"ID_cohort")
    for row in ledger:
        obs=raw[raw[:,0]==row["engine"]]
        check(np.array_equal(obs[:,1],np.arange(1,len(obs)+1)) and len(obs)==row["cutoff"],"cutoff_alignment",engine=row["engine"])
    check(audit["status"]=="PASS" and not audit["exact_pairs"] and not audit["near_pairs"] and audit["near_duplicate_checks"]==10000,"overlap_outcome")
    quantile_records=[];replication_records=[]
    for i in range(1,101):
        terms=dict(np.load(P/f"conditional_terms/engine_{i:03d}.npz",allow_pickle=False))
        mu,var,lw=(terms[k] for k in ("means","variances","log_weights"))
        check(mu.shape==var.shape==lw.shape==(12,8000) and np.isfinite(mu).all() and np.isfinite(var).all() and (var>0).all(),"conditional_terms",engine=i)
        check(int(terms["engine"])==i and int(terms["cutoff"])==ledger[i-1]["cutoff"],"conditional_alignment",engine=i)
        fit_results={}
        for fit,sl in [("pooled",slice(None))]+[(f"v04_main_r{k+1}",slice(k*4,(k+1)*4)) for k in range(3)]:
            m,v,logw=mu[sl],var[sl],lw[sl]
            check(np.isfinite(logw).all(),"weights_finite",engine=i)
            n=m.size;n_draw=m.shape[1]
            w=np.exp(logw-logw.max());sumw=float(w.sum());meanw=sumw/n
            weightESS=min(sumw**2/float((w*w).sum()),float(n))
            fit_results[fit]=[]
            for p in (.05,.5,.95):
                name="pooled" if fit=="pooled" else fit
                record=read(P/f"precision/engine_{i:03d}_{name}_p{int(p*100):02d}.json")
                q=record["quantile_log_rul"];Q=math.exp(q)
                z=(q-m)/np.sqrt(v)
                cdf=float(np.sum((w/sumw)*ndtr(z)))
                density=float(np.sum((w/sumw)*np.exp(-.5*z*z)/np.sqrt(2*np.pi*v)))
                check(abs(cdf-p)<=1e-10 and density>0 and math.isfinite(density),"root_density_guard",engine=i,fit=fit,p=p)
                check(equal(Q,record["quantile_rul"]) and equal(cdf,record["mixture_cdf_at_quantile"]) and equal(density,record["weighted_mixture_density_log_rul"]) and equal(weightESS,record["weight_ess"]),"root_storage_identity",engine=i,fit=fit,p=p)
                check(record["tail_probability"]==.05/(100*3*2) and record["chain_count"]==m.shape[0] and record["draws_per_chain"]==8000,"precision_family",engine=i,fit=fit,p=p)
                Q=float(record["quantile_rul"])  # Use the exact stored endpoint after verifying exp(q).
                h=w*(ndtr(z)-p)
                checks=[]
                for batch,record_b in zip((250,500),record["batch_size_results"]):
                    check(record_b["batch_size"]==batch,"batch_order")
                    nb=n_draw//batch
                    bm=h.reshape(h.shape[0],nb,batch).mean(axis=2)
                    lrv=batch*np.var(bm,axis=1,ddof=1)
                    components=n_draw*lrv/(n*n*meanw**2*density**2)
                    vlog=float(components.sum())
                    active=components[components>0]
                    df=vlog*vlog/float(np.sum(active*active/(nb-1)))
                    ordinary=Q*math.sqrt(vlog)
                    upper=Q*math.sqrt(vlog*df/float(chi2.ppf(.05/(100*3*2),df)))
                    influenceESS=float(np.var(h,ddof=1))/(vlog*(density*meanw)**2)
                    check(all(math.isfinite(t) for t in (ordinary,upper,influenceESS,df)) and equal(ordinary,record_b["quantile_rul_mcse"]) and equal(upper,record_b["approximate_upper_quantile_rul_mcse"]) and equal(influenceESS,record_b["influence_ess"]) and equal(df,record_b["satterthwaite_degrees_of_freedom"]),"independent_MCSE_reconstruction",engine=i,fit=fit,p=p,batch=batch)
                    if fit=="pooled":
                        check(weightESS>=1000 and influenceESS>=400 and upper<=.5,"official_precision_guard",engine=i,p=p,batch=batch)
                    checks.append({"batch":batch,"MCSE":ordinary,"upper":upper,"influence_ESS":influenceESS})
                evidence={"engine":i,"fit":fit,"p":p,"q_cycles":Q,"weight_ESS":weightESS,"CDF_residual":cdf-p,"batches":checks,"PASS":True}
                quantile_records.append(evidence)
                fit_results[fit].append(evidence)
        bayes=read(P/f"Bayesian/engine_{i:03d}.json")
        qs=[r["q_cycles"] for r in fit_results["pooled"]]
        check(np.array_equal(np.array(qs),np.array([bayes[k] for k in ("lower","median","upper")])) and 0<qs[0]<=qs[1]<=qs[2],"Bayesian_stored_quantiles",engine=i)
        cqr=read(P/f"CQR/engine_{i:03d}.json")
        check(np.isfinite([cqr[k] for k in ("lower","median","upper")]).all() and 0<=cqr["lower"]<=cqr["upper"] and cqr["selected_id"]=="gb-depth1-leaf10-lr0p1" and cqr["correction"]==19.987558518873357 and cqr["cutoff"]==bayes["cutoff"]==ledger[i-1]["cutoff"],"CQR_identity_endpoints",engine=i)
        for a,b in itertools.combinations([f"v04_main_r{k}" for k in (1,2,3)],2):
            for ra,rb in zip(fit_results[a],fit_results[b]):
                mcsea=max(r["MCSE"] for r in ra["batches"]);mcseb=max(r["MCSE"] for r in rb["batches"])
                den=math.sqrt(mcsea**2+mcseb**2);diff=abs(ra["q_cycles"]-rb["q_cycles"]);zlim=float(norm.ppf(1-.05/(2*9*100)))
                check(math.isfinite(den) and den>0 and diff<=zlim*den,"independent_replication_guard",engine=i,p=ra["p"],fits=[a,b])
                saved=read(P/f"replication/engine_{i:03d}_{a}_{b}_p{int(ra['p']*100):02d}.json")
                check(saved["PASS"] and equal(saved["denominator"],den) and equal(saved["absolute_difference_cycles"],diff) and saved["z"]==zlim,"replication_storage",engine=i)
                replication_records.append({"engine":i,"p":ra["p"],"fits":[a,b],"standardized_difference":diff/den,"z":zlim,"PASS":True})
    check(len(quantile_records)==1200 and len(replication_records)==900,"complete_direct_verification")
    save(V/"independent_quantile_reconstruction.json",quantile_records)
    save(V/"independent_replication_reconstruction.json",replication_records)
    pooled=[r for r in quantile_records if r["fit"]=="pooled"]
    max_item=max(({"engine":r["engine"],"p":r["p"],**b} for r in pooled for b in r["batches"]),key=lambda r:r["upper"])
    summary={
        "status":"PASS","reviewer":"SOL direct mathematical verifier",
        "at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope":"Independent arithmetic reconstruction from sealed conditional terms and saved roots; no new roots, draws, predictions, labels or scoring",
        "protected_manifest_sha256":sha(P/"PAYLOAD_MANIFEST.json"),"payload_files_verified":len(manifest["files"]),
        "G3_sealed_files_unchanged":len(sealed["files"]),"journal_events_verified":len(events),
        "engine_ledger_rows":100,"all_quantiles_directly_verified":1200,"pooled_official_quantiles":300,
        "independent_fit_quantiles":900,"replication_comparisons":900,"two_batch_reconstructions":2400,
        "MCMC":"Locked diagnostics identity/finite states/divergences/depth verified in preflight; no resampling",
        "upper_MCSE_max_cycles":max_item["upper"],"upper_MCSE_max_location":{k:max_item[k] for k in ("engine","p","batch")},
        "minimum_weight_ESS":min(r["weight_ESS"] for r in pooled),
        "minimum_influence_ESS":min(b["influence_ESS"] for r in pooled for b in r["batches"]),
        "max_CDF_residual_abs":max(abs(r["CDF_residual"]) for r in pooled),
        "replication_max_standardized_difference":max(r["standardized_difference"] for r in replication_records),
        "replication_z":float(norm.ppf(1-.05/(2*9*100))),
        "precision_tail":.05/(100*3*2),
        "arithmetic_match_tolerance":"rtol1e-12/atol1e-14 only for agreement of independent calculations; official acceptance thresholds unchanged",
        "failure_count":0,"labels_accessed":False,"scoring":False,"new_sampling":False,
        "scientific_claim":"Numerical/custody acceptance only; no empirical predictive-performance conclusion",
        "wall_seconds":time.monotonic()-began,
        "procedural_disclosures":["Failure persistence was prospectively specified in committed driver; terminal failure_ledger.json materialized only at sealing; hash-chained registry began before sensors",
        "All100 training trajectories were cross-paired; normalization used existing81 eligible training-prefix population",
        "Headerless sensor column order is bound to official source archive and declared schema; sensor physical units not independently verified",
        "Local byte hashes and exclusive-create discipline do not establish WORM custody, independent identity authentication, encrypted isolation or clean-machine reproducibility"]}
    save(V/"direct_SOL_verification.json",summary)
    vf=[{"path":str(p.relative_to(R)).replace("\\","/"),"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(V.rglob("*")) if p.is_file()]
    save(V/"VERIFICATION_MANIFEST.json",{"files":vf,"excludes":"self","payload_manifest_sha256":sha(P/"PAYLOAD_MANIFEST.json")})
    summary["verification_manifest_sha256"]=sha(V/"VERIFICATION_MANIFEST.json")
    save(D/"DIRECT_SOL_COMPLETION_VERIFICATION.json",summary)
    print(json.dumps({k:summary[k] for k in ("status","payload_files_verified","all_quantiles_directly_verified","replication_comparisons","upper_MCSE_max_cycles","upper_MCSE_max_location","replication_max_standardized_difference","verification_manifest_sha256")}),flush=True)
except Exception as exc:
    failure={"status":"STAGE B BLOCKED","at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"failure":str(exc),"new_sampling":False,"labels_accessed":False,"repair_attempted":False}
    save(V/"VERIFICATION_FAILURE.json",failure)
    save(D/"DIRECT_SOL_VERIFICATION_FAILURE.json",failure)
    print(json.dumps(failure),flush=True)
    raise
