"""Approximate Monte Carlo uncertainty for sensor-reweighted log-RUL mixtures.

The estimator targets the quantile of the self-normalized, importance-weighted
mixture CDF. Its uncertainty uses chain-wise non-overlapping batch means for
the delta-method influence series; it is a finite-asymptotic diagnostic, not a
guaranteed error bound.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.optimize import brentq
from scipy.special import ndtr
from scipy.stats import chi2, norm


def _component_variances(
    variances: np.ndarray,
    sigma_r: np.ndarray | None,
    error: str,
) -> tuple[np.ndarray, ...]:
    if error == "normal":
        return (variances,)
    if error != "contamination":
        raise ValueError("error must be 'normal' or 'contamination'")
    if sigma_r is None:
        raise ValueError("sigma_r is required for the contamination error model")
    try:
        residual_sd = np.broadcast_to(np.asarray(sigma_r, dtype=np.float64), variances.shape)
    except ValueError as exc:
        raise ValueError("sigma_r must be scalar or broadcastable to (chain, draw)") from exc
    if not np.all(np.isfinite(residual_sd)) or np.any(residual_sd < 0):
        raise ValueError("sigma_r must contain finite, nonnegative values")
    with np.errstate(over="ignore", invalid="ignore"):
        broad_variance = variances + 8.0 * residual_sd**2
    if not np.all(np.isfinite(broad_variance)):
        raise ValueError("derived contamination variances must be finite")
    return variances, broad_variance


def _conditional_cdf_and_density(
    x: float,
    means: np.ndarray,
    component_variances: tuple[np.ndarray, ...],
    error: str,
) -> tuple[np.ndarray, np.ndarray]:
    component_cdfs = []
    component_densities = []
    for variance in component_variances:
        sd = np.sqrt(variance)
        standardized = (x - means) / sd
        component_cdfs.append(ndtr(standardized))
        component_densities.append(
            np.exp(-0.5 * standardized**2 - 0.5 * np.log(2.0 * np.pi) - np.log(sd))
        )
    if error == "contamination":
        cdf = 0.95 * component_cdfs[0] + 0.05 * component_cdfs[1]
        density = 0.95 * component_densities[0] + 0.05 * component_densities[1]
        return cdf, density
    return component_cdfs[0], component_densities[0]


def _weighted_quantile(
    means: np.ndarray,
    component_variances: tuple[np.ndarray, ...],
    normalized_weights: np.ndarray,
    probability: float,
    error: str,
) -> tuple[float, float, float]:
    flat_means = means.reshape(-1)
    flat_weights = normalized_weights.reshape(-1)
    flat_variances = tuple(v.reshape(-1) for v in component_variances)

    def cdf_at(x: float) -> float:
        cdf, _ = _conditional_cdf_and_density(x, flat_means, flat_variances, error)
        return float(np.dot(flat_weights, cdf))

    min_mean = float(np.min(flat_means))
    max_mean = float(np.max(flat_means))
    max_sd = max(float(np.sqrt(np.max(v))) for v in flat_variances)
    z_abs = abs(float(norm.ppf(probability)))
    radius = (z_abs + 12.0) * max_sd + (max_mean - min_mean)
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("could not construct a finite quantile bracket")

    lower = min_mean - radius
    upper = max_mean + radius
    for _ in range(100):
        lower_cdf = cdf_at(lower)
        upper_cdf = cdf_at(upper)
        if lower_cdf <= probability <= upper_cdf:
            break
        radius *= 2.0
        if not np.isfinite(radius):
            raise ValueError("mixture quantile could not be bracketed finitely")
        lower = min_mean - radius
        upper = max_mean + radius
    else:
        raise ValueError("mixture quantile could not be bracketed")

    quantile = float(brentq(
        lambda x: cdf_at(x) - probability,
        lower,
        upper,
        xtol=1e-12,
        rtol=4.0 * np.finfo(np.float64).eps,
    ))
    conditional_cdf, conditional_density = _conditional_cdf_and_density(
        quantile, flat_means, flat_variances, error
    )
    mixture_cdf = float(np.dot(flat_weights, conditional_cdf))
    mixture_density = float(np.dot(flat_weights, conditional_density))
    return quantile, mixture_cdf, mixture_density


def _batch_means_lrv(values: np.ndarray, batch_size: int) -> dict[str, float | int]:
    """Estimate one chain's long-run variance by non-overlapping batch means."""
    series = np.asarray(values, dtype=np.float64)
    if series.ndim != 1:
        raise ValueError("values must be one-dimensional")
    if isinstance(batch_size, bool) or int(batch_size) != batch_size or batch_size < 1:
        raise ValueError("batch_size must be a positive integer")
    batch_size = int(batch_size)
    batch_count = len(series) // batch_size
    if batch_count < 2:
        raise ValueError("each chain needs at least two complete batches")
    used = batch_count * batch_size
    batch_means = series[:used].reshape(batch_count, batch_size).mean(axis=1)
    batch_mean_variance = float(np.var(batch_means, ddof=1))
    lrv = float(batch_size * batch_mean_variance)
    return {
        "lrv": lrv,
        "batch_mean_variance": batch_mean_variance,
        "batch_count": batch_count,
        "degrees_of_freedom": batch_count - 1,
        "draws_used": used,
        "draws_dropped": len(series) - used,
    }


def _default_batch_sizes(draws_per_chain: int) -> tuple[int, int]:
    max_size = draws_per_chain // 2
    first = max(1, int(draws_per_chain ** (1.0 / 3.0)))
    second = max(first + 1, int(np.sqrt(draws_per_chain)))
    second = min(second, max_size)
    first = min(first, second - 1)
    if first < 1 or second <= first:
        raise ValueError("at least four draws per chain are required")
    return first, second


def _validate_batch_sizes(
    batch_sizes: Sequence[int] | None, draws_per_chain: int
) -> tuple[int, int]:
    selected = _default_batch_sizes(draws_per_chain) if batch_sizes is None else tuple(batch_sizes)
    if len(selected) != 2:
        raise ValueError("batch_sizes must contain exactly two distinct batch sizes")
    if any(isinstance(b, bool) or int(b) != b or b < 1 for b in selected):
        raise ValueError("batch sizes must be positive integers")
    first, second = (int(selected[0]), int(selected[1]))
    if first == second:
        raise ValueError("batch_sizes must contain two distinct values")
    if max(first, second) > draws_per_chain // 2:
        raise ValueError("each batch size must yield at least two batches per chain")
    return first, second


def estimate_mixture_quantile_mcse(
    means: np.ndarray,
    variances: np.ndarray,
    log_weights: np.ndarray,
    probability: float,
    *,
    tail_probability: float,
    batch_sizes: Sequence[int] | None = None,
    error: str = "normal",
    sigma_r: np.ndarray | float | None = None,
) -> dict[str, object]:
    """Estimate quantile MCSE for a self-normalized importance-weighted mixture.

    Parameters
    ----------
    means, variances, log_weights
        Arrays shaped (chain, draw). Means and variances parameterize each
        conditional Gaussian distribution on log RUL. Log weights are the
        sensor-only importance log likelihoods.
    probability
        Mixture CDF quantile probability, strictly between zero and one.
    tail_probability
        Lower-tail probability used in the chi-square approximation to the
        upper variance bound. For example, 0.05 requests an approximate
        95-percent upper MCSE.
    batch_sizes
        Two distinct batch sizes for the stability diagnostic. If omitted,
        deterministic cube-root and square-root choices are derived from the
        shortest chain. The first is reported as the primary estimate.
    error, sigma_r
        Use error='normal' for a single component. For error='contamination',
        integrate 0.95 N(mean, variance) + 0.05 N(mean, variance + 8*sigma_r^2),
        matching the model's residual contamination parameterization.

    Notes
    -----
    The log-RUL quantile is obtained by solving the weighted mixture CDF
    directly; conditional quantiles are never averaged. For chain c, let
    h_ct = w_ct [F_ct(q) - probability], where w is globally scaled by the
    largest log weight. The reported log-scale variance estimate is

        sum_c n_c LRV_c / (N^2 mean(w)^2 f(q)^2),

    where LRV_c is a non-overlapping batch-means estimate and f is the
    weighted mixture density on log RUL. Cycle-scale MCSEs use the derivative
    exp(q_log) of the exponential transform.
    """
    mu = np.asarray(means, dtype=np.float64)
    var = np.asarray(variances, dtype=np.float64)
    logw = np.asarray(log_weights, dtype=np.float64)
    if mu.ndim != 2 or var.shape != mu.shape or logw.shape != mu.shape:
        raise ValueError("means, variances, and log_weights must share shape (chain, draw)")
    if mu.shape[0] < 1 or mu.shape[1] < 4:
        raise ValueError("at least one chain and four draws per chain are required")
    if not np.all(np.isfinite(mu)):
        raise ValueError("means must be finite")
    if not np.all(np.isfinite(var)) or np.any(var <= 0):
        raise ValueError("variances must be finite and strictly positive")
    if np.any(np.isnan(logw)) or np.any(np.isposinf(logw)):
        raise ValueError("log_weights may be finite or negative infinity, but not NaN or positive infinity")
    if not np.any(np.isfinite(logw)):
        raise ValueError("at least one importance log weight must be finite")
    if not np.isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError("probability must be finite and strictly between zero and one")
    if not np.isfinite(tail_probability) or not 0.0 < tail_probability < 1.0:
        raise ValueError("tail_probability must be finite and strictly between zero and one")

    batches = _validate_batch_sizes(batch_sizes, mu.shape[1])
    component_variances = _component_variances(var, sigma_r, error)
    max_log_weight = float(np.max(logw[np.isfinite(logw)]))
    scaled_weights = np.exp(logw - max_log_weight)
    weight_sum = float(np.sum(scaled_weights))
    n_total = int(mu.size)
    mean_weight = weight_sum / n_total
    if not np.isfinite(weight_sum) or weight_sum <= 0 or not np.isfinite(mean_weight):
        raise ValueError("importance weight normalizer is not finite and positive")
    normalized_weights = scaled_weights / weight_sum

    log_quantile, cdf_at_quantile, density = _weighted_quantile(
        mu, component_variances, normalized_weights, float(probability), error
    )
    if not np.isfinite(log_quantile) or not np.isfinite(density) or density <= 0:
        raise ValueError("mixture quantile and density must be finite, with positive density")
    rul_quantile = float(np.exp(log_quantile))
    if not np.isfinite(rul_quantile) or rul_quantile <= 0:
        raise ValueError("RUL-scale quantile is not finite and positive")
    conditional_cdf = _conditional_cdf_and_density(
        log_quantile,
        mu.reshape(-1),
        tuple(v.reshape(-1) for v in component_variances),
        error,
    )[0].reshape(mu.shape)
    influence = scaled_weights * (conditional_cdf - probability)
    influence_variance = float(np.var(influence, ddof=1))
    weight_ess = float(weight_sum**2 / np.sum(scaled_weights**2))
    weight_ess = min(weight_ess, float(n_total))
    max_normalized_weight = float(np.max(normalized_weights))

    batch_results = []
    for batch_size in batches:
        chain_results = []
        variance_components = []
        for chain_idx, chain_influence in enumerate(influence):
            estimate = _batch_means_lrv(chain_influence, batch_size)
            component = (
                len(chain_influence)
                * float(estimate["lrv"])
                / (n_total**2 * mean_weight**2 * density**2)
            )
            variance_components.append(component)
            chain_results.append({
                "chain": chain_idx,
                "draws": len(chain_influence),
                **estimate,
                "log_quantile_variance_component": component,
            })

        variance_log = float(np.sum(variance_components))
        mcse_log = float(np.sqrt(max(variance_log, 0.0)))
        active = [
            (component, int(result["degrees_of_freedom"]))
            for component, result in zip(variance_components, chain_results)
            if component > 0.0
        ]
        if variance_log > 0.0 and active:
            denominator = sum(component**2 / df for component, df in active)
            satterthwaite_df = float(variance_log**2 / denominator)
            chi_square_lower = float(chi2.ppf(tail_probability, satterthwaite_df))
            if not np.isfinite(chi_square_lower) or chi_square_lower <= 0:
                raise ValueError("chi-square lower quantile is not finite and positive")
            upper_variance_log = variance_log * satterthwaite_df / chi_square_lower
            upper_mcse_log = float(np.sqrt(upper_variance_log))
            upper_defined = True
        else:
            satterthwaite_df = None
            chi_square_lower = None
            upper_mcse_log = None
            upper_defined = False

        variance_of_mean_influence = variance_log * (density * mean_weight) ** 2
        if variance_of_mean_influence > 0.0 and influence_variance >= 0.0:
            influence_ess = float(influence_variance / variance_of_mean_influence)
        elif variance_of_mean_influence == 0.0 and influence_variance == 0.0:
            influence_ess = float(n_total)
        else:
            influence_ess = None

        batch_results.append({
            "batch_size": batch_size,
            "quantile_log_rul_mcse": mcse_log,
            "quantile_rul_mcse": rul_quantile * mcse_log,
            "approximate_upper_quantile_log_rul_mcse": upper_mcse_log,
            "approximate_upper_quantile_rul_mcse": (
                rul_quantile * upper_mcse_log if upper_mcse_log is not None else None
            ),
            "satterthwaite_degrees_of_freedom": satterthwaite_df,
            "chi_square_lower_quantile": chi_square_lower,
            "influence_ess": influence_ess,
            "chains": chain_results,
        })

    first = batch_results[0]
    second = batch_results[1]
    mcse_a = float(first["quantile_rul_mcse"])
    mcse_b = float(second["quantile_rul_mcse"])
    stability_scale = max(mcse_a, mcse_b)
    stability = {
        "batch_sizes": [batches[0], batches[1]],
        "rul_mcse": [mcse_a, mcse_b],
        "absolute_difference": abs(mcse_a - mcse_b),
        "relative_difference_over_max": (
            abs(mcse_a - mcse_b) / stability_scale if stability_scale > 0.0 else 0.0
        ),
        "interpretation": (
            "Descriptive sensitivity to the two requested batch sizes; no "
            "acceptance threshold is imposed by this helper."
        ),
    }
    finite_checks = {
        "means_finite": bool(np.all(np.isfinite(mu))),
        "variances_positive_finite": bool(np.all(np.isfinite(var)) and np.all(var > 0)),
        "log_weights_valid": bool(not np.any(np.isnan(logw)) and not np.any(np.isposinf(logw))),
        "positive_finite_weight_normalizer": bool(np.isfinite(weight_sum) and weight_sum > 0),
        "mixture_cdf_residual_finite": bool(np.isfinite(cdf_at_quantile - probability)),
        "positive_finite_log_rul_density": bool(np.isfinite(density) and density > 0),
        "quantiles_finite": bool(np.isfinite(log_quantile) and np.isfinite(rul_quantile) and rul_quantile > 0),
        "mcse_values_finite": bool(all(np.isfinite(float(r["quantile_rul_mcse"])) for r in batch_results)),
        "upper_mcse_values_finite_or_undefined": bool(all(
            r["approximate_upper_quantile_rul_mcse"] is None
            or np.isfinite(float(r["approximate_upper_quantile_rul_mcse"]))
            for r in batch_results
        )),
    }

    return {
        "probability": float(probability),
        "chain_count": int(mu.shape[0]),
        "draws_per_chain": int(mu.shape[1]),
        "draw_count_total": n_total,
        "quantile_log_rul": log_quantile,
        "quantile_rul": rul_quantile,
        "mixture_cdf_at_quantile": cdf_at_quantile,
        "mixture_cdf_residual": cdf_at_quantile - float(probability),
        "weighted_mixture_density_log_rul": density,
        "importance_weight_mean_scaled": mean_weight,
        "weight_ess": weight_ess,
        "weight_ess_interpretation": "Self-normalized weight-only ESS; it does not adjust for serial dependence.",
        "max_normalized_importance_weight": max_normalized_weight,
        "influence_variance_marginal": influence_variance,
        "influence_ess": first["influence_ess"],
        "influence_ess_interpretation": ("Marginal influence variance divided by the batch-means variance estimate of its mean; approximate."),
        "batch_size_results": batch_results,
        "batch_size_stability": stability,
        "tail_probability": float(tail_probability),
        "approximate_upper_confidence_level": 1.0 - float(tail_probability),
        "finite_checks": finite_checks,
        "assumptions": [
            "Each input chain is stationary and ergodic for the base posterior, and chains are independent.",
            "Importance weights have finite moments adequate for the self-normalized ratio central limit theorem.",
            "The weighted mixture density is positive and locally smooth at the requested quantile.",
            "The requested non-overlapping batch sizes produce enough batches to estimate each chain long-run variance.",
            "The delta method is adequate for the quantile functional at the available Monte Carlo size.",
        ],
        "finite_asymptotic_limitations": [
            "Batch-means long-run variance estimates and the Satterthwaite chi-square upper MCSE are finite-sample approximations, not rigorous error bounds or guaranteed confidence limits.",
            "The approximation can be poor with few batches, slow mixing, nonstationarity, high-variance importance weights, or a small mixture density at the target quantile.",
            "The quantile, density, and influence process are estimated from the same finite sample; this upper value does not account for every source of approximation error.",
            "Agreement across two batch sizes is a sensitivity diagnostic and does not establish calibration or convergence.",
            "The MCSE quantifies numerical integration error conditional on the supplied chains and model; it does not measure model, prior, data, or pipeline uncertainty.",
        ],
        "method": (
            "Direct self-normalized weighted Gaussian-mixture CDF quantile; "
            "delta-method influence w_scaled*(CDF_theta(q)-p); independent-chain "
            "non-overlapping batch means; Satterthwaite chi-square upper approximation."
        ),
    }
