from pathlib import Path
import json,hashlib,subprocess,datetime,xml.etree.ElementTree as ET
R=Path.cwd()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):(R/p).write_text(json.dumps(d,ensure_ascii=True,indent=2)+'\n',encoding='utf8')
old=(R/'research/experiment_registry_v0.3.jsonl').read_bytes();new=(R/'research/experiment_registry.jsonl').read_bytes();assert new.startswith(old);entries=[json.loads(x) for x in new[len(old):].splitlines() if x.strip()]
for d in entries:
 raw=read(d['metrics_file']);run=raw.get('runtime',{})
 if d['cpu_seconds'] is None:d['cpu_seconds']=run.get('scientific_execution_process_cpu_seconds')
 if d['wall_seconds'] is None:d['wall_seconds']=run.get('scientific_execution_wall_seconds')
 assert d['cpu_seconds'] is not None and d['wall_seconds'] is not None,d['run_id']
(R/'research/experiment_registry.jsonl').write_bytes(old+b''.join((json.dumps(d,ensure_ascii=True)+'\n').encode() for d in entries))
raws=[(p,json.loads(p.read_text(encoding='utf8'))) for p in sorted((R/'experiments/v0.4/registry').glob('*.json'))]
source_checks=[]
for p,d in raws:
 if 'recovery_commit' in d:
  versions=[(d['original_scientific_commit'],d['original_scientific_shared_v04_common_provenance']['executed_source_sha256']),(d['recovery_commit'],{d['recovery_helper_path']:d['recovery_helper_sha256']})]
 else:
  prov=d.get('shared_v04_common_provenance',d);commit=prov.get('git_commit',d.get('git_snapshot',{}).get('head_commit'));sources=prov.get('executed_source_sha256',d.get('all_rp001_source_sha256',{}))
  if 'all_rp001_source_sha256' in d:sources=d['all_rp001_source_sha256']
  versions=[(commit,sources)]
 for commit,sources in versions:
  assert commit and sources,p.name
  for rel,h in sources.items():assert hashlib.sha256(subprocess.check_output(['git','show',f'{commit}:{rel}'])).hexdigest()==h,(p.name,rel)
  source_checks.append({'record':p.name,'commit':commit,'verified_blobs':len(sources)})
 for rel,h in d.get('artifacts_sha256',{}).items():assert sha(R/rel)==h,(p.name,rel)
 a=d.get('result_artifact',{})
 if a.get('sha256'):assert sha(R/a['path'])==a['sha256']
summary=read('experiments/v0.4/analysis/summary.json');fits=[d for p,d in raws if d.get('posterior_sha256')];assert len(fits)==33
failed=[d['run_id'] for d in fits if d['diagnostics']['acceptance']=='FAIL'];assert failed==['v04_syn_high_rho_3'];assert sum(d['configuration']['draws']*4 for d in fits)==504000
assert all(d['wall_seconds']<600 for d in fits)
CPU=sum(d['cpu_seconds'] for d in entries);assert CPU==2493.96875,CPU
amap=read('research/v0.4/current_alias_archive_map.json');baseline=read('logs/v0.3_delivery_manifest.json');checks=[]
for e in baseline['files']:
 rel=e['path'];p=R/rel
 if rel=='research/experiment_registry.jsonl':p=R/'research/experiment_registry_v0.3.jsonl'
 elif rel in amap:p=R/amap[rel]
 assert sha(p)==e['sha256'],(rel,p)
 checks.append({'historical_path':rel,'custody_path':p.relative_to(R).as_posix(),'sha256':e['sha256']})
mc=read('experiments/v0.4/precision/v04_precision_mcse_validation.json');assert read('experiments/v0.4/analysis/summary.json')['precision']['mcse_estimator_validation_pass'];assert len(mc['summary']['groups'])==18;assert len(mc['raw_records'])==600
root=ET.parse(R/'logs/v0.4/final_tests.xml').getroot();suites=[root] if root.tag=='testsuite' else list(root);n=sum(int(x.attrib['tests']) for x in suites);assert n==55 and all(int(x.attrib.get('failures',0))==0 and int(x.attrib.get('errors',0))==0 for x in suites)
res={'status':'PASS','created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'direct lead final arithmetic/custody verification, no new simulation or MCMC','records_checked':41,'historical_manifest_files_verified':len(checks),'historical_custody_checks':checks,'source_snapshot_checks':source_checks,'actual_mcmc_fits':33,'mcmc_diagnostic_pass':32,'mcmc_diagnostic_failures':failed,'retained_draws':504000,'CPU_seconds_registered':CPU,'CPU_hours_registered':CPU/3600,'test_cases':n,'official_test_access':False,'confirmatory':False}
write('logs/v0.4/supplemental_final_qc.json',res);print(json.dumps({k:v for k,v in res.items() if not k.endswith('_checks')},indent=2))