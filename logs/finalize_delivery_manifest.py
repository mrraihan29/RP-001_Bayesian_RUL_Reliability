from pathlib import Path
import json,hashlib,datetime,subprocess,csv
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
code=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
ignore=R/'.gitignore';txt=ignore.read_text()
for pattern in ['logs/v0.3_delivery_receipt.json','logs/v0.3_snapshot_validation.json']:
 if pattern not in txt:txt+='\n# Administrative post-commit receipt (avoids circular commit identity)\n'+pattern+'\n'
ignore.write_text(txt,encoding='utf-8')
env=json.loads((R/'logs/pilot_environment.json').read_text())
prov={'artifact_version':'0.3','code_evidence_checkpoint':code,'code_evidence_checkpoint_scope':'Nine reports, fixed implementation, actual results and retained failures; scientific precision gate FAIL','environment_fingerprint':env['fingerprint'],'training_sha256':sha(R/'data/raw/train_FD001.txt'),'source_proposal_sha256':sha(R/'docs/proposal_v0.1.md'),'split_manifest_sha256':sha(R/'configs/proposed_split_manifest.json'),'dependency_lock_sha256':sha(R/'configs/requirements-pilot.lock'),'protocol_v0.3_sha256':sha(R/'configs/proposed_protocol_v0.3.json'),'manifest_path':'logs/v0.3_delivery_manifest.json','final_delivery_commit_receipt':'logs/v0.3_delivery_receipt.json','final_commit_convention':'This source/evidence checkpoint is a concrete existing Git commit. A subsequent commit versions this manifest and provenance; its exact hash is in the ignored administrative receipt and final owner message to avoid a self-referential committed hash.','historical_dirty_state_disclosed':True,'full_independent_reproduction_claimed':False,'research_status':'PROTOCOL_DRAFTED','recommendation':'REVISE AGAIN','final_protocol_approved':False,'official_test_access':False,'confirmatory':False,'practical_threshold_cycles':None,'created_at':now,'unresolved_scientific_risks':'docs/v0.3/08_risks_assumptions_decisions.md'}
(R/'docs/v0.3/delivery_provenance.json').write_text(json.dumps(prov,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
exclude_roots={'.git','.venv','.cache','CodingProjectNAOBI RESEARCHRP-001_Bayesian_RUL_Reliability.cachepytensor'}
exclude_parts={'__pycache__','.pytest_cache','.mypy_cache','.ruff_cache'}
exclude_exact={'logs/v0.3_delivery_manifest.json','logs/v0.3_delivery_receipt.json','logs/v0.3_snapshot_validation.json','research/artifact_map.csv'}
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R)
 if rel.parts[0] in exclude_roots or any(x in exclude_parts for x in rel.parts) or rel.as_posix() in exclude_exact:continue
 files.append({'path':rel.as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
with (R/'research/artifact_map.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['artifact_id','artifact_type','path','claim_ids','generated_by','sha256'])
 for i,x in enumerate(files,1):w.writerow([f'V03-A{i:04d}',Path(x['path']).suffix or 'source',x['path'],'','RP001-development-return',x['sha256']])
files.append({'path':'research/artifact_map.csv','bytes':(R/'research/artifact_map.csv').stat().st_size,'sha256':sha(R/'research/artifact_map.csv')})
manifest={'artifact_version':'0.3','code_evidence_checkpoint':code,'created_at':now,'scope':'Retained project scientific/source/provenance files including local ignored raw/posterior/data/model payloads; no cache or runtime library inventory bytes','environment_fingerprint':env['fingerprint'],'recommendation':'REVISE AGAIN','final_protocol_approved':False,'confirmatory':False,'official_test_payload_extracted_or_inspected':False,'excluded':'Runtime/cache dirs, Python caches, self manifest, post-commit administrative receipts. Git software/package identity is captured separately by exact lock/fingerprint.','files':sorted(files,key=lambda x:x['path']),'file_count':len(files),'retained_bytes':sum(x['bytes'] for x in files)}
(R/'logs/v0.3_delivery_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checkpoint':code,'manifest_files':len(files),'retained_gib':manifest['retained_bytes']/2**30,'manifest_sha256':sha(R/'logs/v0.3_delivery_manifest.json')}))