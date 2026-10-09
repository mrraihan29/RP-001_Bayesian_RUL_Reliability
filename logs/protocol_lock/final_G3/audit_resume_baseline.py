from pathlib import Path
import json,hashlib,subprocess,datetime,importlib.metadata,platform,inspect,ast,math
R=Path.cwd();O=R/'logs/protocol_lock/final_G3';O.mkdir(parents=True,exist_ok=True)
BASE='c583ce62eac9a6b3dcd29c1929cc07c17569beb7';REVIEW='1fc660b3ce09dd2b23b6a05e0698903bf6060355'
def sha(p):
    h=hashlib.sha256()
    with (R/p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def git(*a):return subprocess.check_output(['git',*a])
def write(p,obj):(O/p).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
assert git('rev-parse','HEAD').decode().strip()==REVIEW
old=read('logs/v0.5/delivery_manifest.json');archives=read('research/protocol_lock/baseline_alias_archive_map.json')
checks=[];bad=[]
for row in old['files']:
    p=row['path'];loc=p
    if sha(p)!=row['sha256']:loc=archives[p]['archive'] if p in archives else None
    ok=loc is not None and sha(loc)==row['sha256'] and (R/loc).stat().st_size==row['bytes']
    if not ok:bad.append(p)
    checks.append({'original_path':p,'verified_current_location':loc,'sha256':row['sha256'],'bytes':row['bytes'],'matches':ok,'available_in_original_git_snapshot':row['available_in_git_snapshot']})
assert not bad,bad
src=[]
for p in git('ls-tree','-r','--name-only',BASE,'src').decode().splitlines():
    digest=sha(p);blob=git('show',BASE+':'+p);assert hashlib.sha256(blob).hexdigest()==digest
    src.append({'path':p,'bytes':len(blob),'sha256':digest})
receipt=read('docs/protocol_lock/LOCK_RECEIPT.json')
for row in receipt['sealed_administrative_files']:
    assert sha(row['path'])==row['sha256'] and git('show',REVIEW+':'+row['path'])==(R/row['path']).read_bytes()
assert sha('docs/protocol_lock/LOCK_RECEIPT.json')==read('logs/protocol_lock/receipt_verification.json')['receipt_sha256']
history=[{'path':str(p.relative_to(R)).replace('\\','/'),'sha256':sha(str(p.relative_to(R))),'bytes':p.stat().st_size} for p in sorted((R/'docs/protocol_lock').glob('*')) if p.is_file()]
for row in history:assert git('show',REVIEW+':'+row['path'])==(R/row['path']).read_bytes()
packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
env={'python':platform.python_version(),'implementation':platform.python_implementation(),'platform':platform.platform(),'packages':dict(sorted(packages.items(),key=lambda x:x[0].lower())),'float_dtype':'float64','sampler':'nutpie NUTS','blas_threads':1}
fingerprint=hashlib.sha256(json.dumps(env,sort_keys=True).encode()).hexdigest()
assert fingerprint==read('logs/pilot_environment.json')['fingerprint']=='f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c'
expected={'data/raw/train_FD001.txt':'963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8','configs/proposed_split_manifest.json':'6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b','configs/v0.5/resolution_plan.json':'6046cd808d6a4b68ed42fd7d3458f0f142273aa323f64bb077cb8c0bc7dc0745'}
for p,h in expected.items():assert sha(p)==h
import h5py,numpy as np,sys
sys.path.insert(0,str(R/'src'))
import joblib
post=[]
pre=np.load(R/'results/pilot/refit_preprocessor.npz',allow_pickle=False)
for i in (1,2,3):
    p=f'experiments/v0.4/fits/v04_main_r{i}.nc';rec=read(f'experiments/v0.4/registry/v04_main_r{i}.json');d=rec['diagnostics']
    assert sha(p)==rec['posterior_sha256']==rec['artifacts_sha256'][p]
    assert d['acceptance']=='PASS' and d['rhat_max']<1.01 and d['bulk_ess_min']>=400 and d['tail_ess_min']>=400 and d['divergences']==0 and min(d['bfmi'])>.3 and d['maxdepth_fraction']<=.01
    assert d['auxiliary_rhat_max']<1.01 and d['auxiliary_bulk_min']>=400 and d['auxiliary_tail_min']>=400
    variables={}
    with h5py.File(R/p,'r') as f:
        for key in ('beta','gamma','Gamma','tau','r_g','sigma_z','sigma_r','rho','eta_rho','gcor_u'):
            ds=f['posterior'][key];assert ds.shape[:2]==(4,8000) and np.isfinite(ds[...]).all()
            variables[key]={'shape':list(ds.shape),'dtype':str(ds.dtype),'finite':True}
    other=np.load(R/f'experiments/v0.4/fits/v04_main_r{i}_pre.npz',allow_pickle=False)
    assert all(np.array_equal(pre[k],other[k]) for k in pre.files)
    post.append({'run_id':rec['run_id'],'path':p,'sha256':sha(p),'bytes':(R/p).stat().st_size,'configuration':rec['configuration'],'saved_diagnostics':d,'finite_saved_state_metadata':variables,'original_execution_commit':rec['git_commit'],'preprocessor_sha256':sha(f'experiments/v0.4/fits/v04_main_r{i}_pre.npz'),'preprocessor_equal_to_CQR_refit':True})
objpath='results/pilot/selected_comparator.joblib'
assert sha(objpath)==read('logs/protocol_lock/saved_state_verification.json')['selected_comparator']['sha256']
obj=joblib.load(R/objpath)
assert all(np.array_equal(pre[k],obj['preprocessor'][k]) for k in pre.files)
cqr={}
for label,model in [('lower',obj['selected'].lower_model),('upper',obj['selected'].upper_model),('median',obj['median'].model)]:
    pars=model.get_params();actual={k:pars[k] for k in ('loss','alpha','n_estimators','max_depth','min_samples_leaf','learning_rate','random_state')}
    assert actual['loss']=='quantile' and actual['n_estimators']==200 and actual['max_depth']==1 and actual['min_samples_leaf']==10 and actual['learning_rate']==.1 and actual['random_state']==20261008
    assert actual['alpha']=={'lower':.05,'upper':.95,'median':.5}[label]
    cqr[label]=actual
assert obj['selected'].status==obj['median'].status=='completed' and obj['selected'].train_size==obj['median'].train_size==56
cal=read('results/pilot/comparator_calibration.json');assert cal['rank']==24 and cal['n_calibration']==25
assert max(0.,sorted(cal['raw_engine_scores'])[23])==cal['nonshrinking_correction']==19.987558518873357
assert read('experiments/v0.4/registry/v04_syn_high_rho_3.json')['diagnostics']['acceptance']=='FAIL'
assert read('experiments/v0.5/registry/v05_highrho_innovation.json')['diagnostics']['acceptance']=='PASS'
assert (R/'research/experiment_registry.jsonl').read_bytes()==git('show',BASE+':research/experiment_registry.jsonl')
assert len((R/'research/experiment_registry.jsonl').read_bytes().splitlines())==73
# Static AST/source structure checks only; no root evaluation or scientific function call.
code=(R/'src/rp001/v04_precision.py').read_text(encoding='utf8');module=ast.parse(code)
q=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='_weighted_quantile')
source=ast.get_source_segment(code,q)
assert 'radius = (z_abs + 12.0) * max_sd + (max_mean - min_mean)' in source
assert 'for _ in range(100):' in source and 'radius *= 2.0' in source and 'xtol=1e-12' in source and 'rtol=4.0 * np.finfo(np.float64).eps' in source
assert 'lower_cdf <= probability <= upper_cdf' in source
import scipy,scipy.optimize
quantile={'module':'src/rp001/v04_precision.py','module_sha256':sha('src/rp001/v04_precision.py'),'function_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'public_entry_point':'rp001.v04_precision.estimate_mixture_quantile_mcse','solver_helper':'rp001.v04_precision._weighted_quantile','initial_radius':'(abs(Phi^-1(p))+12)*max(SD)+(max(mu)-min(mu))','bracket':['min(mu)-radius','max(mu)+radius'],'bracket_check_attempts_max':100,'radius_update':'multiply by 2 only if not bracketed; exact loop and failure semantics in pinned source','brent_xtol':1e-12,'brent_rtol':'4*float64 epsilon','scipy_version':scipy.__version__,'brent_signature':str(inspect.signature(scipy.optimize.brentq)),'root_residual_guard':1e-10,'no_root_or_prediction_computation_in_G3':True}
config=[{'path':p,'sha256':sha(p),'bytes':(R/p).stat().st_size} for p in git('ls-tree','-r','--name-only',REVIEW,'configs').decode().splitlines()]
out={'status':'PASS','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Resumed G3 fingerprint/static consistency/saved-state metadata verification only; no scientific experiment, sampling, prediction or protected member access','reviewed_amendment_commit':REVIEW,'original_scientific_commit':BASE,'baseline_files_verified':len(checks),'baseline_git_blob_entries':sum(x['available_in_original_git_snapshot'] for x in checks),'historical_local_only_count':sum(not x['available_in_original_git_snapshot'] for x in checks),'baseline_file_checks':checks,'prior_attempt_sealed_files_verified':len(receipt['sealed_administrative_files']),'prior_attempt_documents':history,'scientific_sources':src,'configurations_before_resume':config,'scientific_source_map_sha256':hashlib.sha256(json.dumps({x['path']:x['sha256'] for x in src},sort_keys=True,separators=(',',':')).encode()).hexdigest(),'live_environment':env,'environment_fingerprint':fingerprint,'input_identities':expected,'principal_posteriors':post,'CQR_fitted_parameters':cqr,'CQR_calibration':{k:cal[k] for k in ('selected_cqr','n_calibration','rank','nonshrinking_correction','calibration_engine_ids')},'authoritative_quantile_route':quantile,'existing_failure_preserved':True,'historical_registry_records':73,'new_scientific_runs':0,'protected_test_access':False,'runtime_policy_note':'float64/nutpie/one-thread labels preserve frozen policy; actual interpreter/platform/packages were freshly observed, without running a workload'}
write('resume_baseline_verification.json',out)
print(json.dumps({k:out[k] for k in ('status','baseline_files_verified','baseline_git_blob_entries','historical_local_only_count','prior_attempt_sealed_files_verified','environment_fingerprint','scientific_source_map_sha256','authoritative_quantile_route','new_scientific_runs')},indent=2))
