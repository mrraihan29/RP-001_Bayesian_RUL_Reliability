"""Prospective synthetic validation runner for the v0.4 quantile MCSE estimator.

This module has no import-time execution. The full run requires an explicit
parent-frozen Git commit and verifies that the plan and source bytes match it.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import norm

from rp001.v04_precision import estimate_mixture_quantile_mcse


ROOT = Path(__file__).resolve().parents[2]
PLAN_RELATIVE = Path("configs/v0.4/remediation_plan.json")
RUNNER_RELATIVE = Path("src/rp001/v04_precision_validation.py")
PRECISION_RELATIVE = Path("src/rp001/v04_precision.py")
RESULT_RELATIVE_PATH = Path("experiments/v0.4/precision/v04_precision_mcse_validation.json")
REGISTRY_RELATIVE_PATH = Path("experiments/v0.4/registry/v04_precision_validation.json")

# Fixed simulator constants specified for the conjugate validation target.
PRIOR_MEAN = 0.0
PRIOR_VARIANCE = 1.0
SENSOR_VALUE = 1.0
SENSOR_VARIANCE = 1.0
PREDICTIVE_INTERCEPT = float(np.log(100.0))
PREDICTIVE_THETA_COEFFICIENT = 0.2
PREDICTIVE_RESIDUAL_SD = 0.3
QUANTILE_PROBABILITIES = (0.05, 0.5, 0.95)
WILSON_CONFIDENCE_LEVEL = 0.95
RMS_MCSE_RATIO_RANGE = (0.75, 1.33)
MINIMUM_NORMAL_INTERVAL_COVERAGE = 0.90


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def _git_bytes(commit: str, relative_path: Path) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{commit}:{relative_path.as_posix()}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout


def _git_text(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _validate_frozen_identity(frozen_commit: str) -> dict[str, Any]:
    if not isinstance(frozen_commit, str) or len(frozen_commit) != 40:
        raise ValueError("frozen_commit must be the full 40-character Git commit hash")
    if any(ch not in "0123456789abcdefABCDEF" for ch in frozen_commit):
        raise ValueError("frozen_commit must be hexadecimal")

    head = _git_text("rev-parse", "HEAD").lower()
    supplied = frozen_commit.lower()
    if head != supplied:
        raise RuntimeError(
            f"working HEAD {head} does not match supplied frozen commit {supplied}"
        )

    tracked_paths = {
        PLAN_RELATIVE: ROOT / PLAN_RELATIVE,
        RUNNER_RELATIVE: ROOT / RUNNER_RELATIVE,
        PRECISION_RELATIVE: ROOT / PRECISION_RELATIVE,
    }
    committed_hashes: dict[str, str] = {}
    for relative, local_path in tracked_paths.items():
        try:
            committed_bytes = _git_bytes(supplied, relative)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"frozen commit does not contain required source: {relative.as_posix()}"
            ) from exc
        local_bytes = local_path.read_bytes()
        if committed_bytes != local_bytes:
            raise RuntimeError(
                f"working file differs from frozen commit: {relative.as_posix()}"
            )
        committed_hashes[relative.as_posix()] = _sha256(committed_bytes)

    return {
        "frozen_commit": supplied,
        "working_head": head,
        "source_hashes_sha256": committed_hashes,
        "working_tree_dirty": bool(_git_text("status", "--porcelain")),
    }


def _load_and_validate_plan() -> tuple[dict[str, Any], dict[str, Any]]:
    path = ROOT / PLAN_RELATIVE
    plan_bytes = path.read_bytes()
    plan = json.loads(plan_bytes)
    validation = plan["precision"]["MCSE_estimator_validation"]

    expected = {
        "replications_per_rho": 200,
        "rho": [0.0, 0.8, 0.95],
        "chains": 4,
        "draws": 2000,
        "seed": 48001,
    }
    observed = {
        "replications_per_rho": validation["replications_per_rho"],
        "rho": [float(rho) for rho in validation["rho"]],
        "chains": validation["chains"],
        "draws": validation["draws"],
        "seed": validation["seed"],
    }
    if observed != expected:
        raise RuntimeError(
            f"frozen precision validation settings differ from the requested design: {observed}"
        )
    if plan.get("prospectively_frozen_before_new_scientific_runs") is not True:
        raise RuntimeError("the remediation plan is not marked prospectively frozen")

    quantiles = tuple(float(p) for p in plan["precision"]["quantiles"])
    if quantiles != QUANTILE_PROBABILITIES:
        raise RuntimeError(f"unexpected frozen quantiles: {quantiles}")
    batch_sizes = tuple(int(b) for b in plan["precision"]["batch_sizes"])
    if batch_sizes != (250, 500):
        raise RuntimeError(f"unexpected frozen batch sizes: {batch_sizes}")
    tail_probability = float(plan["precision"]["upper_mcse_tail_probability"])
    expected_tail = 0.05 / (25 * 3 * 2)
    if not np.isclose(tail_probability, expected_tail, rtol=0.0, atol=1e-18):
        raise RuntimeError(f"unexpected frozen upper-MCSE tail probability: {tail_probability}")

    config = {
        **observed,
        "quantiles": list(quantiles),
        "batch_sizes": list(batch_sizes),
        "upper_mcse_tail_probability": tail_probability,
        "rms_error_to_rms_mcse_ratio_range": list(RMS_MCSE_RATIO_RANGE),
        "minimum_normal_interval_coverage": MINIMUM_NORMAL_INTERVAL_COVERAGE,
        "wilson_confidence_level": WILSON_CONFIDENCE_LEVEL,
    }
    return plan, {
        "plan_sha256": _sha256(plan_bytes),
        "validation_config": config,
    }


def _simulate_stationary_base_chains(
    *,
    rho: float,
    chains: int,
    draws: int,
    base_seed: int,
    rho_index: int,
    replication_index: int,
) -> tuple[np.ndarray, list[list[int]]]:
    """Draw independent stationary Gaussian AR(1) chains from the prior."""
    replication_seed = np.random.SeedSequence(
        [base_seed, rho_index, replication_index]
    )
    chain_seeds = replication_seed.spawn(chains)
    theta = np.empty((chains, draws), dtype=np.float64)

    innovation_sd = np.sqrt(PRIOR_VARIANCE * (1.0 - rho**2))
    stationary_sd = np.sqrt(PRIOR_VARIANCE)
    for chain_index, chain_seed in enumerate(chain_seeds):
        rng = np.random.default_rng(chain_seed)
        theta[chain_index, 0] = rng.normal(PRIOR_MEAN, stationary_sd)
        innovations = rng.normal(size=draws - 1)
        for draw_index, innovation in enumerate(innovations, start=1):
            theta[chain_index, draw_index] = (
                PRIOR_MEAN
                + rho * (theta[chain_index, draw_index - 1] - PRIOR_MEAN)
                + innovation_sd * innovation
            )

    spawn_keys = [list(seed.spawn_key) for seed in chain_seeds]
    return theta, spawn_keys


def _wilson_interval(successes: int, trials: int) -> list[float]:
    if trials <= 0 or successes < 0 or successes > trials:
        raise ValueError("Wilson interval requires 0 <= successes <= trials and trials > 0")
    z = float(norm.ppf(0.5 + WILSON_CONFIDENCE_LEVEL / 2.0))
    proportion = successes / trials
    z2 = z**2
    denominator = 1.0 + z2 / trials
    center = (proportion + z2 / (2.0 * trials)) / denominator
    half_width = (
        z
        * np.sqrt(
            proportion * (1.0 - proportion) / trials
            + z2 / (4.0 * trials**2)
        )
        / denominator
    )
    return [float(center - half_width), float(center + half_width)]


def _summarize_group(
    records: list[dict[str, Any]],
    *,
    rho: float,
    probability: float,
    batch_size: int,
) -> dict[str, Any]:
    errors = np.asarray(
        [record["quantiles"][str(probability)]["error_cycles"] for record in records],
        dtype=np.float64,
    )
    mcse = np.asarray(
        [
            record["quantiles"][str(probability)]["batch_results"][str(batch_size)][
                "quantile_rul_mcse"
            ]
            for record in records
        ],
        dtype=np.float64,
    )
    upper_mcse = np.asarray(
        [
            record["quantiles"][str(probability)]["batch_results"][str(batch_size)][
                "approximate_upper_quantile_rul_mcse"
            ]
            for record in records
        ],
        dtype=np.float64,
    )
    if not np.all(np.isfinite(errors)) or not np.all(np.isfinite(mcse)):
        raise RuntimeError("validation group contains nonfinite errors or MCSE values")
    if not np.all(np.isfinite(upper_mcse)):
        raise RuntimeError("validation group contains undefined/nonfinite approximate upper MCSE")

    rms_error = float(np.sqrt(np.mean(errors**2)))
    rms_mcse = float(np.sqrt(np.mean(mcse**2)))
    rms_upper_mcse = float(np.sqrt(np.mean(upper_mcse**2)))
    ratio = rms_error / rms_mcse if rms_mcse > 0.0 else None
    upper_ratio = rms_error / rms_upper_mcse if rms_upper_mcse > 0.0 else None

    normal_covered = np.abs(errors) <= 1.96 * mcse
    upper_covered = np.abs(errors) <= 1.96 * upper_mcse
    normal_successes = int(normal_covered.sum())
    upper_successes = int(upper_covered.sum())
    n = len(errors)
    normal_coverage = normal_successes / n
    upper_coverage = upper_successes / n

    ratio_pass = (
        ratio is not None
        and RMS_MCSE_RATIO_RANGE[0] <= ratio <= RMS_MCSE_RATIO_RANGE[1]
    )
    coverage_pass = normal_coverage >= MINIMUM_NORMAL_INTERVAL_COVERAGE
    return {
        "rho": float(rho),
        "probability": float(probability),
        "batch_size": int(batch_size),
        "replications": n,
        "rms_actual_error_cycles": rms_error,
        "rms_estimated_mcse_cycles": rms_mcse,
        "rms_actual_error_over_rms_estimated_mcse": ratio,
        "empirical_1p96_mcse_coverage": normal_coverage,
        "empirical_1p96_mcse_coverage_successes": normal_successes,
        "empirical_1p96_mcse_coverage_wilson95": _wilson_interval(
            normal_successes, n
        ),
        "rms_approximate_upper_mcse_cycles": rms_upper_mcse,
        "rms_actual_error_over_rms_approximate_upper_mcse": upper_ratio,
        "empirical_1p96_approximate_upper_mcse_coverage": upper_coverage,
        "empirical_1p96_approximate_upper_mcse_coverage_successes": upper_successes,
        "empirical_1p96_approximate_upper_mcse_coverage_wilson95": _wilson_interval(
            upper_successes, n
        ),
        "plan_criterion_checks": {
            "rms_ratio_in_range_0p75_to_1p33": bool(ratio_pass),
            "normal_interval_coverage_at_least_0p90": bool(coverage_pass),
            "both": bool(ratio_pass and coverage_pass),
            "interpretation": (
                "Targeted validation criteria for this conjugate design; they do "
                "not certify universal MCSE calibration."
            ),
        },
    }


def _run_one_replication(
    *,
    rho: float,
    rho_index: int,
    replication_index: int,
    chains: int,
    draws: int,
    base_seed: int,
    batch_sizes: tuple[int, int],
    tail_probability: float,
) -> dict[str, Any]:
    theta, chain_spawn_keys = _simulate_stationary_base_chains(
        rho=rho,
        chains=chains,
        draws=draws,
        base_seed=base_seed,
        rho_index=rho_index,
        replication_index=replication_index,
    )
    log_weights = norm.logpdf(
        SENSOR_VALUE,
        loc=theta,
        scale=np.sqrt(SENSOR_VARIANCE),
    )
    predictive_means = PREDICTIVE_INTERCEPT + PREDICTIVE_THETA_COEFFICIENT * theta
    predictive_variances = np.full_like(
        theta, PREDICTIVE_RESIDUAL_SD**2, dtype=np.float64
    )
    input_digest = _sha256(
        theta.tobytes(order="C")
        + log_weights.tobytes(order="C")
        + predictive_means.tobytes(order="C")
        + predictive_variances.tobytes(order="C")
    )

    posterior_mean = (
        PRIOR_MEAN / PRIOR_VARIANCE + SENSOR_VALUE / SENSOR_VARIANCE
    ) / (1.0 / PRIOR_VARIANCE + 1.0 / SENSOR_VARIANCE)
    posterior_variance = 1.0 / (
        1.0 / PRIOR_VARIANCE + 1.0 / SENSOR_VARIANCE
    )
    predictive_log_mean = (
        PREDICTIVE_INTERCEPT + PREDICTIVE_THETA_COEFFICIENT * posterior_mean
    )
    predictive_log_variance = (
        PREDICTIVE_THETA_COEFFICIENT**2 * posterior_variance
        + PREDICTIVE_RESIDUAL_SD**2
    )

    quantile_records: dict[str, Any] = {}
    for probability in QUANTILE_PROBABILITIES:
        exact_log_quantile = float(
            predictive_log_mean
            + np.sqrt(predictive_log_variance) * norm.ppf(probability)
        )
        exact_rul_quantile = float(np.exp(exact_log_quantile))
        estimate = estimate_mixture_quantile_mcse(
            means=predictive_means,
            variances=predictive_variances,
            log_weights=log_weights,
            probability=probability,
            tail_probability=tail_probability,
            batch_sizes=batch_sizes,
        )
        batch_results = {
            str(batch["batch_size"]): batch
            for batch in estimate["batch_size_results"]
        }
        quantile_records[str(probability)] = {
            "exact_log_rul_quantile": exact_log_quantile,
            "exact_rul_quantile_cycles": exact_rul_quantile,
            "estimated_log_rul_quantile": estimate["quantile_log_rul"],
            "estimated_rul_quantile_cycles": estimate["quantile_rul"],
            "error_cycles": (
                float(estimate["quantile_rul"]) - exact_rul_quantile
            ),
            "mixture_cdf_residual": estimate["mixture_cdf_residual"],
            "weighted_mixture_density_log_rul": estimate[
                "weighted_mixture_density_log_rul"
            ],
            "weight_ess": estimate["weight_ess"],
            "max_normalized_importance_weight": estimate[
                "max_normalized_importance_weight"
            ],
            "influence_ess_by_batch_size": {
                str(batch["batch_size"]): batch["influence_ess"]
                for batch in estimate["batch_size_results"]
            },
            "batch_results": batch_results,
            "batch_size_stability": estimate["batch_size_stability"],
            "finite_checks": estimate["finite_checks"],
        }

    return {
        "rho": float(rho),
        "rho_index": int(rho_index),
        "replication": int(replication_index + 1),
        "seed_identity": {
            "base_seed": int(base_seed),
            "rho_index": int(rho_index),
            "replication_index_zero_based": int(replication_index),
            "chain_spawn_keys": chain_spawn_keys,
            "bit_generator": "PCG64",
        },
        "input_arrays_sha256": input_digest,
        "quantiles": quantile_records,
    }


def _software_environment() -> dict[str, Any]:
    packages = {}
    for package in ("numpy", "scipy", "threadpoolctl"):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None

    try:
        from threadpoolctl import threadpool_info

        blas_pools = threadpool_info()
    except ImportError:
        blas_pools = None

    return {
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "packages": packages,
        "thread_environment": {
            key: os.environ.get(key)
            for key in (
                "OPENBLAS_NUM_THREADS",
                "OMP_NUM_THREADS",
                "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
            )
        },
        "blas_pools": blas_pools,
    }


def _write_json_new(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, sort_keys=False, allow_nan=False) + chr(10)
    with path.open("x", encoding="utf-8", newline=chr(10)) as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def _write_json_replace(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    encoded = json.dumps(payload, indent=2, sort_keys=False, allow_nan=False) + chr(10)
    with temporary.open("x", encoding="utf-8", newline=chr(10)) as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _ensure_new_paths(root: Path) -> tuple[Path, Path]:
    result_path = root / RESULT_RELATIVE_PATH
    registry_path = root / REGISTRY_RELATIVE_PATH
    if result_path.exists():
        raise FileExistsError(f"Preserving existing result; refusing overwrite: {result_path}")
    if registry_path.exists():
        raise FileExistsError(f"Preserving existing registry; refusing overwrite: {registry_path}")
    return result_path, registry_path


def run_precision_mcse_validation(
    frozen_commit: str,
    *,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run the frozen 200-replicate validation only after parent commit freeze.

    The caller must provide the full frozen Git commit. The function refuses to
    run unless HEAD and the committed plan plus precision source bytes match.
    It pre-registers the run, preserves a failure record if execution aborts,
    and refuses to overwrite either result or registry artifacts.
    """
    root = ROOT.resolve()
    result_path, registry_path = _ensure_new_paths(root)
    commit_identity = _validate_frozen_identity(frozen_commit)
    plan, plan_metadata = _load_and_validate_plan()
    validation = plan["precision"]["MCSE_estimator_validation"]
    config = plan_metadata["validation_config"]
    rhos = [float(value) for value in validation["rho"]]
    batch_sizes = tuple(config["batch_sizes"])
    tail_probability = float(config["upper_mcse_tail_probability"])

    from rp001 import v04_common

    common_provenance = v04_common.provenance()
    if common_provenance["git_commit"].lower() != commit_identity["frozen_commit"]:
        raise RuntimeError("shared v04 provenance and runner disagree on the frozen commit")
    if common_provenance["plan_sha256"] != plan_metadata["plan_sha256"]:
        raise RuntimeError("shared v04 provenance and runner disagree on the frozen plan hash")

    source_hashes = common_provenance["executed_source_sha256"]
    required_sources = (RUNNER_RELATIVE.as_posix(), PRECISION_RELATIVE.as_posix())
    if any(relative not in source_hashes for relative in required_sources):
        raise RuntimeError("shared v04 provenance omitted a precision source file")
    executed_source_hashes = {relative: source_hashes[relative] for relative in required_sources}

    environment_path = Path(v04_common.ENV_PATH)
    environment = {
        "fingerprint": common_provenance["environment_fingerprint"],
        "metadata_path": environment_path.relative_to(root).as_posix(),
        "metadata_sha256": _file_sha256(environment_path),
        "live_runtime": _software_environment(),
    }
    git_snapshot = {
        **commit_identity,
        "branch": _git_text("branch", "--show-current"),
        "full_worktree_status_porcelain_v1": _git_text(
            "status", "--porcelain=v1", "--untracked-files=all"
        ),
        "scientific_sources_and_plan_clean": not bool(
            _git_text(
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
                "--",
                "src/rp001",
                "configs/v0.4",
            )
        ),
    }

    destination = Path(output_path) if output_path is not None else root / RESULT_RELATIVE_PATH
    if not destination.is_absolute():
        destination = root / destination
    destination = destination.resolve()
    try:
        destination.relative_to(root)
    except ValueError as exc:
        raise ValueError("output_path must stay inside the RP-001 project") from exc
    if destination != result_path.resolve():
        if destination.exists():
            raise FileExistsError(f"Preserving existing result; refusing overwrite: {destination}")
        result_path = destination
    if registry_path.exists():
        raise FileExistsError(f"Preserving existing registry; refusing overwrite: {registry_path}")

    started = datetime.now(timezone.utc)
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    registry_record: dict[str, Any] = {
        "run_id": "v04_precision_mcse_validation",
        "status": "registered_running",
        "started_utc": started.isoformat(),
        "frozen_plan_path": PLAN_RELATIVE.as_posix(),
        "frozen_plan_sha256": plan_metadata["plan_sha256"],
        "executed_source_sha256": executed_source_hashes,
        "all_rp001_source_sha256": source_hashes,
        "shared_v04_common_provenance": common_provenance,
        "git_snapshot": git_snapshot,
        "environment": environment,
        "configuration": config,
        "target_specification": {
            "base_theta_distribution": {"mean": PRIOR_MEAN, "variance": PRIOR_VARIANCE},
            "sensor_likelihood": {
                "sensor_value": SENSOR_VALUE,
                "variance": SENSOR_VARIANCE,
            },
            "predictive_log_rul": {
                "mean_formula": "log(100) + 0.2 * theta",
                "residual_sd": PREDICTIVE_RESIDUAL_SD,
                "exact_marginal_mean": float(np.log(100.0) + 0.1),
                "exact_marginal_variance": 0.11,
            },
        },
        "scope": {
            "synthetic_only": True,
            "official_test_sensors_read": False,
            "official_test_labels_read": False,
            "confirmatory": False,
            "uses_training_data_values": False,
        },
        "runtime": {
            "scientific_execution_wall_seconds": None,
            "scientific_execution_process_cpu_seconds": None,
        },
        "result_artifact": {
            "path": result_path.relative_to(root).as_posix(),
            "sha256": None,
        },
    }
    _write_json_new(registry_path, registry_record)

    raw_records: list[dict[str, Any]] = []
    try:
        for rho_index, rho in enumerate(rhos):
            for replication_index in range(int(validation["replications_per_rho"])):
                raw_records.append(
                    _run_one_replication(
                        rho=rho,
                        rho_index=rho_index,
                        replication_index=replication_index,
                        chains=int(validation["chains"]),
                        draws=int(validation["draws"]),
                        base_seed=int(validation["seed"]),
                        batch_sizes=batch_sizes,
                        tail_probability=tail_probability,
                    )
                )

        summaries = []
        for rho in rhos:
            rho_records = [record for record in raw_records if record["rho"] == rho]
            for probability in QUANTILE_PROBABILITIES:
                for batch_size in batch_sizes:
                    summaries.append(
                        _summarize_group(
                            rho_records,
                            rho=rho,
                            probability=probability,
                            batch_size=batch_size,
                        )
                    )
        if len(raw_records) != 600 or len(summaries) != 18:
            raise RuntimeError("completed validation record counts differ from the frozen design")

        finished = datetime.now(timezone.utc)
        wall_seconds = float(time.perf_counter() - wall_start)
        cpu_seconds = float(time.process_time() - cpu_start)
        result_payload: dict[str, Any] = {
            "run_id": "v04_precision_mcse_validation",
            "status": "completed",
            "classification": (
                "prospective synthetic estimator validation; not FD001 performance evaluation"
            ),
            "started_utc": started.isoformat(),
            "finished_utc": finished.isoformat(),
            "commit_identity": commit_identity,
            "shared_v04_common_provenance": common_provenance,
            "plan": {
                "path": PLAN_RELATIVE.as_posix(),
                **plan_metadata,
            },
            "source_identity": {
                "executed_source_sha256": executed_source_hashes,
                "all_rp001_source_sha256": source_hashes,
            },
            "environment": environment,
            "git_snapshot": git_snapshot,
            "target_specification": {
                "base_theta_distribution": {
                    "mean": PRIOR_MEAN,
                    "variance": PRIOR_VARIANCE,
                },
                "sensor_likelihood": {
                    "sensor_value": SENSOR_VALUE,
                    "variance": SENSOR_VARIANCE,
                },
                "conjugate_sensor_posterior": {
                    "mean": 0.5,
                    "variance": 0.5,
                },
                "predictive_log_rul": {
                    "mean_formula": "log(100) + 0.2 * theta",
                    "residual_sd": PREDICTIVE_RESIDUAL_SD,
                    "exact_marginal_mean": float(np.log(100.0) + 0.1),
                    "exact_marginal_variance": 0.11,
                },
                "exact_rul_quantile_formula": (
                    "exp(log(100) + 0.1 + sqrt(0.11) * Phi_inverse(p))"
                ),
                "importance_weights": (
                    "Gaussian sensor likelihood p(z=1 | theta), evaluated at stationary "
                    "base-prior AR(1) draws"
                ),
            },
            "summary": {
                "groups": summaries,
                "group_count": len(summaries),
                "replication_record_count": len(raw_records),
                "criteria_are_targeted_not_universal": True,
            },
            "raw_records": raw_records,
            "runtime": {
                "scientific_execution_wall_seconds": wall_seconds,
                "scientific_execution_process_cpu_seconds": cpu_seconds,
            },
            "scope": registry_record["scope"],
            "registry_path": registry_path.relative_to(root).as_posix(),
        }
        result_bytes = (
            json.dumps(result_payload, indent=2, sort_keys=False, allow_nan=False)
            + chr(10)
        ).encode("utf-8")
        with result_path.open("xb") as stream:
            stream.write(result_bytes)
            stream.flush()
            os.fsync(stream.fileno())

        registry_record.update({
            "status": "completed",
            "finished_utc": finished.isoformat(),
            "runtime": result_payload["runtime"],
            "summary": result_payload["summary"],
            "result_artifact": {
                "path": result_path.relative_to(root).as_posix(),
                "sha256": _sha256(result_bytes),
            },
        })
        _write_json_replace(registry_path, registry_record)
        result_payload["output_path"] = str(result_path)
        result_payload["output_sha256"] = _sha256(result_bytes)
        return result_payload
    except Exception as exc:
        registry_record.update({
            "status": "failed_with_retained_partial_records",
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "runtime": {
                "scientific_execution_wall_seconds": float(time.perf_counter() - wall_start),
                "scientific_execution_process_cpu_seconds": float(time.process_time() - cpu_start),
            },
            "partial_record_count": len(raw_records),
            "partial_raw_records": raw_records,
        })
        _write_json_replace(registry_path, registry_record)
        raise