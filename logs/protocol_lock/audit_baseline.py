from pathlib import Path
import hashlib, importlib.metadata, json, platform, subprocess, datetime, collections, xml.etree.ElementTree as ET
R=Path.cwd(); BASE='c583ce62eac9a6b3dcd29c1929cc07c17569beb7'
AUTH=Path(r'C:\Users\Raihan\.codex\attachments\0b4e45e1-4671-4a5b-80f0-da81ebcfd851\Pasted text.txt')
def git(*args): return subprocess.check_output(['git',*args])
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def item(p):return dict(path=p,bytes=(R/p).stat().st_size,sha256=sha(R/p))
head=git('rev-parse','HEAD').decode().strip(); clean=not git('status','--porcelain').strip()
# This audit script is the sole new untracked payload at the time of this audit.
status=git('status','--porcelain').decode().splitlines()
manifest=read('logs/v0.5/delivery_manifest.json');receipt=read('logs/v0.5/delivery_receipt.json')
checks=[];bad=[];git_count=0;local_count=0
for row in manifest['files']:
    p=R/row['path'];actual=sha(p) if p.is_file() else None
    ok=actual==row['sha256'] and p.stat().st_size==row['bytes'] if p.is_file() else False
    blob_ok=None
    if row['available_in_git_snapshot']:
        blob=git('show',BASE+':'+row['path']);blob_ok=hashlib.sha256(blob).hexdigest()==row['sha256'] and len(blob)==row['bytes'];git_count+=1
    else:local_count+=1
    if not ok or blob_ok is False:bad.append(row['path'])
    checks.append(dict(path=row['path'],sha256=actual,bytes=p.stat().st_size if p.exists() else None,current_matches=ok,git_blob_matches=blob_ok,available_in_git_snapshot=row['available_in_git_snapshot']))
packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
live={'python':platform.python_version(),'implementation':platform.python_implementation(),'platform':platform.platform(),'packages':dict(sorted(packages.items(),key=lambda x:x[0].lower())),'float_dtype':'float64','sampler':'nutpie NUTS','blas_threads':1}
fingerprint=hashlib.sha256(json.dumps(live,sort_keys=True).encode()).hexdigest()
# Float/sampler/thread entries identify the frozen execution policy; runtime package/interpreter/platform entries are freshly observed.
saved_env=read('logs/pilot_environment.json')
expected={'data/raw/train_FD001.txt':'963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8','configs/proposed_split_manifest.json':'6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b','configs/v0.5/resolution_plan.json':'6046cd808d6a4b68ed42fd7d3458f0f142273aa323f64bb077cb8c0bc7dc0745'}
identities={p:{**item(p),'expected_sha256':digest,'matches':sha(R/p)==digest} for p,digest in expected.items()}
source=[item(p) for p in sorted(git('ls-tree','-r','--name-only',BASE,'src').decode().splitlines())]
source_digest=hashlib.sha256(json.dumps({r['path']:r['sha256'] for r in source},sort_keys=True,separators=(',',':')).encode()).hexdigest()
contracts=[item(p) for p in ['docs/v0.5/02_proposed_locked_analysis_contract.md','docs/v0.5/01_prelock_resolution_memo.md','configs/requirements-pilot.lock','logs/pilot_environment.json','logs/v0.5/delivery_manifest.json','logs/v0.5/delivery_receipt.json']]
posteriors=[]
for i in (1,2,3):
    p=f'experiments/v0.4/fits/v04_main_r{i}.nc';rec=read(f'experiments/v0.4/registry/v04_main_r{i}.json')
    posteriors.append({**item(p),'run_id':rec['run_id'],'configuration':rec['configuration'],'diagnostics':rec['diagnostics'],'record_hash_matches':sha(R/p)==rec['artifacts_sha256'][p]})
old_fail=read('experiments/v0.4/registry/v04_syn_high_rho_3.json')
new_fit=read('experiments/v0.5/registry/v05_highrho_innovation.json')
registry=(R/'research/experiment_registry.jsonl').read_bytes(); prior=(R/'research/v0.5/baseline_current_aliases/research/experiment_registry.jsonl').read_bytes()
tests=ET.parse(R/'logs/v0.5/verification_tests.xml').getroot()[0].attrib
eligible=collections.Counter(r['role'] for r in read('configs/proposed_split_manifest.json') if r['eligible_alive'])
ancestor=subprocess.run(['git','merge-base','--is-ancestor',BASE,head]).returncode==0
current_diff=git('diff','--name-only',BASE,head).decode().splitlines()
# Retain exact source evidence excerpts; no root evaluations or predictions are executed.
excerpts={}
for p,lo,hi in [('docs/v0.5/02_proposed_locked_analysis_contract.md',68,72),('src/rp001/v04_precision.py',78,108),('src/rp001/prediction.py',7,17)]:
    lines=(R/p).read_text(encoding='utf8').splitlines();excerpts[p]=[{'line':n,'text':lines[n-1]} for n in range(lo,hi+1)]
baseline_ok=not bad and all(v['matches'] for v in identities.values()) and fingerprint==saved_env['fingerprint']==receipt['environment_fingerprint'] and sha(R/'logs/v0.5/delivery_manifest.json')==receipt['manifest_sha256'] and receipt['scientific_delivery_commit']==BASE and ancestor and all(r['record_hash_matches'] for r in posteriors)
result={'audit_scope':'G3 read-only existing-byte/environment/static verification; no experiment, predictions, sampling, tests rerun or protected archive member access','audited_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner_baseline_commit':BASE,'administrative_head_before_G3':head,'baseline_integrity':'PASS' if baseline_ok else 'FAIL','baseline_ancestor':ancestor,'initial_git_status':status,'changes_since_scientific_baseline':current_diff,'manifest_files_verified':len(checks),'git_blobs_verified':git_count,'historical_local_only_verified':local_count,'mismatches':bad,'file_checks':checks,'live_environment':live,'environment_fingerprint':fingerprint,'environment_matches_saved':fingerprint==saved_env['fingerprint'],'execution_policy_observation_limit':'float64/nutpie/one BLAS thread are preserved policy labels; no sampling or BLAS runtime execution in this verification','owner_directive':{'attachment_sha256':sha(AUTH),'attachment_bytes':AUTH.stat().st_size,'source':'human user attachment in current Codex conversation','sender':'Raihan','stated_research_owners':'Raihan x Rei','verified_identity_limit':'Authenticated conversation context only; no independent legal identity or cryptographic signature','authorization':'G3 Stage A formal lock only; B/C/D not authorized'},'identities':identities,'approved_documents_and_delivery_receipt':contracts,'scientific_source_files':source,'scientific_source_map_sha256':source_digest,'source_map_encoding':'SHA256 of UTF-8 JSON(path->SHA256), sorted keys, compact separators','principal_posteriors':posteriors,'eligible_counts':dict(eligible),'experiment_registry':{'sha256':sha(R/'research/experiment_registry.jsonl'),'records':len(registry.splitlines()),'historical_prefix_unchanged':registry.startswith(prior),'historical_prefix_records':len(prior.splitlines()),'no_G3_experiments_appended':True},'historical_tests':{'source':'logs/v0.5/verification_tests.xml','sha256':sha(R/'logs/v0.5/verification_tests.xml'),'suite_attributes':tests,'rerun':False},'historical_failures':{'v04_syn_high_rho_3_status':old_fail['diagnostics']['acceptance'],'v05_bounded_inquiry_status':new_fit['diagnostics']['acceptance'],'original_record_sha256':sha(R/'experiments/v0.4/registry/v04_syn_high_rho_3.json')},'static_quantile_rule_excerpts':excerpts,'method_freeze_result':'FAIL: G3-AM-001 quantile bracket / tolerance / route conflict','protocol_state':'PROTOCOL_DRAFTED','protected_test_sensor_access':False,'protected_test_label_access':False,'confirmatory_scoring':False,'new_scientific_runs':0}
(R/'logs/protocol_lock/baseline_verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
print(json.dumps({k:result[k] for k in ['baseline_integrity','manifest_files_verified','git_blobs_verified','historical_local_only_verified','environment_fingerprint','mismatches','eligible_counts','method_freeze_result','protocol_state']},indent=2))
assert baseline_ok,'Baseline integrity failed; see persisted report'