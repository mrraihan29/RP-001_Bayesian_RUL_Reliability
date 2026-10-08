from pathlib import Path
import json,hashlib,subprocess
from datetime import datetime,timezone
R=Path('.');git=r'C:\Program Files\Git\cmd\git.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((R/'logs/v0.4/delivery_manifest.json').read_text(encoding='utf8'))
known=set(subprocess.check_output([git,'ls-files'],text=True).splitlines())
new=set(subprocess.check_output([git,'ls-files','--others','--exclude-standard'],text=True).splitlines())
paths=known|new|{f['path'] for f in before['files']}
excluded={'logs/v0.5/delivery_manifest.json','logs/v0.5/delivery_receipt.json'}
paths-=excluded
files=[]
for p in sorted(paths):
    f=R/p
    assert f.is_file(),p
    files.append(dict(path=p,bytes=f.stat().st_size,sha256=sha(f),available_in_git_snapshot=p in known|new))
fit=json.loads((R/'experiments/v0.5/registry/v05_highrho_innovation.json').read_text(encoding='utf8'));demo=json.loads((R/'experiments/v0.5/registry/v05_score_propagation.json').read_text(encoding='utf8'))
manifest=dict(version='0.5',created_at=datetime.now(timezone.utc).isoformat(),owner_reviewed_scientific_commit='61b4c2c63cbad6c1b9bd99168e33d1367aa180bc',preexecution_plan_source_commit=fit['git_commit'],score_demo_source_commit=demo['git_commit'],recommendation='READY FOR OWNER LOCK REVIEW',protocol_status='PROTOCOL_DRAFTED',owner_final_authorization=False,official_test_sensors_accessed=False,official_test_labels_accessed=False,confirmatory_evaluation=False,fallback_activated=False,new_sampler_invocations=1,tests_passed=59,environment_fingerprint=fit['environment_fingerprint'],dataset_fingerprint=fit['dataset_sha256'],split_fingerprint=fit['split_manifest_sha256'],frozen_plan_fingerprint=fit['plan_sha256'],registered_new_scientific_CPU_seconds=fit['cpu_seconds']+demo['cpu_seconds'],timing_scope='Fit and saved-draw demo timers excluding imports/preflight/tests/packaging; no OS-wide total',scientific_payload_bytes=sum(p.stat().st_size for p in (R/'experiments/v0.5').rglob('*') if p.is_file()),original_scientific_baseline_manifest_sha256=sha(R/'logs/v0.4/delivery_manifest.json'),verified_old_manifest_count=537,current_registry_records=73,historical_prefix_unchanged=71,self_and_postcommit_receipt_excluded=sorted(excluded),files=files,note='Snapshot bytes/custody, not universal scientific validation. Final fullGitcommit and manifesthash in separate frozen administrative receipt. Historical ignored payloads local and bound; no protected archive member opened.')
(R/'logs/v0.5/delivery_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
assert not any(Path(p).name.startswith(('test_FD','RUL_FD')) or p.lower().endswith(('.zip','.key','.pem')) or '/data/raw/train_' in '/'+p for p in new|known)
print(json.dumps(dict(manifest_files=len(files),manifest_sha256=sha(R/'logs/v0.5/delivery_manifest.json'),new_bytes=sum((R/p).stat().st_size for p in new),historical_local_only=sum(not f['available_in_git_snapshot'] for f in files))))
