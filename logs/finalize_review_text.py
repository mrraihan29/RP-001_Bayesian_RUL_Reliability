from pathlib import Path
import json
import hashlib
ROOT = Path(__file__).resolve().parents[1]
def load(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8-sig"))
def save(rel, obj): (ROOT/rel).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
# These draft documents were reviewed above; original proposal and audit snapshots are untouched.
replacements = {
    "docs/08_risks_assumptions_decisions.md": [
        ("Asia/Jakarta,8 October2026", "Asia/Jakarta, 8 October 2026"),
        ("Outcome-independent cutoff", "Outcome-blind deterministic cutoff"),
        ("at56 final engines", "at 56 final engines"),
        ("error.4-chain", "error. Four-chain"),
        ("|100 test engines", "| 100 test engines"),
        ("|Calibration25 engine", "| Calibration on 25 engine"),
        ("Exact rank24", "Exact rank 24"),
        ("|Future features", "| Future features"),
        ("outcome-blind30..250", "outcome-blind 30–250"),
        ("counts43/13/25", "counts 43/13/25"),
        ("conformal90%", "conformal 90%"),
        ("|5 score-cycles", "| 5 score-cycles"),
        ("proposed32 CPU-hours/10GiB", "proposed 32 CPU-hours/10 GiB"),
        ("StageA", "Stage A"), ("StageB", "Stage B"),
        ("section18", "section 18"),
        ("implemented model and numerical checks", "implemented model and implementation-specific numerical checks"),
        ("Completed: G0,", "Completed: fixed-parameter numerical equation checks, G0,")
    ],
    "docs/09_methodology_audit.md": [
        ("completed8 October2026", "completed 8 October 2026"),
        ("fitτ0.50", "fit τ=0.50")
    ],
    "docs/07_compute_feasibility_estimate.md": [
        ("Windows11", "Windows 11"), ("processors,15,78", "processors, 15.78"),
        ("GTX1650 Ti4 GiB", "GTX 1650 Ti (4 GiB)"),
        ("reports3.11.9", "reports 3.11.9"),
        ("interpreter3.12.14", "interpreter 3.12.14"),
        ("fitting43", "fitting 43"), ("refit56", "refit 56"),
        ("β2, γ2, Γ4, Σ_g3, σ_z/σ_r2, ρ1", "β: 2; γ: 2; Γ: 4; Σ_g: 3; σ_z/σ_r: 2; ρ: 1"),
        ("Latent2×N", "Latent 2×N"),
        ("blocks30×30", "blocks 30×30"), ("joint31×31", "joint 31×31"),
        ("around56×30³=1,512", "around 56×30³=1.512"),
        ("sekitar56×30³=1,512", "sekitar 56×30³=1.512"),
        ("CQR12 configurations", "CQR 12 configurations"),
        ("Planning5–30", "Planning 5–30"),
        ("Principal4-chain", "Principal 4-chain"),
        ("Planning0,25–3", "Planning 0.25–3"),
        ("Planning2–12", "Planning 2–12"),
        ("Planning8–24", "Planning 8–24"),
        ("Proposed32", "Proposed 32"),
        ("hours;10 GiB", "hours; 10 GiB"),
        ("Prefer2 chains", "Prefer 2 chains"),
        ("if4-chain", "if 4-chain"), ("still4 independent", "still 4 independent"),
        ("proposed<10", "proposed <10"), ("exceeds32", "exceeds 32"),
        ("A4GiB", "A 4 GiB"), ("CPython3.11/3.12", "CPython 3.11/3.12")
    ],
    "README.md": [
        ("October2026", "October 2026"), ("audit:100 engines,20631", "audit: 100 engines, 20,631"),
        ("split55/15/30", "split 55/15/30"), ("cutoff30..250 gives43/13/25", "cutoff 30–250 gives 43/13/25"),
        ("cohort56", "cohort 56"), ("CPython3.12.14", "CPython 3.12.14"), ("Python>=3.11", "Python >=3.11"),
        ("ColabPro", "Colab Pro"), ("StageA", "Stage A"), ("StageB", "Stage B"), ("section18", "section 18")
    ]
}
for rel, pairs in replacements.items():
    p=ROOT/rel
    value=p.read_text(encoding="utf-8")
    for old, new in pairs: value=value.replace(old, new)
    p.write_text(value,encoding="utf-8")
p=ROOT/"docs/00_research_lead_review.md"
value=p.read_text(encoding="utf-8")
value=value.replace("Tidak ada hasil perbandingan model.", "Tidak ada hasil perbandingan model. Pemeriksaan numerik persamaan conditioning Gaussian lulus pada 12 kasus fixed-parameter (history 1/2/30, termasuk correlation negatif/tinggi), bersama interval score, rank conformal, Wilson precision, dan arah bootstrap-t. Ini bukan synthetic parameter recovery atau validasi sampler; log tersimpan di logs/mathematical_preflight.json.")
p.write_text(value,encoding="utf-8")
handoff=load("docs/research_lead_handoff.json")
# The suite schema uses registered skill IDs; human roles remain explicit separately.
handoff["producer"]="scientific-research-engine"
handoff["consumer"]="scientific-research-engine"
handoff["producer_role"]="Rei research lead acting as scientific governor"
handoff["consumer_role"]="Scientific governor receives the review draft for owner decision; human recipient Raihan"
handoff["human_recipient"]="Raihan research owner"
handoff["artifact_identity"]["sha256_or_version"]=hashlib.sha256(p.read_bytes()).hexdigest()
handoff["evidence"].append({
    "evidence_id":"E-MATH",
    "kind":"numerical-equation-verification",
    "location":"logs/mathematical_preflight.json",
    "collected_at":"2026-10-08",
    "method":"Independent precision-form conditional calculation and joint-density identity at fixed parameters",
    "supports":"draft algebra and precision calculations only",
    "provenance_chain":"tests/verify_protocol_mathematics.py -> logs/mathematical_preflight.json"
})
save("docs/research_lead_handoff.json",handoff)
print(json.dumps({"patched_documents":list(replacements),"human_recipient":handoff["human_recipient"],
                  "equation_checks":"PASS; scientific validation deferred"}))
