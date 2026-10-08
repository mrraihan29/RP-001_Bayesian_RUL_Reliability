from pathlib import Path
import json,hashlib,subprocess,datetime,re
R=Path.cwd()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args])
def write(p,obj):(R/p).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
a=read('logs/protocol_lock/baseline_verification.json');arc=read('research/protocol_lock/baseline_alias_archive_map.json');bad=[];modes={}
for row in a['file_checks']:
    p=row['path']
    if sha(p)==row['sha256']:modes[p]='current'
    elif p in arc and sha(arc[p]['archive'])==row['sha256']:modes[p]='byte-preserved-archive'
    else:bad.append(p)
assert not bad,bad
for p,v in arc.items():assert sha(v['archive'])==v['sha256']
base=a['owner_baseline_commit']
for row in a['scientific_source_files']:assert sha(row['path'])==row['sha256']
unchanged=git('diff','--name-only',a['administrative_head_before_G3'],'--','src','configs','experiments','docs/v0.5','logs/v0.5','data').decode().splitlines()
assert unchanged==[],unchanged
assert (R/'research/experiment_registry.jsonl').read_bytes()==git('show',base+':research/experiment_registry.jsonl')
assert (R/'research/claim_ledger.csv').read_bytes()==git('show',base+':research/claim_ledger.csv')
for p in ['research/artifact_map.csv','research/decision_log.md']:assert (R/p).read_bytes().startswith((R/arc[p]['archive']).read_bytes())
state=read('research/state_manifest.json');protocol=read('research/protocol.json')
assert state['protocol_status']==protocol['status']=='PROTOCOL_DRAFTED'
assert state['protocol_lock_authorized'] and not state['protocol_lock_succeeded'] and state['protocol_locked_at'] is None
assert state['protected_evaluation_authorization']=={'stage_A_formal_lock':True,'stage_B_official_test_sensors':False,'stage_C_prediction_freeze_acceptance':False,'stage_D_official_test_labels_and_scoring':False}
assert not state['official_test_access'] and not state['confirmatory']
assert protocol['research_question']==read(arc['research/protocol.json']['archive'])['research_question']
assert not (R/'docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md').exists() and not (R/'docs/protocol_lock/LOCKED_RESEARCH_PROTOCOL.md').exists()
protected=re.compile(r'^(?:test|RUL)_FD00[1-4]\.txt$',re.I)
assert not [p.name for p in (R/'data/raw').iterdir() if protected.match(p.name)]
h=read('docs/protocol_lock/research_lead_handoff.json')
for e in h['evidence']:assert sha(e['location'])==e['sha256']
assert sha(h['artifact_identity']['path_or_uri'])==h['artifact_identity']['sha256_or_version']
validation={}
commands={'handoff':['C:/Users/Raihan/.codex/skills/rei-research-engineering-suite/scripts/validate_handoff.py','C:/Users/Raihan/.codex/skills/rei-research-engineering-suite','docs/protocol_lock/research_lead_handoff.json'],'research':['C:/Users/Raihan/.codex/skills/scientific-research-engine/scripts/validate_research_project.py','.','--json']}
for key,args in commands.items():
    p=subprocess.run([str(R/'.venv/Scripts/python.exe'),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    validation[key]=json.loads(p.stdout.decode())
assert validation['handoff']['result']=='PASS'
assert not validation['research']['hard_failures'] and validation['research']['protocol_status']=='PROTOCOL_DRAFTED'
write('logs/protocol_lock/native_validation.json',validation)
links=[];missing=[]
for file in (R/'docs/protocol_lock').glob('*.md'):
    if file.name=='OWNER_AUTHORIZATION_G3.md':continue
    for target in re.findall(r'\]\(([^)]+)\)',file.read_text(encoding='utf8')):
        if '://' in target or target.startswith('#'):continue
        resolved=(file.parent/target.split('#')[0]).resolve()
        if resolved.name=='LOCK_RECEIPT.json':continue
        links.append({'document':str(file.relative_to(R)).replace('\\','/'),'target':target})
        if not resolved.exists():missing.append(target)
assert not missing,missing
import sys
sys.path.insert(0,str(R/'src'))
import joblib,numpy as np
s=read('logs/protocol_lock/saved_state_verification.json')
p=s['selected_comparator']['path'];assert sha(p)==s['selected_comparator']['sha256']
obj=joblib.load(R/p);pre=np.load(R/'results/pilot/refit_preprocessor.npz',allow_pickle=False)
embedded={k:bool(np.array_equal(pre[k],obj['preprocessor'][k])) for k in pre.files}
assert all(embedded.values()),embedded
result={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package_integrity':'PASS','formal_protocol_lock':'FAIL_G3_AM_001','protocol_status':'PROTOCOL_DRAFTED','baseline_files_preserved':len(modes),'baseline_files_current':list(modes.values()).count('current'),'baseline_files_byte_archived':list(modes.values()).count('byte-preserved-archive'),'all_scientific_sources_configs_results_v05_evidence_unchanged':True,'historical_experiment_registry_unchanged':True,'historical_claim_ledger_unchanged':True,'new_scientific_experiments':0,'protected_access':False,'native_structural_validation':validation,'relative_document_links_checked':len(links),'receipt_links_deferred_until_postcommit':True,'embedded_comparator_preprocessor_identity':embedded,'owner_authorization':state['protected_evaluation_authorization'],'source_map_sha256':a['scientific_source_map_sha256']}
write('logs/protocol_lock/package_qc.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ('embedded_comparator_preprocessor_identity','native_structural_validation')},indent=2))
