from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path
import sys

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rp001.comparators import CandidateFit, MedianFit
from rp001.metrics import correction
from rp001.v04_pipeline import (
    CANONICAL_HASH_SEED,
    build_bootstrap_pipeline_data,
    fit_weighted_preprocessor,
    reselect_refit_calibrate_cqr,
)


def _canonical_cutoff(engine: int) -> int:
    digest = hashlib.sha256(
        f"{CANONICAL_HASH_SEED}|cutoff|{engine}".encode("utf-8")
    ).hexdigest()
    return 30 + int(digest, 16) % 221


def _role_map() -> dict[int, str]:
    ordered = sorted(
        range(1, 101),
        key=lambda engine: hashlib.sha256(
            f"{CANONICAL_HASH_SEED}|split|{engine}".encode("utf-8")
        ).hexdigest(),
    )
    return {
        engine: ("fit" if index < 55 else "tune" if index < 70 else "calibration")
        for index, engine in enumerate(ordered)
    }


def _engine_rows(engine: int, lifetime: int) -> np.ndarray:
    cycles = np.arange(1, lifetime + 1, dtype=np.float64)
    rows = np.zeros((lifetime, 26), dtype=np.float64)
    rows[:, 0] = engine
    rows[:, 1] = cycles
    rows[:, 2:5] = np.column_stack(
        (engine / 10.0 + cycles * 0.001, cycles % 3, np.full_like(cycles, engine % 7))
    )
    rows[:, 5] = 518.67
    for channel in range(1, 21):
        rows[:, 5 + channel] = (
            0.02 * engine * channel
            + 0.003 * cycles * (channel + 1)
            + np.sin(cycles / (channel + 2.0) + engine / 11.0)
        )
    return rows


def _fixture(*, all_tune_ineligible: bool = False):
    roles = _role_map()
    ineligible = {
        "fit": set(sorted(i for i, role in roles.items() if role == "fit")[:12]),
        "tune": set(sorted(i for i, role in roles.items() if role == "tune")[:2]),
        "calibration": set(sorted(i for i, role in roles.items() if role == "calibration")[:5]),
    }
    if all_tune_ineligible:
        ineligible["tune"] = set(i for i, role in roles.items() if role == "tune")

    manifest = []
    engines = {}
    for engine in range(1, 101):
        cutoff = _canonical_cutoff(engine)
        role = roles[engine]
        is_ineligible = engine in ineligible[role]
        lifetime = 30 if all_tune_ineligible and role == "tune" else cutoff if is_ineligible else 300
        manifest.append({
            "dataset": "FD001_train",
            "engine": engine,
            "role": role,
            "proposed_cutoff": cutoff,
            "eligible_alive": cutoff < lifetime,
        })
        engines[engine] = _engine_rows(engine, lifetime)
    return engines, manifest


def _assert_landmark_equal(left, right):
    np.testing.assert_array_equal(left.a, right.a)
    np.testing.assert_array_equal(left.z, right.z)
    np.testing.assert_array_equal(left.ids, right.ids)
    np.testing.assert_array_equal(left.B, right.B)
    if left.y is None:
        assert right.y is None
    else:
        np.testing.assert_array_equal(left.y, right.y)


def test_paired_role_bootstrap_and_cutoff_hashes_are_deterministic():
    engines, manifest = _fixture()
    canonical = build_bootstrap_pipeline_data(
        engines, 4021, cutoff_mode="canonical", split_manifest=manifest
    )
    alternate = build_bootstrap_pipeline_data(
        engines,
        4021,
        cutoff_mode="alternate",
        cutoff_salt="cutoff-sensitivity-001",
        split_manifest=manifest,
    )
    assert canonical.status == alternate.status == "ready"
    for role, assigned_size in (("fit", 55), ("tune", 15), ("calibration", 30)):
        left = canonical.metadata["role_stages"][role]
        right = alternate.metadata["role_stages"][role]
        assert len(left["bootstrap_draw_ids"]) == assigned_size
        assert left["bootstrap_draw_ids"] == right["bootstrap_draw_ids"]
        assert sum(left["multiplicity_by_engine"].values()) == assigned_size
        assert sum(right["multiplicity_by_engine"].values()) == assigned_size
        assert left["no_redraw"] is True and right["no_redraw"] is True
    assert canonical.metadata["role_stages"]["fit"]["stage_sha256"] != (
        alternate.metadata["role_stages"]["fit"]["stage_sha256"]
    )
    fit_meta = alternate.metadata["role_stages"]["fit"]
    for engine_id, hash_input in fit_meta["cutoff_hash_input_by_engine"].items():
        assert hash_input == f"{CANONICAL_HASH_SEED}|cutoff-sensitivity-001|{engine_id}"


def test_bootstrap_datasets_expand_multiplicities_and_anchor_has_no_outcome():
    engines, manifest = _fixture()
    result = build_bootstrap_pipeline_data(
        engines, 117, cutoff_mode="canonical", split_manifest=manifest
    )
    assert result.status == "ready", result.failure_reasons
    assert result.fit is not None and result.tune is not None
    assert result.refit_fit_tune is not None and result.calibration is not None
    assert result.anchor is not None and result.anchor_features is not None

    for role, data in (("fit", result.fit), ("tune", result.tune), ("calibration", result.calibration)):
        stage = result.metadata["role_stages"][role]
        expected = Counter(
            int(engine_id)
            for engine_id in stage["eligible_draw_ids"]
        )
        assert Counter(data.ids.tolist()) == expected
        assert len(data.ids) == stage["eligible_multiplicity_count"]
        assert len(set(data.ids.tolist())) == stage["eligible_unique_count"]
        assert data.y is not None
    assert len(result.refit_fit_tune.ids) == len(result.fit.ids) + len(result.tune.ids)
    assert Counter(result.refit_fit_tune.ids.tolist()) == (
        Counter(result.fit.ids.tolist()) + Counter(result.tune.ids.tolist())
    )

    assert result.anchor.y is None
    assert len(result.anchor.ids) == 25
    assert len(set(result.anchor.ids.tolist())) == 25
    assert result.metadata["anchor"]["outcomes_allowed_for_selection"] is False
    assert result.anchor_features["summary"].shape == (25, 5)
    assert result.anchor_features["full_sequence"].shape == (25, 31)
    assert np.isfinite(result.anchor_features["summary"]).all()
    assert np.isfinite(result.anchor_features["full_sequence"]).all()


def test_weighted_pca_uses_multiplicity_over_prefix_length_and_drops_constants():
    engines = {1: _engine_rows(1, 300), 2: _engine_rows(2, 300)}
    cutoffs = {1: 30, 2: 50}
    multiplicities = {1: 2, 2: 1}
    pre = fit_weighted_preprocessor(engines, cutoffs, multiplicities)

    x1 = engines[1][:30, 5:]
    x2 = engines[2][:50, 5:]
    x = np.vstack((x1, x2))
    weights = np.r_[
        np.full(30, 2.0 / (3.0 * 30.0)),
        np.full(50, 1.0 / (3.0 * 50.0)),
    ]
    mean = np.sum(x * weights[:, None], axis=0)
    sd = np.sqrt(np.sum((x - mean) ** 2 * weights[:, None], axis=0))
    retained = sd > 1e-8
    standardized = (x[:, retained] - mean[retained]) / sd[retained]
    covariance = standardized.T @ (standardized * weights[:, None])
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    pc = eigenvectors[:, -1]
    if pc[np.argmax(np.abs(pc))] < 0:
        pc = -pc

    np.testing.assert_allclose(pre["mean"], mean, rtol=0, atol=1e-12)
    np.testing.assert_allclose(pre["sd"], sd, rtol=0, atol=1e-12)
    np.testing.assert_array_equal(pre["retained"], retained)
    np.testing.assert_allclose(pre["pc"], pc, rtol=1e-11, atol=1e-12)
    np.testing.assert_allclose(pre["pc_scale"], np.sqrt(eigenvalues[-1]), rtol=1e-12)
    np.testing.assert_allclose(pre["fit_weight_sum"], 1.0, atol=1e-14)
    assert not bool(pre["retained"][0])
    np.testing.assert_array_equal(pre["fit_ids"], [1, 2])
    np.testing.assert_array_equal(pre["fit_multiplicities"], [2, 1])


def test_future_sensor_changes_do_not_change_any_stage_or_anchor():
    engines, manifest = _fixture()
    baseline = build_bootstrap_pipeline_data(
        engines,
        902,
        cutoff_mode="alternate",
        cutoff_salt="cutoff-sensitivity-004",
        split_manifest=manifest,
    )
    assert baseline.status == "ready", baseline.failure_reasons

    cutoffs = {
        int(engine): int(cutoff)
        for stage in baseline.metadata["role_stages"].values()
        for engine, cutoff in stage["cutoff_by_engine"].items()
    }
    for engine, cutoff in baseline.metadata["anchor"]["cutoff_by_engine"].items():
        cutoffs[int(engine)] = max(cutoffs.get(int(engine), 0), int(cutoff))
    altered = {engine: rows.copy() for engine, rows in engines.items()}
    for engine in set(cutoffs):
        rows = altered[engine]
        rows[rows[:, 1] > cutoffs[engine], 5:] += 1e6

    changed = build_bootstrap_pipeline_data(
        altered,
        902,
        cutoff_mode="alternate",
        cutoff_salt="cutoff-sensitivity-004",
        split_manifest=manifest,
    )
    assert changed.status == "ready", changed.failure_reasons
    for key in baseline.selection_preprocessor:
        np.testing.assert_array_equal(
            baseline.selection_preprocessor[key], changed.selection_preprocessor[key]
        )
    for key in baseline.refit_preprocessor:
        np.testing.assert_array_equal(
            baseline.refit_preprocessor[key], changed.refit_preprocessor[key]
        )
    for name in ("fit", "tune", "refit_fit_tune", "calibration", "anchor"):
        _assert_landmark_equal(getattr(baseline, name), getattr(changed, name))
    for name in ("summary", "full_sequence"):
        np.testing.assert_array_equal(
            baseline.anchor_features[name], changed.anchor_features[name]
        )


def test_insufficient_unique_tune_engines_is_retained_without_redraw():
    engines, manifest = _fixture(all_tune_ineligible=True)
    result = build_bootstrap_pipeline_data(
        engines,
        55,
        cutoff_mode="alternate",
        cutoff_salt="cutoff-sensitivity-002",
        split_manifest=manifest,
    )
    assert result.status == "failed"
    assert result.fit is None and result.tune is None
    stage = result.metadata["role_stages"]["tune"]
    assert len(stage["bootstrap_draw_ids"]) == 15
    assert stage["eligible_unique_count"] == 0
    assert stage["eligible_multiplicity_count"] == 0
    assert stage["no_redraw"] is True
    assert any("tune" in reason and "no redraw" in reason for reason in result.failure_reasons)


def test_cqr_helper_uses_fixed_grid_then_refits_and_corrects(monkeypatch):
    engines, manifest = _fixture()
    bootstrap = build_bootstrap_pipeline_data(
        engines, 117, cutoff_mode="canonical", split_manifest=manifest
    )
    assert bootstrap.status == "ready", bootstrap.failure_reasons

    fit_calls = []
    median_calls = []

    def fake_fit_candidate(Xsummary, Xfull, R, candidate, *, linear_scaler=None, random_state):
        fit_calls.append((candidate.candidate_id, len(R), random_state, linear_scaler))
        return CandidateFit(
            spec=candidate,
            status="completed",
            lower_model=object(),
            upper_model=object(),
            linear_scaler=linear_scaler,
            train_size=len(R),
        )

    def fake_median_fit(Xsummary, Xfull, R, selected_candidate, *, linear_scaler=None, random_state):
        median_calls.append((selected_candidate.candidate_id, len(R), random_state))
        spec = selected_candidate.candidate if hasattr(selected_candidate, "candidate") else selected_candidate
        return MedianFit(
            spec=spec,
            status="completed",
            model=object(),
            linear_scaler=linear_scaler,
            train_size=len(R),
        )

    def fake_endpoints(fitted, Xsummary, Xfull):
        return np.full(len(Xsummary), 20.0), np.full(len(Xsummary), 30.0)

    monkeypatch.setattr("rp001.v04_pipeline.fit_candidate", fake_fit_candidate)
    monkeypatch.setattr("rp001.v04_pipeline.fit_median_candidate", fake_median_fit)
    monkeypatch.setattr("rp001.v04_pipeline.predict_endpoints", fake_endpoints)

    result = reselect_refit_calibrate_cqr(bootstrap)
    assert result.status == "completed"
    assert len(result.candidate_summaries) == 12
    assert len(fit_calls) == 13  # 12 tuning candidates plus one selected refit
    assert len(median_calls) == 1
    assert result.selection.candidate.candidate_id == "linear-l1-alpha1"
    assert result.interval_refit.train_size == len(bootstrap.refit_fit_tune.ids)
    assert result.median_refit.train_size == len(bootstrap.refit_fit_tune.ids)

    rul = np.exp(bootstrap.calibration.y)
    expected = correction(np.maximum(20.0 - rul, rul - 30.0))
    assert result.calibration_correction == expected
    calibration = result.calibration_metadata
    assert calibration["unique_eligible_calibration_engine_count"] == len(
        set(bootstrap.calibration.ids.tolist())
    )
    assert calibration["bootstrap_score_row_count"] == len(bootstrap.calibration.ids)
    assert calibration["formal_exchangeability_guarantee"] is False
    assert calibration["calibration_outcomes_use"].endswith("not CQR or prior/algorithm selection")