import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from rp001.comparators import (
    CQR_CANDIDATES,
    GaussianLogRReferenceFit,
    build_full_sequence_features,
    build_summary_features,
    mean90_interval_score,
    ordered_endpoints,
    predict_gaussian_logr_reference,
    select_candidate,
)


def test_fixed_candidate_budget_and_parameters():
    gb = [candidate for candidate in CQR_CANDIDATES if candidate.family == "gradient_boosting"]
    linear = [candidate for candidate in CQR_CANDIDATES if candidate.family == "linear"]
    assert len(CQR_CANDIDATES) == 12
    assert len(gb) == 8
    assert len(linear) == 4
    assert {(c.get("max_depth"), c.get("min_samples_leaf"), c.get("learning_rate")) for c in gb} == {
        (1, 5, 0.03), (1, 5, 0.10), (1, 10, 0.03), (1, 10, 0.10),
        (2, 5, 0.03), (2, 5, 0.10), (2, 10, 0.03), (2, 10, 0.10),
    }
    assert {c.get("n_estimators") for c in gb} == {200}
    assert {c.get("alpha") for c in linear} == {0.001, 0.01, 0.1, 1.0}


def test_full_sequence_grid_uses_only_observed_values():
    sequences = [np.array([7.0]), np.array([1.0, 3.0]), np.arange(30, dtype=float)]
    full = build_full_sequence_features([0.0, 1.0, 2.0], sequences)
    assert full.shape == (3, 31)
    np.testing.assert_array_equal(full[0, 1:], np.full(30, 7.0))
    np.testing.assert_allclose(full[1, 1:], np.linspace(1.0, 3.0, 30), atol=1e-14)
    np.testing.assert_array_equal(full[2, 1:], np.arange(30, dtype=float))


def test_summary_feature_order_is_documented():
    result = build_summary_features(
        [0.0, 0.5], [11.0, 12.0], [10.0, 10.5], [0.2, 0.3], [0.0, 0.1]
    )
    np.testing.assert_array_equal(
        result,
        np.array([[0.0, 11.0, 10.0, 0.2, 0.0], [0.5, 12.0, 10.5, 0.3, 0.1]]),
    )


def test_endpoint_ordering_and_known_interval_score():
    lower, upper = ordered_endpoints([5.0, 10.0], [4.0, 15.0])
    np.testing.assert_array_equal(lower, [4.0, 10.0])
    np.testing.assert_array_equal(upper, [5.0, 15.0])
    assert mean90_interval_score([5.0, 20.0], [6.0, 10.0], [15.0, 15.0]) == 67.0


def test_tie_within_half_cycle_prefers_linear_then_stronger_l1():
    gb_id = next(c.candidate_id for c in CQR_CANDIDATES if c.family == "gradient_boosting")
    alpha_small = next(c.candidate_id for c in CQR_CANDIDATES if c.family == "linear" and c.get("alpha") == 0.01)
    alpha_large = next(c.candidate_id for c in CQR_CANDIDATES if c.family == "linear" and c.get("alpha") == 0.1)
    scores = {candidate.candidate_id: 50.0 for candidate in CQR_CANDIDATES}
    scores[gb_id] = 10.0
    scores[alpha_small] = 10.4
    scores[alpha_large] = 10.4
    decision = select_candidate(scores)
    assert decision.best_observed_score == 10.0
    assert decision.candidate.candidate_id == alpha_large
    assert decision.selected_candidate_score == 10.4
    assert set(decision.tie_candidate_ids) == {gb_id, alpha_small, alpha_large}


def test_gaussian_reference_known_predictive_t_quantiles_and_median():
    reference = GaussianLogRReferenceFit(
        coefficients=np.array([0.2, 1.0]),
        right_singular_vectors=np.eye(2),
        singular_values=np.array([1.0, 1.0]),
        residual_variance=0.25,
        degrees_of_freedom=10,
        rank=2,
        feature_count=1,
    )
    result = predict_gaussian_logr_reference(reference, np.array([[0.0]]), alpha=0.10)
    critical = 1.8124611228107335  # t(.95, 10), fixed known value
    scale = math.sqrt(0.25 * (1.0 + 1.0))  # new residual + parameter uncertainty
    assert math.isclose(result.median[0], math.exp(0.2), rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(result.lower[0], math.exp(0.2 - critical * scale), rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(result.upper[0], math.exp(0.2 + critical * scale), rel_tol=1e-12, abs_tol=1e-12)

