from pathlib import Path
import json,hashlib,subprocess,datetime
R=Path.cwd()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a])
a=read('logs/protocol_lock/baseline_verification.json');head=git('rev-parse','HEAD').decode().strip()
assert head!=a['administrative_head_before_G3'],'Commit attempted evidence before creating receipt'
assert not git('status','--porcelain').strip(),'Receipt requires clean committed evidence'
qc=read('logs/protocol_lock/package_qc.json');assert qc['package_integrity']=='PASS' and qc['formal_protocol_lock']=='FAIL_G3_AM_001'
changed=git('diff','--name-only',a['administrative_head_before_G3'],head).decode().splitlines()
files=[]
for p in changed:
    if p=='docs/protocol_lock/LOCK_RECEIPT.json':continue
    blob=git('show',head+':'+p);digest=hashlib.sha256(blob).hexdigest()
    assert sha(p)==digest
    files.append({'path':p,'bytes':len(blob),'sha256':digest})
m={'version':'G3-lock-attempt-1','status':'FORMAL_LOCK_NOT_COMPLETED_AMENDMENT_REQUIRED','protocol_status':'PROTOCOL_DRAFTED','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'successful_lock_commit':None,'locked_protocol_version':None,'administrative_evidence_commit':head,'owner_reviewed_scientific_commit':a['owner_baseline_commit'],'administrative_baseline_head':a['administrative_head_before_G3'],'owner_authorization':a['owner_directive'],'authorization_document_sha256':sha('docs/protocol_lock/OWNER_AUTHORIZATION_G3.md'),'approved_contract_sha256':sha('docs/v0.5/02_proposed_locked_analysis_contract.md'),'scientific_source_map_sha256':a['scientific_source_map_sha256'],'environment_fingerprint':a['environment_fingerprint'],'dataset_split_plan':a['identities'],'principal_posteriors':[{k:p[k] for k in ('path','sha256','bytes','run_id')} for p in a['principal_posteriors']],'baseline_files_verified':593,'exact_baseline_git_blobs_verified':560,'historical_local_only_verified':33,'new_scientific_experiments':0,'official_test_access':False,'confirmatory_scoring':False,'protected_phase_authorization':qc['owner_authorization'],'outstanding_amendment':'G3-AM-001','amendment_applied':False,'repository_visibility':'PUBLIC','scientific_publication_authorized':False,'sealed_administrative_files':files,'sealed_file_map_sha256':hashlib.sha256(json.dumps({p['path']:p['sha256'] for p in files},sort_keys=True,separators=(',',':')).encode()).hexdigest(),'self_reference_policy':'This post-commit receipt is stored in a later administrative commit. It records the evidence commit, not a successful lock or its own storage commit. The receipt and later verification outputs are excluded from the sealed prior evidence file map.','no_cryptographic_owner_signature':True}
(R/'docs/protocol_lock/LOCK_RECEIPT.json').write_text(json.dumps(m,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
print(json.dumps({'administrative_evidence_commit':head,'successful_lock_commit':None,'sealed_files':len(files),'status':m['status']},indent=2))
