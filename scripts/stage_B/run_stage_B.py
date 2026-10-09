"""Stage B custody/orchestration only; calls pinned scientific primitives.
Never reads official labels; no fitting, scoring, sampling or remediation.
All output files are exclusive-create; execution is single attempt.
"""
from pathlib import Path
import ast, datetime, hashlib, importlib.metadata, inspect, io, itertools
import json, math, os, platform, statistics, subprocess, sys, time, traceback, zipfile
R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "src"))
P = R / ".protected/stage_B/B001"
D = R / "docs/stage_B"
PLAN = R / "configs/stage_B_execution_plan.json"
VERSION = "RP-001-G3-v0.5-AM1"
RECEIPT_COMMIT = "da4da0bd51b86239a36effcb92a1106490835c6b"
LOCK_COMMIT = "fc7083d23d3cff5e4ee9a9f5d0af9036ec32e26d"
PHYSICAL = ("beta", "gamma", "Gamma", "tau", "r_g", "sigma_z", "sigma_r", "rho")
ALL_VARS = PHYSICAL + ("eta_rho", "gcor_u")

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest_bytes(b):
    return hashlib.sha256(b).hexdigest()
def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""):
            h.update(b)
    return h.hexdigest()
def read(path):
    return json.loads(Path(path).read_text(encoding="utf8"))
def save(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        f.write((json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode())
def git(*args):
    return subprocess.check_output(["git", "-C", str(R), *args], text=True).strip()
def file_record(path):
    return {"path":str(path.relative_to(R)).replace("\\","/"), "bytes":path.stat().st_size, "sha256":sha(path)}

class Halt(Exception):
    pass

class Journal:
    def __init__(self):
        self.folder = P / "events"
        self.folder.mkdir(parents=True, exist_ok=True)
        files = sorted(self.folder.glob("*.json"))
        self.index = len(files)
        self.previous = sha(files[-1]) if files else None
    def add(self, kind, **values):
        self.index += 1
        obj = {"event":self.index, "at_utc":now(), "kind":kind, "previous_sha256":self.previous, **values}
        path = self.folder / f"{self.index:06d}.json"
        save(path, obj)
        self.previous = sha(path)
        return self.previous

def guard(condition, gate, **details):
    if not bool(condition):
        raise Halt(json.dumps({"gate":gate, **details}, allow_nan=False))

def environment():
    packages = {d.metadata["Name"]:d.version for d in importlib.metadata.distributions()}
    result = {"python":platform.python_version(), "implementation":platform.python_implementation(),
        "platform":platform.platform(), "packages":dict(sorted(packages.items(), key=lambda x:x[0].lower())),
        "float_dtype":"float64", "sampler":"nutpie NUTS", "blas_threads":1}
    return result, digest_bytes(json.dumps(result, sort_keys=True).encode())

def fingerprints():
    """Pre-sensor lock checks; no ZipFile construction or protected member reads."""
    import numpy as np, h5py, joblib, scipy, scipy.optimize
    receipt_path = R / "docs/protocol_lock/LOCK_RECEIPT.json"
    guard(sha(receipt_path) == "9803eba8f616e6fd8bd95780ba829863cd629643d7e13590d8a4f5535509bade", "receipt_hash")
    receipt = read(receipt_path)
    guard(receipt["version"] == VERSION and receipt["lock_commit"] == LOCK_COMMIT, "receipt_identity")
    sealed = read(R / receipt["payload_manifest_path"])
    guard(sha(R / receipt["payload_manifest_path"]) == receipt["payload_manifest_sha256"], "payload_manifest_identity")
    checks = []
    for row in sealed["files"]:
        p = R / row["path"]
        guard(p.is_file() and sha(p) == row["sha256"] and p.stat().st_size == row["bytes"], "sealed_lock_payload", path=row["path"])
        checks.append(row)
    code = read(R / "docs/protocol_lock/FROZEN_CODE_AND_ENVIRONMENT_MANIFEST.json")
    for row in code["scientific_sources"] + code["scientific_configurations"]:
        guard(sha(R / row["path"]) == row["sha256"], "scientific_hash", path=row["path"])
    source_map = {row["path"]:row["sha256"] for row in code["scientific_sources"]}
    guard(digest_bytes(json.dumps(source_map,sort_keys=True,separators=(",",":")).encode()) == receipt["scientific_source_map_sha256"], "scientific_map")
    env, env_hash = environment()
    guard(env == code["live_environment"] and env_hash == receipt["environment_fingerprint"], "environment")
    for field in ("dependency_lock", "saved_environment_record"):
        guard(sha(R / code[field]["path"]) == code[field]["sha256"], field)
    quantile_code = (R / "src/rp001/v04_precision.py").read_text(encoding="utf8")
    quantile_ast = next(n for n in ast.parse(quantile_code).body if isinstance(n,ast.FunctionDef) and n.name == "_weighted_quantile")
    guard(digest_bytes(ast.get_source_segment(quantile_code,quantile_ast).encode()) == code["canonical_quantile_source"]["function_source_sha256"], "canonical_quantile_AST")
    guard(str(inspect.signature(scipy.optimize.brentq)) == code["canonical_quantile_source"]["brent_signature"], "Brent_defaults")
    model = read(R / "docs/protocol_lock/FROZEN_MODEL_AND_CONFIGURATION_MANIFEST.json")
    data = read(R / "docs/protocol_lock/FROZEN_DATA_AND_SPLIT_MANIFEST.json")
    pre = dict(np.load(R / model["CQR"]["preprocessor"]["path"],allow_pickle=False))
    guard(sha(R / model["CQR"]["preprocessor"]["path"]) == model["CQR"]["preprocessor"]["sha256"], "preprocessor")
    posterior_records = []
    for row in model["principal_posteriors"]:
        guard(sha(R / row["path"]) == row["sha256"], "posterior_hash", run=row["run_id"])
        registry = read(R / f"experiments/v0.4/registry/{row['run_id']}.json")
        diag = row["saved_diagnostics"]
        guard(registry["posterior_sha256"] == row["sha256"] and registry["diagnostics"] == diag, "saved_diagnostics_identity", run=row["run_id"])
        vals = [diag[k] for k in ("rhat_max","bulk_ess_min","tail_ess_min","auxiliary_rhat_max","auxiliary_bulk_min","auxiliary_tail_min","maxdepth_fraction")] + diag["bfmi"]
        guard(all(math.isfinite(v) for v in vals) and diag["rhat_max"] < 1.01 and diag["auxiliary_rhat_max"] < 1.01
            and min(diag[k] for k in ("bulk_ess_min","tail_ess_min","auxiliary_bulk_min","auxiliary_tail_min")) >= 400
            and diag["divergences"] == 0 and min(diag["bfmi"]) > .3 and diag["maxdepth_fraction"] <= .01, "MCMC", run=row["run_id"])
        with h5py.File(R / row["path"],"r") as f:
            for name in ALL_VARS:
                arr = f["posterior"][name][...]
                guard(arr.shape[:2] == (4,8000) and arr.dtype == np.float64 and np.isfinite(arr).all(), "retained_posterior", run=row["run_id"], variable=name)
            guard(int(f["sample_stats"]["diverging"][...].sum()) == 0, "saved_divergences", run=row["run_id"])
            guard(float(np.mean(f["sample_stats"]["depth"][...] >= 12)) <= .01, "saved_depth", run=row["run_id"])
        other_path = R / f"experiments/v0.4/fits/{row['run_id']}_pre.npz"
        guard(sha(other_path) == row["preprocessor_sha256"], "per_fit_preprocessor", run=row["run_id"])
        other = dict(np.load(other_path,allow_pickle=False))
        guard(pre.keys() == other.keys() and all(np.array_equal(pre[k],other[k]) for k in pre), "per_fit_maps", run=row["run_id"])
        posterior_records.append({"run_id":row["run_id"],"sha256":row["sha256"],"saved_diagnostics":diag,"retained_shape":[4,8000],"metadata_PASS":True})
    cqr_path = R / model["CQR"]["selected_fitted_object"]["path"]
    guard(sha(cqr_path) == model["CQR"]["selected_fitted_object"]["sha256"], "CQR_object_hash")
    obj = joblib.load(cqr_path)
    guard(all(np.array_equal(pre[k],obj["preprocessor"][k]) for k in pre), "CQR_map")
    guard(obj["selected"].status == obj["median"].status == "completed"
        and obj["selected"].train_size == obj["median"].train_size == 56
        and obj["selected"].spec.candidate_id == obj["median"].spec.candidate_id == model["CQR"]["selected_id"], "CQR_selected")
    for label, fitted in [("lower",obj["selected"].lower_model),("upper",obj["selected"].upper_model),("median",obj["median"].model)]:
        actual = fitted.get_params()
        guard(all(actual[k] == v for k,v in model["CQR"]["fitted_parameters"][label].items()), "CQR_parameters", model=label)
    guard(sha(R / "results/pilot/comparator_calibration.json") == model["CQR"]["calibration_record_sha256"], "calibration_hash")
    calibration = read(R / "results/pilot/comparator_calibration.json")
    guard(all(calibration[k] == v for k,v in model["CQR"]["calibration"].items()), "calibration_values")
    for row in data["opaque_archive_identities"]:
        guard(sha(R / row["path"]) == row["sha256"] and (R / row["path"]).stat().st_size == row["size_bytes"], "opaque_archive", path=row["path"])
    for path, expected in receipt["dataset_split_plan_sha256"].items():
        guard(sha(R / path) == expected, "input_identity", path=path)
    guard(sha(R / data["data_provenance_record"]["path"]) == data["data_provenance_record"]["sha256"], "data_provenance")
    for path in [R / "data/raw/schema_contract.json", R / "experiments/development_data_audit.json"]:
        guard(git("show",RECEIPT_COMMIT+":"+str(path.relative_to(R)).replace("\\","/")) == path.read_text().strip(), "existing_audit_schema")
    return {"status":"PASS","verified_at_utc":now(),"sealed_lock_files":len(checks),
        "scientific_source_map_sha256":receipt["scientific_source_map_sha256"],
        "environment_fingerprint":env_hash,"live_environment":env,
        "principal_posteriors":posterior_records,"archive_member_content_reads":0,
        "schema_sha256":sha(R/"data/raw/schema_contract.json"),
        "baseline_overlap_audit_sha256":sha(R/"experiments/development_data_audit.json"),
        "receipt_sha256":sha(receipt_path),"plan_sha256":sha(PLAN),
        "driver_sha256":sha(Path(__file__))}

def preflight():
    guard(not P.exists(), "campaign_not_previously_started")
    guard(git("status","--porcelain") == "", "clean_execution_checkout")
    j = Journal()
    j.add("CAMPAIGN_REGISTERED", campaign="B001", stage_B_only=True, authority_sha256=sha(D/"OWNER_AUTHORIZATION_STAGE_B.md"),
        plan_sha256=sha(PLAN), driver_sha256=sha(Path(__file__)), git_commit=git("rev-parse","HEAD"))
    try:
        result = fingerprints()
    except Exception as exc:
        failure = json.loads(str(exc)) if isinstance(exc,Halt) else {"gate":"preflight_execution","type":type(exc).__name__,"message":str(exc)}
        seal(j,"STAGE B BLOCKED",failure,None,None,time.monotonic())
        return
    result.update({"execution_code_commit":git("rev-parse","HEAD"),"working_tree":"CLEAN",
        "owner_authorization_sha256":sha(D/"OWNER_AUTHORIZATION_STAGE_B.md"),
        "scientific_implementation_changed":False,"sensor_accessed":False,"labels_accessed":False,
        "initial_journal_head_sha256":j.previous})
    save(P/"preflight.json",result)
    j.add("PREFLIGHT_PASS", artifact_sha256=sha(P/"preflight.json"))
    save(D/"PREFLIGHT_VERIFICATION.json",result)
    print(json.dumps({"status":"PREFLIGHT_PASS","environment":result["environment_fingerprint"],"sealed_files":result["sealed_lock_files"],"sensor_accessed":False}),flush=True)

def input_audit(j):
    import numpy as np
    target = R / "data/raw/test_FD001.txt"
    guard(not target.exists(), "sensor_not_previously_extracted")
    # Open only the explicitly authorized member; no namelist, extractall or testzip.
    with zipfile.ZipFile(R / "data/raw/CMAPSSData.zip","r") as zf:
        info = zf.getinfo("test_FD001.txt")
        j.add("SENSOR_ACCESS_BEGIN", member="test_FD001.txt", archive_sha256=sha(R/"data/raw/CMAPSSData.zip"))
        with zf.open(info,"r") as member:
            sensor_bytes = member.read()
    guard(len(sensor_bytes) == info.file_size, "sensor_member_size")
    with target.open("xb") as f:
        f.write(sensor_bytes)
    j.add("SENSOR_EXTRACTED", sha256=sha(target), bytes=len(sensor_bytes), CRC32=info.CRC, members_opened=["test_FD001.txt"])
    lines = sensor_bytes.decode("ascii").splitlines()
    guard(all(len(line.split()) == 26 for line in lines), "schema_26_fields")
    raw = np.loadtxt(io.StringIO(sensor_bytes.decode("ascii")),dtype=np.float64)
    guard(raw.ndim == 2 and raw.shape[1] == 26 and np.isfinite(raw).all(), "sensor_finite_schema")
    guard(np.all(raw[:,:2] == np.floor(raw[:,:2])) and np.all(raw[:,:2] > 0), "positive_integer_ID_cycle")
    ids = np.unique(raw[:,0]).astype(int)
    guard(np.array_equal(ids,np.arange(1,101)), "expected_100_ID_namespace", count=len(ids))
    guard(len(np.unique(raw[:,:2],axis=0)) == len(raw), "unique_engine_cycle_keys")
    engines = {int(i):raw[raw[:,0] == i] for i in ids}
    for i, rows in engines.items():
        guard(np.array_equal(rows[:,1],np.arange(1,len(rows)+1)), "contiguous_ordered_cycles", engine=i)
    schema = read(R/"data/raw/schema_contract.json")
    save(P/"engine_ledger_initial.json",[{"dataset":"FD001_test","engine":i,"cutoff":len(engines[i]),
        "sensor_input":"PASS","CQR":"NOT_STARTED","Bayesian":"NOT_STARTED","failure":None} for i in engines])
    training = np.loadtxt(R/"data/raw/train_FD001.txt",dtype=np.float64)
    train = {i:training[training[:,0] == i] for i in range(1,101)}
    # Preserve the existing normalization population: eligible canonical training
    # prefixes only, raw operating settings + 21 sensors, population SD and 1 fallback.
    split = read(R/"configs/proposed_split_manifest.json")
    allowed = np.vstack([train[r["engine"]][:r["proposed_cutoff"],2:] for r in split if r["eligible_alive"]])
    scales = []
    for column in allowed.T:
        values = column.tolist()
        mean = statistics.fmean(values)
        sd = math.sqrt(math.fsum((v-mean)**2 for v in values)/len(values))
        scales.append(sd if sd > 1e-12 else 1.0)
    scales = np.asarray(scales)
    distances, exact, near = [], [], []
    for i, a in engines.items():
        for k, b in train.items():
            common = min(len(a),len(b))
            exact_flag = np.array_equal(a[:common,2:],b[:common,2:])
            if exact_flag:
                exact.append({"test_engine":i,"train_engine":k,"common_cycles":common})
            if common < 30:
                continue
            d = (a[:common,2:]-b[:common,2:])/scales
            channel = np.sqrt(np.mean(d*d,axis=0))
            mean = math.sqrt(math.fsum(float(v*v) for v in channel)/len(channel))
            maximum = float(channel.max())
            row = {"test_engine":i,"train_engine":k,"common_cycles":common,"mean_feature_nrmse":mean,"max_channel_nrmse":maximum}
            distances.append(row)
            if not exact_flag and mean <= .02 and maximum <= .10:
                near.append(row)
    distances.sort(key=lambda row:(row["mean_feature_nrmse"],row["max_channel_nrmse"],-row["common_cycles"]))
    audit = {"status":"FAIL" if exact or near else "PASS","at_utc":now(),"sensor_sha256":sha(target),
        "bytes":len(sensor_bytes),"rows":len(raw),"engines":len(engines),"fields":26,
        "schema_contract":schema,"schema_sha256":sha(R/"data/raw/schema_contract.json"),
        "namespaces":["FD001_train","FD001_test"],"ID_is_never_predictor":True,
        "finite_values":True,"positive_integer_ID_cycle":True,"contiguous_ordered_cycles":True,"unique_engine_cycle_keys":True,
        "cutoffs":{str(i):len(rows) for i,rows in engines.items()},"features_labels_or_future_rows":False,
        "exact_prefix_checks":10000,"near_duplicate_checks":len(distances),
        "normalization":"Frozen rule: population SD over all 81 canonical eligible training prefixes, 24 settings/sensor channels, SD<=1e-12 scale1; test excluded",
        "scales":scales.tolist(),"mean_threshold":.02,"max_channel_threshold":.10,"min_common_cycles":30,
        "comparison":"All 100 training trajectories vs all 100 test histories, cycle-aligned shared initial prefix; exact screen at any positive common length",
        "exact_pairs":exact,"near_pairs":near,"closest_pairs":distances[:5],
        "limitation":"Heuristic only; cannot certify independent source identity or rule out semantic contamination"}
    save(P/"input_overlap_audit.json",audit)
    j.add("INPUT_AUDIT", status=audit["status"],artifact_sha256=sha(P/"input_overlap_audit.json"))
    guard(not exact and not near,"train_test_overlap",exact_count=len(exact),near_count=len(near))
    return engines, audit

def dataset(i, rows, pre):
    import numpy as np
    from rp001.data import LandmarkData, transform_prefix
    c = len(rows)
    z = transform_prefix(rows,c,pre)
    w = len(z)
    return LandmarkData(np.array([[1.,np.log(c/100.)]],dtype=np.float64),z[None,:],None,np.array([i]),
        np.column_stack((np.ones(w),np.arange(-(w-1),1,dtype=np.float64)/30.)),"FD001_test sensor-only endpoint")

def check_quantile(result, pooled, engine, probability, fit):
    # All pooled official precision guards; independent fits supply compatibility
    # MCSEs and must have finite well-defined canonical roots/MCSEs.
    checks = [
        all(result["finite_checks"].values()), math.isfinite(result["weight_ess"]),
        abs(result["mixture_cdf_residual"]) <= 1e-10,
        result["importance_weight_mean_scaled"] > 0,
        result["weighted_mixture_density_log_rul"] > 0]
    for b in result["batch_size_results"]:
        checks.append(b["approximate_upper_quantile_rul_mcse"] is not None and math.isfinite(b["approximate_upper_quantile_rul_mcse"]))
        checks.append(b["influence_ess"] is not None and math.isfinite(b["influence_ess"]))
        if pooled:
            checks.extend([b["approximate_upper_quantile_rul_mcse"] is not None and b["approximate_upper_quantile_rul_mcse"] <= .5,
                b["influence_ess"] is not None and b["influence_ess"] >= 400])
    if pooled:
        checks.append(result["weight_ess"] >= 1000)
    guard(all(checks),"quantile_precision" if pooled else "independent_fit_numerics",
        engine=engine,probability=probability,fit=fit,weight_ess=result["weight_ess"],
        batches=[{k:b[k] for k in ("batch_size","quantile_rul_mcse","approximate_upper_quantile_rul_mcse","influence_ess")} for b in result["batch_size_results"]],
        CDF_residual=result["mixture_cdf_residual"])

def predict(engines, j, ledger):
    import numpy as np, arviz as az, joblib
    from scipy.stats import norm
    from rp001.data import features
    from rp001.comparators import predict_endpoints, predict_median_candidate
    from rp001.metrics import apply_correction
    from rp001.v04_predict import arrays, sensor_terms
    from rp001.v04_precision import estimate_mixture_quantile_mcse
    from threadpoolctl import threadpool_info
    model = read(R/"docs/protocol_lock/FROZEN_MODEL_AND_CONFIGURATION_MANIFEST.json")
    pre = dict(np.load(R/"results/pilot/refit_preprocessor.npz",allow_pickle=False))
    obj = joblib.load(R/"results/pilot/selected_comparator.joblib")
    correction = model["CQR"]["calibration"]["nonshrinking_correction"]
    posterior = []
    for row in model["principal_posteriors"]:
        idata = az.from_netcdf(R/row["path"])
        guard(idata.posterior.sizes["chain"] == 4 and idata.posterior.sizes["draw"] == 8000,"posterior_dimensions")
        guard(all(idata.posterior[n].dims[:2] == ("chain","draw") for n in PHYSICAL),"posterior_dimension_order")
        posterior.append(arrays(idata))
        idata.close()
    threads = threadpool_info()
    guard(all(t["num_threads"] == 1 for t in threads), "actual_BLAS_threads")
    save(P/"compute_environment.json",{"at_utc":now(),"threadpool_info":threads,"local_CPU":platform.processor(),"logical_cores":os.cpu_count(),
        "Colab":False,"spending":0,"live_environment":environment()[0],"new_draws":0})
    zlimit = float(norm.ppf(1-.05/(2*9*100)))
    tail = .05/(100*3*2)
    pooled_results, rep_results, cqr_rows = [], [], []
    for i, rows in engines.items():
        data = dataset(i,rows,pre)
        xs, xf = features(data), features(data,full=True)
        guard(np.isfinite(xs).all() and np.isfinite(xf).all() and data.y is None, "label_free_features",engine=i)
        lower, upper = predict_endpoints(obj["selected"],xs,xf)
        median = predict_median_candidate(obj["median"],xs,xf)
        lower, upper = apply_correction(lower,upper,correction)
        cqr = {"engine":i,"cutoff":len(rows),"lower":float(lower[0]),"median":float(median[0]),"upper":float(upper[0]),
            "negative_median_flag":bool(median[0]<0),"selected_id":obj["selected"].spec.candidate_id,"correction":correction}
        save(P/f"CQR/engine_{i:03d}.json",cqr)
        guard(np.isfinite([cqr["lower"],cqr["median"],cqr["upper"]]).all() and 0 <= cqr["lower"] <= cqr["upper"],"CQR_endpoints",engine=i)
        ledger[i-1]["CQR"] = "PASS"
        cqr_rows.append(cqr)
        j.add("CQR_PASS",engine=i,artifact_sha256=sha(P/f"CQR/engine_{i:03d}.json"))
        triples = [sensor_terms(p,data) for p in posterior]
        means = np.concatenate([t[1][:,0].reshape(4,8000) for t in triples],axis=0)
        variances = np.concatenate([t[2][:,0].reshape(4,8000) for t in triples],axis=0)
        logweights = np.concatenate([t[0][:,0].reshape(4,8000) for t in triples],axis=0)
        terms_path = P/f"conditional_terms/engine_{i:03d}.npz"
        terms_path.parent.mkdir(parents=True,exist_ok=True)
        with terms_path.open("xb") as f:
            np.savez_compressed(f,means=means,variances=variances,log_weights=logweights,engine=i,cutoff=len(rows))
        engine_results = []
        for probability in (.05,.50,.95):
            result = estimate_mixture_quantile_mcse(means,variances,logweights,probability,tail_probability=tail,batch_sizes=(250,500),error="normal")
            result.update({"engine":i,"fit":"pooled_12_chains","cutoff":len(rows)})
            path = P/f"precision/engine_{i:03d}_pooled_p{int(probability*100):02d}.json"
            save(path,result)
            pooled_results.append(result)
            j.add("QUANTILE_RESULT",engine=i,probability=probability,artifact_sha256=sha(path))
            check_quantile(result,True,i,probability,"pooled")
            engine_results.append(result)
        guard(engine_results[0]["quantile_rul"] <= engine_results[1]["quantile_rul"] <= engine_results[2]["quantile_rul"],"ordered_Bayesian_endpoints",engine=i)
        bayes = {"engine":i,"cutoff":len(rows),**{key:r["quantile_rul"] for key,r in zip(("lower","median","upper"),engine_results)}}
        save(P/f"Bayesian/engine_{i:03d}.json",bayes)
        individual = {}
        for run_index in range(3):
            run = f"v04_main_r{run_index+1}"
            individual[run] = []
            sl = slice(run_index*4,(run_index+1)*4)
            for probability in (.05,.50,.95):
                result = estimate_mixture_quantile_mcse(means[sl],variances[sl],logweights[sl],probability,tail_probability=tail,batch_sizes=(250,500),error="normal")
                result.update({"engine":i,"fit":run,"cutoff":len(rows)})
                path = P/f"precision/engine_{i:03d}_{run}_p{int(probability*100):02d}.json"
                save(path,result)
                check_quantile(result,False,i,probability,run)
                individual[run].append(result)
        for a,b in itertools.combinations(individual,2):
            for ra,rb in zip(individual[a],individual[b]):
                mcsea = max(v["quantile_rul_mcse"] for v in ra["batch_size_results"])
                mcseb = max(v["quantile_rul_mcse"] for v in rb["batch_size_results"])
                denominator = math.sqrt(mcsea**2+mcseb**2)
                difference = abs(ra["quantile_rul"]-rb["quantile_rul"])
                passed = denominator > 0 and math.isfinite(denominator) and math.isfinite(difference) and difference <= zlimit*denominator
                rec = {"engine":i,"probability":ra["probability"],"fits":[a,b],"absolute_difference_cycles":difference,
                    "MCSE_a":mcsea,"MCSE_b":mcseb,"denominator":denominator,"z":zlimit,"limit":zlimit*denominator,"PASS":bool(passed)}
                path = P/f"replication/engine_{i:03d}_{a}_{b}_p{int(ra['probability']*100):02d}.json"
                save(path,rec)
                rep_results.append(rec)
                guard(passed,"independent_fit_compatibility",**rec)
        ledger[i-1]["Bayesian"] = "PASS"
        j.add("ENGINE_PASS",engine=i,bayesian_sha256=sha(P/f"Bayesian/engine_{i:03d}.json"))
        save(P/f"ledger_checkpoints/engine_{i:03d}.json",ledger)
        print(json.dumps({"engine":i,"status":"PASS","completed":i,"of":100}),flush=True)
    guard(len(ledger)==100 and all(r["Bayesian"]==r["CQR"]=="PASS" for r in ledger),"complete_100_endpoints")
    guard(len(pooled_results)==300 and len(rep_results)==900,"complete_numerical_coverage")
    return {"pooled_quantiles_PASS":300,"replication_comparisons_PASS":900,
        "upper_MCSE_max":max(b["approximate_upper_quantile_rul_mcse"] for r in pooled_results for b in r["batch_size_results"]),
        "weight_ESS_min":min(r["weight_ess"] for r in pooled_results),
        "influence_ESS_min":min(b["influence_ess"] for r in pooled_results for b in r["batch_size_results"]),
        "CDF_residual_abs_max":max(abs(r["mixture_cdf_residual"]) for r in pooled_results),
        "negative_CQR_median_count":sum(r["negative_median_flag"] for r in cqr_rows),
        "replication_z":zlimit,"quantile_tail":tail}

def seal(j, status, failure, ledger, summary, began):
    import psutil
    j.add("EXECUTION_STOP",status=status,failure=failure,labels_accessed=False,scoring=False)
    if ledger is None and (P/"engine_ledger_initial.json").exists():
        ledger = read(P/"engine_ledger_initial.json")
    if ledger is not None:
        save(P/"engine_ledger_final.json",ledger)
    failures = [] if failure is None else [{"at_utc":now(),"failure":failure,"repair_attempted":False}]
    save(P/"failure_ledger.json",failures)
    outcome = {"version":VERSION,"campaign":"B001","status":status,"completed_at_utc":now(),
        "execution_git_commit":git("rev-parse","HEAD"),"execution_driver_sha256":sha(Path(__file__)),"plan_sha256":sha(PLAN),
        "environment_fingerprint":environment()[1],"wall_seconds":time.monotonic()-began,"CPU_seconds":time.process_time(),
        "peak_working_set_bytes":getattr(psutil.Process().memory_info(),"peak_wset",None),
        "sensor_accessed":(R/"data/raw/test_FD001.txt").exists(),"labels_accessed":False,"scoring":False,
        "new_draws":0,"retraining":False,"fallback":False,"Stage_C_accepted":False,"Stage_D_authorized":False,
        "engine_ID_ledger_rows":len(ledger) if ledger else 0,
        "Bayesian_engine_PASS":sum(r["Bayesian"]=="PASS" for r in ledger) if ledger else 0,
        "CQR_engine_PASS":sum(r["CQR"]=="PASS" for r in ledger) if ledger else 0,
        "failure":failure,"numerical_summary":summary,"journal_head_sha256":j.previous}
    if (P/"input_overlap_audit.json").exists():
        audit = read(P/"input_overlap_audit.json")
        outcome["input_summary"] = {k:audit[k] for k in ("status","sensor_sha256","bytes","rows","engines","fields","exact_prefix_checks","near_duplicate_checks")}
        outcome["input_summary"].update({"exact_overlap_flags":len(audit["exact_pairs"]),"near_duplicate_flags":len(audit["near_pairs"])})
    outcome["partial_pooled_quantile_files"] = len(list((P/"precision").glob("*pooled*.json"))) if (P/"precision").exists() else 0
    outcome["partial_replication_files"] = len(list((P/"replication").glob("*.json"))) if (P/"replication").exists() else 0
    save(P/"outcome.json",outcome)
    files = [file_record(p) for p in sorted(P.rglob("*")) if p.is_file()]
    manifest = {"version":VERSION,"campaign":"B001","status":"CANDIDATE_FREEZE" if status=="READY FOR OWNER STAGE C REVIEW" else "SEALED_FAILED_ATTEMPT",
        "created_at_utc":now(),"files":files,"noncircular_policy":"Manifest excludes itself and subsequent public receipts; raw sensor source bound by input audit",
        "immutable_policy":"Exclusive-create per artifact, hash-chained events, final hashes; local filesystem is not WORM or independently notarized",
        "labels_accessed":False,"owner_stage_C_acceptance":False}
    save(P/"PAYLOAD_MANIFEST.json",manifest)
    public = {**outcome,"protected_payload_manifest_sha256":sha(P/"PAYLOAD_MANIFEST.json"),
        "protected_payload_file_count":len(files),"protected_payload_location":".protected/stage_B/B001",
        "raw_sensor_payload_published":False,"predictions_published":False,
        "data_rights":"Unresolved; raw sensors and restricted payloads kept local"}
    save(D/"STAGE_B_RESULT.json",public)
    print(json.dumps({"status":status,"Bayesian_engine_PASS":outcome["Bayesian_engine_PASS"],"CQR_engine_PASS":outcome["CQR_engine_PASS"],
        "failure":failure,"protected_manifest_sha256":public["protected_payload_manifest_sha256"]}),flush=True)

def execute():
    began = time.monotonic()
    guard((P/"preflight.json").exists() and not (P/"execution_started.json").exists(), "single_attempt")
    guard(git("status","--porcelain")=="","clean_execution_checkout")
    preflight_result = read(P/"preflight.json")
    guard(preflight_result["plan_sha256"]==sha(PLAN) and preflight_result["driver_sha256"]==sha(Path(__file__)),"unchanged_execution_plan")
    j = Journal()
    save(P/"execution_started.json",{"at_utc":now(),"git_commit":git("rev-parse","HEAD"),"working_tree":"CLEAN","attempt":1})
    j.add("EXECUTION_STARTED",git_commit=git("rev-parse","HEAD"),preflight_sha256=sha(P/"preflight.json"))
    ledger, summary = None, None
    try:
        repeated = fingerprints()
        save(P/"execution_preflight.json",repeated)
        engines,audit = input_audit(j)
        ledger = read(P/"engine_ledger_initial.json")
        summary = predict(engines,j,ledger)
        status,failure = "READY FOR OWNER STAGE C REVIEW",None
    except Exception as exc:
        if isinstance(exc,Halt):
            failure = json.loads(str(exc))
        else:
            failure = {"gate":"execution_exception","type":type(exc).__name__,"message":str(exc)}
            save(P/"execution_exception.json",{"failure":failure,"traceback":traceback.format_exc()})
        if ledger is not None and "engine" in failure:
            engine = failure["engine"]
            ledger[engine-1]["failure"] = failure
            if ledger[engine-1]["Bayesian"] != "PASS":
                ledger[engine-1]["Bayesian"] = "FAIL"
        status = "STAGE B BLOCKED"
    seal(j,status,failure,ledger,summary,began)

def prevent_label_file_access(event,args):
    if event == "open" and args and isinstance(args[0],(str,bytes,os.PathLike)):
        name = os.fsdecode(args[0]).replace("\\","/").split("/")[-1].lower()
        if name == "rul_fd001.txt":
            raise PermissionError("Official label access is outside Stage B authority")

if __name__ == "__main__":
    sys.addaudithook(prevent_label_file_access)
    if len(sys.argv)!=2 or sys.argv[1] not in ("preflight","execute"):
        raise SystemExit("Use exactly preflight or execute; no scoring mode exists")
    if sys.argv[1]=="preflight":
        preflight()
    else:
        execute()
