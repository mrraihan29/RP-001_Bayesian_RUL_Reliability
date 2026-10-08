"""Storage-only reconstruction of the v0.4 precision-validation artifact.

This script consumes the 600 raw replication records retained by the original
failed registry. It never samples, resamples, or reinvokes the validation
runner. The original registry is copied byte-for-byte to an archive before any
recovery registry is written.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from rp001.v04_precision_validation import (  # noqa: E402
    _load_and_validate_plan,
    _sha256,
    _summarize_group,
)

ORIGINAL_REGISTRY = Path("experiments/v0.4/registry/v04_precision_validation.json")
RECOVERY_REGISTRY = Path(
    "experiments/v0.4/registry/v04_precision_validation_storage_recovery.json"
)
RESULT_PATH = Path(
    "experiments/v0.4/precision/v04_precision_mcse_validation.json"
)
ARCHIVE_PATH = Path(
    "logs/v0.4/archive/v04_precision_validation_original_failed_registry.json"
)
HELPER_PATH = Path("logs/v0.4/recover_precision_serialization.py")
EXPECTED_COMMIT = "ba44bc1c3e4a155a704eec9afce932757b6d4fa9"
EXPECTED_COUNTS = {0.0: 200, 0.8: 200, 0.95: 200}
PROBABILITIES = (0.05, 0.5, 0.95)
BATCH_SIZES = (250, 500)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=False, allow_nan=False) + "\n").encode("utf-8")


def _canonical_raw_bytes(records: list[dict[str, Any]]) -> bytes:
    """Stable canonical representation used only for the raw-record digest."""
    return json.dumps(
        records, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _validate_original_and_records(
    original: dict[str, Any], records: list[dict[str, Any]]
) -> None:
    if original.get("status") != "failed_with_retained_partial_records":
        raise RuntimeError("the original registry is not the retained failed attempt")
    if original.get("error_type") != "FileNotFoundError":
        raise RuntimeError("the retained failure is not the expected serialization-path error")
    if len(records) != 600 or original.get("partial_record_count") != 600:
        raise RuntimeError("the retained raw-record count is not exactly 600")

    provenance = original["shared_v04_common_provenance"]
    if provenance["git_commit"].lower() != EXPECTED_COMMIT:
        raise RuntimeError("the original scientific run does not match the frozen commit")
    if original["git_snapshot"]["frozen_commit"].lower() != EXPECTED_COMMIT:
        raise RuntimeError("the original runner identity does not match the frozen commit")

    expected_keys = {
        (rho_index, replication_index + 1)
        for rho_index in range(3)
        for replication_index in range(200)
    }
    observed_keys: set[tuple[int, int]] = set()
    for row in records:
        key = (int(row["rho_index"]), int(row["replication"]))
        if key in observed_keys:
            raise RuntimeError(f"duplicate retained replication identity: {key}")
        observed_keys.add(key)
        if row["rho"] != (0.0, 0.8, 0.95)[key[0]]:
            raise RuntimeError(f"rho/index mismatch in retained record: {key}")
    if observed_keys != expected_keys:
        raise RuntimeError("retained records do not cover the frozen 3 x 200 design")

    for relative, expected_sha in original["executed_source_sha256"].items():
        current = ROOT / relative
        if not current.is_file() or _sha256(current.read_bytes()) != expected_sha:
            raise RuntimeError(f"original executed source has changed: {relative}")


def _build_groups(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for rho in (0.0, 0.8, 0.95):
        rho_records = [row for row in records if row["rho"] == rho]
        if len(rho_records) != EXPECTED_COUNTS[rho]:
            raise RuntimeError(f"rho={rho} has an unexpected retained record count")
        for probability in PROBABILITIES:
            for batch_size in BATCH_SIZES:
                groups.append(
                    _summarize_group(
                        rho_records,
                        rho=rho,
                        probability=probability,
                        batch_size=batch_size,
                    )
                )
    if len(groups) != 18:
        raise RuntimeError("reconstructed summary does not contain exactly 18 groups")
    return groups


def _write_new(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def recover() -> dict[str, Any]:
    start_utc = datetime.now(timezone.utc)
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    original_path = ROOT / ORIGINAL_REGISTRY
    original_bytes = original_path.read_bytes()
    original_sha = hashlib.sha256(original_bytes).hexdigest()
    original = json.loads(original_bytes)
    records = original.get("partial_raw_records")
    if not isinstance(records, list):
        raise RuntimeError("original failed registry does not contain raw records")
    _validate_original_and_records(original, records)

    plan, plan_metadata = _load_and_validate_plan()
    if plan_metadata["plan_sha256"] != original["frozen_plan_sha256"]:
        raise RuntimeError("current frozen plan differs from the original run registry")
    config = plan_metadata["validation_config"]
    raw_sha = hashlib.sha256(_canonical_raw_bytes(records)).hexdigest()
    groups = _build_groups(records)

    recovery_commit = _git("rev-parse", "HEAD").lower()
    helper_bytes = (ROOT / HELPER_PATH).read_bytes()
    helper_sha = hashlib.sha256(helper_bytes).hexdigest()
    committed_helper = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{recovery_commit}:{HELPER_PATH.as_posix()}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout
    if committed_helper != helper_bytes:
        raise RuntimeError("storage recovery helper must be committed before execution")

    result_abs = ROOT / RESULT_PATH
    recovery_registry_abs = ROOT / RECOVERY_REGISTRY
    archive_abs = ROOT / ARCHIVE_PATH
    for path in (result_abs, recovery_registry_abs, archive_abs):
        if path.exists():
            raise FileExistsError(f"Preserving existing artifact; refusing overwrite: {path}")

    # Preserve the failed registry byte-for-byte before writing any new status.
    _write_new(archive_abs, original_bytes)
    archive_sha = hashlib.sha256(archive_abs.read_bytes()).hexdigest()
    if archive_sha != original_sha:
        raise RuntimeError("archived original registry bytes do not match")

    preparation_wall = float(time.perf_counter() - wall_start)
    preparation_cpu = float(time.process_time() - cpu_start)
    prepared_utc = datetime.now(timezone.utc)
    storage_recovery = {
        "mode": "storage_only_raw_record_reconstruction",
        "resampling_performed": False,
        "validation_runner_reinvoked": False,
        "original_failed_registry_path": ORIGINAL_REGISTRY.as_posix(),
        "original_failed_registry_sha256": original_sha,
        "archived_original_registry_path": ARCHIVE_PATH.as_posix(),
        "archived_original_registry_sha256": archive_sha,
        "raw_record_count": len(records),
        "raw_records_sha256_canonical_json": raw_sha,
        "recovery_commit": recovery_commit,
        "recovery_helper_path": HELPER_PATH.as_posix(),
        "recovery_helper_sha256": helper_sha,
        "prepared_utc": prepared_utc.isoformat(),
        "preparation_wall_seconds": preparation_wall,
        "preparation_process_cpu_seconds": preparation_cpu,
        "preparation_runtime_scope": (
            "Includes input verification, digesting, and deterministic group-summary reconstruction; "
            "excludes result and registry serialization/fsync."
        ),
    }

    source_identity = {
        "executed_source_sha256": original["executed_source_sha256"],
        "all_rp001_source_sha256": original["all_rp001_source_sha256"],
    }
    summary = {
        "groups": groups,
        "group_count": len(groups),
        "replication_record_count": len(records),
        "criteria_are_targeted_not_universal": True,
    }
    result_payload: dict[str, Any] = {
        "run_id": "v04_precision_mcse_validation",
        "status": "completed_from_retained_raw_records",
        "classification": "prospective synthetic estimator validation; not FD001 performance evaluation",
        "started_utc": original["started_utc"],
        "finished_utc": prepared_utc.isoformat(),
        "commit_identity": original["git_snapshot"],
        "shared_v04_common_provenance": original["shared_v04_common_provenance"],
        "plan": {
            "path": original["frozen_plan_path"],
            "plan_sha256": original["frozen_plan_sha256"],
            "validation_config": config,
        },
        "source_identity": source_identity,
        "environment": original["environment"],
        "git_snapshot": original["git_snapshot"],
        "target_specification": original["target_specification"],
        "summary": summary,
        "raw_records": records,
        "runtime": original["runtime"],
        "scope": original["scope"],
        "registry_path": RECOVERY_REGISTRY.as_posix(),
        "storage_recovery": storage_recovery,
    }
    result_bytes = _json_bytes(result_payload)
    _write_new(result_abs, result_bytes)
    result_sha = hashlib.sha256(result_bytes).hexdigest()

    total_wall = float(time.perf_counter() - wall_start)
    total_cpu = float(time.process_time() - cpu_start)
    finished_utc = datetime.now(timezone.utc)
    recovery_registry = {
        "run_id": "v04_precision_mcse_validation_storage_recovery",
        "status": "completed",
        "status_interpretation": (
            "The original validation execution completed 600 replications and retained all raw records; "
            "this record documents storage-only reconstruction. The original failed registry remains unchanged."
        ),
        "original_scientific_run_id": "v04_precision_mcse_validation",
        "original_scientific_status": original["status"],
        "original_scientific_error_type": original["error_type"],
        "original_scientific_error_message": original["error_message"],
        "original_scientific_runtime": original["runtime"],
        "original_scientific_commit": original["shared_v04_common_provenance"]["git_commit"],
        "original_scientific_shared_v04_common_provenance": original[
            "shared_v04_common_provenance"
        ],
        "frozen_plan_sha256": original["frozen_plan_sha256"],
        "executed_source_sha256": original["executed_source_sha256"],
        "raw_record_count": len(records),
        "raw_records_sha256_canonical_json": raw_sha,
        "original_registry_path": ORIGINAL_REGISTRY.as_posix(),
        "original_registry_sha256": original_sha,
        "archived_original_registry_path": ARCHIVE_PATH.as_posix(),
        "archived_original_registry_sha256": archive_sha,
        "recovery_commit": recovery_commit,
        "recovery_helper_path": HELPER_PATH.as_posix(),
        "recovery_helper_sha256": helper_sha,
        "recovery_started_utc": start_utc.isoformat(),
        "recovery_finished_utc": finished_utc.isoformat(),
        "recovery_wall_seconds": total_wall,
        "recovery_process_cpu_seconds": total_cpu,
        "recovery_runtime_scope": "Includes archive, deterministic reconstruction, result serialization/fsync; excludes this registry serialization/fsync.",
        "result_artifact": {
            "path": RESULT_PATH.as_posix(),
            "sha256": result_sha,
        },
        "summary": summary,
        "storage_recovery": storage_recovery,
    }
    _write_new(recovery_registry_abs, _json_bytes(recovery_registry))
    return {
        "status": recovery_registry["status"],
        "result_path": str(result_abs),
        "result_sha256": result_sha,
        "registry_path": str(recovery_registry_abs),
        "raw_record_count": len(records),
        "raw_records_sha256_canonical_json": raw_sha,
        "summary": summary,
        "recovery_commit": recovery_commit,
        "recovery_helper_sha256": helper_sha,
        "recovery_wall_seconds": total_wall,
        "recovery_process_cpu_seconds": total_cpu,
    }


if __name__ == "__main__":
    print(json.dumps(recover(), indent=2, allow_nan=False))

