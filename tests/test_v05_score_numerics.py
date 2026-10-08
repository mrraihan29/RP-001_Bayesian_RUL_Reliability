import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pytest
from scipy.stats import chi2

from rp001.v05_score_numerics import (
    INTERVAL_SCORE_LIPSCHITZ_CONSTANT,
    endpoint_cycle_quantile_influence,
    estimate_joint_interval_score_mcse,
    interval_score_90,
    interval_score_influence_from_endpoints,
)


def test_endpoint_cycle_quantile_influence_keeps_engine_and_chain_draw_axes():
    weights = np.array(
        [
            [[1.0, 2.0], [3.0, 4.0]],
            [[2.0, 1.0], [6.0, 2.0]],
        ]
    )
    log_weights = np.log(weights)
    cdf = np.array(
        [
            [[0.1, 0.9], [0.3, 0.7]],
            [[0.2, 0.8], [0.4, 0.6]],
        ]
    )
    probabilities = np.array([0.25, 0.75])
    quantiles = np.array([10.0, 20.0])
    densities = np.array([0.5, 0.25])

    result = endpoint_cycle_quantile_influence(
        log_weights, cdf, probabilities, quantiles, densities
    )

    normalized_scale = weights / weights.mean(axis=(0, 1), keepdims=True)
    expected = (
        -quantiles[None, None, :]
        * normalized_scale
        * (cdf - probabilities[None, None, :])
        / densities[None, None, :]
    )
    assert result["influence_cycles"].shape == (2, 2, 2)
    assert result["engine_axis_preserved"] is True
    np.testing.assert_allclose(result["influence_cycles"], expected, rtol=0, atol=1e-14)
    np.testing.assert_allclose(
        result["scaled_weight_mean_by_engine"], np.array([0.5, 9.0 / 16.0]), rtol=0, atol=1e-14
    )


def test_exact_interval_score_gradient_kinks_and_score_lipschitz_bound():
    chains, draws, engines = 2, 8, 3
    lower = np.arange(chains * draws * engines, dtype=float).reshape(
        chains, draws, engines
    ) / 10.0
    upper = 2.0 - lower / 3.0
    outcomes = np.array([9.9, 26.0, 35.0])
    lower_cycles = np.array([10.0, 20.0, 30.0])
    upper_cycles = np.array([15.0, 25.0, 35.0])
    lower_upper_mcse = np.array([[0.1, 0.1, 0.1], [0.05, 2.1, 0.0]])
    upper_upper_mcse = np.array([[0.1, 0.2, 0.1], [0.1, 0.4, 0.0]])

    result = interval_score_influence_from_endpoints(
        lower,
        upper,
        outcomes,
        lower_cycles,
        upper_cycles,
        lower_upper_mcse,
        upper_upper_mcse,
        batch_sizes=(4, 2),
    )

    gradient_lower = np.array([19.0, -1.0, -1.0])
    gradient_upper = np.array([1.0, -19.0, 1.0])
    expected_h = np.mean(
        lower * gradient_lower[None, None, :]
        + upper * gradient_upper[None, None, :],
        axis=2,
    )
    np.testing.assert_array_equal(result["gradient_lower_by_engine"], gradient_lower)
    np.testing.assert_array_equal(result["gradient_upper_by_engine"], gradient_upper)
    np.testing.assert_allclose(result["score_influence"], expected_h, rtol=0, atol=1e-14)
    np.testing.assert_allclose(
        result["score_per_engine_cycles"], np.array([7.0, 25.0, 5.0])
    )
    assert result["label_kink"]["any"] is True
    first, second = result["label_kink"]["by_batch_size"]
    np.testing.assert_array_equal(first["lower_endpoint_by_engine"], [True, False, False])
    np.testing.assert_array_equal(first["upper_endpoint_by_engine"], [False, False, True])
    np.testing.assert_array_equal(second["lower_endpoint_by_engine"], [True, True, False])
    np.testing.assert_array_equal(second["upper_endpoint_by_engine"], [False, True, True])

    radii_lower = np.array([0.1, 0.2, 0.3])
    radii_upper = np.array([0.2, 0.3, 0.4])
    bound = (
        INTERVAL_SCORE_LIPSCHITZ_CONSTANT
        * np.sum(radii_lower + radii_upper)
        / len(outcomes)
    )
    perturbed = interval_score_90(
        outcomes,
        lower_cycles + np.array([0.1, -0.2, 0.3]),
        upper_cycles + np.array([-0.2, 0.3, -0.4]),
    )
    original = interval_score_90(outcomes, lower_cycles, upper_cycles)
    assert np.mean(np.abs(perturbed - original)) <= bound + 1e-12


def test_joint_chain_batch_covariance_projects_to_scalar_score_mcse():
    chains, draws, engines = 2, 12, 2
    t = np.arange(draws, dtype=float)[None, :, None]
    c = np.arange(chains, dtype=float)[:, None, None]
    e = np.arange(engines, dtype=float)[None, None, :]
    lower = 0.1 * (t + 1.0) * (e + 1.0) + 0.4 * c * (-1.0) ** t + (t % 3) * (
        0.2 + e * 0.1
    )
    upper = -0.08 * (t + 1.0) * (e + 1.0) + 0.15 * c * (t % 4) + (-1.0) ** t * (
        0.3 + e * 0.05
    )
    outcomes = np.array([25.0, 35.0])
    lower_cycles = np.array([20.0, 30.0])
    upper_cycles = np.array([30.0, 40.0])
    lower_radii = np.array([[0.1, 0.2], [0.3, 0.4]])
    upper_radii = np.array([[0.2, 0.3], [0.4, 0.5]])
    batch_sizes = (3, 6)

    result = estimate_joint_interval_score_mcse(
        lower,
        upper,
        outcomes,
        lower_cycles,
        upper_cycles,
        lower_radii,
        upper_radii,
        tail_probability=0.05,
        batch_sizes=batch_sizes,
    )
    joint = np.concatenate((lower, upper), axis=2)
    contrast = np.array([-1.0, -1.0, 1.0, 1.0]) / engines
    np.testing.assert_allclose(result["score_contrast"], contrast)
    np.testing.assert_allclose(
        result["score_influence"], np.einsum("cde,e->cd", joint, contrast)
    )

    total_draws = chains * draws
    for group in result["batch_size_results"]:
        batch_size = group["batch_size"]
        expected_joint_covariance = np.zeros((2 * engines, 2 * engines))
        variance_components = []
        dfs = []
        for chain_index in range(chains):
            series = joint[chain_index]
            batch_count = draws // batch_size
            used = batch_count * batch_size
            batch_means = series[:used].reshape(
                batch_count, batch_size, 2 * engines
            ).mean(axis=1)
            centered = batch_means - batch_means.mean(axis=0, keepdims=True)
            lrv = batch_size * centered.T @ centered / (batch_count - 1)
            expected_joint_covariance += draws * lrv / total_draws**2
            scalar_lrv = float(contrast @ lrv @ contrast)
            variance_components.append(draws * scalar_lrv / total_draws**2)
            dfs.append(batch_count - 1)

        expected_joint_covariance = 0.5 * (
            expected_joint_covariance + expected_joint_covariance.T
        )
        expected_variance = float(sum(variance_components))
        np.testing.assert_allclose(
            group["joint_endpoint_mc_error_covariance_cycles_squared"],
            expected_joint_covariance,
            rtol=1e-13,
            atol=1e-14,
        )
        assert group["score_variance_cycles_squared"] == pytest.approx(
            expected_variance, rel=1e-13, abs=1e-14
        )
        assert group["score_variance_from_joint_covariance_cycles_squared"] == pytest.approx(
            expected_variance, rel=1e-13, abs=1e-14
        )
        assert group["quantile_score_mcse_cycles"] == pytest.approx(
            np.sqrt(expected_variance), rel=1e-13
        )
        denom = sum(v**2 / df for v, df in zip(variance_components, dfs))
        expected_df = expected_variance**2 / denom
        expected_upper = np.sqrt(
            expected_variance
            * expected_df
            / chi2.ppf(0.05, expected_df)
        )
        assert group["satterthwaite_degrees_of_freedom"] == pytest.approx(expected_df)
        assert group["approximate_upper_quantile_score_mcse_cycles"] == pytest.approx(
            expected_upper
        )

    bounds = [
        group["interval_score_lipschitz_sensitivity_cycles"]["conditional_bound"]
        for group in result["batch_size_results"]
    ]
    np.testing.assert_allclose(bounds, [7.6, 15.2])
    assert "not an MCSE coverage theorem" in result["batch_size_results"][0]["interval_score_lipschitz_sensitivity_cycles"]["interpretation"]


def test_invalid_alignment_density_and_batch_layout_are_rejected():
    log_weights = np.zeros((2, 8, 2))
    cdf = np.full_like(log_weights, 0.5)
    with pytest.raises(ValueError, match="share shape"):
        endpoint_cycle_quantile_influence(
            log_weights, cdf[:, :, :1], 0.5, [10.0, 20.0], [0.2, 0.3]
        )
    with pytest.raises(ValueError, match="strictly positive"):
        endpoint_cycle_quantile_influence(
            log_weights, cdf, 0.5, [10.0, 20.0], [0.2, 0.0]
        )

    influences = np.zeros((2, 8, 2))
    with pytest.raises(ValueError, match="two distinct"):
        estimate_joint_interval_score_mcse(
            influences,
            influences,
            [10.0, 20.0],
            [9.0, 19.0],
            [11.0, 21.0],
            [0.1, 0.1],
            [0.1, 0.1],
            tail_probability=0.05,
            batch_sizes=(2, 2),
        )
    with pytest.raises(ValueError, match="at least two batches"):
        estimate_joint_interval_score_mcse(
            influences,
            influences,
            [10.0, 20.0],
            [9.0, 19.0],
            [11.0, 21.0],
            [0.1, 0.1],
            [0.1, 0.1],
            tail_probability=0.05,
            batch_sizes=(2, 5),
        )


