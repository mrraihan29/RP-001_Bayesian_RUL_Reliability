"""Paired bootstrap-t operating-characteristic framework for RP-001.

No project data are read here. A call to run_operating_characteristics creates
synthetic engine-level paired differences only; it does not run on benchmark
predictions or change the project's confirmatory status.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from pathlib import Path
from statistics import NormalDist
from time import perf_counter
from typing import Any, Mapping
import platform
import sys

import numpy as np


SCENARIOS = (
    "normal",
    "centered_lognormal_sigma1",
    "centered_lognormal_sigma1p5",
    "student_t3",
    "rare_outlier_mixture",
    "student_t1p5_infinite_variance",
    "sparse_discrete_pm1",
    "all_zero",
)

SCENARIO_DEFINITIONS: dict[str, dict[str, Any]] = {
    "normal": {"distribution": "N(0, 1)", "mean": 0.0, "variance": 1.0,
               "parameters": {"loc": 0.0, "scale": 1.0}, "stress_only": False},
    "centered_lognormal_sigma1": {
        "distribution": "Lognormal(0,1) - exp(1/2)", "mean": 0.0,
        "variance": float((np.exp(1.0) - 1.0) * np.exp(1.0)),
        "parameters": {"log_mean": 0.0, "log_sigma": 1.0, "centering_constant": float(np.exp(0.5))},
        "stress_only": False,
    },
    "centered_lognormal_sigma1p5": {
        "distribution": "Lognormal(0,1.5) - exp(1.125)", "mean": 0.0,
        "variance": float((np.exp(2.25) - 1.0) * np.exp(2.25)),
        "parameters": {"log_mean": 0.0, "log_sigma": 1.5, "centering_constant": float(np.exp(1.125))},
        "stress_only": False,
    },
    "student_t3": {"distribution": "Student-t(df=3, loc=0, scale=1)", "mean": 0.0,
                    "variance": 3.0, "parameters": {"df": 3.0, "loc": 0.0, "scale": 1.0},
                    "stress_only": False},
    "rare_outlier_mixture": {
        "distribution": "0.99*N(0,1) + 0.01*N(0,30^2)", "mean": 0.0,
        "variance": 9.99, "parameters": {"outlier_probability": 0.01, "base_sd": 1.0, "outlier_sd": 30.0},
        "stress_only": False,
    },
    "student_t1p5_infinite_variance": {
        "distribution": "Student-t(df=1.5, loc=0, scale=1)", "mean": 0.0,
        "variance": None, "parameters": {"df": 1.5, "loc": 0.0, "scale": 1.0},
        "stress_only": True,
    },
    "sparse_discrete_pm1": {
        "distribution": "P(-1)=0.01, P(0)=0.98, P(+1)=0.01", "mean": 0.0,
        "variance": 0.02, "parameters": {"probability_minus_one": 0.01, "probability_zero": 0.98,
                                         "probability_plus_one": 0.01}, "stress_only": True,
    },
    "all_zero": {"distribution": "point mass at 0", "mean": 0.0, "variance": 0.0,
                  "parameters": {}, "stress_only": True},
}


@dataclass(frozen=True)
class NumericalPolicy:
    """Numerical choices; undefined pivots always fail, never get dropped."""

    quantile_method: str = "linear"
    resampling_chunk_size: int = 256
    dtype: str = "float64"
    zero_standard_error_policy: str = "invalidate_replicate_if_any_zero"
    nonfinite_policy: str = "invalidate_replicate"


@dataclass(frozen=True)
class OperatingCharacteristicsConfig:
    """Prospective run settings. Seeds are required separately for all scenarios."""

    nsim: int
    bootstrap_count: int
    scenario_seeds: Mapping[str, int]
    n: int = 100
    numerical_policy: NumericalPolicy = field(default_factory=NumericalPolicy)


def _finite_vector(values: Any, *, name: str = "paired differences") -> np.ndarray:
    try:
        x = np.asarray(values, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a one-dimensional finite numeric vector") from exc
    if x.ndim != 1 or x.size < 2:
        raise ValueError(f"{name} must be one-dimensional with at least two paired engines")
    if not np.isfinite(x).all():
        raise ValueError(f"{name} contains NaN or infinite values; retain the failure and resolve it")
    return x


def finite_benchmark_mean(paired_differences: Any) -> dict[str, Any]:
    """Return the exact observed finite-benchmark average when every pair is finite."""
    x = _finite_vector(paired_differences)
    value = float(np.mean(x, dtype=np.float64))
    if not np.isfinite(value):
        raise ValueError("finite-benchmark mean overflowed; preserve as an input failure")
    return {
        "estimand": "arithmetic mean of the complete set of stored per-engine paired differences",
        "n_paired_engines": int(x.size),
        "mean_difference": value,
        "is_exact_for_supplied_finite_benchmark": True,
        "population_inference_performed": False,
    }


def _influence_diagnostics(x: np.ndarray, mean: float, standard_error: float) -> dict[str, Any]:
    centered_abs = np.abs(x - mean)
    contribution_sum = float(np.sum(centered_abs, dtype=np.float64))
    if np.isfinite(contribution_sum) and contribution_sum > 0.0:
        max_share: float | None = float(np.max(centered_abs) / contribution_sum)
    else:
        max_share = None

    if np.isfinite(standard_error) and standard_error > 0.0:
        loo_shifts = np.abs((mean - x) / (x.size - 1)) / standard_error
        max_loo: float | None = float(np.max(loo_shifts)) if np.isfinite(loo_shifts).all() else None
    else:
        max_loo = None
    return {
        "max_abs_centered_contribution_share": max_share,
        "max_leave_one_out_mean_shift_in_sample_se_units": max_loo,
        "leave_one_out_shift_formula": "max_i |mean(x[-i])-mean(x)| / (sd(x, ddof=1)/sqrt(n))",
    }


def paired_bootstrap_t(
    paired_differences: Any,
    *,
    bootstrap_count: int,
    seed: int,
    numerical_policy: NumericalPolicy | None = None,
) -> dict[str, Any]:
    """Compute a paired engine bootstrap-t interval and upper bound.

    T*=(mean(x*)-mean(x))/SE(x*). The two-sided interval is
    [mean(x)-q(.975)SE(x), mean(x)-q(.025)SE(x)]; the one-sided upper bound
    is mean(x)-q(.05)SE(x) for H0: population mean >= 0 versus mean < 0.
    Any zero or nonfinite bootstrap standard error invalidates the replicate;
    no bootstrap draws are silently removed.
    """
    x = _finite_vector(paired_differences)
    if isinstance(bootstrap_count, bool) or not isinstance(bootstrap_count, (int, np.integer)) or bootstrap_count < 1:
        raise ValueError("bootstrap_count must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    policy = numerical_policy or NumericalPolicy()
    _validate_numerical_policy(policy)

    n = int(x.size)
    b_count = int(bootstrap_count)
    seed = int(seed)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        mean = float(np.mean(x, dtype=np.float64))
        sample_sd = float(np.std(x, ddof=1, dtype=np.float64))
        se = float(sample_sd / np.sqrt(n))
    result: dict[str, Any] = {
        "status": "ok",
        "n": n,
        "bootstrap_count_requested": b_count,
        "bootstrap_seed": seed,
        "sample_mean": mean if np.isfinite(mean) else None,
        "sample_standard_error": se if np.isfinite(se) else None,
        "bootstrap_zero_standard_error_draws": 0,
        "bootstrap_nonfinite_draws": 0,
        "bootstrap_draws_attempted": 0,
        "bootstrap_zero_standard_error_fraction": None,
        "interval_lower_95": None,
        "interval_upper_95": None,
        "one_sided_upper_95": None,
        "contains_zero": None,
        "reject_h0_mean_ge_zero": None,
        "numerical_policy": asdict(policy),
        "influence": _influence_diagnostics(x, mean, se) if np.isfinite(mean) else {
            "max_abs_centered_contribution_share": None,
            "max_leave_one_out_mean_shift_in_sample_se_units": None,
        },
    }
    if not np.isfinite(mean) or not np.isfinite(se):
        result["status"] = "nonfinite_observed_statistic"
        return result

    rng = np.random.default_rng(seed)
    pivots = np.empty(b_count, dtype=np.float64)
    zero_se_count = 0
    nonfinite_count = 0
    cursor = 0
    while cursor < b_count:
        batch = min(policy.resampling_chunk_size, b_count - cursor)
        indices = rng.integers(0, n, size=(batch, n), endpoint=False)
        draws = x[indices]
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            draw_means = np.mean(draws, axis=1, dtype=np.float64)
            draw_sds = np.std(draws, axis=1, ddof=1, dtype=np.float64)
            draw_ses = draw_sds / np.sqrt(n)
            numerators = draw_means - mean
            bad_numeric = ~np.isfinite(draw_means) | ~np.isfinite(draw_ses) | ~np.isfinite(numerators)
            zero_se = (draw_ses == 0.0) & ~bad_numeric
            good = ~(bad_numeric | zero_se)
            batch_pivots = np.full(batch, np.nan, dtype=np.float64)
            batch_pivots[good] = numerators[good] / draw_ses[good]
            bad_pivot = ~np.isfinite(batch_pivots) & good
        zero_se_count += int(np.count_nonzero(zero_se))
        nonfinite_count += int(np.count_nonzero(bad_numeric | bad_pivot))
        pivots[cursor:cursor + batch] = batch_pivots
        cursor += batch

    result["bootstrap_zero_standard_error_draws"] = zero_se_count
    result["bootstrap_nonfinite_draws"] = nonfinite_count
    result["bootstrap_draws_attempted"] = b_count
    result["bootstrap_zero_standard_error_fraction"] = zero_se_count / b_count
    if se == 0.0:
        result["status"] = "zero_observed_standard_error"
        return result
    if zero_se_count:
        result["status"] = "zero_bootstrap_standard_error"
        return result
    if nonfinite_count or not np.isfinite(pivots).all():
        result["status"] = "nonfinite_bootstrap_pivot"
        return result

    q025, q05, q975 = np.quantile(
        pivots, [0.025, 0.05, 0.975], method=policy.quantile_method
    )
    with np.errstate(over="ignore", invalid="ignore"):
        lower = float(mean - q975 * se)
        upper = float(mean - q025 * se)
        one_sided_upper = float(mean - q05 * se)
    if not np.isfinite([lower, upper, one_sided_upper]).all():
        result["status"] = "nonfinite_interval_endpoint"
        return result
    result.update({
        "interval_lower_95": lower,
        "interval_upper_95": upper,
        "one_sided_upper_95": one_sided_upper,
        "contains_zero": bool(lower <= 0.0 <= upper),
        "reject_h0_mean_ge_zero": bool(one_sided_upper < 0.0),
    })
    return result


def _validate_numerical_policy(policy: NumericalPolicy) -> None:
    if not isinstance(policy, NumericalPolicy):
        raise ValueError("numerical_policy must be a NumericalPolicy")
    if policy.dtype != "float64":
        raise ValueError("Only float64 computation is supported")
    if policy.zero_standard_error_policy != "invalidate_replicate_if_any_zero":
        raise ValueError("Zero-SE bootstrap draws must invalidate the replicate; dropping draws is unsupported")
    if policy.nonfinite_policy != "invalidate_replicate":
        raise ValueError("Nonfinite inputs or pivots must invalidate the replicate")
    if isinstance(policy.resampling_chunk_size, bool) or not isinstance(policy.resampling_chunk_size, int) or policy.resampling_chunk_size < 1:
        raise ValueError("resampling_chunk_size must be a positive integer")
    try:
        np.quantile(np.array([0.0, 1.0]), [0.5], method=policy.quantile_method)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Unsupported NumPy quantile method: {policy.quantile_method!r}") from exc


def _draw_sample(name: str, n: int, rng: np.random.Generator) -> np.ndarray:
    if name == "normal":
        return rng.normal(0.0, 1.0, size=n)
    if name == "centered_lognormal_sigma1":
        return rng.lognormal(0.0, 1.0, size=n) - np.exp(0.5)
    if name == "centered_lognormal_sigma1p5":
        return rng.lognormal(0.0, 1.5, size=n) - np.exp(1.125)
    if name == "student_t3":
        return rng.standard_t(3.0, size=n)
    if name == "rare_outlier_mixture":
        outlier = rng.random(n) < 0.01
        values = rng.normal(0.0, 1.0, size=n)
        values[outlier] = rng.normal(0.0, 30.0, size=int(np.count_nonzero(outlier)))
        return values
    if name == "student_t1p5_infinite_variance":
        return rng.standard_t(1.5, size=n)
    if name == "sparse_discrete_pm1":
        return rng.choice(np.array([-1.0, 0.0, 1.0]), size=n, p=[0.01, 0.98, 0.01])
    if name == "all_zero":
        return np.zeros(n, dtype=np.float64)
    raise ValueError(f"Unknown scenario: {name}")


def _validate_config(config: OperatingCharacteristicsConfig) -> None:
    if not isinstance(config, OperatingCharacteristicsConfig):
        raise ValueError("config must be an OperatingCharacteristicsConfig")
    for name, value, minimum in (("nsim", config.nsim, 1), ("bootstrap_count", config.bootstrap_count, 1), ("n", config.n, 2)):
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(f"{name} must be an integer >= {minimum}")
    if not isinstance(config.scenario_seeds, Mapping):
        raise ValueError("scenario_seeds must map every scenario to an integer seed")
    missing = sorted(set(SCENARIOS) - set(config.scenario_seeds))
    extra = sorted(set(config.scenario_seeds) - set(SCENARIOS))
    if missing or extra:
        raise ValueError(f"scenario_seeds must cover exactly all eight scenarios; missing={missing}, extra={extra}")
    for name, seed in config.scenario_seeds.items():
        if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) or seed < 0:
            raise ValueError(f"scenario seed for {name} must be a nonnegative integer")
    _validate_numerical_policy(config.numerical_policy)


def _wilson_summary(successes: int, trials: int, confidence: float = 0.95) -> dict[str, Any]:
    if trials < 1:
        return {"successes": int(successes), "trials": int(trials), "proportion": None,
                "binomial_mcse": None, "wilson_interval": None}
    p = successes / trials
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    z2 = z * z
    denominator = 1.0 + z2 / trials
    center = (p + z2 / (2.0 * trials)) / denominator
    half = z * np.sqrt((p * (1.0 - p) / trials) + z2 / (4.0 * trials * trials)) / denominator
    return {
        "successes": int(successes),
        "trials": int(trials),
        "proportion": float(p),
        "binomial_mcse": float(np.sqrt(p * (1.0 - p) / trials)),
        "wilson_interval": [float(max(0.0, center - half)), float(min(1.0, center + half))],
    }


def _quantile_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"n_defined": 0, "median": None, "p95": None, "maximum": None}
    return {"n_defined": len(values), "median": float(np.quantile(values, 0.5)),
            "p95": float(np.quantile(values, 0.95)), "maximum": float(np.max(values))}


def _scenario_summary(name: str, records: list[dict[str, Any]], elapsed: float,
                       bootstrap_count: int) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for row in records:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    valid = [row for row in records if row["status"] == "ok"]
    zero_draws = sum(row["bootstrap_zero_standard_error_draws"] for row in records)
    draw_attempts = sum(row["bootstrap_draws_attempted"] for row in records)
    all_zero_se = sum(row["status"] == "zero_observed_standard_error" for row in records)
    any_zero_draw = sum(row["bootstrap_zero_standard_error_draws"] > 0 for row in records)
    influence_share = [row["influence"]["max_abs_centered_contribution_share"] for row in records
                       if row.get("influence", {}).get("max_abs_centered_contribution_share") is not None]
    loo_shift = [row["influence"]["max_leave_one_out_mean_shift_in_sample_se_units"] for row in records
                 if row.get("influence", {}).get("max_leave_one_out_mean_shift_in_sample_se_units") is not None]
    covered = sum(bool(row["contains_zero"]) for row in valid)
    rejected = sum(bool(row["reject_h0_mean_ge_zero"]) for row in valid)
    return {
        "scenario": name,
        "definition": SCENARIO_DEFINITIONS[name],
        "nsim_attempted": len(records),
        "nsim_interval_available": len(valid),
        "simulation_failure_counts_by_status": status_counts,
        "coverage_95_conditional_on_interval_available": _wilson_summary(covered, len(valid)),
        "one_sided_h0_mean_ge_zero_rejection_conditional_on_interval_available": _wilson_summary(rejected, len(valid)),
        "interval_availability": _wilson_summary(len(valid), len(records)),
        "bootstrap_count_per_valid_generated_dataset": bootstrap_count,
        "bootstrap_zero_standard_error_draws_total": int(zero_draws),
        "bootstrap_draws_attempted_total": int(draw_attempts),
        "bootstrap_zero_standard_error_fraction": float(zero_draws / draw_attempts) if draw_attempts else None,
        "simulations_with_any_zero_bootstrap_se_draw": int(any_zero_draw),
        "simulations_with_zero_observed_se": int(all_zero_se),
        "bootstrap_nonfinite_draws_total": int(sum(row["bootstrap_nonfinite_draws"] for row in records)),
        "influence_max_abs_centered_contribution_share": _quantile_summary(influence_share),
        "influence_max_leave_one_out_mean_shift_in_se_units": _quantile_summary(loo_shift),
        "elapsed_seconds": float(elapsed),
        "nominal_interpretation": (
            "Stress-only diagnostic; do not interpret as conventional variance-based bootstrap coverage"
            if SCENARIO_DEFINITIONS[name]["stress_only"] else
            "Conditional on interval availability; failures and zero-SE fractions are separately retained"
        ),
    }


def run_operating_characteristics(config: OperatingCharacteristicsConfig) -> dict[str, Any]:
    """Run every registered synthetic scenario and retain every replicate row.

    Seeds are split deterministically by scenario and replicate into independent
    sample-generation and bootstrap streams. No generated data or result is saved
    to disk; the caller decides where a prospectively authorized result belongs.
    """
    _validate_config(config)
    run_start = perf_counter()
    records: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []

    for scenario in SCENARIOS:
        scenario_start = perf_counter()
        scenario_records: list[dict[str, Any]] = []
        root_seed = int(config.scenario_seeds[scenario])
        for simulation_index in range(config.nsim):
            replicate_start = perf_counter()
            replicate_sequence = np.random.SeedSequence(root_seed, spawn_key=(simulation_index,))
            sample_sequence, bootstrap_sequence = replicate_sequence.spawn(2)
            sample_seed = int(sample_sequence.generate_state(1, dtype=np.uint64)[0])
            bootstrap_seed = int(bootstrap_sequence.generate_state(1, dtype=np.uint64)[0])
            base: dict[str, Any] = {
                "scenario": scenario,
                "simulation_index": simulation_index,
                "root_scenario_seed": root_seed,
                "sample_seed": sample_seed,
                "bootstrap_seed": bootstrap_seed,
                "status": "input_failure",
                "sample_mean": None,
                "sample_standard_error": None,
                "interval_lower_95": None,
                "interval_upper_95": None,
                "one_sided_upper_95": None,
                "contains_zero": None,
                "reject_h0_mean_ge_zero": None,
                "bootstrap_zero_standard_error_draws": 0,
                "bootstrap_nonfinite_draws": 0,
                "bootstrap_draws_attempted": 0,
                "bootstrap_zero_standard_error_fraction": None,
                "influence": {"max_abs_centered_contribution_share": None,
                              "max_leave_one_out_mean_shift_in_sample_se_units": None},
                "failure_type": None,
                "failure_message": None,
            }
            try:
                sample = _draw_sample(scenario, config.n, np.random.default_rng(sample_seed))
                x = _finite_vector(sample, name=f"generated sample for {scenario}")
                inferred = paired_bootstrap_t(
                    x,
                    bootstrap_count=config.bootstrap_count,
                    seed=bootstrap_seed,
                    numerical_policy=config.numerical_policy,
                )
                base.update({key: inferred[key] for key in (
                    "status", "sample_mean", "sample_standard_error", "interval_lower_95",
                    "interval_upper_95", "one_sided_upper_95", "contains_zero",
                    "reject_h0_mean_ge_zero", "bootstrap_zero_standard_error_draws",
                    "bootstrap_nonfinite_draws", "bootstrap_draws_attempted",
                    "bootstrap_zero_standard_error_fraction", "influence",
                )})
                base["failure_type"] = None if inferred["status"] == "ok" else inferred["status"]
                base["failure_message"] = None if inferred["status"] == "ok" else inferred["status"]
            except (ValueError, TypeError, FloatingPointError, OverflowError) as exc:
                base["failure_type"] = type(exc).__name__
                base["failure_message"] = str(exc)
            except Exception as exc:  # Retain unexpected worker/runtime failures as rows.
                base["status"] = "unexpected_error"
                base["failure_type"] = type(exc).__name__
                base["failure_message"] = str(exc)
            base["elapsed_seconds"] = float(perf_counter() - replicate_start)
            scenario_records.append(base)
            records.append(base)
        scenario_elapsed = perf_counter() - scenario_start
        summaries.append(_scenario_summary(scenario, scenario_records, scenario_elapsed, config.bootstrap_count))

    module_hash = sha256(Path(__file__).read_bytes()).hexdigest()
    total_elapsed = perf_counter() - run_start
    return {
        "schema_version": "rp001.v04.paired_bootstrap_t_oc.v1",
        "analysis_class": "exploratory_synthetic_operating_characteristics",
        "confirmatory": False,
        "official_test_access": False,
        "primary_estimand_boundary": (
            "The primary benchmark effect is the exact arithmetic mean of the complete paired stored-prediction differences. "
            "This simulation's population inference is a secondary conditional diagnostic only."
        ),
        "configuration": {
            "n": int(config.n),
            "nsim_per_scenario": int(config.nsim),
            "bootstrap_count": int(config.bootstrap_count),
            "confidence_level": 0.95,
            "one_sided_hypothesis": "H0: population mean >= 0 versus H1: population mean < 0",
            "scenario_seeds": {name: int(config.scenario_seeds[name]) for name in SCENARIOS},
            "seed_derivation": "SeedSequence(root_scenario_seed, spawn_key=(simulation_index,)).spawn(2); generated uint64 sample/bootstrap seeds",
            "bit_generator": "PCG64 via numpy.random.default_rng",
            "scenarios": {name: SCENARIO_DEFINITIONS[name] for name in SCENARIOS},
            "numerical_policy": asdict(config.numerical_policy),
            "paired_bootstrap_t": {
                "pivot": "T*=(mean(x*)-mean(x))/(sd(x*,ddof=1)/sqrt(n))",
                "standard_error": "sd(x,ddof=1)/sqrt(n)",
                "two_sided_interval": "[mean(x)-q(.975)*SE, mean(x)-q(.025)*SE]",
                "one_sided_upper": "mean(x)-q(.05)*SE",
                "zero_or_nonfinite_bootstrap_se": "invalidate replicate; retain every draw count; never drop invalid draws",
            },
        },
        "results_by_scenario": summaries,
        "simulation_records": records,
        "failure_counts": {
            "attempted": len(records),
            "completed_with_interval": sum(row["status"] == "ok" for row in records),
            "failed_or_unavailable": sum(row["status"] != "ok" for row in records),
            "by_status": {status: sum(row["status"] == status for row in records)
                          for status in sorted({row["status"] for row in records})},
            "input_failures": sum(row["failure_type"] in {"ValueError", "TypeError", "FloatingPointError", "OverflowError"}
                                  for row in records),
            "unexpected_errors": sum(row["status"] == "unexpected_error" for row in records),
        },
        "runtime": {
            "total_elapsed_seconds": float(total_elapsed),
            "scenario_elapsed_seconds": {row["scenario"]: row["elapsed_seconds"] for row in summaries},
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy_version": np.__version__,
            "module_sha256": module_hash,
        },
        "interpretation_limits": [
            "The synthetic engine pairs are iid from the named law; this does not establish independence or law adequacy for real engines.",
            "Coverage and rejection Wilson intervals and binomial MCSE condition on simulations with an available interval; availability and all failures are reported separately.",
            "Inner bootstrap Monte Carlo error is not included in the outer binomial MCSE.",
            "The Student-t(1.5) mean exists but variance is infinite; its rates are stress diagnostics, not a variance-regularity certification.",
            "The sparse discrete and all-zero cases expose ties and degenerate standard errors; no trimming, winsorization, omission, imputation, or favorable fallback is used.",
            "No synthetic operating characteristic is a result for the official FD001 benchmark or evidence of superiority.",
        ],
    }
