from pathlib import Path
import hashlib,json,h5py,numpy as np,joblib,sys
R=Path.cwd();sys.path.insert(0,str(R/'src'))
a=json.loads((R/'logs/protocol_lock/baseline_verification.json').read_text(encoding='utf8'))
assert a['baseline_integrity']=='PASS'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for p in a['principal_posteriors']:
    with h5py.File(R/p['path'],'r') as f:
        group=f['posterior'];variables={}
        for key in ('beta','gamma','Gamma','tau','r_g','sigma_z','sigma_r','rho','eta_rho','gcor_u'):
            d=group[key];values=d[...];variables[key]={'shape':list(d.shape),'dtype':str(d.dtype),'finite':bool(np.isfinite(values).all())}
        records.append({'path':p['path'],'sha256':p['sha256'],'variables':variables,'principal_chain_draw_shape_pass':all(v['shape'][:2]==[4,8000] for v in variables.values()),'finite_pass':all(v['finite'] for v in variables.values())})
expected={r['path']:r['sha256'] for r in a['file_checks']}
model_path='results/pilot/selected_comparator.joblib';assert sha(R/model_path)==expected[model_path]
# Only the previously trusted, fingerprint-verified local fitted object is deserialized. No fit/predict call.
obj=joblib.load(R/model_path)
metadata={}
for key,value in obj.items():
    entry={'type':type(value).__name__}
    for name in ('spec','status','train_size','quantile','conformal_shift_applied'):
        if hasattr(value,name):entry[name]=str(getattr(value,name))
    for name in ('lower_model','upper_model','model'):
        m=getattr(value,name,None)
        if m is not None:entry[name]={'type':type(m).__name__,'parameters':{k:m.get_params()[k] for k in ('loss','alpha','n_estimators','max_depth','min_samples_leaf','learning_rate','random_state')}}
    metadata[key]=entry
pre_path='results/pilot/refit_preprocessor.npz'
pre=np.load(R/pre_path,allow_pickle=False);precomp=[]
for i in (1,2,3):
    p=f'experiments/v0.4/fits/v04_main_r{i}_pre.npz';other=np.load(R/p,allow_pickle=False)
    equal={k:bool(np.array_equal(pre[k],other[k])) for k in pre.files};precomp.append({'path':p,'sha256':sha(R/p),'equal_to_refit_preprocessor':equal,'all_equal':all(equal.values())})
cal=json.loads((R/'results/pilot/comparator_calibration.json').read_text());post=json.loads((R/'experiments/v0.4/analysis/principal_posthoc_calibration.json').read_text())
output={'scope':'Saved-state metadata/finite-value/array identity audit only; no fit, predictions, sampling, score calculation or new scientific run','posterior_states':records,'selected_comparator':{'path':model_path,'sha256':expected[model_path],'object_metadata':metadata},'refit_preprocessor':{'path':pre_path,'sha256':expected[pre_path],'fit_engine_count':len(pre['fit_ids']),'comparisons':precomp},'CQR_calibration':{'file_sha256':expected['results/pilot/comparator_calibration.json'],'selected_candidate':cal['selected_cqr'],'n_calibration':cal['n_calibration'],'rank':cal['rank'],'q':cal['nonshrinking_correction'],'calibration_engine_ids':cal['calibration_engine_ids']},'Bayesian_secondary_calibration_record':post,'overall_saved_state_integrity':'PASS' if all(x['principal_chain_draw_shape_pass'] and x['finite_pass'] for x in records) and all(x['all_equal'] for x in precomp) else 'FAIL'}
(R/'logs/protocol_lock/saved_state_verification.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:output[k] for k in ('overall_saved_state_integrity','selected_comparator','CQR_calibration')},indent=2))