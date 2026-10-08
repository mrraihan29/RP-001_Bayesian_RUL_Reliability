"""Frozen synthetic paired bootstrap-t run entry for RP-001 v0.4.

Callable, but gated on a committed frozen plan and executed source snapshot.
This entry writes results only when explicitly called after the parent signal.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rp001 import v04_inference as inference  # noqa: E402

PLAN_RELATIVE_PATH = Path("configs/v0.4/remediation_plan.json")
PLAN_SCENARIOS = (
    "normal",
    "lognormal1",
    "lognormal1p5",
    "t3",
    "rare_outlier",
    "t1p5",
    "sparse_discrete",
    "all_zero",
)
PLAN_TO_IMPLEMENTATION_SCENARIO = dict(zip(PLAN_SCENARIOS, inference.SCENARIOS, strict=True))
RESULT_RELATIVE_PATH = Path("experiments/v0.4/inference/v04_paired_bootstrap_t_oc.json")
REGISTRY_RELATIVE_PATH = Path("experiments/v0.4/registry/v04_inference_oc.json")
RUN_ID = "v04_inference_oc_500x1999_n100_seed50001"


def _sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    return completed.stdout.strip()


def _load_frozen_plan(root: Path) -> tuple[dict[str, Any], bytes]:
    plan_path = root / PLAN_RELATIVE_PATH
    raw = plan_path.read_bytes()
    plan = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(plan, dict):
        raise ValueError("Frozen remediation plan must be a JSON object")
    if plan.get("prospectively_frozen_before_new_scientific_runs") is not True:
        raise RuntimeError("The remediation plan is not marked prospectively frozen")
    for key in ("official_test_sensors_authorized", "official_test_labels_authorized", "confirmatory_authorized"):
        if plan.get(key) is not False:
            raise RuntimeError(f"Synthetic inference OC requires {key}=false")

    design = plan.get("inference_simulation")
    if not isinstance(design, dict):
        raise ValueError("Frozen plan has no inference_simulation object")
    if tuple(design.get("scenarios", ())) != PLAN_SCENARIOS:
        raise RuntimeError("Frozen plan scenario names/order differ from the reviewed eight-family design")
    expected = {"n": 100, "replications": 500, "bootstrap_count": 1999, "seed": 50001}
    observed = {key: design.get(key) for key in expected}
    if observed != expected:
        raise RuntimeError(f"Frozen synthetic OC settings differ from the authorized run: {observed!r}")
    if len(inference.SCENARIOS) != len(PLAN_SCENARIOS):
        raise RuntimeError("Implementation and frozen plan scenario counts differ")
    return plan, raw


def _committed_git_snapshot(root: Path, plan_bytes: bytes, common_commit: str) -> dict[str, Any]:
    head = _git(root, "rev-parse", "HEAD")
    if head != common_commit:
        raise RuntimeError("Shared provenance helper and runner observed different Git HEAD commits")
    committed_plan = subprocess.run(
        ["git", "show", f"HEAD:{PLAN_RELATIVE_PATH.as_posix()}"],
        cwd=root, check=True, capture_output=True,
    ).stdout
    if committed_plan != plan_bytes:
        raise RuntimeError("Working-tree plan bytes do not match the committed frozen plan")
    scoped_status = _git(root, "status", "--porcelain=v1", "--untracked-files=all", "--", "src/rp001", "configs/v0.4")
    if scoped_status:
        raise RuntimeError("Shared sources or frozen plan are dirty; commit them before scientific execution")
    return {
        "head_commit": head,
        "branch": _git(root, "branch", "--show-current"),
        "scientific_sources_and_plan_clean_at_run_start": True,
        "full_worktree_status_porcelain_v1": _git(root, "status", "--porcelain=v1", "--untracked-files=all"),
        "plan_git_blob_oid": _git(root, "rev-parse", f"HEAD:{PLAN_RELATIVE_PATH.as_posix()}"),
    }


def _ensure_new_paths(root: Path) -> tuple[Path, Path]:
    result_path = root / RESULT_RELATIVE_PATH
    registry_path = root / REGISTRY_RELATIVE_PATH
    if result_path.exists():
        raise FileExistsError(f"Preserving existing run output; refusing overwrite: {result_path}")
    if registry_path.exists():
        raise FileExistsError(f"Preserving existing run registry; refusing overwrite: {registry_path}")
    return result_path, registry_path


def _write_json_new(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=False, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def _build_seed_map(seed: int) -> tuple[dict[str, int], list[dict[str, Any]]]:
    seeds: dict[str, int] = {}
    assignments: list[dict[str, Any]] = []
    for index, plan_name in enumerate(PLAN_SCENARIOS):
        implementation_name = PLAN_TO_IMPLEMENTATION_SCENARIO[plan_name]
        root_seed = seed + index
        seeds[implementation_name] = root_seed
        assignments.append({
            "scenario_index": index,
            "frozen_plan_name": plan_name,
            "implementation_name": implementation_name,
            "root_seed": root_seed,
        })
    return seeds, assignments


def run_inference_oc(project_root: str | Path | None = None) -> dict[str, Any]:
    """Execute the frozen 500 x 1999 synthetic OC and register every replicate.

    The 20,000-draw bootstrap described for a future official-benchmark
    secondary diagnostic is separate and is not run by this synthetic OC.
    """
    root = Path(project_root).resolve() if project_root is not None else PROJECT_ROOT
    result_path, registry_path = _ensure_new_paths(root)
    plan, plan_bytes = _load_frozen_plan(root)

    from rp001 import v04_common  # Lazy: provenance is evaluated only on explicit run.

    common_provenance = v04_common.provenance()
    plan_hash = _sha256_bytes(plan_bytes)
    if common_provenance["plan_sha256"] != plan_hash:
        raise RuntimeError("Shared provenance and runner disagree on the frozen plan SHA-256")
    git_snapshot = _committed_git_snapshot(root, plan_bytes, common_provenance["git_commit"])
    source_hashes = common_provenance["executed_source_sha256"]
    runner_rel = "src/rp001/v04_inference_run.py"
    inference_rel = "src/rp001/v04_inference.py"
    if runner_rel not in source_hashes or inference_rel not in source_hashes:
        raise RuntimeError("Shared provenance omitted an executed inference source file")
    explicit_source_hashes = {runner_rel: source_hashes[runner_rel], inference_rel: source_hashes[inference_rel]}
    env_path = Path(v04_common.ENV_PATH)
    environment = {
        "fingerprint": common_provenance["environment_fingerprint"],
        "metadata_path": env_path.relative_to(root).as_posix(),
        "metadata_sha256": _sha256_file(env_path),
    }
    design = plan["inference_simulation"]
    seeds, seed_assignments = _build_seed_map(int(design["seed"]))
    config = inference.OperatingCharacteristicsConfig(
        n=int(design["n"]),
        nsim=int(design["replications"]),
        bootstrap_count=int(design["bootstrap_count"]),
        scenario_seeds=seeds,
        numerical_policy=inference.NumericalPolicy(
            quantile_method="linear",
            resampling_chunk_size=256,
            dtype="float64",
            zero_standard_error_policy="invalidate_replicate_if_any_zero",
            nonfinite_policy="invalidate_replicate",
        ),
    )
    _ensure_new_paths(root)

    started_utc = datetime.now(timezone.utc).isoformat()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    try:
        raw_result = inference.run_operating_characteristics(config)
    except Exception as exc:
        failure_record: dict[str, Any] = {
            "run_id": RUN_ID,
            "status": "worker_execution_failed",
            "started_utc": started_utc,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "frozen_plan_sha256": plan_hash,
            "executed_source_sha256": explicit_source_hashes,
            "all_rp001_source_sha256": source_hashes,
            "git_snapshot": git_snapshot,
            "environment": environment,
            "dataset_sha256": common_provenance["dataset_sha256"],
            "runtime": {
                "wall_seconds": float(time.perf_counter() - wall_start),
                "process_cpu_seconds": float(time.process_time() - cpu_start),
            },
            "configuration": {
                "n": config.n,
                "replications_per_scenario": config.nsim,
                "bootstrap_count_per_dataset": config.bootstrap_count,
                "scenario_seed_assignments_in_frozen_order": seed_assignments,
            },
            "result_artifact": None,
            "failure_retained": True,
        }
        _write_json_new(registry_path, failure_record)
        raise
    wall_seconds = time.perf_counter() - wall_start
    cpu_seconds = time.process_time() - cpu_start
    finished_utc = datetime.now(timezone.utc).isoformat()

    failure_count = int(raw_result["failure_counts"]["failed_or_unavailable"])
    status = "completed_with_retained_replicate_failures" if failure_count else "completed"
    provenance = {
        "run_id": RUN_ID,
        "status": status,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "frozen_plan_path": PLAN_RELATIVE_PATH.as_posix(),
        "frozen_plan_sha256": plan_hash,
        "executed_source_sha256": explicit_source_hashes,
        "all_rp001_source_sha256": source_hashes,
        "git_snapshot": git_snapshot,
        "environment": environment,
        "dataset_sha256": common_provenance["dataset_sha256"],
        "configuration": {
            "n": config.n,
            "replications_per_scenario": config.nsim,
            "bootstrap_count_per_dataset": config.bootstrap_count,
            "scenario_seed_assignments_in_frozen_order": seed_assignments,
            "numerical_policy": raw_result["configuration"]["numerical_policy"],
            "future_official_benchmark_secondary_bootstrap_count": 20000,
            "future_official_benchmark_secondary_bootstrap_status": "not run; separate plan item requiring owner lock/authorization",
        },
        "runtime": {
            "scientific_execution_wall_seconds": float(wall_seconds),
            "scientific_execution_process_cpu_seconds": float(cpu_seconds),
        },
        "scope": {
            "synthetic_only": True,
            "official_test_sensors_read": False,
            "official_test_labels_read": False,
            "confirmatory": False,
            "primary_benchmark_effect": "exact finite-benchmark stored-prediction mean; not evaluated by this run",
            "bootstrap_role": "secondary conditional synthetic operating-characteristic diagnostic",
        },
        "failure_counts": raw_result["failure_counts"],
        "scenario_results": raw_result["results_by_scenario"],
    }
    result_payload = {"provenance": provenance, "operating_characteristics": raw_result}
    _write_json_new(result_path, result_payload)
    result_hash = _sha256_file(result_path)
    registry_record = {
        **provenance,
        "result_artifact": {
            "path": RESULT_RELATIVE_PATH.as_posix(),
            "sha256": result_hash,
            "replicate_records": len(raw_result["simulation_records"]),
        },
        "registry_path": REGISTRY_RELATIVE_PATH.as_posix(),
    }
    _write_json_new(registry_path, registry_record)
    return registry_record


def main() -> int:
    record = run_inference_oc()
    print(json.dumps({
        "run_id": record["run_id"],
        "status": record["status"],
        "result_artifact": record["result_artifact"],
        "failure_counts": record["failure_counts"],
        "runtime": record["runtime"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
