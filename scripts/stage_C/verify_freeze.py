"""Stage C final verification: existing artifacts only, never regenerate or score."""
from pathlib import Path
import csv, datetime, hashlib, importlib.metadata, itertools, json, math, os
import platform, subprocess, sys, time
R=Path(__file__).resolve().parents[2]
D=R/"docs/stage_C"
O=R/".protected/stage_C/C001"
B=R/".protected/stage_B/B001"
T=R/".protected/stage_B/B001_review_tables"
V=R/".protected/stage_B/B001_verification"
BASELINE="e3ce076de4bd6e1eec4844f5c53dc4d3d15d03cd"
EXPECTED={
"base_payload_manifest":"09ae59cb40c33af4170ae8b041550a9d1f8e49042b1ef8065e764c45e55fb7a1",
"verification_manifest":"6090ea4a08eaffb758b48042c8629c42e18cc82e5729d94b08e8eb96a15116df",
"review_tables_manifest":"2911bf37b68668584e1bf71564003ad5820a2073c32263cf048be456fd6404b3"}
BUNDLE="96084deb61336367b48f19251f0cd529e5deb98c754eb09a05dca5f52ef4263e"
VERSION="RP-001-G3-v0.5-AM1"
checks=[]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding="utf8"))
def save(p,data):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("xb") as f:f.write((json.dumps(data,indent=2,allow_nan=False)+"\n").encode())
def git(*args):return subprocess.check_output(["git","-C",str(R),*args],text=True).strip()
def check(value,gate,**detail):
    if not bool(value):raise ValueError(json.dumps({"gate":gate,**detail},allow_nan=False))
def file_check(path,expected,size=None):
    check(path.is_file(),"required_file",path=str(path.relative_to(R)))
    actual=sha(path)
    check(actual==expected and (size is None or path.stat().st_size==size),"byte_identity",path=str(path.relative_to(R)),expected=expected,actual=actual)
    checks.append({"path":str(path.relative_to(R)).replace("\\","/"),"sha256":actual,"bytes":path.stat().st_size,"PASS":True})
def member_inventory(manifest,folder,table=False):
    expected=set()
    for row in manifest["files"]:
        path=folder/row["name"] if table else R/row["path"]
        check(path.resolve().is_relative_to(folder.resolve()),"manifest_path_custody")
        file_check(path,row["sha256"],row["bytes"])
        expected.add(path.resolve())
    actual={p.resolve() for p in folder.rglob("*") if p.is_file()}
    actual.discard((folder/("REVIEW_TABLES_MANIFEST.json" if table else "VERIFICATION_MANIFEST.json" if folder==V else "PAYLOAD_MANIFEST.json")).resolve())
    check(actual==expected,"complete_payload_inventory",folder=str(folder.relative_to(R)),expected=len(expected),actual=len(actual))
    return len(expected)
def label_guard(event,args):
    if event=="open" and args and isinstance(args[0],(str,bytes,os.PathLike)):
        name=os.fsdecode(args[0]).replace("\\","/").split("/")[-1].lower()
        if name=="rul_fd001.txt":raise PermissionError("Stage D label access is not authorized")
sys.addaudithook(label_guard)

began=time.monotonic()
try:
    check(not O.exists(),"single_stage_C_attempt")
    check(git("status","--porcelain")=="","clean_verification_checkout")
    code_commit=git("rev-parse","HEAD")
    check(git("merge-base","--is-ancestor",BASELINE,code_commit)=="","reviewed_baseline_ancestor")
    plan=read(R/"configs/stage_C_verification_plan.json")
    file_check(Path(__file__),plan["verifier_sha256"])
    file_check(D/"OWNER_STAGE_C_DECISION.md",plan["owner_directive_sha256"])
    check(plan["candidate_bundle_sha256"]==BUNDLE and plan["expected_manifest_sha256"]==EXPECTED,"prospective_identifiers")

    # Preserve every Stage B tracked byte, including historical authorization state.
    public_paths=git("ls-tree","-r","--name-only",BASELINE,"docs/stage_B","scripts/stage_B","configs/stage_B_execution_plan.json").splitlines()
    for p in public_paths:
        historical=subprocess.check_output(["git","-C",str(R),"show",BASELINE+":"+p])
        file_check(R/p,hashlib.sha256(historical).hexdigest(),len(historical))
    candidate=read(R/"docs/stage_B/CANDIDATE_PACKAGE_RECEIPT.json")
    manifest_counts={}
    for key,expected in EXPECTED.items():
        row=candidate[key];path=R/row["path"]
        check(row["sha256"]==expected,"owner_manifest_identity",manifest=key)
        file_check(path,expected)
        manifest_counts[key]=member_inventory(read(path),T if key=="review_tables_manifest" else V if key=="verification_manifest" else B,key=="review_tables_manifest")
    check(manifest_counts=={"base_payload_manifest":3016,"verification_manifest":3,"review_tables_manifest":3},"required_manifest_member_counts")
    computed=hashlib.sha256(json.dumps(EXPECTED,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    check(computed==BUNDLE==candidate["candidate_bundle_identity_sha256"],"exact_candidate_bundle")
    check(candidate["science_commit"]=="fc7083d23d3cff5e4ee9a9f5d0af9036ec32e26d","G3_snapshot")
    check(candidate["official_sensor_prediction_execution_commit"]=="a85412ba7c8ada34c5c284251ef05d35cfaf15ee","Stage_B_execution_identity")

    receipt=read(R/"docs/protocol_lock/LOCK_RECEIPT.json")
    file_check(R/"docs/protocol_lock/LOCK_RECEIPT.json","9803eba8f616e6fd8bd95780ba829863cd629643d7e13590d8a4f5535509bade")
    file_check(R/receipt["payload_manifest_path"],receipt["payload_manifest_sha256"])
    g3=read(R/receipt["payload_manifest_path"])
    for row in g3["files"]:file_check(R/row["path"],row["sha256"],row["bytes"])
    code=read(R/"docs/protocol_lock/FROZEN_CODE_AND_ENVIRONMENT_MANIFEST.json")
    for row in code["scientific_sources"]+code["scientific_configurations"]:
        file_check(R/row["path"],row["sha256"],row["bytes"])
    source_map={r["path"]:r["sha256"] for r in code["scientific_sources"]}
    source_fp=hashlib.sha256(json.dumps(source_map,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    check(source_fp==candidate["scientific_source_map_sha256"]==receipt["scientific_source_map_sha256"],"scientific_source_map")
    packages={d.metadata["Name"]:d.version for d in importlib.metadata.distributions()}
    env={"python":platform.python_version(),"implementation":platform.python_implementation(),"platform":platform.platform(),
        "packages":dict(sorted(packages.items(),key=lambda x:x[0].lower())),"float_dtype":"float64","sampler":"nutpie NUTS","blas_threads":1}
    env_fp=hashlib.sha256(json.dumps(env,sort_keys=True).encode()).hexdigest()
    check(env==code["live_environment"] and env_fp==candidate["environment_fingerprint"],"live_environment_matches")
    for path,expected in receipt["dataset_split_plan_sha256"].items():file_check(R/path,expected)
    model=read(R/"docs/protocol_lock/FROZEN_MODEL_AND_CONFIGURATION_MANIFEST.json")
    posterior_hashes=[]
    for row in model["principal_posteriors"]:
        file_check(R/row["path"],row["sha256"],row["bytes"])
        file_check(R/f"experiments/v0.4/fits/{row['run_id']}_pre.npz",row["preprocessor_sha256"])
        registry=read(R/f"experiments/v0.4/registry/{row['run_id']}.json")
        check(registry["posterior_sha256"]==row["sha256"] and registry["diagnostics"]==row["saved_diagnostics"],"frozen_sampling_evidence")
        diag=row["saved_diagnostics"]
        check(all(math.isfinite(diag[k]) for k in ("rhat_max","bulk_ess_min","tail_ess_min","auxiliary_rhat_max","auxiliary_bulk_min","auxiliary_tail_min","maxdepth_fraction")),"finite_saved_MCMC")
        check(diag["rhat_max"]<1.01 and diag["auxiliary_rhat_max"]<1.01 and min(diag[k] for k in ("bulk_ess_min","tail_ess_min","auxiliary_bulk_min","auxiliary_tail_min"))>=400
            and diag["divergences"]==0 and all(math.isfinite(v) and v>.3 for v in diag["bfmi"]) and diag["maxdepth_fraction"]<=.01,"unchanged_saved_MCMC_gate")
        posterior_hashes.append({"run_id":row["run_id"],"path":row["path"],"sha256":row["sha256"]})
    cqr=model["CQR"]
    for key in ("selected_fitted_object","preprocessor"):
        file_check(R/cqr[key]["path"],cqr[key]["sha256"])
    file_check(R/"results/pilot/comparator_calibration.json",cqr["calibration_record_sha256"])
    calibration=read(R/"results/pilot/comparator_calibration.json")
    check(all(calibration[k]==v for k,v in cqr["calibration"].items()),"frozen_calibration_values")
    check(calibration["n_calibration"]==25 and calibration["rank"]==24 and calibration["nonshrinking_correction"]==19.987558518873357,"unchanged_CQR_policy")
    file_check(R/"scripts/stage_B/run_stage_B.py",candidate["canonical_prediction_driver_sha256"])
    file_check(R/"scripts/stage_B/verify_sealed_stage_B.py",candidate["independent_arithmetic_verifier_sha256"])

    ledger=read(B/"engine_ledger_final.json")
    check(len(ledger)==100 and [r["engine"] for r in ledger]==list(range(1,101)),"complete_100_ID_ledger")
    check(all(r["dataset"]=="FD001_test" and r["sensor_input"]==r["CQR"]==r["Bayesian"]=="PASS" and r["failure"] is None for r in ledger),"complete_endpoint_status")
    table_records=[]
    for method in ("Bayesian","CQR"):
        path=T/f"{method}_predictions.csv"
        with path.open(newline="",encoding="utf8") as f:
            reader=csv.DictReader(f);check(reader.fieldnames==["engine","cutoff","lower","median","upper"],"table_schema")
            rows=list(reader)
        check(len(rows)==100 and [int(r["engine"]) for r in rows]==list(range(1,101)),"prediction_table_complete")
        for row in rows:
            i=int(row["engine"]);original=read(B/f"{method}/engine_{i:03d}.json")
            check(int(row["cutoff"])==original["cutoff"]==ledger[i-1]["cutoff"],"cutoff_alignment",engine=i,method=method)
            check(all(math.isfinite(float(row[k])) and float(row[k]).hex()==float(original[k]).hex() for k in ("lower","median","upper")),"unchanged_float64_predictions",engine=i,method=method)
            check(0<=float(row["lower"])<=float(row["upper"]),"stored_interval_order",engine=i,method=method)
            if method=="Bayesian":check(float(row["lower"])>0 and float(row["lower"])<=float(row["median"])<=float(row["upper"]),"stored_Bayesian_quantile_order")
        table_records.append({"name":path.name,"rows":100,"sha256":sha(path),"exact_saved_float64_match":True})
    with (T/"engine_ledger.csv").open(newline="",encoding="utf8") as f:table_ledger=list(csv.DictReader(f))
    check(len(table_ledger)==100 and [int(r["engine"]) for r in table_ledger]==list(range(1,101)),"ledger_table_complete")
    for original,row in zip(ledger,table_ledger):
        check(int(row["engine"])==original["engine"] and int(row["cutoff"])==original["cutoff"]
            and all(row[k]==original[k] for k in ("dataset","sensor_input","CQR","Bayesian")) and row["failure"]=="","ledger_table_exact_match")
    table_records.append({"name":"engine_ledger.csv","rows":100,"sha256":sha(T/"engine_ledger.csv"),"exact_saved_ledger_match":True})

    # Validate unchanged stored diagnostics. No root/helper/prediction calls.
    pooled=[];independent={};exceedances=[]
    for i in range(1,101):
        for fit in ("pooled","v04_main_r1","v04_main_r2","v04_main_r3"):
            independent[i,fit]=[]
            for p in (.05,.5,.95):
                record=read(B/f"precision/engine_{i:03d}_{fit}_p{int(p*100):02d}.json")
                check(record["engine"]==i and record["probability"]==p and record["draws_per_chain"]==8000 and record["chain_count"]==(12 if fit=="pooled" else 4)
                    and record["tail_probability"]==.05/(100*3*2),"recorded_quantile_family")
                check(all(record["finite_checks"].values()) and math.isfinite(record["mixture_cdf_residual"]) and abs(record["mixture_cdf_residual"])<=1e-10
                    and math.isfinite(record["weighted_mixture_density_log_rul"]) and record["weighted_mixture_density_log_rul"]>0,"stored_root_validity")
                check([b["batch_size"] for b in record["batch_size_results"]]==[250,500],"stored_batch_policy")
                for b in record["batch_size_results"]:
                    check(all(b[k] is not None and math.isfinite(b[k]) for k in ("quantile_rul_mcse","approximate_upper_quantile_rul_mcse","influence_ess")),"stored_MCSE_finite")
                    if fit=="pooled":
                        check(record["weight_ess"]>=1000 and b["influence_ess"]>=400 and b["approximate_upper_quantile_rul_mcse"]<=.5,"unchanged_pooled_gate")
                    elif b["approximate_upper_quantile_rul_mcse"]>.5:
                        exceedances.append({"engine":i,"fit":fit,"p":p,"batch":b["batch_size"],"upper":b["approximate_upper_quantile_rul_mcse"]})
                if fit=="pooled":
                    key={.05:"lower",.5:"median",.95:"upper"}[p]
                    check(float(read(B/f"Bayesian/engine_{i:03d}.json")[key]).hex()==float(record["quantile_rul"]).hex(),"stored_quantile_prediction_identity")
                    pooled.append(record)
                independent[i,fit].append(record)
    comparisons=[]
    for i in range(1,101):
        for a,b in itertools.combinations(("v04_main_r1","v04_main_r2","v04_main_r3"),2):
            for ra,rb in zip(independent[i,a],independent[i,b]):
                p=ra["probability"];rec=read(B/f"replication/engine_{i:03d}_{a}_{b}_p{int(p*100):02d}.json")
                ca=max(r["quantile_rul_mcse"] for r in ra["batch_size_results"]);cb=max(r["quantile_rul_mcse"] for r in rb["batch_size_results"])
                den=math.sqrt(ca*ca+cb*cb);diff=abs(ra["quantile_rul"]-rb["quantile_rul"])
                check(rec["engine"]==i and rec["probability"]==p and rec["fits"]==[a,b] and rec["MCSE_a"]==ca and rec["MCSE_b"]==cb
                    and rec["denominator"]==den and rec["absolute_difference_cycles"]==diff and rec["z"]==4.030934372846465 and rec["limit"]==rec["z"]*den,
                    "unchanged_replication_arithmetic")
                check(rec["PASS"] and math.isfinite(den) and den>0 and diff<=rec["limit"],"unchanged_compatibility_gate")
                comparisons.append(rec)
    check(len(pooled)==300 and len(comparisons)==900 and len(exceedances)==13,"unchanged_accepted_numerical_summary")
    disclosure=read(R/"docs/stage_B/INDEPENDENT_FIT_DIAGNOSTIC_DISCLOSURE.json")
    check(disclosure["batches_above_half_cycle"]==len(exceedances)==13 and disclosure["distinct_individual_quantiles_above_half_cycle"]==len({(r["engine"],r["fit"],r["p"]) for r in exceedances})==7,"retained_individual_fit_disclosure")
    max_upper=max(b["approximate_upper_quantile_rul_mcse"] for r in pooled for b in r["batch_size_results"])
    outcome=read(B/"outcome.json");public=read(R/"docs/stage_B/STAGE_B_RESULT.json")
    check(public["numerical_summary"]["upper_MCSE_max"]==max_upper and max_upper<=.5,"reported_upper_MCSE_consistency")
    audit=read(B/"input_overlap_audit.json")
    check(audit["status"]=="PASS" and audit["engines"]==100 and audit["fields"]==26 and not audit["exact_pairs"] and not audit["near_pairs"],"unchanged_input_overlap_evidence")
    check(read(B/"failure_ledger.json")==[] and outcome["failure"] is None and outcome["status"]=="READY FOR OWNER STAGE C REVIEW","unchanged_failure_history")
    events=sorted((B/"events").glob("*.json"));previous=None
    for index,path in enumerate(events,1):
        event=read(path)
        check(event["event"]==index and event["previous_sha256"]==previous,"intact_B_event_chain")
        check("LABEL" not in event["kind"] and "SCORING" not in event["kind"],"no_label_or_score_event")
        previous=sha(path)
    check(previous==public["journal_head_sha256"]==outcome["journal_head_sha256"] and len(events)==507,"unchanged_event_head")
    for obj in (candidate,public,outcome,read(V/"direct_SOL_verification.json")):
        check(obj["labels_accessed"] is False,"documented_label_boundary")
    check(not (R/"data/raw/RUL_FD001.txt").exists(),"labels_remain_unextracted")
    check(outcome["scoring"] is False and outcome["new_draws"]==0 and outcome["retraining"] is False and outcome["fallback"] is False
        and candidate["primary_comparison_scored"] is False and public["Stage_D_authorized"] is False,"no_recorded_science_or_scoring_change")
    check(git("status","--porcelain")=="","no_verification_side_effects")

    details={"at_utc":now(),"status":"PASS","existing_file_checks":checks,"table_checks":table_records,
        "retained_individual_exceedances":exceedances,"source_map_sha256":source_fp,
        "posterior_hashes":posterior_hashes,"label_boundary_limit":"Procedural evidence only, not independent OS forensic proof"}
    save(O/"INTEGRITY_DETAILS.json",details)
    summary={"status":"STAGE_C_ACCEPTED","verified_at_utc":now(),"protocol_version":VERSION,"campaign":"B001","Stage_C_record":"C001",
        "verification_code_commit":code_commit,"verification_code_sha256":sha(Path(__file__)),"owner_directive_sha256":sha(D/"OWNER_STAGE_C_DECISION.md"),
        "candidate_bundle_sha256":BUNDLE,"manifest_sha256":EXPECTED,"base_payload_files_rehashed":3016,
        "verification_manifest_members_rehashed":3,"review_tables_rehashed":3,"G3_sealed_files_unchanged":len(g3["files"]),
        "Stage_B_public_files_preserved":len(public_paths),"scientific_source_map_sha256":source_fp,"environment_fingerprint":env_fp,
        "posterior_identities":posterior_hashes,"calibration_sha256":cqr["calibration_record_sha256"],
        "CQR_object_sha256":cqr["selected_fitted_object"]["sha256"],"preprocessor_sha256":cqr["preprocessor"]["sha256"],
        "prediction_tables":table_records,"all_100_engine_ledger_rows_verified":True,"prediction_values_unchanged":True,
        "pooled_quantiles_PASS":300,"compatibility_comparisons_PASS":900,"pooled_upper_MCSE_max":max_upper,
        "mandatory_failure_count":0,"individual_fit_batch_exceedances":13,"individual_fit_affected_quantiles":7,
        "failure_ledger_unchanged_and_empty":True,"B_journal_events_verified":len(events),
        "label_boundary":"Intact pre-label sealing, prior access records, absent extracted label file, unchanged sealed metadata; procedural evidence only",
        "official_labels_opened_this_verification":False,"outcome_scoring_performed":False,
        "new_predictions":0,"new_roots":0,"posterior_draws":0,"fitting_or_recalibration":False,
        "stage_D_authorized":False,"scientific_result_validated":False,"wall_seconds":time.monotonic()-began,
        "protected_details_sha256":sha(O/"INTEGRITY_DETAILS.json")}
    save(O/"INTEGRITY_SUMMARY.json",summary)
    members=[{"path":str(p.relative_to(R)).replace("\\","/"),"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(O.glob("*.json"))]
    save(O/"STAGE_C_VERIFICATION_MANIFEST.json",{"files":members,"candidate_bundle_sha256":BUNDLE,"excludes":"self"})
    summary["Stage_C_verification_manifest_sha256"]=sha(O/"STAGE_C_VERIFICATION_MANIFEST.json")
    summary["Stage_C_verification_manifest_path"]=".protected/stage_C/C001/STAGE_C_VERIFICATION_MANIFEST.json"
    save(D/"FINAL_INTEGRITY_VERIFICATION.json",summary)
    print(json.dumps({k:summary[k] for k in ("status","base_payload_files_rehashed","candidate_bundle_sha256","prediction_values_unchanged","individual_fit_batch_exceedances","stage_D_authorized","wall_seconds")}),flush=True)
except Exception as exc:
    failure={"status":"STAGE_C_BLOCKED","at_utc":now(),"failure_type":type(exc).__name__,"failure":str(exc),
        "candidate_bundle_sha256":BUNDLE,"candidate_modified":False,"labels_opened":False,"new_predictions":0,"stage_D_authorized":False}
    save(D/"FINAL_INTEGRITY_FAILURE.json",failure)
    print(json.dumps(failure),flush=True)
    raise
