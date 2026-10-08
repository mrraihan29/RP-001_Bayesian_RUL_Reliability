import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pytest
from scipy.stats import norm

from rp001.v04_precision import _batch_means_lrv, estimate_mixture_quantile_mcse


def test_conjugate_importance_mixture_quantile_matches_analytic_predictive():
    rng = np.random.default_rng(240108)
    n_chains, draws = 4, 2048
    observed = 0.8
    theta = rng.normal(size=(n_chains, draws))
    log_weights = norm.logpdf(observed, loc=theta, scale=1.0)
    conditional_variance = 0.36
    result = estimate_mixture_quantile_mcse(
        means=theta,
        variances=np.full_like(theta, conditional_variance),
        log_weights=log_weights,
        probability=0.95,
        tail_probability=0.05,
        batch_sizes=(16, 64),
    )

    # Prior theta~N(0,1), observation~N(theta,1): theta|y~N(y/2,1/2).
    # Integrating log-RUL|theta~N(theta,0.36) gives N(0.4,0.86).
    oracle = 0.4 + np.sqrt(0.5 + conditional_variance) * norm.ppf(0.95)
    np.testing.assert_allclose(result["quantile_log_rul"], oracle, atol=0.10, rtol=0.0)
    averaged_conditional_quantile = (
        np.sum(np.exp(log_weights - np.max(log_weights)) * theta)
        / np.sum(np.exp(log_weights - np.max(log_weights)))
        + np.sqrt(conditional_variance) * norm.ppf(0.95)
    )
    assert abs(float(result["quantile_log_rul"]) - averaged_conditional_quantile) > 0.10
    assert result["weight_ess"] > 1000
    assert result["batch_size_stability"]["batch_sizes"] == [16, 64]
    assert result["finite_checks"]["mcse_values_finite"]
    assert result["finite_checks"]["upper_mcse_values_finite_or_undefined"]
    assert result["approximate_upper_confidence_level"] == pytest.approx(0.95)


def _stationary_ar1(rng, chains, draws, phi):
    innovations = rng.normal(size=(chains, draws))
    values = np.empty_like(innovations)
    values[:, 0] = innovations[:, 0]
    scale = np.sqrt(1.0 - phi**2)
    for t in range(1, draws):
        values[:, t] = phi * values[:, t - 1] + scale * innovations[:, t]
    return values


def _pooled_chain_lrv(values, batch_size):
    estimates = [_batch_means_lrv(chain, batch_size)["lrv"] for chain in values]
    return float(np.mean(estimates))


def test_batch_means_influence_lrv_matches_iid_and_ar1_scales():
    rng = np.random.default_rng(240109)
    chains, draws, batch_size = 4, 8192, 64

    iid_influence = rng.normal(size=(chains, draws))
    iid_lrv = _pooled_chain_lrv(iid_influence, batch_size)
    assert iid_lrv == pytest.approx(1.0, abs=0.20)

    phi = 0.6
    ar1_influence = _stationary_ar1(rng, chains, draws, phi)
    ar1_lrv = _pooled_chain_lrv(ar1_influence, batch_size)
    theoretical_lrv = (1.0 + phi) / (1.0 - phi)
    assert ar1_lrv == pytest.approx(theoretical_lrv, rel=0.20)


def test_contamination_component_matches_residual_scale_parameterization():
    means = np.zeros((2, 128))
    variances = np.full_like(means, 0.5)
    log_weights = np.zeros_like(means)
    sigma_r = np.full_like(means, 0.2)

    normal = estimate_mixture_quantile_mcse(
        means, variances, log_weights, 0.95, tail_probability=0.05, error="normal"
    )
    contaminated = estimate_mixture_quantile_mcse(
        means,
        variances,
        log_weights,
        0.95,
        tail_probability=0.05,
        error="contamination",
        sigma_r=sigma_r,
    )
    assert contaminated["quantile_log_rul"] > normal["quantile_log_rul"]


def test_invalid_shapes_and_batch_counts_are_rejected():
    values = np.zeros((2, 64))
    with pytest.raises(ValueError, match="share shape"):
        estimate_mixture_quantile_mcse(
            values, values[:, :-1], values, 0.5, tail_probability=0.05
        )
    with pytest.raises(ValueError, match="two distinct"):
        estimate_mixture_quantile_mcse(
            values,
            np.ones_like(values),
            values,
            0.5,
            tail_probability=0.05,
            batch_sizes=(8, 8),
        )
    with pytest.raises(ValueError, match="positive infinity"):
        invalid_weights = values.copy()
        invalid_weights[0, 0] = np.inf
        estimate_mixture_quantile_mcse(
            values,
            np.ones_like(values),
            invalid_weights,
            0.5,
            tail_probability=0.05,
        )
