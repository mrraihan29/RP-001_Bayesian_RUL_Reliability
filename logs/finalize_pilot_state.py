from pathlib import Path
import json,hashlib,datetime,subprocess,csv
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,s): (R/p).write_text(s,encoding='utf-8')
def dump(p,v):write(p,json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def backup(p,q):
 if not (R/q).exists(): (R/q).write_bytes((R/p).read_bytes())
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
backup('research/protocol.json','research/protocol_v0.2.json');backup('configs/protocol_lock_record.json','configs/protocol_lock_record_v0.2.json');backup('research/environment_manifest.json','research/environment_manifest_v0.2.json');backup('research/artifact_map.csv','research/artifact_map_v0.2.csv');backup('research/claim_ledger.csv','research/claim_ledger_v0.2.csv')
p=read('configs/proposed_protocol_v0.2.json')
p.update(schema_version='0.3',artifact_version='0.3',owner='Raihan × Rei',owner_stage_a_approved=True,owner_stage_b_approved=False,status='PROTOCOL_DRAFTED',updated_at=now)
p['primary_claims']=['Comparative superiority unresolved; no official endpoint comparison executed','Development implementation checks and sampler diagnostics pass within tested scope; predictive precision fails']
p['confirmatory_or_exploratory']='Current work exploratory development only; one proposed primary comparison requires future final owner authorization'
p['practical_threshold_cycles']=None
p['practical_decision_rule']='Report effect sizes/intervals/decomposition; no practical superiority/equivalence claim without owner-approved utility mapping'
p['analysis_plan']='docs/v0.3/06_comparative_evaluation_design.md; proposed paired bootstrap-t20000, frozen-pipeline conditional inference; influential/degenerate failure policy pending'
p['new_engine_conditioning']='Full per-engine sensor-only global posterior update via importance-weighted mixture CDF; conjugate and one exact MCMC oracle verified; cohort approximate quantile MCSE gate FAIL'
p['uncertainty_plan']='Conditional assessment-engine uncertainty excludes training/PCA/HPO/calibration variation; illustrative total-variance simulation executed, full-pipeline study unresolved'
p['compute_budget']='Local CPU;32 aggregate CPU-hour/10GiB envelope; logged sampler CPU623.015625seconds including failures; no Colab or extra spending'
p['test_access_policy']='No official test sensors or labels in development. Final protocol and test/confirmatory access require explicit Research Owner authorization; prediction hashes before future label scoring.'
p['pilot_disposition']='REVISE AGAIN'
p['pilot_precision_acceptance']='FAIL: maximum approximate predictive quantile MCSE0.728972>.5cycle'
p['deviations'].append({'date':'2026-10-08','phase':'authorized pre-lock development','disclosed':True,'change':'Two storage-only backend repairs; existing refit56 step plus sensor-only oracle; comparator feature/estimability checks; no principal question or winner substitution','held_out_labels_visible':False,'development_calibration_outcomes_visible_after_freeze':True})
assert p['research_question']==read('configs/proposed_protocol_v0.2.json')['research_question']
dump('configs/proposed_protocol_v0.3.json',p);dump('research/protocol.json',p)
lock={'artifact_version':'0.3','status':'PROPOSED_NOT_LOCKED','owner':'Raihan × Rei','stage_a_approved':True,'stage_b_approved':False,'locked_at':None,'proposed_protocol_sha256':sha('configs/proposed_protocol_v0.3.json'),'proposed_split_sha256':sha('configs/proposed_split_manifest.json'),'approval_source':'Owner conditional development decision in current chat; configs/development_authorization.json','test_labels_access_authorized':False,'confirmatory_evaluation_authorized':False,'practical_threshold_cycles':None,'pilot_recommendation':'REVISE AGAIN','next':'Prospective numerical/scientific revision -> owner review -> final authorization separately'}
dump('configs/protocol_lock_record.json',lock)
env=read('logs/pilot_environment.json'); git=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
dump('research/environment_manifest.json',{'schema_version':'0.3','git_commit':git,'git_dirty':True,'runtime':'IsolatedCPython3.12.14;float64;nutpieNUTS;Windows11','dependency_lock':'configs/requirements-pilot.lock','environment_fingerprint':env['fingerprint'],'hardware':{'cpu':'Intel i7-10750H','physical_cores':6,'logical_cores':12,'ram_gib':env['total_ram_gib'],'gpu_used':False},'pilot_environment_validated':True,'final_research_authorized':False,'full_metadata':'logs/pilot_environment.json','notes':'Start identities and dirty flags retained per run; final code/evidence checkpoint in delivery provenance; environment fingerprint does not certify final scientific readiness'})
data=read('research/data_manifest.json');data['schema_version']='0.3';data['datasets'][0]['development_audit']='experiments/development_data_audit.json';data['datasets'][0]['eligible']={'fit':43,'tune':13,'calibration':25,'refit':56};data['datasets'][0]['official_test_covariates_read']=False;dump('research/data_manifest.json',data)
claims=list(csv.DictReader((R/'research/claim_ledger.csv').open(encoding='utf-8')))
for c in claims:
 if c['claim_id']=='C02':c['caveats']='Models fitted for development; no official primary endpoint comparison; quantile precision FAIL'
 if c['claim_id']=='C07':c['evidence_ids']='E-MATH;E-SYN;E-PPC';c['caveats']='Likelihood/gradient and four fixed synthetic recovery cases verified; identifiability/domain plausibility qualified; not a generative survival model'
with (R/'research/claim_ledger.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=claims[0].keys());w.writeheader();w.writerows(claims)
registry=R/'research/experiment_registry.jsonl';entries=[json.loads(x) for x in registry.read_text().splitlines() if x.strip()];existing={x['run_id'] for x in entries}
for rid,file,source,method,seed in [('statistical_design_pilot','results/pilot/statistical_design.json','src/rp001/statistical_design.py','Synthetic rank, bootstrap and pipeline-variance design checks',[8103301,8103302,8103303]),('prior_predictive_pilot','results/pilot/prior_predictive.json','src/rp001/pilot.py','Working-prior predictive diagnostics',7710),('development_cutoff_audit','experiments/development_data_audit.json','src/rp001/development_data_audit.py','Training split/cutoff/salt audit',None)]:
 if rid in existing:continue
 result=read(file);source_commit=subprocess.check_output(['git','log','-1','--format=%H','--',source],cwd=R,text=True).strip()
 entry={'run_id':rid,'phase':'exploratory','method':method,'status':'completed','metrics_file':file,'seed':seed,'environment_fingerprint':env['fingerprint'],'protected_test_access':False,'confirmatory':False,'source_file':source,'retained_source_sha256':sha(source),'code_commit':source_commit,'code_identity_kind':'retained-source archive commit; not a verified clean start','historical_run_source_verified':bool(result.get('script_sha256')==sha(source)),'registration':'retrospective evidence registration; original result unchanged','registered_at':now,'cpu_seconds':None}
 if 'wall_seconds' in result:entry['wall_seconds']=result['wall_seconds']
 if rid=='statistical_design_pilot':entry['code_dirty_at_execution']=True;entry['note']='Executed before source commit; original output binds exact script SHA. Archive commit verified by current source identity.'
 if rid=='prior_predictive_pilot':entry['note']='Original result stores seed/draws but no execution source snapshot or timing. Current retained script is not represented as verified original source.'
 entries.append(entry)
write('research/experiment_registry.jsonl',''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in entries))
with (R/'research/decision_log.md').open('a',encoding='utf-8') as f:f.write('\n## Development return v0.3 — 2026-10-08\n\nOwner StageA approved; final StageB absent. Development completed; REVISE AGAIN after predictive MCSE.728972>.5cycle. LocalCPU used; test covariates/labels untouched. Detailed decisions/deviations/risks: docs/v0.3/08_risks_assumptions_decisions.md.\n')
write('README.md','''# RP-001 — Bayesian RUL Reliability

**PROTOCOL_DRAFTED / REVISE AGAIN — development return v0.3,8 October2026.**

Start with [Owner Return and Recommendation](docs/v0.3/09_owner_return_recommendation.md). [All nine deliverables](docs/v0.3/README.md) include updated protocol, direct mathematics, recovery/MCMC/PPC, cutoff and calibration audits, comparison design, compute and open risks. Eleven fits completed; two failed storage attempts preserved. Predictive quantile precision failed the fixed criterion. Final research remains unapproved.

Only synthetic and official FD001 training data were used. Test sensors and labels remain unextracted/unread; the original NASA archive contains unopened test members, so custody is policy-based. No confirmatory evaluation. Owners: Raihan × Rei. Lead mathematical review remains distinct from final owner authorization.

Training:100 engines/20,631 rows. Reserved55/15/30 hash roles, one outcome-blind cutoff30..250, eligibility43/13/25, refit56. Survival selection and unknown official cutoffs prevent an asserted transported conformal guarantee.

Isolated CPython3.12.14/PyMC5.28.5/nutpie CPU environment is locked and fingerprinted; Colab Pro unused. [Compute/provenance](docs/v0.3/07_compute_environment_report.md), [exact reproduction commands](experiments/REPRODUCE_DEVELOPMENT.md), run registry and hashes retained. Git local, no remote/publication. Raw payloads, posterior stores, models and caches ignored; exact local scientific hashes are in the delivery manifest.

Original proposal remains byte-identical: docs/proposal_v0.1.md. [Historical v0.2 review](docs/00_research_lead_review.md), original lock/environment/ledgers and initial development plan remain available. Current protocol/authorization reflect StageA approval and final StageB=false. No fixed5cycle practical decision margin.
''')
ignore=R/'.gitignore';text=ignore.read_text();cache='CodingProjectNAOBI RESEARCHRP-001_Bayesian_RUL_Reliability.cachepytensor/'
if cache not in text:write('.gitignore',text+'\n# Windows PyTensor configuration parsing artifact\n'+cache+'\n')
print(json.dumps({'updated_state':'PROTOCOL_DRAFTED','stage_a':True,'stage_b':False,'registry_entries':len(entries)}))