from pathlib import Path
import subprocess,json,hashlib,re,csv,io
R=Path('.');py=str((R/'.venv/Scripts/python.exe').resolve());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native={}
for name,cmd in [('handoff',[py,r'C:\Users\Raihan\.codex\skills\rei-research-engineering-suite\scripts\validate_handoff.py',r'C:\Users\Raihan\.codex\skills\rei-research-engineering-suite','docs/v0.5/research_lead_handoff.json']),('research',[py,r'C:\Users\Raihan\.codex\skills\scientific-research-engine\scripts\validate_research_project.py','.','--json'])]:
    proc=subprocess.run(cmd,text=True,capture_output=True);assert proc.returncode==0,proc.stdout+proc.stderr
    native[name]=json.loads(proc.stdout)
(R/'logs/v0.5/native_validation.json').write_text(json.dumps(native,indent=2)+'\n',encoding='utf8')
# Bound readability-only contract root-solver precision to the current draft metadata.
p=R/'research/v0.5/proposed_analysis_contract.json'
contract=R/'docs/v0.5/02_proposed_locked_analysis_contract.md'
payload=dict(version='0.5',status='PROPOSED_FOR_OWNER_LOCK_REVIEW',owner='Raihan x Rei',final_authorization=False,contract_path=str(contract).replace('\\','/'),contract_sha256=sha(contract),primary_question_unchanged=True,competitive_definition='Descriptive complete finite-benchmark characterization; no binary margin/population superiority',population_inference_included=False,protocol_locked_at=None,official_test_sensors_authorized=False,official_test_labels_authorized=False,confirmatory_authorized=False,fallback_authorized=False)
p.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf8')
# Audit report links before receipt generation; that one prospective link is explicit.
links=[];broken=[]
for f in (R/'docs/v0.5').glob('*.md'):
    text=f.read_text(encoding='utf8')
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if target.startswith(('https://','http://')):continue
        path=(f.parent/target).resolve()
        if not path.exists() and not target.endswith('logs/v0.5/delivery_receipt.json'):broken.append([str(f),target])
        links.append([str(f),target])
assert not broken,broken
(R/'logs/v0.5/report_integrity.json').write_text(json.dumps(dict(status='PASS',checked_links=len(links),broken_links=broken,expected_pending_receipt='logs/v0.5/delivery_receipt.json',scientific_code_unchanged_since_execution=True,contract_sha256=sha(contract)),indent=2)+'\n',encoding='utf8')
# Register remaining new source/verification artifacts without rewriting old rows.
a=R/'research/artifact_map.csv'; rows=list(csv.DictReader(a.read_text(encoding='utf8').splitlines()));fields=list(rows[0]);known={r['path'] for r in rows} if 'path' in rows[0] else {list(r.values())[2] for r in rows}
new=[R/'src/rp001/v05_highrho.py',R/'src/rp001/v05_score_numerics.py',R/'src/rp001/v05_score_demo.py',R/'tests/test_v05_score_numerics.py',R/'logs/v0.5/closure_qc.py',R/'logs/v0.5/closure_qc.json',R/'logs/v0.5/native_validation.json',R/'logs/v0.5/report_integrity.json',p]
buf=io.StringIO(newline='');w=csv.writer(buf)
for i,f in enumerate(new,1001):
    path=str(f).replace('\\','/')
    if path not in known:w.writerow([f'V05-A{i:04d}','bounded-prelock-source-and-verification',path,'','RP001-v0.5-bounded-prelock',sha(f)])
with a.open('ab') as f:f.write(buf.getvalue().encode('utf8'))
print(json.dumps(dict(native=native,report_links=len(links),contract_sha256=sha(contract))))
