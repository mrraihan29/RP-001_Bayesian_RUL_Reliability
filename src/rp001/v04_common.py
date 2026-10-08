"""Executed-source and environment provenance for v0.4 scientific runs."""
import hashlib,json,platform,subprocess,sys,importlib.metadata
from datetime import datetime,timezone
from pathlib import Path
from .data import ROOT
PLAN_PATH=ROOT/'configs/v0.4/remediation_plan.json'
PLAN=json.loads(PLAN_PATH.read_text())
ENV_PATH=ROOT/'logs/pilot_environment.json'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,allow_nan=False,default=lambda x:x.tolist())+'\n',encoding='utf8')
def provenance():
    git=r'C:\Program Files\Git\cmd\git.exe'
    commit=subprocess.check_output([git,'-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    sources={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted((ROOT/'src/rp001').glob('*.py'))}
    env=json.loads(ENV_PATH.read_text())
    live={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    assert live==env['packages'], 'Installed packages changed from environment fingerprint'
    keys=['python','implementation','platform','packages','float_dtype','sampler','blas_threads']
    canonical={k:env[k] for k in keys}
    fingerprint=hashlib.sha256(json.dumps(canonical,sort_keys=True).encode()).hexdigest()
    dirty=subprocess.check_output([git,'-C',str(ROOT),'status','--porcelain','--','src/rp001','configs/v0.4'],text=True).strip()
    if dirty: raise RuntimeError('Scientific execution requires committed source/plan: '+dirty)
    return dict(created_at=datetime.now(timezone.utc).isoformat(),git_commit=commit,source_dirty=False,
        executed_source_sha256=sources,plan_sha256=sha(PLAN_PATH),environment_fingerprint=fingerprint,
        dataset_sha256=sha(ROOT/'data/raw/train_FD001.txt'),confirmatory=False,official_test_access=False)