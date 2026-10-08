"""Final review-package checks and artifact identities. No model or held-out data access."""
from __future__ import annotations
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8-sig"))
required_dirs = ["docs", "literature", "data/raw", "data/interim", "data/processed",
                 "src", "notebooks", "configs", "experiments", "results", "figures",
                 "tests", "manuscript", "logs"]
assert all((ROOT/p).is_dir() for p in required_dirs)
required_docs = [
 "01_literature_gap_novelty_review.md", "02_dataset_feasibility_sample_precision.md",
 "03_candidate_mathematical_model.md", "04_statistical_analysis_plan.md",
 "05_fair_comparator_design.md", "06_proposed_protocol_lock.md",
 "07_compute_feasibility_estimate.md", "08_risks_assumptions_decisions.md"]
assert all((ROOT/"docs"/p).stat().st_size > 2000 for p in required_docs)
source_expected = "4ff06a6cf6f7a699dcbb9c66a76bfe6e21d60b64bc738c345e3b08c1f5118346"
assert sha(ROOT/"docs/proposal_v0.1.md") == source_expected
for entry in load("logs/methodology_audit_inputs.json")["documents"]:
    assert sha(ROOT/entry["path"]) == entry["sha256"]
train = load("data/raw/training_audit.json")
assert (train["engines"], train["rows"], train["fields"]) == (100, 20631, 26)
assert train["unique_engine_cycle"] and train["complete_monotone_cycles"]
assert train["nonfinite"] == 0 and not train["official_test_files_read"]
assert not train["calibration_residuals_computed"]
assert sha(ROOT/"data/raw/train_FD001.txt") == train["raw_sha256"]
assert sha(ROOT/"data/raw/NASA_CMAPSS_original.zip") == "c9c5dec12a945a82e8bb4446589d7fb3cc057b5e5d81fa1a12e25ee9912ad3b2"
splits = load("configs/proposed_split_manifest.json")
assert len(splits) == 100 and len({r["engine"] for r in splits}) == 100
assigned = Counter(r["role"] for r in splits)
eligible = Counter(r["role"] for r in splits if r["eligible_alive"])
assert assigned == {"fit":55, "tune":15, "calibration":30}
assert eligible == {"fit":43, "tune":13, "calibration":25}
assert all(30 <= r["proposed_cutoff"] <= 250 for r in splits)
lock = load("configs/protocol_lock_record.json")
assert not lock["stage_a_approved"] and not lock["stage_b_approved"] and lock["locked_at"] is None
assert sha(ROOT/"configs/proposed_protocol_v0.2.json") == lock["proposed_protocol_sha256"]
assert sha(ROOT/"configs/proposed_split_manifest.json") == lock["proposed_split_sha256"]
assert load("research/protocol.json")["status"] == "PROTOCOL_DRAFTED"
assert not (ROOT/"research/experiment_registry.jsonl").read_text(encoding="utf-8").strip()
assert load("logs/research_validation.json")["hard_failures"] == []
assert load("logs/handoff_validation.json")["result"] == "PASS"
assert load("logs/mathematical_preflight.json")["status"] == "PASS"
assert sha(ROOT/"tests/verify_protocol_mathematics.py") == load("logs/mathematical_preflight.json")["script_sha256"]
handoff = load("docs/research_lead_handoff.json")
assert sha(ROOT/handoff["artifact_identity"]["path_or_uri"]) == handoff["artifact_identity"]["sha256_or_version"]
# Physical absence of extracted official test/RUL files within project.
protected = [p.relative_to(ROOT).as_posix() for p in (ROOT/"data").rglob("*")
             if p.is_file() and re.match(r"(?i)(test_FD|RUL_FD)", p.name)]
assert not protected
# Markdown relative-link check; internet links are evidence references, not local files.
broken_links = []
for p in [ROOT/"README.md", *[ROOT/"docs"/d for d in required_docs]]:
    for target in re.findall(r"\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
        if "://" in target or target.startswith("#"):
            continue
        local = target.split("#",1)[0]
        if not (p.parent/local).exists():
            broken_links.append({"source":p.relative_to(ROOT).as_posix(),"target":target})
assert not broken_links
# Inventory excludes self-referential manifests and cache/Git internals.
excluded = {"research/artifact_map.csv", "research/state_manifest.json", "logs/delivery_verification.json"}
artifact_rows = []
for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(ROOT)
    path = rel.as_posix()
    if path in excluded or any(part in {".git", ".venv", "__pycache__"} for part in rel.parts):
        continue
    kind = "review" if rel.parts[0] == "docs" else (
        "dataset-source-or-metadata" if rel.parts[0] == "data" else rel.parts[0])
    artifact_rows.append({"artifact_id":f"A{len(artifact_rows)+1:04d}", "artifact_type":kind,
                          "path":path, "claim_ids":"", "generated_by":"RP001-preimplementation-review",
                          "sha256":sha(p)})
with (ROOT/"research/artifact_map.csv").open("w",encoding="utf-8",newline="") as stream:
    writer=csv.DictWriter(stream,fieldnames=["artifact_id","artifact_type","path","claim_ids","generated_by","sha256"])
    writer.writeheader()
    writer.writerows(artifact_rows)
result = {"status":"PASS", "scope":"Review delivery integrity; scientific and sampling validation deferred",
          "mandatory_documents":required_docs, "required_directories_verified":len(required_dirs),
          "source_proposal_byte_identity":True, "prior_audit_inputs_verified":5,
          "training":{"engines":100,"rows":20631,"fields":26},
          "proposed_assigned":dict(assigned), "eligible":dict(eligible),
          "protected_test_files_extracted":protected,
          "access_policy_limitation":"Archive contains test label bytes; no cryptographic separation",
          "cutoff_correction":"Historical training audit wording independent is superseded by docs/02 outcome-blind proxy qualification",
          "protocol_status":"PROTOCOL_DRAFTED","owner_approvals":False,
          "model_fitting_performed":False,"confirmatory_experiment_count":0,
          "equation_checks":"PASS","static_draft_validation":"PASS","handoff_schema":"PASS",
          "artifact_inventory_count":len(artifact_rows), "broken_local_links":broken_links}
(ROOT/"logs/delivery_verification.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,indent=2))
