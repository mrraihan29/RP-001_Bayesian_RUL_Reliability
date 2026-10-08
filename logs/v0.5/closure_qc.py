from pathlib import Path
import json,hashlib,subprocess,xml.etree.ElementTree as ET,csv,io
R=Path('.');git=r'C:\Program Files\Git\cmd\git.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
# Only v05 artifact rows can be refreshed; preserve exact historical CSV prefix.
artifact=R/'research/artifact_map.csv';raw=artifact.read_bytes();lines=raw.splitlines(keepends=True)
h='docs/v0.5/research_lead_handoff.json'
for i,line in enumerate(lines):
    if line.startswith(b'V05-') and h.encode() in line:
        fields=next(csv.reader([line.decode()]));fields[-1]=sha(R/h);buf=io.StringIO(newline='');csv.writer(buf).writerow(fields);lines[i]=buf.getvalue().encode()
artifact.write_bytes(b''.join(lines))
# Inspect and bind every scientific assertion/custody gate independently.
maps=read('research/v0.5/baseline_alias_archive_map.json')
baseline=read('logs/v0.4/delivery_manifest.json');verified=[];bad=[]
for f in baseline['files']:
    path=R/f['path']
    direct=path.exists() and sha(path)==f['sha256']
    archive=maps.get(f['path'],{}).get('archive')
    archived=archive and (R/archive).exists() and sha(R/archive)==f['sha256']
    if not direct and not archived:bad.append(f['path'])
    else:verified.append(dict(path=f['path'],mode='current' if direct else 'byte-preserved-v05archive'))
assert not bad,bad
for k,v in maps.items():assert sha(R/v['archive'])==v['sha256']
prior=(R/maps['research/experiment_registry.jsonl']['archive']).read_bytes();current=(R/'research/experiment_registry.jsonl').read_bytes()
assert current.startswith(prior) and len(prior.splitlines())==71 and len(current.splitlines())==73
runs=[json.loads(x) for x in current.splitlines()];assert len({r['run_id'] for r in runs})==73
fit=read('experiments/v0.5/registry/v05_highrho_innovation.json');pre=read('experiments/v0.5/analysis/math_preflight.json');demo=read('experiments/v0.5/registry/v05_score_propagation.json');score=read('experiments/v0.5/analysis/score_propagation.json')
assert fit['scientific_sampler_invocation_count']==1 and fit['diagnostics']['acceptance']=='PASS'
assert read('experiments/v0.4/registry/v04_syn_high_rho_3.json')['diagnostics']['acceptance']=='FAIL'
assert fit['configuration']==read('configs/v0.5/resolution_plan.json')['investigation']
assert fit['configuration']['seed']==54103 and fit['configuration']['truth']['rho']==.95
assert pre['status']=='PASS' and len(pre['grid'])==12 and pre['n_gradient_coordinates']==48
assert demo['sampler_invocations']==0 and not score['primary_CQR_contrast_computed']
assert fit['plan_sha256']==demo['plan_sha256']==pre['plan_sha256']==sha(R/'configs/v0.5/resolution_plan.json')
assert fit['git_commit']==pre['git_commit']=='304d8e76d03fe7d69dc7f8f9bb6de3c600a219dd'
# Git blobs independently certify exact source bytes at each run's actual execution.
source_counts={}
for name,rec in [('fit',fit),('preflight',pre),('score',demo)]:
    for path,digest in rec['executed_source_sha256'].items():
        blob=subprocess.check_output([git,'show',rec['git_commit']+':'+path])
        assert hashlib.sha256(blob).hexdigest()==digest and sha(R/path)==digest,(name,path)
    assert not rec['official_test_access'] and not rec['confirmatory']
    source_counts[name]=len(rec['executed_source_sha256'])
for p,digest in fit['artifacts_sha256'].items():assert sha(R/p)==digest
for p,digest in demo['input_sha256'].items():assert sha(R/p)==digest
for e in read('docs/v0.5/research_lead_handoff.json')['evidence']:assert sha(R/e['location'])==e['sha256']
tree=ET.parse(R/'logs/v0.5/verification_tests.xml');s=tree.getroot()[0]
assert int(s.attrib['tests'])==59 and int(s.attrib['failures'])==int(s.attrib['errors'])==0
prot=read('research/protocol.json');state=read('research/state_manifest.json')
assert prot['status']=='PROTOCOL_DRAFTED' and not prot['owner_stage_b_approved'] and prot['protocol_locked_at'] is None
assert not state['official_test_access'] and not state['confirmatory'] and not state['protocol_lock_authorized']
assert prot['research_question']==read(maps['research/protocol.json']['archive'])['research_question']
assert prot['secondary_population_hypothesis'] is None
oldreceipt=subprocess.check_output([git,'show','25f7110f37de57d63521a3ce6b660183fd9e5101:logs/v0.4/delivery_receipt.json'])
assert oldreceipt==(R/'logs/v0.4/delivery_receipt.json').read_bytes()
# No unexpected changes to any owner-reviewed scientific path.
changes=subprocess.check_output([git,'diff','--name-only','61b4c2c63cbad6c1b9bd99168e33d1367aa180bc','--','src','configs','experiments','docs/v0.4','logs/v0.4'],text=True).splitlines()
assert all('/v0.5/' in p or '/v05_' in p or p=='logs/v0.4/delivery_receipt.json' for p in changes),changes
result=dict(status='PASS',verified_old_manifest_files=len(verified),old_custody=verified,advanced_aliases_preserved=len(maps),historical_registry_prefix_records=71,total_registry_records=73,actual_new_sampler_invocations=1,new_fit_acceptance='PASS',original_failed_case_retained='FAIL',direct_math_grid_points=12,direct_math_gradient_coordinates=48,run_source_blob_counts=source_counts,tests_passed=59,score_propagation_status=score['numerical_policy_result'],max_approximate_upper_score_mcse=max(b['approximate_upper_quantile_score_mcse_cycles'] for b in score['batch_size_results']),protocol_status='PROTOCOL_DRAFTED',owner_final_authorization=False,official_test_access=False,confirmatory=False,environment_fingerprint=pre['environment_fingerprint'],dataset_fingerprint=pre['dataset_sha256'],plan_fingerprint=pre['plan_sha256'])
(R/'logs/v0.5/closure_qc.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='old_custody'}))
