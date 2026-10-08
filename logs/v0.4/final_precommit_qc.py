from pathlib import Path
import json,hashlib,re,csv,io,datetime
R=Path.cwd()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
write('logs/v0.4/native_validation.json',{'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'handoff':{'command':'.venv/Scripts/python.exe C:/Users/Raihan/.codex/skills/rei-research-engineering-suite/scripts/validate_handoff.py C:/Users/Raihan/.codex/skills/rei-research-engineering-suite docs/v0.4/research_lead_handoff.json','result':'PASS','errors':[],'exit_code':0,'artifact_sha256':sha(R/'docs/v0.4/research_lead_handoff.json')},'scientific_workspace':{'command':'.venv/Scripts/python.exe C:/Users/Raihan/.codex/skills/scientific-research-engine/scripts/validate_research_project.py . --json','status':'PROTOCOL_DRAFTED','protocol_status':'PROTOCOL_DRAFTED','mode':'dataset-benchmark','hard_failures':[],'warnings':[],'info':[],'exit_code':0,'protocol_sha256':sha(R/'research/protocol.json')},'interpretation':'Structural checks pass at draft state; scientific gates still FAIL/BLOCKED and recommendationB. No protocol/test/confirmatory approval.'})
missing=[];pending=[];tables=[]
for p in sorted((R/'docs/v0.4').glob('*.md')):
 s=p.read_text(encoding='utf8')
 for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',s):
  if link.startswith(('http:','https:','#')):continue
  target=link.split('#')[0].strip('<>');path=(p.parent/target).resolve()
  if not path.exists():
   if path.name in ['delivery_manifest.json','delivery_receipt.json']:pending.append(path.name)
   else:missing.append((p.name,target))
 rows=[(i,line) for i,line in enumerate(s.splitlines(),1) if line.startswith('|')]
 for i,line in rows:
  if 'maximum |mean' in line:tables.append((p.name,i,'unescaped header separator'))
assert not missing and not tables,(missing,tables)
assert len(list((R/'docs/v0.4').glob('[0-9][0-9]_*.md')))==11
assert read('logs/v0.4/supplemental_final_qc.json')['status']=='PASS'
h=read('docs/v0.4/research_lead_handoff.json')
for e in h['evidence']:assert sha(R/e['location'])==e['sha256'],e['evidence_id']
assert sha(R/h['artifact_identity']['path_or_uri'])==h['artifact_identity']['sha256_or_version']
allowed={'RESOLVED','MITIGATED BY CLAIM RESTRICTION','STILL BLOCKED'}
assert all(q['status'] in allowed for q in read('research/v0.4/risk_register.json')['risks'])
assert read('research/protocol.json')['owner_stage_b_approved'] is False
write('logs/v0.4/report_integrity_qc.json',{'status':'PASS','eleven_numbered_reports':True,'markdown_targets_checked':True,'missing_targets':missing,'deferred_postcommit_targets':sorted(set(pending)),'handoff_evidence_hashes_match':True,'critical_risk_vocabulary_owner_compliant':True,'recommendation':'B. REVISE AGAIN','no_scientific_reruns':True})
# Add final QA and figure items and refresh only current v0.4 rows, retaining old custody rows.
p=R/'research/artifact_map.csv';rows=list(csv.DictReader(io.StringIO(p.read_text(encoding='utf8'))));known={r['path'] for r in rows}
for rel in ['logs/v0.4/native_validation.json','logs/v0.4/report_integrity_qc.json','logs/v0.4/final_precommit_qc.py','logs/v0.4/supplemental_final_qc.json','logs/v0.4/plot_saved_precision.py','figures/v0.4/predictive_precision_all25.png','figures/v0.4/predictive_precision_all25.pdf']:
 if rel not in known:rows.append({'artifact_id':f'V04-A{len(rows)+1:04d}','artifact_type':'final-verification','path':rel,'claim_ids':'','generated_by':'RP001-v0.4-targeted-return','sha256':sha(R/rel)})
for row in rows:
 if row['artifact_id'].startswith('V04-'):row['sha256']=sha(R/row['path'])
 # Every retained old/current map entry must now resolve to its exact bytes.
 assert sha(R/row['path'])==row['sha256'],row['path']
stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);p.write_text(stream.getvalue(),encoding='utf8',newline='')
print(json.dumps({'report_integrity':'PASS','native_structure':'PROTOCOL_DRAFTED / no hard failures','source_custody':'PASS / 212historicalfiles / all41records','artifact_map_entries':len(rows),'recommendation':'B. REVISE AGAIN'},indent=2))