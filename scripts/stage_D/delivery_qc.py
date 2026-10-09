"""Delivery QC: rehash protected seal, journals, prior snapshots, public allowlist."""
import datetime,hashlib,json,subprocess
from pathlib import Path
R=Path.cwd();D=R/"docs/stage_D";O=R/".protected/stage_D/D001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(p,x):
    with p.open("xb") as f:f.write((json.dumps(x,indent=2,allow_nan=False)+"\n").encode())
def git(*a):return subprocess.check_output(["git",*a],text=True).strip()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt=read(D/"PROTECTED_COMPLETION_RECEIPT.json")
manifest=O/"PROTECTED_RESULT_MANIFEST.json";assert sha(manifest)==receipt["protected_manifest_sha256"]
members=read(manifest)["files"]
paths=set()
for row in members:
    p=R/row["path"];assert p.resolve().is_relative_to(O.resolve())
    assert p.stat().st_size==row["bytes"] and sha(p)==row["sha256"];paths.add(p.resolve())
assert {p.resolve() for p in O.rglob("*") if p.is_file()}==paths|{manifest.resolve()}
events=sorted((O/"events").glob("*.json"));previous=None;labels_begin=None
for i,p in enumerate(events,1):
    e=read(p);assert e["event"]==i and e["previous_sha256"]==previous;previous=sha(p)
    if e["kind"]=="LABEL_ACCESS_BEGIN":labels_begin=e["at_utc"]
assert labels_begin and read(O/"PRE_LABEL_RECEIPT.json")["at_utc"]<labels_begin
assert not list((O/"failures").glob("*.json"))
seed=read(O/"FAILURE_LEDGER_INITIAL.json");assert seed["failures"]==[] and seed["at_utc"]<labels_begin
candidate=read(R/"docs/stage_B/CANDIDATE_PACKAGE_RECEIPT.json")
protected_counts={}
for key in ("base_payload_manifest","verification_manifest","review_tables_manifest"):
    record=candidate[key];p=R/record["path"];assert sha(p)==record["sha256"]
    folder=p.parent;inventory=set()
    for row in read(p)["files"]:
        q=folder/row["name"] if key=="review_tables_manifest" else R/row["path"]
        assert sha(q)==row["sha256"] and q.stat().st_size==row["bytes"];inventory.add(q.resolve())
    assert {q.resolve() for q in folder.rglob("*") if q.is_file()}==inventory|{p.resolve()}
    protected_counts[key]=len(inventory)
c_manifest=R/".protected/stage_C/C001/STAGE_C_VERIFICATION_MANIFEST.json"
assert sha(c_manifest)=="072f7937ab0ca845cad3804352aac3afb791db4f46a36a5516995b30ef11a5cd"
for row in read(c_manifest)["files"]:assert sha(R/row["path"])==row["sha256"]
baseline="62892ff054a967daa28f5314dbd2e5981f902268"
tree=git("ls-tree","-r",baseline).splitlines()
rows=[]
for line in tree:
    spec,path=line.split("\t",1);mode,kind,obj=spec.split();assert kind=="blob";rows.append((path,obj))
hashes=subprocess.check_output(["git","hash-object","--no-filters","--stdin-paths"],
    input="".join(p+"\n" for p,h in rows),text=True).splitlines()
assert len(hashes)==len(rows)
assert all(a==h for (p,h),a in zip(rows,hashes))
changed=git("diff","--name-status",baseline).splitlines()
assert all(x.startswith("A\t") for x in changed)
pending=git("status","--porcelain").splitlines()
assert all(x[3:].startswith(("docs/stage_D/","scripts/stage_D/")) for x in pending)
assert git("check-ignore",".protected/stage_D/D001/PRIMARY_EVALUATION.json")
assert not any(p.startswith(".protected/") or (p.startswith("data/raw/") and p.lower().endswith("rul_fd001.txt")) for p in git("ls-files").splitlines())
safe_docs=["PROTECTED_COMPLETION_RECEIPT.json","CURRENT_PROTECTED_PHASE_STATUS.json",
    "research_lead_handoff.json","README.md","STAGE_D_ADMINISTRATIVE_COMPLETION_REPORT.md"]
prohibited=("paired_difference_cycles","coverage_count","RUL_cycles","mean_interval_score_cycles",
    "median_MAE_cycles","median_RMSE_cycles","label_kink","engines_flagged","approximate_upper_quantile_score_mcse_cycles")
for name in safe_docs:
    s=(D/name).read_text();assert not any(k in s for k in prohibited),(name,"restricted metric marker")
sourceplan=read(R/"configs/stage_D_execution_plan.json")
for path,h in sourceplan["prelabel_source_sha256"].items():assert sha(R/path)==h
save(D/"STRUCTURAL_VALIDATION.json",dict(at_utc=now,handoff="PASS",native_scientific_status="PROTOCOL_LOCKED",
    native_hard_failures=[],scope="Structural validation only; independent scientific evidence is protected"))
save(D/"PUBLIC_PACKAGE_QC.json",dict(at_utc=now,status="PASS",public_policy="Administrative/code/fingerprints only; no restricted outcome payload",
    original_baseline_commit=baseline,all_baseline_tracked_bytes_preserved=len(rows),protected_manifest_rehash_PASS=True,
    protected_manifest_sha256=sha(manifest),protected_members_rehashed=len(members),D_event_chain_PASS=True,
    prelabel_receipt_and_failure_seed_precede_label_access=True,accepted_B_inventory_counts=protected_counts,
    accepted_C_manifest_unchanged=True,protected_payloads_git_ignored=True,public_admin_metric_marker_scan="PASS",
    prelabel_sources_unchanged=True,scientific_results_publicly_released=False,raw_labels_or_predictions_staged=False))
public=[p for folder in ("docs/stage_D","scripts/stage_D","tests/stage_D") for p in sorted((R/folder).glob("*"))
    if p.is_file()]+[R/"configs/stage_D_execution_plan.json"]
save(D/"PUBLIC_DELIVERY_MANIFEST.json",dict(at_utc=now,status="ADMINISTRATIVE_CODE_DELIVERY_ONLY",
    files=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in public],
    excludes="self and later post-commit administrative Git receipt",
    protected_results_uploaded=False,protected_manifest_sha256=sha(manifest)))
print(json.dumps(dict(QC="PASS",original_tracked_bytes_preserved=len(rows),
    sealed_protected_member_count=len(members),public_manifest_member_count=len(public),
    public_scientific_results=False),indent=2))
