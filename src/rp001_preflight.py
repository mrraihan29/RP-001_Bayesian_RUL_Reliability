"""RP-001 pre-model feasibility audit. Never reads official test or RUL label files."""
from pathlib import Path
import hashlib, json, math, statistics, sys
from datetime import datetime
from statistics import NormalDist
import importlib.util
ROOT = Path(__file__).resolve().parents[1]
raw = ROOT / "data/raw/train_FD001.txt"
groups = {}
payloads = set()
duplicate_keys = []
rows = 0
for line in raw.read_text(encoding="ascii").splitlines():
    if not line.strip():
        continue
    parts = line.split()
    if len(parts) != 26:
        raise ValueError(f"expected 26 fields at row {rows+1}, got {len(parts)}")
    values = list(map(float, parts))
    if not all(math.isfinite(x) for x in values):
        raise ValueError("nonfinite input")
    unit, cycle = int(values[0]), int(values[1])
    if unit != values[0] or cycle != values[1] or cycle < 1:
        raise ValueError("invalid identity/cycle")
    groups.setdefault(unit, []).append((cycle, values[2:]))
    key = (unit, cycle)
    if key in payloads:
        duplicate_keys.append(key)
    payloads.add(key)
    rows += 1
assert not duplicate_keys
assert len(groups) == 100
assert set(groups) == set(range(1,101))
for unit, records in groups.items():
    cycles = [r[0] for r in records]
    assert cycles == list(range(1, max(cycles)+1))
lifetimes = {unit: max(r[0] for r in records) for unit, records in groups.items()}
sensor_ranges = {}
for j in range(21):
    vals = [r[1][j+3] for records in groups.values() for r in records]
    sensor_ranges[f"s{j+1}"] = {"min":min(vals),"max":max(vals),"variance":statistics.pvariance(vals)}
seed = "RP001-20261008-v0.2"
def digest(tag, unit):
    return hashlib.sha256(f"{seed}|{tag}|{unit}".encode()).hexdigest()
ordered = sorted(groups, key=lambda unit:digest("split", unit))
roles = {unit:("fit" if k < 55 else "tune" if k < 70 else "calibration") for k,unit in enumerate(ordered)}
manifest = []
for unit in sorted(groups):
    # One ex-ante pseudo-cutoff independent of lifetime. Never redraw failures.
    cutoff = 30 + int(digest("cutoff",unit),16) % 221
    eligible = lifetimes[unit] > cutoff
    manifest.append({"dataset":"FD001_train","engine":unit,"role":roles[unit],
                     "proposed_cutoff":cutoff,"eligible_alive":eligible})
role_counts = {role:{"assigned":sum(x["role"]==role for x in manifest),
                    "eligible":sum(x["role"]==role and x["eligible_alive"] for x in manifest)}
               for role in ("fit","tune","calibration")}
profile = {"audit_date":"2026-10-08","scope":"FD001 official training only",
 "raw_sha256":hashlib.sha256(raw.read_bytes()).hexdigest(),
 "rows":rows,"engines":len(groups),"fields":26,
 "unique_engine_cycle":True,"complete_monotone_cycles":True,"nonfinite":0,
 "lifetimes":{"min":min(lifetimes.values()),"max":max(lifetimes.values()),
              "median":statistics.median(lifetimes.values())},
 "sensor_ranges":sensor_ranges,"proposed_design":role_counts,
 "cutoff_generator":"single independent hash-based DiscreteUniform approximation over 30..250, reject C>=T; no redraw",
 "official_test_files_read":False,"calibration_residuals_computed":False,
 "limits":["training IDs and test IDs are separate namespaces; equal numeric IDs are not shared engines",
           "no cross train-test duplicate or test-schema audit yet",
           "modulo reduction negligible hash-uniform approximation, deterministic not an experimental randomization guarantee"]}
z = NormalDist().inv_cdf(0.975)
def wilson(k,n):
    p=k/n
    den=1+z*z/n
    ctr=(p+z*z/(2*n))/den
    rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [ctr-rad,ctr+rad]
caln=role_counts["calibration"]["eligible"]
precision = {"calculation_date":"2026-10-08","n_test_planned":100,
 "coverage_90_of_100_wilson95":wilson(90,100),
 "coverage_expected_se_if_p_0_9":math.sqrt(.9*.1/100),
 "coverage_n_normal_approx_halfwidth_0_02":math.ceil(z*z*.9*.1/.02**2),
 "coverage_n_normal_approx_halfwidth_0_05":math.ceil(z*z*.9*.1/.05**2),
 "standardized_paired_mde_80pct_one_sided_0_05_normal_approx":(NormalDist().inv_cdf(.95)+NormalDist().inv_cdf(.80))/10,
 "score_precision_scenarios":[{"sd_difference_cycles":sd,"two_sided95_halfwidth_t99_approx":1.9842169515*sd/10,
                              "mde80_one_sided_cycles_normal_approx":(NormalDist().inv_cdf(.95)+NormalDist().inv_cdf(.8))*sd/10}
                             for sd in [10,20,40,80]],
 "conformal_rank_scenarios":[{"n":n,"rank":math.ceil((n+1)*.9),
                            "rank_fraction":math.ceil((n+1)*.9)/(n+1),
                            "granularity":1/(n+1),"finite":math.ceil((n+1)*.9)<=n}
                           for n in sorted(set([8,9,19,20,30,caln]))],
 "assumptions":["engine Bernoulli independence for Wilson interpretation","all power numbers are planning approximations, not observed power",
                "paired MDE does not establish SESOI","score SD unknown; no model fit or actual scores used"]}
env = {"python_version":sys.version,"executable":sys.executable,
       "available_without_install":{pkg:importlib.util.find_spec(pkg) is not None
                                  for pkg in ["numpy","scipy","pandas","pymc","arviz","statsmodels","sklearn","matplotlib","pytest"]}}
for rel,obj in [("data/raw/training_audit.json",profile),("configs/proposed_split_manifest.json",manifest),
                ("logs/sample_precision.json",precision),("logs/python_capabilities.json",env)]:
    target=ROOT/rel
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps(obj,indent=2),encoding="utf8")
print(json.dumps({"profile":{k:v for k,v in profile.items() if k!="sensor_ranges"},
                  "precision":precision,"environment":env},indent=2))
