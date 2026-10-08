import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pytest

from rp001.v04_inference import (
    SCENARIOS,
    NumericalPolicy,
    OperatingCharacteristicsConfig,
    finite_benchmark_mean,
    paired_bootstrap_t,
    run_operating_characteristics,
)


def test_bootstrap_t_uses_centered_pivot_and_correct_endpoint_signs():
    x = np.array([-3.2, -1.7, -0.9, -0.2, 0.1, 0.6, 1.3, 1.9, 2.4, 3.8, 4.7, 7.1])
    count, seed = 181, 9431
    policy = NumericalPolicy(resampling_chunk_size=23)
    observed = paired_bootstrap_t(x, bootstrap_count=count, seed=seed, numerical_policy=policy)

    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(x), size=(count, len(x)), endpoint=False)
    draws = x[indices]
    means = draws.mean(axis=1)
    ses = draws.std(axis=1, ddof=1) / np.sqrt(len(x))
    pivots = (means - x.mean()) / ses
    q025, q05, q975 = np.quantile(pivots, [0.025, 0.05, 0.975], method="linear")
    se = x.std(ddof=1) / np.sqrt(len(x))

    assert observed["status"] == "ok"
    assert observed["bootstrap_zero_standard_error_draws"] == 0
    assert observed["interval_lower_95"] == pytest.approx(x.mean() - q975 * se)
    assert observed["interval_upper_95"] == pytest.approx(x.mean() - q025 * se)
    assert observed["one_sided_upper_95"] == pytest.approx(x.mean() - q05 * se)
    assert observed["reject_h0_mean_ge_zero"] is (observed["one_sided_upper_95"] < 0.0)


def test_finite_benchmark_mean_is_exact_and_has_no_population_claim():
    result = finite_benchmark_mean([-2.0, 0.0, 1.0, 5.0])
    assert result["n_paired_engines"] == 4
    assert result["mean_difference"] == 1.0
    assert result["is_exact_for_supplied_finite_benchmark"] is True
    assert result["population_inference_performed"] is False


def test_all_zero_case_retains_every_zero_se_draw_and_fails_closed():
    result = paired_bootstrap_t(
        np.zeros(100), bootstrap_count=17, seed=17,
        numerical_policy=NumericalPolicy(resampling_chunk_size=5),
    )
    assert result["status"] == "zero_observed_standard_error"
    assert result["bootstrap_draws_attempted"] == 17
    assert result["bootstrap_zero_standard_error_draws"] == 17
    assert result["bootstrap_zero_standard_error_fraction"] == 1.0
    assert result["interval_lower_95"] is None
    assert result["one_sided_upper_95"] is None


def test_nonfinite_paired_inputs_are_retained_as_failures():
    with pytest.raises(ValueError, match="NaN or infinite"):
        finite_benchmark_mean([1.0, float("nan"), 2.0])
    with pytest.raises(ValueError, match="NaN or infinite"):
        paired_bootstrap_t([0.0, float("inf")], bootstrap_count=20, seed=5)


def test_small_debug_run_records_all_scenarios_and_degenerate_failures():
    config = OperatingCharacteristicsConfig(
        n=100,
        nsim=1,
        bootstrap_count=13,
        scenario_seeds={name: 1200 + index for index, name in enumerate(SCENARIOS)},
        numerical_policy=NumericalPolicy(resampling_chunk_size=7),
    )
    result = run_operating_characteristics(config)
    assert result["confirmatory"] is False
    assert result["official_test_access"] is False
    assert [row["scenario"] for row in result["results_by_scenario"]] == list(SCENARIOS)
    assert len(result["simulation_records"]) == len(SCENARIOS)
    assert result["configuration"]["scenario_seeds"] == dict(config.scenario_seeds)
    all_zero = next(row for row in result["simulation_records"] if row["scenario"] == "all_zero")
    assert all_zero["status"] == "zero_observed_standard_error"
    assert all_zero["bootstrap_zero_standard_error_fraction"] == 1.0
    assert result["failure_counts"]["failed_or_unavailable"] >= 1
    normal = next(row for row in result["results_by_scenario"] if row["scenario"] == "normal")
    assert normal["coverage_95_conditional_on_interval_available"]["wilson_interval"] is not None
    assert normal["coverage_95_conditional_on_interval_available"]["binomial_mcse"] is not None
