from pathlib import Path
import json,hashlib,subprocess,re,csv,datetime
R=Path.cwd()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a])
def write(p,x):(R/p).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
A=read('logs/protocol_lock/final_G3/resume_baseline_verification.json');P=read('research/protocol_lock/final_G3/preservation_map.json');C=read('docs/protocol_lock/AMENDMENT_CHANGE_RECORD.json')
for p,v in P.items():assert sha(v['archive'])==v['sha256'] and (R/v['archive']).stat().st_size==v['bytes']
n=0
for row in A['baseline_file_checks']:
 loc=row['verified_current_location'];expected=row['sha256']
 if sha(loc)!=expected:
  loc=P[row['original_path']]['archive']
 assert sha(loc)==expected and (R/loc).stat().st_size==row['bytes'];n+=1
prior=read(P['docs/protocol_lock/LOCK_RECEIPT.json']['archive'])
for row in prior['sealed_administrative_files']:
 loc=row['path']
 if sha(loc)!=row['sha256']:loc=P[loc]['archive']
 assert sha(loc)==row['sha256']
for row in A['scientific_sources']:assert sha(row['path'])==row['sha256']
for row in A['configurations_before_resume']:
 loc=row['path'] if row['path']!='configs/protocol_lock_record.json' else P[row['path']]['archive']
 assert sha(loc)==row['sha256']
changes=git('diff','--name-only',A['reviewed_amendment_commit'],'--','src','configs','experiments','docs/v0.5','logs/v0.5','data').decode().splitlines()
assert changes==['configs/protocol_lock_record.json'],changes
for p in ['research/experiment_registry.jsonl','research/claim_ledger.csv']:assert (R/p).read_bytes()==git('show',A['reviewed_amendment_commit']+':'+p)
original=(R/C['original_contract_path']).read_bytes();amended=(R/C['amended_source_contract_path']).read_bytes()
assert original.count(C['removed_clause'].encode())==1
assert amended==original.replace(C['removed_clause'].encode(),C['approved_replacement_clause'].encode())
assert amended.replace(C['approved_replacement_clause'].encode(),C['removed_clause'].encode())==original
locked=(R/'docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md').read_bytes()
assert locked[C['administrative_cover_bytes']:]==amended[amended.index(b'## Question, primary estimand, and competitive'):]
assert sha('docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md')==C['locked_contract_sha256']
for row in A['principal_posteriors']:assert sha(row['path'])==row['sha256']
manifest=read('docs/protocol_lock/FROZEN_MODEL_AND_CONFIGURATION_MANIFEST.json')
assert manifest['prior_policy']==read('configs/v0.4/remediation_plan.json')['prior']
assert manifest['CQR']['calibration']==A['CQR_calibration']
assert manifest['new_engine_prediction']['authoritative_quantile_route']==A['authoritative_quantile_route']
assert manifest['MCMC_policy']==read('configs/v0.4/remediation_plan.json')['mcmc_acceptance']
assert manifest['CQR']['reselection_allowed'] is False and manifest['fresh_sampling_retraining_fallback_allowed'] is False
s=read('research/state_manifest.json');p=read('research/protocol.json');lockrec=read('configs/protocol_lock_record.json')
permissions={'stage_A_formal_lock':True,'stage_B_official_test_sensors':False,'stage_C_prediction_freeze_acceptance':False,'stage_D_official_test_labels_and_scoring':False}
assert s['protocol_status']==p['status']==lockrec['status']=='PROTOCOL_LOCKED'
assert s['protected_evaluation_authorization']==p['protected_evaluation_authorization']==lockrec['protected_evaluation_authorization']==permissions
assert not s['official_test_access'] and not s['confirmatory'] and s['protocol_locked_at'] is not None
before=read(P['research/protocol.json']['archive'])
admin={'status','protocol_locked_at','updated_at','artifact_version','pilot_disposition','owner_stage_b_approved','formal_lock_integrity','locked_analysis_contract','locked_analysis_contract_sha256','locked_research_protocol','approved_amendment','owner_amendment_decision','protected_evaluation_authorization','legacy_owner_stage_b_field_note','authoritative_scientific_contract_note','preregistration'}
unexpected=[key for key in set(before)|set(p) if before.get(key)!=p.get(key) and key not in admin]
assert not unexpected,unexpected
core=['LOCKED_RESEARCH_PROTOCOL.md','LOCKED_ANALYSIS_CONTRACT.md','LOCK_DECISION_RECORD.md','FROZEN_MODEL_AND_CONFIGURATION_MANIFEST.json','FROZEN_CODE_AND_ENVIRONMENT_MANIFEST.json','FROZEN_DATA_AND_SPLIT_MANIFEST.json','SCIENTIFIC_CLAIM_BOUNDARIES.md','PROTECTED_EVALUATION_ACCESS_POLICY.md','LOCK_VERIFICATION_REPORT.md','LOCK_RECEIPT.json']
assert all((R/'docs/protocol_lock'/f).is_file() for f in core)
review=read('logs/protocol_lock/final_G3/direct_SOL_component_review.json')
assert len(review['components'])==9 and all(x['disposition']=='PASS_FOR_LOCK_CONSISTENCY' for x in review['components'])
assert review['amended_contract_sha256']==sha('docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md')
bad=[]
for row in csv.DictReader((R/'research/artifact_map.csv').open(encoding='utf8',newline='')):
 if not (R/row['path']).is_file() or sha(row['path'])!=row['sha256']:bad.append(row['artifact_id'])
assert not bad,bad
h=read('docs/protocol_lock/research_lead_handoff.json')
for e in h['evidence']:assert sha(e['location'])==e['sha256']
missing=[];links=0
for file in (R/'docs/protocol_lock').glob('*.md'):
 if file.name in ('OWNER_AUTHORIZATION_G3.md','OWNER_AMENDMENT_DECISION_G3_AM_001.md'):continue
 for target in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf8')):
  if '://' in target or target.startswith('#'):continue
  resolved=(file.parent/target.split('#')[0]).resolve();links+=1
  if resolved.name in ('package_qc.json',):continue
  if not resolved.exists():missing.append((file.name,target))
assert not missing,missing
vals={}
for key,args in {'handoff':['C:/Users/Raihan/.codex/skills/rei-research-engineering-suite/scripts/validate_handoff.py','C:/Users/Raihan/.codex/skills/rei-research-engineering-suite','docs/protocol_lock/research_lead_handoff.json'],'research':['C:/Users/Raihan/.codex/skills/scientific-research-engine/scripts/validate_research_project.py','.','--json']}.items():
 result=subprocess.run([str(R/'.venv/Scripts/python.exe'),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True);vals[key]=json.loads(result.stdout.decode())
assert vals['handoff']['result']=='PASS' and vals['research']['protocol_status']=='PROTOCOL_LOCKED' and not vals['research']['hard_failures']
write('logs/protocol_lock/final_G3/native_validation.json',vals)
result={'status':'PASS','scope':'Formal lock document/source/artifact/provenance and structural checks only','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_status':'PROTOCOL_LOCKED','core_files_present':len(core),'original_baseline_entries_verified':n,'failed_attempt_sealed_files_preserved':len(prior['sealed_administrative_files']),'history_and_alias_copies_verified':len(P),'original_contract_preserved':True,'approved_substitution_count':1,'exact_locked_scientific_body_verified':True,'all_scientific_source_config_priors_posterior_CQR_unchanged':True,'sole_config_change':'Administrative configs/protocol_lock_record.json; old bytes preserved','native_protocol_unexpected_scientific_field_changes':unexpected,'claim_and_experiment_ledgers_unchanged':True,'all_artifact_map_references_hash_valid':True,'direct_material_components':9,'document_links_checked':links,'native_structural_validation':vals,'new_scientific_runs':0,'protected_access':False,'phase_permissions':permissions,'receipt_status':'Pending payload commit; final postcommit receipt verification follows'}
write('logs/protocol_lock/final_G3/package_qc.json',result)
print(json.dumps({k:v for k,v in result.items() if k!='native_structural_validation'},indent=2))
