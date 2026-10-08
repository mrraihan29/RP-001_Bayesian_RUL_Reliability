from pathlib import Path
import json,hashlib,platform,importlib.metadata,xml.etree.ElementTree as ET,subprocess
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
checks=[]
def check(name,ok,details=None):checks.append({'check':name,'status':'PASS' if ok else 'FAIL','details':details})
check('original_proposal_unchanged',sha('docs/proposal_v0.1.md')=='4ff06a6cf6f7a699dcbb9c66a76bfe6e21d60b64bc738c345e3b08c1f5118346')
check('training_fingerprint',sha('data/raw/train_FD001.txt')=='963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8')
check('archive_fingerprint',sha('data/raw/NASA_CMAPSS_original.zip')=='c9c5dec12a945a82e8bb4446589d7fb3cc057b5e5d81fa1a12e25ee9912ad3b2')
protected=[str(x.relative_to(R)) for x in (R/'data').rglob('*') if x.is_file() and (x.name.startswith('test_FD') or x.name.startswith('RUL_FD'))]
check('no_extracted_official_test_payload',not protected,protected)
env=read('logs/pilot_environment.json');fields=['python','implementation','platform','packages','float_dtype','sampler','blas_threads'];basis={k:env[k] for k in fields}
check('environment_hash_recomputed',hashlib.sha256(json.dumps(basis,sort_keys=True).encode()).hexdigest()==env['fingerprint'])
live={d.metadata['Name']:d.version for d in importlib.metadata.distributions()};delta={k:[v,live.get(k)] for k,v in env['packages'].items() if live.get(k)!=v}
check('actual_pilot_runtime_matches',platform.python_version()==env['python'] and platform.python_implementation()==env['implementation'] and platform.platform()==env['platform'] and not delta and set(live)==set(env['packages']),delta)
p=read('configs/proposed_protocol_v0.3.json');lock=read('configs/protocol_lock_record.json');a=read('configs/development_authorization.json')
check('owner_scope_consistent',a['stage_a_approved'] and lock['stage_a_approved'] and not lock['stage_b_approved'] and lock['locked_at'] is None and not a['confirmatory_evaluation_authorized'] and not a['test_labels_access_authorized'] and p['practical_threshold_cycles'] is None)
check('primary_question_unchanged',p['research_question']==read('configs/proposed_protocol_v0.2.json')['research_question'])
check('protocol_and_split_hashes',lock['proposed_protocol_sha256']==sha('configs/proposed_protocol_v0.3.json') and lock['proposed_split_sha256']==sha('configs/proposed_split_manifest.json'))
reports=[x for x in (R/'docs/v0.3').glob('0[1-9]_*.md')]
check('nine_deliverables_present',len(reports)==9,[x.name for x in sorted(reports)])
xml=ET.parse(R/'logs/final_pilot_tests.xml'); suites=list(xml.getroot().iter('testsuite'));n=sum(int(s.attrib['tests']) for s in suites);failure=sum(int(s.attrib.get('failures',0))+int(s.attrib.get('errors',0)) for s in suites)
check('final_integrated_tests',n==36 and failure==0,{'tests':n,'failures_errors':failure})
reg=[json.loads(s) for s in (R/'research/experiment_registry.jsonl').read_text().splitlines() if s.strip()]
check('registry_unique_and_protected',len(reg)==len({x['run_id'] for x in reg}) and all(not x.get('protected_test_access') and not x.get('confirmatory',False) for x in reg),len(reg))
errors=[];samplers=[]
for item in reg:
 path=item['metrics_file'].replace('\\','/');res=read(path)
 if 'Bayesian joint landmark' in item['method']:
  samplers.append(res)
  if sha(item['data_file'])!=item['data_fingerprint']:errors.append(item['run_id']+': datahash')
  if item['config_hash']!=hashlib.sha256(json.dumps(res['config'],sort_keys=True).encode()).hexdigest():errors.append(item['run_id']+': confighash')
  if res.get('posterior_file') and sha(res['posterior_file'].replace('\\','/'))!=res['posterior_sha256']:errors.append(item['run_id']+': posteriorhash')
 if not (R/path).is_file():errors.append(path)
check('registered_data_config_posterior_hashes',not errors,errors)
completed=[x for x in samplers if x['status']=='completed'];failed=[x for x in samplers if x['status']=='failed']
check('successful_fits_and_retained_failures',len(completed)==11 and len(failed)==2,{'completed':len(completed),'failed':len(failed)})
check('sampler_gates',all(x['diagnostics']['rhat_max']<1.01 and x['diagnostics']['bulk_ess_min']>=400 and x['diagnostics']['tail_ess_min']>=400 and x['diagnostics']['divergences']==0 and min(x['diagnostics']['bfmi'])>.3 and x['diagnostics']['maxdepth_fraction']<=.01 for x in completed))
aux=read('logs/auxiliary_diagnostics.json');check('auxiliary_sampler_gates',all(x['rhat_aux_max']<1.01 and x['ess_aux_min']>=400 and x['tail_aux_min']>=400 for x in aux))
pred=read('results/pilot/predictive_integration.json')
check('predictive_failure_propagated',pred['prediction_acceptance']=='FAIL' and pred['quantile_mcse_max_approx']>.5 and not pred['bayesian_calibration_ablation']['accepted_for_inference'] and p['pilot_disposition']=='REVISE AGAIN',{'quantile_mcse_max_approx':pred['quantile_mcse_max_approx'],'threshold':.5})
check('analysis_source_identity',sha('src/rp001/predictive_analysis.py')==pred['script_sha256'] and sha('src/rp001/statistical_design.py')==read('results/pilot/statistical_design.json')['script_sha256'])
h=read('docs/v0.3/research_lead_handoff.json')
check('handoff_evidence_hashes',h['artifact_identity']['sha256_or_version']==sha(h['artifact_identity']['path_or_uri']) and all(sha(x['location'])==x['sha256'] for x in h['evidence']))
old={'R01':'critical','R02':'critical','R03':'critical','R04':'high','R05':'high','R06':'critical','R07':'high','R08':'high','R09':'high','R10':'medium','R11':'high','R12':'medium','R13':'high','R14':'medium','R15':'medium'};new={x['risk_id']:x['severity'] for x in read('research/pilot_risk_register_v0.3.json')['risks']}
check('risk_ids_and_severities_preserved',all(new.get(k)==v for k,v in old.items()))
check('critical_fail_not_marked_ready',any(x['gate']=='PREDICTIVE_PRECISION' and x['state']=='FAIL' for x in h['gate_results']) and any(x['gate']=='PROTOCOL_LOCK' and x['state']=='BLOCKED' for x in h['gate_results']))
out={'status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','meaning':'Delivery integrity only; predictive readiness remains FAIL and protocol not locked','checks':checks,'environment_fingerprint':env['fingerprint'],'training_sha256':sha('data/raw/train_FD001.txt')}
(R/'logs/pilot_delivery_validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'delivery_integrity':out['status'],'checks':len(checks),'failed':[x for x in checks if x['status']=='FAIL'],'scientific_recommendation':'REVISE AGAIN'},indent=2))
raise SystemExit(out['status']!='PASS')