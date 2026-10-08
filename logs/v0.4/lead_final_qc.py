"""Direct lead QC of fixed raw summaries and source/identity custody; no new sampling."""
import json,hashlib,subprocess
from pathlib import Path
import numpy as np
from scipy.stats import norm
R=Path.cwd();Q=R/'logs/v0.4/lead_final_qc.json'
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mc=read('experiments/v0.4/precision/v04_precision_mcse_validation.json');old=read('experiments/v0.4/registry/v04_precision_validation.json');assert mc['raw_records']==old['partial_raw_records']
checks=[]
for g in mc['summary']['groups']:
    records=[r for r in mc['raw_records'] if r['rho']==g['rho']];key=str(g['probability']);batch=str(g['batch_size'])
    err=np.array([r['quantiles'][key]['error_cycles'] for r in records]);se=np.array([r['quantiles'][key]['batch_results'][batch]['quantile_rul_mcse'] for r in records]);exact=np.exp(np.log(100)+.1+np.sqrt(.11)*norm.ppf(g['probability']))
    np.testing.assert_allclose([r['quantiles'][key]['exact_rul_quantile_cycles'] for r in records],exact,rtol=1e-14)
    ratio=np.sqrt(np.mean(err**2)/np.mean(se**2));coverage=np.mean(np.abs(err)<=1.96*se)
    np.testing.assert_allclose(ratio,g['rms_actual_error_over_rms_estimated_mcse'],rtol=1e-14);assert coverage==g['empirical_1p96_mcse_coverage']
    checks.append(dict(rho=g['rho'],p=g['probability'],batch=g['batch_size'],ratio=float(ratio),coverage=float(coverage)))
oc=read('experiments/v0.4/inference/v04_paired_bootstrap_t_oc.json')['operating_characteristics'];records=oc['simulation_records']
for g in oc['results_by_scenario']:
    v=[r for r in records if r['scenario']==g['scenario'] and r['status']=='ok'];assert len(v)==g['nsim_interval_available'];assert sum(r['reject_h0_mean_ge_zero'] for r in v)==g['one_sided_h0_mean_ge_zero_rejection_conditional_on_interval_available']['successes'];assert sum(r['contains_zero'] for r in v)==g['coverage_95_conditional_on_interval_available']['successes']
prec=read('experiments/v0.4/analysis/principal_precision_all25.json')['results'];manifest=read('configs/proposed_split_manifest.json');ids=sorted(r['engine'] for r in manifest if r['role']=='calibration' and r['eligible_alive']);assert len(prec)==75 and {r['engine'] for r in prec}==set(ids);assert len({(r['engine'],r['probability']) for r in prec})==75
source_checks=[]
for path in sorted((R/'experiments/v0.4/registry').glob('*.json')):
    d=json.loads(path.read_text());prov=d.get('shared_v04_common_provenance',d);sources=prov.get('executed_source_sha256',{})
    commit=prov.get('git_commit')
    if commit and sources:
        for rel,expected in sources.items():
            blob=subprocess.check_output(['git','-C',str(R),'show',f'{commit}:{rel}']);assert hashlib.sha256(blob).hexdigest()==expected,(path.name,rel)
        split=subprocess.check_output(['git','-C',str(R),'show',f'{commit}:configs/proposed_split_manifest.json']);assert hashlib.sha256(split).hexdigest()=='6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b'
        source_checks.append(dict(record=path.name,commit=commit,source_file_count=len(sources),split_manifest_match=True))
    for rel,expected in d.get('artifacts_sha256',{}).items():assert sha(R/rel)==expected
assert sha(R/'experiments/v0.4/registry/v04_precision_validation.json')==sha(R/'logs/v0.4/archive/v04_precision_validation_original_failed_registry.json')
old_manifest=read('logs/v0.3_delivery_manifest.json');entries=old_manifest.get('files',old_manifest.get('artifacts',[]));assert entries
unchanged=[]
for e in entries:
    path=e['path']
    if path.startswith(('docs/v0.3/','results/pilot/','src/rp001/')) and not 'v04' in path:
        assert sha(R/path)==e['sha256'],path;unchanged.append(path)
result=dict(status='PASS',method='Direct SOL arithmetic recomputation, exact known-target quantiles, complete identity counts, Git blob hashing and old-evidence custody checks; no additional sampling',mcse_groups=checks,oc_replicates_recounted=len(records),source_snapshot_checks=source_checks,historical_immutable_files_verified=len(unchanged),calibration_engine_ids=ids,n_quantiles_verified=75,official_test_access=False)
Q.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in result.items() if k not in ('mcse_groups','source_snapshot_checks','calibration_engine_ids')},indent=2))