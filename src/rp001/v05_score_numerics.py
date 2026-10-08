"""Numerical influence and Monte Carlo uncertainty for a finite mean 90% interval score.

All inputs are arrays from the caller. The module does not load project data,
fit models, sample chains, or choose a scientific acceptance gate. Chain/draw
alignment and engine identity are retained until the scalar score influence is
formed so shared-draw dependence across endpoints and engines is preserved.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from scipy.stats import chi2


INTERVAL_SCORE_ALPHA = 0.10
INTERVAL_SCORE_MULTIPLIER = 2.0 / INTERVAL_SCORE_ALPHA
INTERVAL_SCORE_LIPSCHITZ_CONSTANT = INTERVAL_SCORE_MULTIPLIER - 1.0


def _engine_vector(
    values: Any,
    *,
    name: str,
    engine_count: int,
    strictly_positive: bool = False,
    nonnegative: bool = False,
) -> np.ndarray:
    try:
        result = np.asarray(values, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite numeric engine vector") from exc
    if result.ndim == 0:
        result = np.full(engine_count, float(result), dtype=np.float64)
    if result.shape != (engine_count,):
        raise ValueError(f"{name} must be scalar or have shape ({engine_count},)")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite")
    if strictly_positive and np.any(result <= 0.0):
        raise ValueError(f"{name} must be strictly positive")
    if nonnegative and np.any(result < 0.0):
        raise ValueError(f"{name} must be nonnegative")
    return result


def _influence_cube(values: Any, *, name: str) -> np.ndarray:
    try:
        result = np.asarray(values, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite (chain, draw, engine) array") from exc
    if result.ndim != 3:
        raise ValueError(f"{name} must have shape (chain, draw, engine)")
    if result.shape[0] < 1 or result.shape[1] < 2 or result.shape[2] < 1:
        raise ValueError(f"{name} needs at least one chain, two draws, and one engine")
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite")
    return result


def _batch_engine_matrix(
    values: Any,
    *,
    name: str,
    batch_count: int,
    engine_count: int,
) -> np.ndarray:
    try:
        result = np.asarray(values, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must contain finite endpoint radii") from exc
    if result.shape == (engine_count,):
        result = np.broadcast_to(result, (batch_count, engine_count)).copy()
    if result.shape != (batch_count, engine_count):
        raise ValueError(
            f"{name} must have shape ({engine_count},) or "
            f"({batch_count}, {engine_count})"
        )
    if not np.all(np.isfinite(result)) or np.any(result < 0.0):
        raise ValueError(f"{name} must be finite and nonnegative")
    return result


def _validate_batch_sizes(
    batch_sizes: Sequence[int], draws_per_chain: int
) -> tuple[int, int]:
    selected = tuple(batch_sizes)
    if len(selected) != 2:
        raise ValueError("batch_sizes must contain exactly two distinct sizes")
    if any(
        isinstance(size, (bool, np.bool_))
        or int(size) != size
        or size < 1
        for size in selected
    ):
        raise ValueError("batch sizes must be positive integers")
    first, second = (int(selected[0]), int(selected[1]))
    if first == second:
        raise ValueError("batch_sizes must contain exactly two distinct sizes")
    if any(draws_per_chain // size < 2 for size in (first, second)):
        raise ValueError("each batch size must produce at least two batches per chain")
    return first, second


def endpoint_cycle_quantile_influence(
    log_weights: Any,
    conditional_cdf_at_quantile: Any,
    probability: float | np.ndarray,
    quantile_cycles: Any,
    density_log_rul: Any,
) -> dict[str, Any]:
    """Return per-draw cycle-scale influence for one endpoint quantile per engine.

    ``log_weights`` and ``conditional_cdf_at_quantile`` have shape
    ``(chain, draw, engine)`` and must share the exact chain/draw alignment.
    ``density_log_rul[e]`` is the self-normalized mixture density with respect
    to log-RUL, evaluated at that engine's log quantile. Weights are scaled
    independently by engine for numerical stability; the ratio ``w / mean(w)``
    is invariant to this arbitrary positive scaling.

    For engine ``e``, this implements

        X_cte = -Q_e * w_cte * (F_cte(q_e) - p_e)
                / (mean_cte(w_cte) * f_log,e(q_e)),

    where ``Q_e = exp(q_e)`` is the endpoint in cycles. No engine or draw axis
    is flattened or reordered.
    """
    try:
        logw = np.asarray(log_weights, dtype=np.float64)
        cdf = np.asarray(conditional_cdf_at_quantile, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("weights and conditional CDF must be numeric arrays") from exc
    if logw.ndim != 3 or cdf.shape != logw.shape:
        raise ValueError(
            "log_weights and conditional CDF must share shape (chain, draw, engine)"
        )
    chains, draws, engines = logw.shape
    if chains < 1 or draws < 2 or engines < 1:
        raise ValueError("at least one chain, two draws, and one engine are required")
    if np.any(np.isnan(logw)) or np.any(np.isposinf(logw)):
        raise ValueError("log_weights may be finite or negative infinity, but not NaN/+infinity")
    if not np.all(np.isfinite(cdf)) or np.any(cdf < 0.0) or np.any(cdf > 1.0):
        raise ValueError("conditional CDF values must be finite and lie in [0, 1]")

    p = _engine_vector(
        probability, name="probability", engine_count=engines
    )
    if np.any(p <= 0.0) or np.any(p >= 1.0):
        raise ValueError("probabilities must lie strictly between zero and one")
    q_cycles = _engine_vector(
        quantile_cycles,
        name="quantile_cycles",
        engine_count=engines,
        strictly_positive=True,
    )
    density = _engine_vector(
        density_log_rul,
        name="density_log_rul",
        engine_count=engines,
        strictly_positive=True,
    )

    maximum = np.max(logw, axis=(0, 1))
    if not np.all(np.isfinite(maximum)):
        raise ValueError("every engine must have at least one finite log weight")
    with np.errstate(under="ignore", over="ignore", invalid="ignore"):
        scaled_weights = np.exp(logw - maximum[None, None, :])
    mean_scaled_weight = np.mean(scaled_weights, axis=(0, 1), dtype=np.float64)
    if not np.all(np.isfinite(mean_scaled_weight)) or np.any(mean_scaled_weight <= 0.0):
        raise ValueError("scaled mean importance weights must be finite and positive")

    influence = (
        -q_cycles[None, None, :]
        * scaled_weights
        * (cdf - p[None, None, :])
        / (mean_scaled_weight[None, None, :] * density[None, None, :])
    )
    if not np.all(np.isfinite(influence)):
        raise ValueError("cycle-scale endpoint influence is nonfinite")
    return {
        "influence_cycles": influence,
        "scaled_weight_mean_by_engine": mean_scaled_weight,
        "scaled_weight_max_by_engine": np.max(scaled_weights, axis=(0, 1)),
        "probability_by_engine": p,
        "quantile_cycles_by_engine": q_cycles,
        "density_log_rul_by_engine": density,
        "shape_chain_draw_engine": [int(chains), int(draws), int(engines)],
        "engine_axis_preserved": True,
        "formula": (
            "-Q_e*w_cte*(F_cte(q_e)-p_e)/(mean_cte(w_cte)*"
            "f_log,e(q_e)); Q_e is exp(q_e) in cycles"
        ),
    }


def interval_score_90(
    outcomes_cycles: Any, lower_cycles: Any, upper_cycles: Any
) -> np.ndarray:
    """Per-engine 90% interval score in cycle units."""
    try:
        outcomes = np.asarray(outcomes_cycles, dtype=np.float64)
        lower = np.asarray(lower_cycles, dtype=np.float64)
        upper = np.asarray(upper_cycles, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("outcomes and endpoints must be numeric engine vectors") from exc
    if outcomes.ndim != 1 or lower.shape != outcomes.shape or upper.shape != outcomes.shape:
        raise ValueError("outcomes and interval endpoints must share one-dimensional shape")
    if outcomes.size < 1 or not all(np.all(np.isfinite(x)) for x in (outcomes, lower, upper)):
        raise ValueError("outcomes and endpoints must be nonempty and finite")
    if np.any(outcomes <= 0.0) or np.any(lower <= 0.0) or np.any(upper <= 0.0):
        raise ValueError("RUL outcomes and endpoints must be strictly positive cycles")
    if np.any(lower > upper):
        raise ValueError("lower interval endpoints must not exceed upper endpoints")
    return (
        upper
        - lower
        + INTERVAL_SCORE_MULTIPLIER * np.maximum(lower - outcomes, 0.0)
        + INTERVAL_SCORE_MULTIPLIER * np.maximum(outcomes - upper, 0.0)
    )


def interval_score_influence_from_endpoints(
    lower_influence_cycles: Any,
    upper_influence_cycles: Any,
    outcomes_cycles: Any,
    lower_cycles: Any,
    upper_cycles: Any,
    lower_upper_mcse_cycles: Any,
    upper_upper_mcse_cycles: Any,
    *,
    batch_sizes: Sequence[int] = (250, 500),
) -> dict[str, Any]:
    """Form the exact finite-mean interval-score influence and kink diagnostics.

    The score gradient uses the specified strict indicators:
    ``g_L=-1+20*I[y<L]`` and ``g_U=1-20*I[y>U]``. Thus equality is assigned
    to the non-miss branch for the algebraic influence, while the separate kink
    diagnostic flags labels close to either endpoint.

    Endpoint upper-MCSE inputs may be one vector (broadcast to both batch sizes)
    or a ``(batch_size, engine)`` array aligned to ``batch_sizes``. A kink is
    flagged when an observed label lies within three times the corresponding
    endpoint's approximate upper MCSE for that batch size.
    """
    lower_influence = _influence_cube(
        lower_influence_cycles, name="lower_influence_cycles"
    )
    upper_influence = _influence_cube(
        upper_influence_cycles, name="upper_influence_cycles"
    )
    if lower_influence.shape != upper_influence.shape:
        raise ValueError("lower and upper influences must share chain/draw/engine alignment")
    chains, draws, engines = lower_influence.shape
    batches = _validate_batch_sizes(batch_sizes, draws)

    outcomes = _engine_vector(
        outcomes_cycles, name="outcomes_cycles", engine_count=engines, strictly_positive=True
    )
    lower = _engine_vector(
        lower_cycles, name="lower_cycles", engine_count=engines, strictly_positive=True
    )
    upper = _engine_vector(
        upper_cycles, name="upper_cycles", engine_count=engines, strictly_positive=True
    )
    if np.any(lower > upper):
        raise ValueError("lower endpoints must not exceed upper endpoints")
    lower_radii = _batch_engine_matrix(
        lower_upper_mcse_cycles,
        name="lower_upper_mcse_cycles",
        batch_count=len(batches),
        engine_count=engines,
    )
    upper_radii = _batch_engine_matrix(
        upper_upper_mcse_cycles,
        name="upper_upper_mcse_cycles",
        batch_count=len(batches),
        engine_count=engines,
    )

    lower_miss = outcomes < lower
    upper_miss = outcomes > upper
    gradient_lower = -1.0 + INTERVAL_SCORE_MULTIPLIER * lower_miss.astype(np.float64)
    gradient_upper = 1.0 - INTERVAL_SCORE_MULTIPLIER * upper_miss.astype(np.float64)
    score_influence = np.mean(
        lower_influence * gradient_lower[None, None, :]
        + upper_influence * gradient_upper[None, None, :],
        axis=2,
        dtype=np.float64,
    )
    if not np.all(np.isfinite(score_influence)):
        raise ValueError("scalar interval-score influence must be finite")

    lower_distance = np.abs(outcomes - lower)
    upper_distance = np.abs(outcomes - upper)
    kink_by_batch_size: list[dict[str, Any]] = []
    for index, batch_size in enumerate(batches):
        lower_flags = lower_distance <= 3.0 * lower_radii[index]
        upper_flags = upper_distance <= 3.0 * upper_radii[index]
        kink_by_batch_size.append(
            {
                "batch_size": int(batch_size),
                "lower_endpoint_by_engine": lower_flags,
                "upper_endpoint_by_engine": upper_flags,
                "any_by_engine": lower_flags | upper_flags,
                "any": bool(np.any(lower_flags) or np.any(upper_flags)),
            }
        )

    scores = interval_score_90(outcomes, lower, upper)
    return {
        "score_influence": score_influence,
        "gradient_lower_by_engine": gradient_lower,
        "gradient_upper_by_engine": gradient_upper,
        "score_per_engine_cycles": scores,
        "finite_mean_interval_score_cycles": float(np.mean(scores, dtype=np.float64)),
        "label_kink": {
            "any": any(item["any"] for item in kink_by_batch_size),
            "definition": (
                "For each batch size, flag an engine when |y-endpoint| is no more "
                "than 3 times that endpoint's approximate upper quantile MCSE in cycles."
            ),
            "by_batch_size": kink_by_batch_size,
            "interpretation": (
                "A diagnostic for possible crossing of the interval-score derivative kink; "
                "it is not a probability statement about label coverage."
            ),
        },
        "chain_count": int(chains),
        "draws_per_chain": int(draws),
        "engine_count": int(engines),
        "batch_sizes": list(batches),
        "score_influence_formula": (
            "H_ct = (1/N) sum_e(g_L,e*X_L,cte + g_U,e*X_U,cte), "
            "with g_L=-1+20*I[y<L], g_U=1-20*I[y>U]"
        ),
    }


def _batch_lrv_covariance(
    series: np.ndarray, batch_size: int
) -> tuple[np.ndarray, int, int, int]:
    """Joint non-overlapping batch-means LRV covariance for one chain."""
    draws, dimension = series.shape
    batch_count = draws // batch_size
    used_draws = batch_count * batch_size
    batch_means = series[:used_draws].reshape(batch_count, batch_size, dimension).mean(axis=1)
    centered = batch_means - np.mean(batch_means, axis=0, keepdims=True)
    covariance_of_batch_means = centered.T @ centered / (batch_count - 1)
    lrv_covariance = batch_size * covariance_of_batch_means
    lrv_covariance = 0.5 * (lrv_covariance + lrv_covariance.T)
    if not np.all(np.isfinite(lrv_covariance)):
        raise ValueError("joint batch-means covariance is nonfinite")
    return lrv_covariance, batch_count, used_draws, draws - used_draws


def estimate_joint_interval_score_mcse(
    lower_influence_cycles: Any,
    upper_influence_cycles: Any,
    outcomes_cycles: Any,
    lower_cycles: Any,
    upper_cycles: Any,
    lower_upper_mcse_cycles: Any,
    upper_upper_mcse_cycles: Any,
    *,
    tail_probability: float,
    batch_sizes: Sequence[int] = (250, 500),
) -> dict[str, Any]:
    """Estimate MCSE of the finite mean 90% interval score from joint influences.

    The full endpoint vector has coordinate order ``[L_1,...,L_N,U_1,...,U_N]``.
    Each chain receives a joint batch-means LRV covariance. The covariance of
    the pooled endpoint estimator is ``sum_c n_c*LRV_c / M^2`` for total draws
    ``M``. The scalar score variance is the exact linear projection of this
    matrix by ``[g_L/N,g_U/N]``; this preserves shared-draw dependence among
    engines and between interval endpoints.

    The one-sided upper MCSE is an approximate Satterthwaite/chi-square bound.
    It is not a guaranteed finite-sample confidence limit.
    """
    if not np.isfinite(tail_probability) or not 0.0 < tail_probability < 1.0:
        raise ValueError("tail_probability must lie strictly between zero and one")
    lower_influence = _influence_cube(
        lower_influence_cycles, name="lower_influence_cycles"
    )
    upper_influence = _influence_cube(
        upper_influence_cycles, name="upper_influence_cycles"
    )
    if lower_influence.shape != upper_influence.shape:
        raise ValueError("lower and upper influences must share chain/draw/engine alignment")
    chains, draws, engines = lower_influence.shape
    batches = _validate_batch_sizes(batch_sizes, draws)
    score_details = interval_score_influence_from_endpoints(
        lower_influence,
        upper_influence,
        outcomes_cycles,
        lower_cycles,
        upper_cycles,
        lower_upper_mcse_cycles,
        upper_upper_mcse_cycles,
        batch_sizes=batches,
    )

    # Retain all engine coordinates until after the joint covariance is formed.
    joint_endpoint_influence = np.concatenate(
        (lower_influence, upper_influence), axis=2
    )
    contrast = np.concatenate(
        (
            score_details["gradient_lower_by_engine"],
            score_details["gradient_upper_by_engine"],
        )
    ) / engines
    total_draws = chains * draws
    batch_results: list[dict[str, Any]] = []
    for batch_size in batches:
        chain_lrv_covariances: list[np.ndarray] = []
        chain_score_lrv: list[float] = []
        chain_results: list[dict[str, Any]] = []
        variance_components: list[float] = []
        degrees_of_freedom: list[int] = []
        joint_covariance_sum = np.zeros(
            (2 * engines, 2 * engines), dtype=np.float64
        )
        for chain_index in range(chains):
            lrv, batch_count, used, dropped = _batch_lrv_covariance(
                joint_endpoint_influence[chain_index], batch_size
            )
            score_lrv = float(contrast @ lrv @ contrast)
            # The projected matrix is positive semidefinite in exact arithmetic.
            if score_lrv < 0.0 and abs(score_lrv) <= 1e-12 * max(1.0, float(np.max(np.abs(lrv)))):
                score_lrv = 0.0
            if not np.isfinite(score_lrv) or score_lrv < 0.0:
                raise ValueError("projected score long-run variance must be finite/nonnegative")
            component = draws * score_lrv / (total_draws**2)
            df = batch_count - 1
            chain_lrv_covariances.append(lrv)
            chain_score_lrv.append(score_lrv)
            variance_components.append(float(component))
            degrees_of_freedom.append(int(df))
            joint_covariance_sum += draws * lrv
            chain_results.append(
                {
                    "chain": int(chain_index),
                    "batch_count": int(batch_count),
                    "degrees_of_freedom": int(df),
                    "draws_used": int(used),
                    "draws_dropped": int(dropped),
                    "joint_endpoint_lrv_covariance_cycles_squared": lrv,
                    "score_lrv_cycles_squared": score_lrv,
                    "score_variance_component": float(component),
                }
            )

        joint_mc_error_covariance = joint_covariance_sum / (total_draws**2)
        joint_mc_error_covariance = 0.5 * (
            joint_mc_error_covariance + joint_mc_error_covariance.T
        )
        score_variance = float(np.sum(variance_components, dtype=np.float64))
        projected_variance = float(contrast @ joint_mc_error_covariance @ contrast)
        if projected_variance < 0.0 and abs(projected_variance) <= 1e-12:
            projected_variance = 0.0
        if not np.isfinite(projected_variance) or projected_variance < 0.0:
            raise ValueError("pooled score variance must be finite and nonnegative")
        score_mcse = float(np.sqrt(score_variance))

        active = [
            (component, df)
            for component, df in zip(variance_components, degrees_of_freedom)
            if component > 0.0
        ]
        if score_variance > 0.0 and active:
            denominator = sum(component**2 / df for component, df in active)
            satterthwaite_df = float(score_variance**2 / denominator)
            chi_square_lower = float(chi2.ppf(tail_probability, satterthwaite_df))
            if not np.isfinite(chi_square_lower) or chi_square_lower <= 0.0:
                raise ValueError("Satterthwaite chi-square lower quantile is invalid")
            upper_score_mcse = float(
                np.sqrt(score_variance * satterthwaite_df / chi_square_lower)
            )
        else:
            satterthwaite_df = None
            chi_square_lower = None
            upper_score_mcse = None

        lower_radii = _batch_engine_matrix(
            lower_upper_mcse_cycles,
            name="lower_upper_mcse_cycles",
            batch_count=len(batches),
            engine_count=engines,
        )[batches.index(batch_size)]
        upper_radii = _batch_engine_matrix(
            upper_upper_mcse_cycles,
            name="upper_upper_mcse_cycles",
            batch_count=len(batches),
            engine_count=engines,
        )[batches.index(batch_size)]
        lipschitz_bound = float(
            INTERVAL_SCORE_LIPSCHITZ_CONSTANT
            * np.sum(lower_radii + upper_radii, dtype=np.float64)
            / engines
        )
        batch_results.append(
            {
                "batch_size": int(batch_size),
                "quantile_score_mcse_cycles": score_mcse,
                "approximate_upper_quantile_score_mcse_cycles": upper_score_mcse,
                "satterthwaite_degrees_of_freedom": satterthwaite_df,
                "chi_square_lower_quantile": chi_square_lower,
                "score_variance_cycles_squared": score_variance,
                "score_variance_from_joint_covariance_cycles_squared": projected_variance,
                "joint_score_variance_projection_abs_residual": abs(
                    score_variance - projected_variance
                ),
                "variance_components_by_chain": variance_components,
                "degrees_of_freedom_by_chain": degrees_of_freedom,
                "joint_endpoint_mc_error_covariance_cycles_squared": joint_mc_error_covariance,
                "chain_results": chain_results,
                "interval_score_lipschitz_sensitivity_cycles": {
                    "conditional_bound": lipschitz_bound,
                    "constant": INTERVAL_SCORE_LIPSCHITZ_CONSTANT,
                    "formula": "19/N * sum_e(r_L,e + r_U,e)",
                    "endpoint_error_radii_lower_cycles": lower_radii,
                    "endpoint_error_radii_upper_cycles": upper_radii,
                    "interpretation": (
                        "Deterministic score sensitivity conditional on actual endpoint errors "
                        "being within the supplied radii. Since these radii are approximate upper "
                        "MCSEs, this is not an MCSE coverage theorem or guaranteed bound."
                    ),
                },
            }
        )

    first_mcse = float(batch_results[0]["quantile_score_mcse_cycles"])
    second_mcse = float(batch_results[1]["quantile_score_mcse_cycles"])
    scale = max(first_mcse, second_mcse)
    stability = {
        "batch_sizes": list(batches),
        "score_mcse_cycles": [first_mcse, second_mcse],
        "absolute_difference_cycles": abs(first_mcse - second_mcse),
        "relative_difference_over_max": (
            abs(first_mcse - second_mcse) / scale if scale > 0.0 else 0.0
        ),
        "interpretation": (
            "Descriptive sensitivity to the two requested batch sizes; no gate is imposed here."
        ),
    }
    finite_checks = {
        "endpoint_influences_finite": bool(
            np.all(np.isfinite(lower_influence)) and np.all(np.isfinite(upper_influence))
        ),
        "score_influence_finite": bool(
            np.all(np.isfinite(score_details["score_influence"]))
        ),
        "covariance_matrices_finite": all(
            np.all(
                np.isfinite(
                    item["joint_endpoint_mc_error_covariance_cycles_squared"]
                )
            )
            for item in batch_results
        ),
        "mcse_values_finite": all(
            np.isfinite(item["quantile_score_mcse_cycles"])
            for item in batch_results
        ),
        "upper_mcse_finite_or_undefined": all(
            item["approximate_upper_quantile_score_mcse_cycles"] is None
            or np.isfinite(item["approximate_upper_quantile_score_mcse_cycles"])
            for item in batch_results
        ),
    }

    return {
        **score_details,
        "joint_endpoint_coordinate_order": (
            "[lower engine 0..N-1, upper engine 0..N-1]"
        ),
        "joint_endpoint_influence_cycles": joint_endpoint_influence,
        "score_contrast": contrast,
        "draw_count_total": int(total_draws),
        "tail_probability": float(tail_probability),
        "approximate_upper_confidence_level": 1.0 - float(tail_probability),
        "batch_size_results": batch_results,
        "batch_size_stability": stability,
        "finite_checks": finite_checks,
        "assumptions": [
            "Each supplied chain is stationary and ergodic for the joint endpoint-influence process; chains are independent.",
            "The endpoint quantile influence functions are adequate under positive, locally smooth log-RUL mixture densities and a self-normalized ratio CLT.",
            "Shared chain/draw dependence across engines and endpoints is represented by the joint batch-means covariance.",
            "The 90% interval-score derivative is locally represented by the stated strict-indicator gradient; kink flags diagnose labels near endpoint thresholds.",
            "The Satterthwaite chi-square upper MCSE is a finite-asymptotic approximation, not a guaranteed confidence limit.",
        ],
        "limitations": [
            "The MCSE is conditional on supplied chains, model, outcomes, and endpoint estimates; it does not include model, data, or pipeline uncertainty.",
            "Approximate upper MCSEs can be inaccurate with few/short batches, slow mixing, nonstationarity, or unstable endpoint densities.",
            "The 19/N Lipschitz sensitivity value is conditional on actual endpoint errors being bounded by the supplied radii; approximate MCSE radii do not make it a probabilistic coverage guarantee.",
            "A label-kink flag is a numerical proximity diagnostic, not evidence of label coverage or a reason to retry after seeing labels.",
            "This module computes diagnostics only; it does not implement policy gates or trigger additional draws.",
        ],
    }
