"""Exclusive-create artifacts and chained events for one authorized Stage D attempt."""
from pathlib import Path
import datetime, hashlib, json, subprocess
import numpy as np
R=Path(__file__).resolve().parents[2]
D=R/"docs/stage_D"
O=R/".protected/stage_D/D001"
B=R/".protected/stage_B/B001"
T=R/".protected/stage_B/B001_review_tables"
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()
def default(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)
def read(p):return json.loads(Path(p).read_text(encoding="utf8"))
def save(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("xb") as f:f.write((json.dumps(data,indent=2,allow_nan=False,default=default)+"\n").encode())
def save_text(p,s):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("xb") as f:f.write(s.encode())
def save_npz(p,**arrays):
    with Path(p).open("xb") as f:np.savez_compressed(f,**arrays)
def git(*args):return subprocess.check_output(["git","-C",str(R),*args],text=True).strip()
def check(ok,msg):
    if not bool(ok):raise ValueError(msg)
def event(kind,**data):
    paths=sorted((O/"events").glob("*.json"))
    i=len(paths)+1
    save(O/f"events/{i:06d}.json",dict(event=i,at_utc=now(),kind=kind,
        previous_sha256=sha(paths[-1]) if paths else None,**data))
def failure(exc,phase):
    event("FAILURE",phase=phase,failure_type=type(exc).__name__)
    save(O/f"failures/{len(list((O/'failures').glob('*.json')))+1:06d}.json",
        dict(at_utc=now(),phase=phase,type=type(exc).__name__,message=str(exc),
        prediction_repair=False,primary_status="UNAVAILABLE"))
def source_check():
    plan=read(R/"configs/stage_D_execution_plan.json")
    for p,h in plan["prelabel_source_sha256"].items():check(sha(R/p)==h,"Frozen Stage D source mismatch: "+p)
    check(sha(D/"OWNER_STAGE_D_AUTHORIZATION.md")==plan["owner_authorization_sha256"],"Owner source identity")
    return plan
