"""Training-only bootstrap and cutoff perturbation builders for RP-001 v0.4.

This module never opens files or fits the Bayesian model. Callers supply the
FD001 training engine arrays. Bootstrap copies are represented as repeated
LandmarkData rows and explicit multiplicities for the same engine IDs.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Literal, Mapping, Sequence

import numpy as np

from .comparators import (
    CQR_CANDIDATES,
    CQR_RANDOM_STATE,
    CandidateFit,
    MedianFit,
    SelectionDecision,
    fit_candidate,
    fit_linear_scaler,
    fit_median_candidate,
    mean90_interval_score,
    predict_endpoints,
    select_candidate,
)
from .data import LandmarkData, features, manifest as load_split_manifest
from .metrics import calibrate, conformal_rank


CANONICAL_HASH_SEED = "RP001-20261008-v0.2"
ROLE_SIZES = {"fit": 55, "tune": 15, "calibration": 30}
MIN_UNIQUE_ELIGIBLE = {"fit": 20, "tune": 5, "calibration": 9}
CUTOFF_MIN = 30
CUTOFF_MAX = 250
CUTOFF_WIDTH = CUTOFF_MAX - CUTOFF_MIN + 1
SENSOR_COLUMN_START = 5
SEQUENCE_LENGTH = 30
ROLE_ORDER = ("fit", "tune", "calibration")
CutoffMode = Literal["canonical", "alternate"]


@dataclass
class BootstrapPipelineData:
    """One paired, training-only resampling and cutoff perturbation."""

    status: Literal["ready", "failed"]
    replicate_id: str
    bootstrap_seed: int
    cutoff_mode: CutoffMode
    metadata: dict[str, Any]
    failure_reasons: tuple[str, ...] = ()
    selection_preprocessor: dict[str, Any] | None = None
    refit_preprocessor: dict[str, Any] | None = None
    fit: LandmarkData | None = None
    tune: LandmarkData | None = None
    refit_fit_tune: LandmarkData | None = None
    calibration: LandmarkData | None = None
    anchor: LandmarkData | None = None
    anchor_features: dict[str, Any] | None = None


@dataclass
class CQRBootstrapResult:
    """Fixed-grid CQR selection/refit/correction for one bootstrap cohort."""

    status: Literal["completed", "failed"]
    selection: SelectionDecision | None = None
    tuning_scores: dict[str, float | None] = field(default_factory=dict)
    candidate_summaries: list[dict[str, Any]] = field(default_factory=list)
    interval_refit: CandidateFit | None = None
    median_refit: MedianFit | None = None
    calibration_correction: float | None = None
    calibration_metadata: dict[str, Any] = field(default_factory=dict)
    failure_reasons: tuple[str, ...] = ()


def _json_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _array_sha256(value: np.ndarray | None) -> str:
    if value is None:
        return _json_sha256({"value": None})
    array = np.ascontiguousarray(np.asarray(value))
    header = json.dumps(
        {"dtype": array.dtype.str, "shape": list(array.shape)},
        sort_keys=True, separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(header + b"\0" + array.tobytes()).hexdigest()


def _normalise_manifest(
    records: Sequence[Mapping[str, Any]],
) -> tuple[dict[int, dict[str, Any]], dict[str, list[int]]]:
    by_engine: dict[int, dict[str, Any]] = {}
    for source in records:
        row = dict(source)
        if row.get("dataset", "FD001_train") != "FD001_train":
            raise ValueError("Only the frozen FD001 training split is accepted.")
        engine = int(row["engine"])
        if engine in by_engine:
            raise ValueError(f"Split manifest repeats engine {engine}.")
        role = str(row["role"])
        if role not in ROLE_SIZES:
            raise ValueError(f"Engine {engine} has unsupported role {role!r}.")
        cutoff = int(row["proposed_cutoff"])
        if not CUTOFF_MIN <= cutoff <= CUTOFF_MAX:
            raise ValueError(f"Engine {engine} has cutoff outside 30..250.")
        by_engine[engine] = {
            "engine": engine,
            "role": role,
            "proposed_cutoff": cutoff,
            "eligible_alive": bool(row["eligible_alive"]),
        }
    if len(by_engine) != 100 or set(by_engine) != set(range(1, 101)):
        raise ValueError("The frozen split must contain training engines 1..100 exactly once.")
    counts = Counter(row["role"] for row in by_engine.values())
    if dict(counts) != ROLE_SIZES:
        raise ValueError(f"Frozen role sizes must be 55/15/30; found {dict(counts)}.")

    ordered = sorted(
        by_engine,
        key=lambda engine: hashlib.sha256(
            f"{CANONICAL_HASH_SEED}|split|{engine}".encode("utf-8")
        ).hexdigest(),
    )
    expected_roles = {
        engine: ("fit" if index < 55 else "tune" if index < 70 else "calibration")
        for index, engine in enumerate(ordered)
    }
    if any(by_engine[engine]["role"] != role for engine, role in expected_roles.items()):
        raise ValueError("Role assignments do not reproduce the frozen v0.3 SHA-256 split.")
    rosters = {
        role: sorted(engine for engine, row in by_engine.items() if row["role"] == role)
        for role in ROLE_ORDER
    }
    return by_engine, rosters


def _validate_training_engines(
    engines: Mapping[int, Sequence[Sequence[float]]],
    by_engine: Mapping[int, Mapping[str, Any]],
) -> tuple[dict[int, np.ndarray], dict[int, int]]:
    if set(map(int, engines)) != set(by_engine):
        raise ValueError("Engine arrays must match the 100 frozen FD001 training IDs exactly.")
    arrays: dict[int, np.ndarray] = {}
    lifetimes: dict[int, int] = {}
    for raw_id, source in engines.items():
        engine = int(raw_id)
        rows = np.asarray(source, dtype=np.float64)
        if rows.ndim != 2 or rows.shape[1] != 26 or rows.shape[0] < 1:
            raise ValueError(f"Engine {engine} must be a nonempty 26-column training matrix.")
        if not np.all(rows[:, 0] == engine):
            raise ValueError(f"Engine key {engine} does not match its engine_id column.")
        cycles = rows[:, 1]
        if (
            not np.isfinite(cycles).all()
            or np.any(cycles != np.floor(cycles))
            or not np.array_equal(cycles, np.arange(1, len(rows) + 1, dtype=np.float64))
        ):
            raise ValueError(f"Engine {engine} cycles must be ordered 1..T.")
        lifetime = int(cycles[-1])
        arrays[engine] = rows
        lifetimes[engine] = lifetime
        canonical = int(by_engine[engine]["proposed_cutoff"])
        expected_alive = canonical < lifetime
        if bool(by_engine[engine]["eligible_alive"]) != expected_alive:
            raise ValueError(f"Engine {engine}: stored canonical eligibility does not equal C<T.")
    return arrays, lifetimes


def _cutoff_record(
    engine: int,
    row: Mapping[str, Any],
    mode: CutoffMode,
    cutoff_salt: str | None,
) -> tuple[int, str, str]:
    if mode == "canonical":
        hash_input = f"{CANONICAL_HASH_SEED}|cutoff|{engine}"
        digest = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
        cutoff = int(row["proposed_cutoff"])
        reproduced = CUTOFF_MIN + int(digest, 16) % CUTOFF_WIDTH
        if cutoff != reproduced:
            raise ValueError(f"Engine {engine}: canonical cutoff does not match its SHA-256 rule.")
        return cutoff, hash_input, digest
    if not isinstance(cutoff_salt, str) or not cutoff_salt.strip() or "|" in cutoff_salt:
        raise ValueError("Alternate cutoff mode requires a nonempty cutoff_salt without '|'.")
    hash_input = f"{CANONICAL_HASH_SEED}|{cutoff_salt}|{engine}"
    digest = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    cutoff = CUTOFF_MIN + int(digest, 16) % CUTOFF_WIDTH
    return cutoff, hash_input, digest


def _stage_metadata(
    *,
    role: str,
    roster: Sequence[int],
    draw_ids: Sequence[int],
    cutoffs: Mapping[int, int],
    lifetimes: Mapping[int, int],
    hash_inputs: Mapping[int, str],
    cutoff_hashes: Mapping[int, str],
    cutoff_mode: CutoffMode,
    cutoff_salt: str | None,
    bootstrap_seed: int,
) -> dict[str, Any]:
    draws = [int(engine) for engine in draw_ids]
    multiplicities = Counter(draws)
    unique_ids = sorted(multiplicities)
    eligibility = {engine: int(cutoffs[engine]) < int(lifetimes[engine]) for engine in unique_ids}
    eligible_unique = [engine for engine in unique_ids if eligibility[engine]]
    eligible_draws = [engine for engine in draws if eligibility[engine]]
    core = {
        "role": role,
        "role_roster_ids": [int(engine) for engine in roster],
        "role_roster_sha256": _json_sha256([int(engine) for engine in roster]),
        "bootstrap_seed": int(bootstrap_seed),
        "bootstrap_algorithm": "numpy.random.Generator(PCG64).choice(sorted role roster, size=role size, replace=True)",
        "numpy_version": np.__version__,
        "bootstrap_draw_ids": draws,
        "bootstrap_draw_ids_sha256": _json_sha256(draws),
        "unique_drawn_ids": unique_ids,
        "multiplicity_by_engine": {str(i): int(multiplicities[i]) for i in unique_ids},
        "multiplicity_sha256": _json_sha256(
            {str(i): int(multiplicities[i]) for i in unique_ids}
        ),
        "cutoff_mode": cutoff_mode,
        "cutoff_salt": cutoff_salt,
        "cutoff_rule_seed": CANONICAL_HASH_SEED,
        "cutoff_hash_input_by_engine": {str(i): hash_inputs[i] for i in unique_ids},
        "cutoff_sha256_by_engine": {str(i): cutoff_hashes[i] for i in unique_ids},
        "cutoff_by_engine": {str(i): int(cutoffs[i]) for i in unique_ids},
        "eligibility_by_engine": {str(i): bool(eligibility[i]) for i in unique_ids},
        "eligible_unique_ids": eligible_unique,
        "eligible_draw_ids": eligible_draws,
        "eligible_unique_count": len(eligible_unique),
        "eligible_multiplicity_count": len(eligible_draws),
        "minimum_unique_eligible": MIN_UNIQUE_ELIGIBLE[role],
        "minimum_passed": len(eligible_unique) >= MIN_UNIQUE_ELIGIBLE[role],
        "no_redraw": True,
        "eligibility_rule": "C<T using the training lifetime; ineligible draws remain recorded and are excluded",
    }
    core["stage_sha256"] = _json_sha256(core)
    return core


def fit_weighted_preprocessor(
    engines: Mapping[int, Sequence[Sequence[float]]],
    cutoffs: Mapping[int, int],
    multiplicities: Mapping[int, int],
) -> dict[str, Any]:
    """Fit v0.3 sign/scale PCA using prefixes and multiplicity/prefix-length weights.

    Each unique engine has total PCA weight proportional to its bootstrap
    multiplicity. Copies are not treated as distinct engine identifiers.
    """
    counts: dict[int, int] = {}
    for raw_engine, raw_count in multiplicities.items():
        if isinstance(raw_count, (bool, np.bool_)) or not isinstance(raw_count, (int, np.integer)):
            raise ValueError("PCA multiplicities must be positive integers.")
        count = int(raw_count)
        if count <= 0:
            raise ValueError("PCA multiplicities must be positive integers.")
        counts[int(raw_engine)] = count
    if not counts:
        raise ValueError("PCA multiplicities must be positive for at least one eligible engine.")
    total_multiplicity = sum(counts.values())
    sensor_rows: list[np.ndarray] = []
    row_weights: list[np.ndarray] = []
    prefix_lengths: list[int] = []
    unique_ids = sorted(counts)
    for engine in unique_ids:
        if engine not in engines or engine not in cutoffs:
            raise ValueError(f"Missing training prefix or cutoff for engine {engine}.")
        cutoff = int(cutoffs[engine])
        rows = np.asarray(engines[engine], dtype=np.float64)
        prefix = rows[rows[:, 1] <= cutoff]
        if len(prefix) != cutoff:
            raise ValueError(f"Engine {engine}: cutoff prefix must contain exactly C rows.")
        sensors = prefix[:, SENSOR_COLUMN_START:]
        if sensors.shape[1] != 21 or not np.isfinite(sensors).all():
            raise ValueError(f"Engine {engine}: prefix sensors must be finite 21-channel values.")
        sensor_rows.append(sensors)
        prefix_lengths.append(cutoff)
        per_row_weight = counts[engine] / (total_multiplicity * cutoff)
        row_weights.append(np.full(cutoff, per_row_weight, dtype=np.float64))

    x = np.vstack(sensor_rows)
    weight = np.concatenate(row_weights)
    mean = np.sum(x * weight[:, None], axis=0)
    sd = np.sqrt(np.sum((x - mean) ** 2 * weight[:, None], axis=0))
    retained = sd > 1e-8
    if not np.any(retained):
        raise ValueError("All fitting-prefix sensor channels have weighted SD<=1e-8.")
    standardized = (x[:, retained] - mean[retained]) / sd[retained]
    covariance = standardized.T @ (standardized * weight[:, None])
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    pc = eigenvectors[:, -1]
    if pc[int(np.argmax(np.abs(pc)))] < 0:
        pc = -pc
    scale = float(np.sqrt(eigenvalues[-1]))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("Weighted fitting-prefix PC1 has zero or invalid variance.")
    ratio = float(eigenvalues[-1] / np.sum(eigenvalues))
    return {
        "mean": mean,
        "sd": sd,
        "retained": retained,
        "pc": pc,
        "pc_scale": scale,
        "fit_ids": np.asarray(unique_ids, dtype=np.int64),
        "fit_multiplicities": np.asarray([counts[i] for i in unique_ids], dtype=np.int64),
        "fit_prefix_lengths": np.asarray(prefix_lengths, dtype=np.int64),
        "fit_weight_sum": float(weight.sum()),
        "pc1_explained_ratio": ratio,
    }


def transform_prefix(
    rows: Sequence[Sequence[float]],
    cutoff: int,
    preprocessor: Mapping[str, np.ndarray],
) -> np.ndarray:
    """Transform only the last at most 30 observed sensor values through C."""
    matrix = np.asarray(rows, dtype=np.float64)
    allowed = matrix[matrix[:, 1] <= int(cutoff)]
    if len(allowed) != int(cutoff):
        raise ValueError("Observed prefix does not contain exactly the requested cycles.")
    sensors = allowed[-min(SEQUENCE_LENGTH, int(cutoff)):, SENSOR_COLUMN_START:]
    retained = np.asarray(preprocessor["retained"], dtype=bool)
    values = (
        (sensors[:, retained] - np.asarray(preprocessor["mean"])[retained])
        / np.asarray(preprocessor["sd"])[retained]
    ) @ np.asarray(preprocessor["pc"]) / float(preprocessor["pc_scale"])
    if values.shape != (SEQUENCE_LENGTH,) or not np.isfinite(values).all():
        raise ValueError("Transformed prefix must be a finite 30-value PC sequence.")
    return values


def _landmark_data(
    engines: Mapping[int, np.ndarray],
    *,
    draw_ids: Sequence[int],
    cutoffs: Mapping[int, int],
    preprocessor: Mapping[str, np.ndarray],
    include_outcomes: bool,
    source: str,
) -> LandmarkData:
    aa: list[list[float]] = []
    zz: list[np.ndarray] = []
    yy: list[float] = []
    ids: list[int] = []
    for engine in draw_ids:
        engine = int(engine)
        cutoff = int(cutoffs[engine])
        rows = engines[engine]
        aa.append([1.0, float(np.log(cutoff / 100.0))])
        zz.append(transform_prefix(rows, cutoff, preprocessor))
        ids.append(engine)
        if include_outcomes:
            rul = int(rows[-1, 1]) - cutoff
            if rul <= 0:
                raise ValueError(f"Engine {engine}: only C<T records may carry an outcome.")
            yy.append(float(np.log(rul)))
    age_basis = np.column_stack(
        (np.ones(SEQUENCE_LENGTH), np.arange(-(SEQUENCE_LENGTH - 1), 1) / 30.0)
    )
    return LandmarkData(
        a=np.asarray(aa, dtype=np.float64).reshape((-1, 2)),
        z=np.asarray(zz, dtype=np.float64).reshape((-1, SEQUENCE_LENGTH)),
        y=np.asarray(yy, dtype=np.float64) if include_outcomes else None,
        ids=np.asarray(ids, dtype=np.int64),
        B=age_basis,
        source=source,
    )


def _preprocessor_sha256(preprocessor: Mapping[str, np.ndarray]) -> str:
    content = {}
    for key in sorted(preprocessor):
        value = np.asarray(preprocessor[key])
        content[key] = {"dtype": value.dtype.str, "shape": list(value.shape), "values": value.tolist()}
    return _json_sha256(content)


def _landmark_sha256(data: LandmarkData) -> str:
    return _json_sha256({
        "a": _array_sha256(data.a),
        "z": _array_sha256(data.z),
        "y": _array_sha256(data.y),
        "ids": _array_sha256(data.ids),
        "B": _array_sha256(data.B),
        "source": data.source,
    })


def _anchor_manifest(
    by_engine: Mapping[int, Mapping[str, Any]],
    lifetimes: Mapping[int, int],
) -> tuple[list[int], dict[int, int], dict[int, str], dict[int, str]]:
    ids = sorted(
        engine for engine, row in by_engine.items()
        if row["role"] == "calibration"
        and int(row["proposed_cutoff"]) < int(lifetimes[engine])
    )
    if len(ids) != 25:
        raise ValueError(f"The fixed v0.3 anchor must contain 25 canonical eligible calibration IDs; found {len(ids)}.")
    cutoffs: dict[int, int] = {}
    hash_inputs: dict[int, str] = {}
    hashes: dict[int, str] = {}
    for engine in ids:
        cutoff, hash_input, digest = _cutoff_record(engine, by_engine[engine], "canonical", None)
        cutoffs[engine] = cutoff
        hash_inputs[engine] = hash_input
        hashes[engine] = digest
    return ids, cutoffs, hash_inputs, hashes


def build_bootstrap_pipeline_data(
    engines: Mapping[int, Sequence[Sequence[float]]],
    bootstrap_seed: int,
    *,
    cutoff_mode: CutoffMode = "canonical",
    cutoff_salt: str | None = None,
    split_manifest: Sequence[Mapping[str, Any]] | None = None,
    input_source_sha256: str | None = None,
) -> BootstrapPipelineData:
    """Build one role-stratified training bootstrap with canonical/alternate cutoffs.

    The same nonnegative bootstrap_seed produces paired role draws in both
    cutoff modes. Alternate salts follow the v0.3 audit rule:
    SEED|cutoff-sensitivity-<salt>|engine (or the same supplied salt string).

    Failure minima count distinct eligible IDs. No failed draw or cutoff is
    redrawn. Successful datasets expand draws in their original bootstrap order.
    """
    if (
        isinstance(bootstrap_seed, (bool, np.bool_))
        or not isinstance(bootstrap_seed, (int, np.integer))
        or bootstrap_seed < 0
    ):
        raise ValueError("bootstrap_seed must be a nonnegative integer.")
    seed = int(bootstrap_seed)
    if cutoff_mode not in ("canonical", "alternate"):
        raise ValueError("cutoff_mode must be 'canonical' or 'alternate'.")
    if cutoff_mode == "canonical" and cutoff_salt is not None:
        raise ValueError("cutoff_salt is only valid with cutoff_mode='alternate'.")
    if cutoff_mode == "alternate" and (
        not isinstance(cutoff_salt, str) or not cutoff_salt.strip() or "|" in cutoff_salt
    ):
        raise ValueError("Alternate cutoff mode requires a nonempty cutoff_salt without '|'.")
    source_manifest = load_split_manifest() if split_manifest is None else split_manifest
    by_engine, rosters = _normalise_manifest(source_manifest)
    arrays, lifetimes = _validate_training_engines(engines, by_engine)

    rng = np.random.Generator(np.random.PCG64(seed))
    role_draws = {
        role: [int(i) for i in rng.choice(rosters[role], size=ROLE_SIZES[role], replace=True)]
        for role in ROLE_ORDER
    }
    role_metadata: dict[str, dict[str, Any]] = {}
    cutoffs_all: dict[int, int] = {}
    cutoff_hash_inputs_all: dict[int, str] = {}
    cutoff_hashes_all: dict[int, str] = {}
    for role in ROLE_ORDER:
        unique_ids = sorted(set(role_draws[role]))
        cutoffs: dict[int, int] = {}
        hash_inputs: dict[int, str] = {}
        cutoff_hashes: dict[int, str] = {}
        for engine in unique_ids:
            cutoff, hash_input, digest = _cutoff_record(
                engine, by_engine[engine], cutoff_mode, cutoff_salt
            )
            cutoffs[engine] = cutoff
            hash_inputs[engine] = hash_input
            cutoff_hashes[engine] = digest
        cutoffs_all.update(cutoffs)
        cutoff_hash_inputs_all.update(hash_inputs)
        cutoff_hashes_all.update(cutoff_hashes)
        role_metadata[role] = _stage_metadata(
            role=role,
            roster=rosters[role],
            draw_ids=role_draws[role],
            cutoffs=cutoffs,
            lifetimes=lifetimes,
            hash_inputs=hash_inputs,
            cutoff_hashes=cutoff_hashes,
            cutoff_mode=cutoff_mode,
            cutoff_salt=cutoff_salt,
            bootstrap_seed=seed,
        )

    failures = [
        f"{role}: {role_metadata[role]['eligible_unique_count']} distinct eligible IDs "
        f"< required {MIN_UNIQUE_ELIGIBLE[role]}; no redraw performed"
        for role in ROLE_ORDER if not role_metadata[role]["minimum_passed"]
    ]
    anchor_ids, anchor_cutoffs, anchor_hash_inputs, anchor_hashes = _anchor_manifest(
        by_engine, lifetimes
    )
    anchor_metadata = {
        "source": "fixed original eligible calibration sensor prefixes",
        "ids": anchor_ids,
        "cutoff_by_engine": {str(i): int(anchor_cutoffs[i]) for i in anchor_ids},
        "eligibility_by_engine": {str(i): True for i in anchor_ids},
        "cutoff_hash_input_by_engine": {str(i): anchor_hash_inputs[i] for i in anchor_ids},
        "cutoff_sha256_by_engine": {str(i): anchor_hashes[i] for i in anchor_ids},
        "outcomes_attached": False,
        "outcomes_allowed_for_selection": False,
    }
    anchor_metadata["anchor_sha256"] = _json_sha256(anchor_metadata)

    replicate_id = (
        f"bootstrap-{seed}-{cutoff_mode}"
        + (f"-{cutoff_salt}" if cutoff_salt is not None else "")
    )
    metadata: dict[str, Any] = {
        "contract_version": "RP-001-v0.4-worker-pipeline-1",
        "replicate_id": replicate_id,
        "scope": "training-only conditional empirical pipeline perturbation",
        "primary_question_changed": False,
        "official_test_sensors_or_labels_accessed": False,
        "protected_archive_entries_accessed": False,
        "bayesian_fit_or_prediction_run": False,
        "bootstrap_seed": seed,
        "bootstrap_algorithm": "one PCG64 engine bootstrap within each frozen reserved role",
        "role_sizes": dict(ROLE_SIZES),
        "role_stages": role_metadata,
        "cutoff_mode": cutoff_mode,
        "cutoff_salt": cutoff_salt,
        "cutoff_rule": (
            "canonical manifest C=30+SHA256(SEED|cutoff|engine) mod 221"
            if cutoff_mode == "canonical"
            else "alternate C=30+SHA256(SEED|<cutoff_salt>|engine) mod 221"
        ),
        "cutoff_hashes": {
            str(i): cutoff_hashes_all[i] for i in sorted(cutoff_hashes_all)
        },
        "cutoff_hash_inputs": {
            str(i): cutoff_hash_inputs_all[i] for i in sorted(cutoff_hash_inputs_all)
        },
        "eligibility_rule": "C<T; no redraw",
        "minimums_count_distinct_eligible_ids": dict(MIN_UNIQUE_ELIGIBLE),
        "failure_reasons": failures,
        "anchor": anchor_metadata,
        "expected_training_sha256": "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8",
        "input_source_sha256": input_source_sha256,
        "input_source_sha256_verified_by_this_module": False,
        "multiplicity_interpretation": (
            "Repeated rows encode bootstrap multiplicity for the same ID; they do not create new independent engines."
        ),
        "empirical_perturbation_limit": (
            "The planned eight conditional perturbations do not estimate true total pipeline sampling uncertainty "
            "or independent loss/performance."
        ),
    }
    if failures:
        metadata["pipeline_sha256"] = _json_sha256(metadata)
        return BootstrapPipelineData(
            status="failed",
            replicate_id=replicate_id,
            bootstrap_seed=seed,
            cutoff_mode=cutoff_mode,
            metadata=metadata,
            failure_reasons=tuple(failures),
        )

    try:
        fit_stage = role_metadata["fit"]
        fit_draws = [int(i) for i in fit_stage["eligible_draw_ids"]]
        fit_counts = {
            int(i): int(count)
            for i, count in fit_stage["multiplicity_by_engine"].items()
            if fit_stage["eligibility_by_engine"][i]
        }
        selection_pre = fit_weighted_preprocessor(engines=arrays, cutoffs=cutoffs_all, multiplicities=fit_counts)
        tune_stage = role_metadata["tune"]
        tune_draws = [int(i) for i in tune_stage["eligible_draw_ids"]]
        fit_data = _landmark_data(
            arrays, draw_ids=fit_draws, cutoffs=cutoffs_all, preprocessor=selection_pre,
            include_outcomes=True, source=f"{replicate_id}:fit selection rows",
        )
        tune_data = _landmark_data(
            arrays, draw_ids=tune_draws, cutoffs=cutoffs_all, preprocessor=selection_pre,
            include_outcomes=True, source=f"{replicate_id}:tune selection rows",
        )

        combined_counts = dict(fit_counts)
        combined_counts.update({
            int(i): int(count)
            for i, count in tune_stage["multiplicity_by_engine"].items()
            if tune_stage["eligibility_by_engine"][i]
        })
        combined_cutoffs = {
            int(i): int(cutoffs_all[int(i)]) for i in combined_counts
        }
        refit_pre = fit_weighted_preprocessor(
            engines=arrays, cutoffs=combined_cutoffs, multiplicities=combined_counts
        )
        combined_draws = fit_draws + tune_draws
        refit_data = _landmark_data(
            arrays, draw_ids=combined_draws, cutoffs=cutoffs_all, preprocessor=refit_pre,
            include_outcomes=True, source=f"{replicate_id}:fit+tune refit rows",
        )
        cal_stage = role_metadata["calibration"]
        cal_draws = [int(i) for i in cal_stage["eligible_draw_ids"]]
        cal_data = _landmark_data(
            arrays, draw_ids=cal_draws, cutoffs=cutoffs_all, preprocessor=refit_pre,
            include_outcomes=True, source=f"{replicate_id}:calibration correction rows",
        )
        anchor = _landmark_data(
            arrays, draw_ids=anchor_ids, cutoffs=anchor_cutoffs, preprocessor=refit_pre,
            include_outcomes=False, source=f"{replicate_id}:fixed sensor-only anchor; labels omitted",
        )
        anchor_features = {
            "summary": features(anchor),
            "full_sequence": features(anchor, full=True),
        }
    except Exception as exc:
        failure = f"Pipeline data construction failed: {type(exc).__name__}: {exc}"
        metadata["failure_reasons"] = [failure]
        metadata["pipeline_sha256"] = _json_sha256(metadata)
        return BootstrapPipelineData(
            status="failed",
            replicate_id=replicate_id,
            bootstrap_seed=seed,
            cutoff_mode=cutoff_mode,
            metadata=metadata,
            failure_reasons=(failure,),
        )

    metadata["dataset_shapes"] = {
        "fit": {"rows": len(fit_data.ids), "unique_ids": len(set(fit_data.ids.tolist()))},
        "tune": {"rows": len(tune_data.ids), "unique_ids": len(set(tune_data.ids.tolist()))},
        "refit_fit_tune": {
            "rows": len(refit_data.ids), "unique_ids": len(set(refit_data.ids.tolist()))
        },
        "calibration": {
            "rows": len(cal_data.ids), "unique_ids": len(set(cal_data.ids.tolist()))
        },
        "anchor": {"rows": len(anchor.ids), "unique_ids": len(set(anchor.ids.tolist()))},
    }
    metadata["preprocessor_sha256"] = {
        "selection_fit": _preprocessor_sha256(selection_pre),
        "refit_fit_tune": _preprocessor_sha256(refit_pre),
    }
    metadata["landmark_data_sha256"] = {
        "fit": _landmark_sha256(fit_data),
        "tune": _landmark_sha256(tune_data),
        "refit_fit_tune": _landmark_sha256(refit_data),
        "calibration": _landmark_sha256(cal_data),
        "anchor_sensor_only": _landmark_sha256(anchor),
    }
    metadata["anchor"]["feature_sha256"] = {
        "summary": _array_sha256(anchor_features["summary"]),
        "full_sequence": _array_sha256(anchor_features["full_sequence"]),
    }
    metadata["pipeline_sha256"] = _json_sha256(metadata)
    return BootstrapPipelineData(
        status="ready",
        replicate_id=replicate_id,
        bootstrap_seed=seed,
        cutoff_mode=cutoff_mode,
        metadata=metadata,
        selection_preprocessor=selection_pre,
        refit_preprocessor=refit_pre,
        fit=fit_data,
        tune=tune_data,
        refit_fit_tune=refit_data,
        calibration=cal_data,
        anchor=anchor,
        anchor_features=anchor_features,
    )
def reselect_refit_calibrate_cqr(
    bootstrap: BootstrapPipelineData,
) -> CQRBootstrapResult:
    """Run the fixed 12-configuration CQR rule on one prepared bootstrap.

    Selection uses only the expanded fit/tune rows. The selected interval model
    is refit on expanded fit+tune rows transformed by the refit PCA. Calibration
    outcomes are read afterward only to compute the existing nonshrinking CQR
    correction; duplicate bootstrap scores do not receive a formal exchangeability
    guarantee.
    """
    if bootstrap.status != "ready":
        return CQRBootstrapResult(
            status="failed",
            failure_reasons=(
                f"Bootstrap {bootstrap.replicate_id} is {bootstrap.status}: "
                + "; ".join(bootstrap.failure_reasons),
            ),
        )
    if any(value is None for value in (bootstrap.fit, bootstrap.tune, bootstrap.refit_fit_tune, bootstrap.calibration)):
        return CQRBootstrapResult(
            status="failed",
            failure_reasons=("Ready bootstrap is missing fit, tune, refit, or calibration data.",),
        )
    fit = bootstrap.fit
    tune = bootstrap.tune
    refit = bootstrap.refit_fit_tune
    calibration = bootstrap.calibration
    if fit.y is None or tune.y is None or refit.y is None or calibration.y is None:
        return CQRBootstrapResult(
            status="failed",
            failure_reasons=("CQR selection/refit/calibration requires the training-only log-R targets.",),
        )
    if bootstrap.anchor is None or bootstrap.anchor.y is not None:
        return CQRBootstrapResult(
            status="failed",
            failure_reasons=("The fixed prediction anchor must be sensor-only with y=None.",),
        )

    fit_summary, fit_full = features(fit), features(fit, full=True)
    tune_summary, tune_full = features(tune), features(tune, full=True)
    try:
        selection_linear_scaler = fit_linear_scaler(fit_full)
    except Exception as exc:
        return CQRBootstrapResult(
            status="failed",
            failure_reasons=(f"Selection scaler failed: {type(exc).__name__}: {exc}",),
        )

    scores: dict[str, float | None] = {}
    failures: dict[str, str] = {}
    candidate_summaries: list[dict[str, Any]] = []
    for spec in CQR_CANDIDATES:
        score: float | None = None
        candidate: CandidateFit | None = None
        status = "failed"
        reason: str | None = None
        try:
            candidate = fit_candidate(
                fit_summary,
                fit_full,
                np.exp(fit.y),
                spec,
                linear_scaler=selection_linear_scaler if spec.family == "linear" else None,
                random_state=CQR_RANDOM_STATE,
            )
            status = candidate.status
            if candidate.status != "completed":
                reason = candidate.failure_message or "Candidate fitting returned failed."
            else:
                lower, upper = predict_endpoints(candidate, tune_summary, tune_full)
                score = mean90_interval_score(np.exp(tune.y), lower, upper)
                status = "completed"
        except Exception as exc:
            reason = f"{type(exc).__name__}: {exc}"
            status = "failed_during_tuning"
        scores[spec.candidate_id] = score
        if score is None:
            failures[spec.candidate_id] = reason or "No tuning score was produced."
        candidate_summaries.append({
            "candidate_id": spec.candidate_id,
            "family": spec.family,
            "parameters": {key: value for key, value in spec.parameters},
            "status": status,
            "tuning_mean90_interval_score": score,
            "failure": reason,
        })

    try:
        decision = select_candidate(
            scores,
            tie_tolerance=0.5,
            failure_reasons=failures,
        )
    except Exception as exc:
        return CQRBootstrapResult(
            status="failed",
            tuning_scores=scores,
            candidate_summaries=candidate_summaries,
            failure_reasons=(f"No CQR candidate could be selected: {type(exc).__name__}: {exc}",),
        )

    refit_summary, refit_full = features(refit), features(refit, full=True)
    calibration_summary = features(calibration)
    calibration_full = features(calibration, full=True)
    try:
        refit_scaler = (
            fit_linear_scaler(refit_full)
            if decision.candidate.family == "linear"
            else None
        )
        interval_refit = fit_candidate(
            refit_summary,
            refit_full,
            np.exp(refit.y),
            decision.candidate,
            linear_scaler=refit_scaler,
            random_state=CQR_RANDOM_STATE,
        )
    except Exception as exc:
        return CQRBootstrapResult(
            status="failed",
            selection=decision,
            tuning_scores=scores,
            candidate_summaries=candidate_summaries,
            failure_reasons=(f"Selected CQR refit failed: {type(exc).__name__}: {exc}",),
        )
    if interval_refit.status != "completed":
        return CQRBootstrapResult(
            status="failed",
            selection=decision,
            tuning_scores=scores,
            candidate_summaries=candidate_summaries,
            interval_refit=interval_refit,
            failure_reasons=(
                "Selected CQR refit failed: "
                + (interval_refit.failure_message or "no failure message supplied"),
            ),
        )

    issues: list[str] = []
    try:
        median_refit = fit_median_candidate(
            refit_summary,
            refit_full,
            np.exp(refit.y),
            decision.candidate,
            linear_scaler=refit_scaler,
            random_state=CQR_RANDOM_STATE,
        )
    except Exception as exc:
        median_refit = None
        issues.append(f"Selected median refit failed: {type(exc).__name__}: {exc}")
    if median_refit is not None and median_refit.status != "completed":
        issues.append(
            "Selected median refit failed: "
            + (median_refit.failure_message or "no failure message supplied")
        )

    try:
        lower, upper = predict_endpoints(
            interval_refit, calibration_summary, calibration_full
        )
        calibration_rul = np.exp(calibration.y)
        correction = float(calibrate(calibration_rul, lower, upper))
        ordered_lower = np.minimum(lower, upper)
        ordered_upper = np.maximum(lower, upper)
        raw_scores = np.maximum(
            ordered_lower - calibration_rul,
            calibration_rul - ordered_upper,
        )
        calibration_counts = Counter(int(i) for i in calibration.ids)
        calibration_metadata = {
            "unique_eligible_calibration_engine_count": len(calibration_counts),
            "bootstrap_score_row_count": len(calibration.ids),
            "multiplicity_by_engine": {
                str(i): int(calibration_counts[i]) for i in sorted(calibration_counts)
            },
            "rank": conformal_rank(len(calibration.ids)),
            "alpha": 0.10,
            "nonshrinking": True,
            "correction_cycles": correction,
            "calibration_outcomes_use": "correction only; not CQR or prior/algorithm selection",
            "formal_exchangeability_guarantee": False,
            "guarantee_limitation": (
                "Bootstrap copies repeat engine scores and are not independent calibration engines; "
                "official cutoff transport is also unverified."
            ),
            "raw_score_sequence_sha256": _array_sha256(raw_scores),
            "raw_endpoint_matrix_sha256": _array_sha256(
                np.column_stack((ordered_lower, ordered_upper))
            ),
        }
    except Exception as exc:
        return CQRBootstrapResult(
            status="failed",
            selection=decision,
            tuning_scores=scores,
            candidate_summaries=candidate_summaries,
            interval_refit=interval_refit,
            median_refit=median_refit,
            failure_reasons=tuple(
                issues + [f"CQR calibration correction failed: {type(exc).__name__}: {exc}"]
            ),
        )

    calibration_metadata.update({
        "selection_candidate_id": decision.candidate.candidate_id,
        "selection_best_tuning_score": decision.best_observed_score,
        "selection_selected_tuning_score": decision.selected_candidate_score,
        "selection_tie_candidate_ids": list(decision.tie_candidate_ids),
        "fit_unique_engine_count": len(set(fit.ids.tolist())),
        "fit_bootstrap_row_count": len(fit.ids),
        "tune_unique_engine_count": len(set(tune.ids.tolist())),
        "tune_bootstrap_row_count": len(tune.ids),
        "refit_unique_engine_count": len(set(refit.ids.tolist())),
        "refit_bootstrap_row_count": len(refit.ids),
        "selection_rule": (
            "12 fixed candidates; lowest uncalibrated tuning mean 90% interval score; "
            "within 0.5 cycles prefer linear, then the existing deterministic simplicity key"
        ),
        "random_state": CQR_RANDOM_STATE,
    })
    return CQRBootstrapResult(
        status="completed",
        selection=decision,
        tuning_scores=scores,
        candidate_summaries=candidate_summaries,
        interval_refit=interval_refit,
        median_refit=median_refit,
        calibration_correction=correction,
        calibration_metadata=calibration_metadata,
        failure_reasons=tuple(issues),
    )