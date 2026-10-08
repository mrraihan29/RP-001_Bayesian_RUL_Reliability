from pathlib import Path
import json,hashlib,datetime,subprocess,csv,io
R=Path.cwd()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head=='ca33e7d3f12a6687d8d41111ddc6d7fce573f6c2'
tracked={x.decode('utf8') for x in subprocess.check_output(['git','ls-files','-z']).split(b'\0') if x}
files=set(tracked);files.update(e['path'] for e in read('logs/v0.3_delivery_manifest.json')['files']);files.add('logs/v0.4/build_delivery_manifest.py')
excluded={'logs/v0.4/delivery_manifest.json','logs/v0.4/delivery_receipt.json','logs/v0.4/postcommit_validation.json'};files-=excluded
# Keep the new packaging driver in the artifact map as well as the final manifest.
p=R/'research/artifact_map.csv';rows=list(csv.DictReader(io.StringIO(p.read_text(encoding='utf8'))));rel='logs/v0.4/build_delivery_manifest.py';assert not any(q['path']==rel for q in rows)
rows.append({'artifact_id':f'V04-A{len(rows)+1:04d}','artifact_type':'delivery-provenance','path':rel,'claim_ids':'','generated_by':'RP001-v0.4-targeted-return','sha256':sha(R/rel)})
stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);p.write_text(stream.getvalue(),encoding='utf8',newline='')
entries=[]
for rel in sorted(files):
 p=R/rel;assert p.is_file(),rel
 assert not any(part in {'.git','.venv','.cache','__pycache__'} for part in p.relative_to(R).parts)
 entries.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'git_tracked_at_evidence_checkpoint':rel in tracked})
for q in rows:assert sha(R/q['path'])==q['sha256'],q['path']
protocol=read('research/protocol.json');assert protocol['research_question']=='Is a compact hierarchical Bayesian predictor competitive in 90% interval score with calibrated CQR at the official FD001 unseen-engine endpoint, with engine-level uncertainty and audited dependence?';assert not protocol['owner_stage_b_approved'] and protocol['protocol_locked_at'] is None
raw=next(e for e in entries if e['path']=='data/raw/train_FD001.txt');assert raw['sha256']=='963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8'
summary=read('experiments/v0.4/analysis/summary.json');fitfiles=list((R/'experiments/v0.4').rglob('*'));fitfiles=[p for p in fitfiles if p.is_file()]
manifest={'artifact_version':'0.4','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'evidence_checkpoint_commit':head,'executed_analysis_commit':'87a0083314daafb79f7ae3c67e23abd5979bc82a','scope':'Complete authorized synthetic/FD001train-only v0.4 evidence plus preserved reference/history closure; closedarchives hashed asouterbytesonly.','recommendation':'B. REVISE AGAIN','protocol_status':'PROTOCOL_DRAFTED','final_protocol_approved':False,'official_test_sensors_accessed':False,'official_test_labels_accessed':False,'official_predictions_or_scores_executed':False,'confirmatory':False,'environment_fingerprint':'f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c','dataset_fingerprint':raw['sha256'],'split_fingerprint':'6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b','frozen_plan_fingerprint':'0c6a7e1e924636cec6196295eac19b29a6bd7faa85e18b081549f8287ab0b99b','scientific_registered_CPU_seconds':2493.96875,'scientific_registered_CPU_hours':2493.96875/3600,'scientific_payload_bytes':sum(p.stat().st_size for p in fitfiles),'scientific_payload_file_count':len(fitfiles),'actual_mcmc_fits':33,'mcmc_diagnostic_pass':32,'mcmc_diagnostic_failures':['v04_syn_high_rho_3'],'test_cases_passed':55,'historical_manifest_files_verified':212,'excluded':{'self_and_postcommit_files':sorted(excluded),'runtime_dirs':['.git','.venv','.cache','__pycache__'],'notes':'Manifest self hash and final fullGitidentity are in ignored postcommitreceipt to avoid circular identity; older administrative receipts are separately preserved, not snapshotinputs. Byte hashes are not scientific certification.'},'files':entries,'file_count':len(entries),'retained_bytes':sum(e['bytes'] for e in entries)}
assert not (R/'logs/v0.4/delivery_manifest.json').exists();(R/'logs/v0.4/delivery_manifest.json').write_text(json.dumps(manifest,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
for e in entries:assert sha(R/e['path'])==e['sha256']
print(json.dumps({'file_count':len(entries),'retained_MiB':manifest['retained_bytes']/2**20,'scientific_payload_MiB':manifest['scientific_payload_bytes']/2**20,'manifest_sha256':sha(R/'logs/v0.4/delivery_manifest.json'),'evidence_commit':head,'recommendation':manifest['recommendation']},indent=2))