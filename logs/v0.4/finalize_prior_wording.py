from pathlib import Path
import json,hashlib,datetime,csv,io,subprocess
R=Path.cwd()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
oldhead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert oldhead=='bade492ddba310b8a3443597ea525974a88ba659'
for rel in ['logs/v0.4/delivery_manifest.json','logs/v0.4/delivery_receipt.json','logs/v0.4/postcommit_validation.json']:
 p=R/'logs/v0.4/archive'/('preclarification_'+Path(rel).name);assert not p.exists();p.write_bytes((R/rel).read_bytes())
for rel in ['docs/v0.4/01_updated_research_protocol.md','docs/v0.4/03_bayesian_prior_plausibility.md']:
 p=R/rel;s=p.read_text(encoding='utf8');assert 'Gamma row SD[.5,.35]' in s;s=s.replace('Gamma row SD[.5,.35]','Each of the two Gamma rows uses the same independent intercept/age-coefficient SD vector [.5,.35]');p.write_text(s,encoding='utf8')
p=R/'docs/v0.4/08_independent_mathematical_reverification.md';s=p.read_text(encoding='utf8');key='At sensor basis [1,t], Var(z)';assert key in s;s=s.replace(key,'In these formulas G0/G1 denote the intercept/age-coefficient prior SDs within each Gamma row, not different SDs for the two latent coordinates. Both Gamma rows repeat [.5,.35], exactly as `np.tile(Gamma_sd,(2,1))` in the executed model and prior generator. '+key);p.write_text(s,encoding='utf8')
p=R/'docs/v0.4/11_prelock_recommendation.md';s=p.read_text(encoding='utf8');s=s.replace('No source/model/seed/threshold or scientific evidence was changed to close these reporting findings.','No source/model/seed/threshold or scientific evidence was changed to close these reporting findings. Final audit also clarified that the same Gamma intercept/age-coefficient SD vector [.5,.35] is repeated in both latent rows; report wording now matches the executed model and prior generator, with no prior or result change.');p.write_text(s,encoding='utf8')
write('logs/v0.4/final_prior_index_clarification.json',{'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parent_evidence_commit':oldhead,'type':'report-only index clarification','finding':'Gamma rowSD wording could be misread as distinct scalar SDs for latent rows. Executed source uses a repeated intercept/age vector in each row.','exact_executed_structure':'np.tile([0.5,0.35],(2,1)) = [[.5,.35],[.5,.35]]','scope':'Reports01/03/08/11 wording; no scientific source/config/prior/seed/draw/target/threshold/result changed; no new science.','material_prior_moment_verdict':'PASS; existing formula G0^2+G1^2*x^2 uses age-coefficient scales, consistent with repeated rows.','historical_manifest_receipt_custody':'Exact original manifest/receipts in archive/preclarification_* and Git parent bade492.'})
# Refresh handoff hashes for direct math and the finished recommendation, with no gate-state change.
h=read('docs/v0.4/research_lead_handoff.json')
for e in h['evidence']:e['sha256']=sha(R/e['location'])
h['artifact_identity']['sha256_or_version']=sha(R/h['artifact_identity']['path_or_uri']);h['report_only_clarification']='logs/v0.4/final_prior_index_clarification.json';write('docs/v0.4/research_lead_handoff.json',h)
v=read('logs/v0.4/native_validation.json');v['handoff']['artifact_sha256']=sha(R/'docs/v0.4/research_lead_handoff.json');v['handoff']['postvalidation_change']='Evidence hashes refreshed after report-only Gamma-index clarification; schema and gate structure unchanged.';write('logs/v0.4/native_validation.json',v)
# Add these final disclosure/archive files to the explicit map and manifest; preserve prior snapshot in Git/archive.
p=R/'research/artifact_map.csv';rows=list(csv.DictReader(io.StringIO(p.read_text(encoding='utf8'))));known={q['path'] for q in rows}
extra=['logs/v0.4/final_prior_index_clarification.json','logs/v0.4/finalize_prior_wording.py']+[p.relative_to(R).as_posix() for p in (R/'logs/v0.4/archive').glob('preclarification_*')]
for rel in extra:
 if rel not in known:rows.append({'artifact_id':f'V04-A{len(rows)+1:04d}','artifact_type':'report-clarification-custody','path':rel,'claim_ids':'','generated_by':'RP001-v0.4-targeted-return','sha256':sha(R/rel)})
for q in rows:
 if q['artifact_id'].startswith('V04-'):q['sha256']=sha(R/q['path'])
 assert sha(R/q['path'])==q['sha256'],q['path']
stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);p.write_text(stream.getvalue(),encoding='utf8',newline='')
m=read('logs/v0.4/delivery_manifest.json');files={e['path'] for e in m['files']}|set(extra);tracked={x.decode() for x in subprocess.check_output(['git','ls-files','-z']).split(b'\0') if x};entries=[]
for rel in sorted(files):
 p=R/rel;entries.append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p),'git_tracked_at_evidence_checkpoint':rel in tracked})
m.update(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),preclarification_manifest_commit=oldhead,report_only_clarification='logs/v0.4/final_prior_index_clarification.json',files=entries,file_count=len(entries),retained_bytes=sum(e['bytes'] for e in entries));write('logs/v0.4/delivery_manifest.json',m)
for e in entries:assert sha(R/e['path'])==e['sha256']
print(json.dumps({'report_index_clarification':'complete','scientific_source_or_outputs_changed':False,'files_verified':len(entries),'manifest_sha256':sha(R/'logs/v0.4/delivery_manifest.json')},indent=2))