from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Literal, Mapping, Sequence

import numpy as np
from scipy.stats import t as student_t
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import QuantileRegressor
from sklearn.preprocessing import StandardScaler


CQR_RANDOM_STATE = 20261008
LOWER_QUANTILE = 0.05
UPPER_QUANTILE = 0.95
MEDIAN_QUANTILE = 0.50
DEFAULT_ALPHA = 0.10
SUMMARY_FEATURE_COUNT = 5
FULL_FEATURE_COUNT = 31


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    family: Literal["gradient_boosting", "linear"]
    parameters: tuple[tuple[str, float | int], ...]

    def get(self, name: str) -> float | int:
        try:
            return dict(self.parameters)[name]
        except KeyError as exc:
            raise KeyError(f"{self.candidate_id} has no parameter {name!r}.") from exc


@dataclass
class CandidateFit:
    spec: CandidateSpec
    status: Literal["completed", "failed"]
    lower_model: Any | None = None
    upper_model: Any | None = None
    linear_scaler: StandardScaler | None = None
    train_size: int = 0
    failure_type: str | None = None
    failure_message: str | None = None


@dataclass
class MedianFit:
    spec: CandidateSpec
    status: Literal["completed", "failed"]
    model: Any | None = None
    linear_scaler: StandardScaler | None = None
    train_size: int = 0
    quantile: float = MEDIAN_QUANTILE
    conformal_shift_applied: bool = False
    failure_type: str | None = None
    failure_message: str | None = None


@dataclass(frozen=True)
class SelectionDecision:
    candidate: CandidateSpec
    best_observed_score: float
    selected_candidate_score: float
    tie_candidate_ids: tuple[str, ...]
    unscored_candidate_ids: tuple[str, ...]
    failure_reasons: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class GaussianLogRReferenceFit:
    coefficients: np.ndarray
    right_singular_vectors: np.ndarray
    singular_values: np.ndarray
    residual_variance: float
    degrees_of_freedom: int
    rank: int
    feature_count: int = SUMMARY_FEATURE_COUNT


@dataclass(frozen=True)
class PredictiveIntervals:
    lower: np.ndarray
    upper: np.ndarray
    median: np.ndarray


def candidate_specs() -> list[CandidateSpec]:
    """Return the fixed 8-tree + 4-linear CQR candidate budget in stable order."""
    result: list[CandidateSpec] = []
    for depth, leaf, rate in product((1, 2), (5, 10), (0.03, 0.10)):
        rate_name = f"{rate:g}".replace(".", "p")
        result.append(CandidateSpec(
            candidate_id=f"gb-depth{depth}-leaf{leaf}-lr{rate_name}",
            family="gradient_boosting",
            parameters=(
                ("max_depth", depth),
                ("min_samples_leaf", leaf),
                ("learning_rate", rate),
                ("n_estimators", 200),
            ),
        ))
    for alpha in (0.001, 0.01, 0.1, 1.0):
        alpha_name = f"{alpha:g}".replace(".", "p")
        result.append(CandidateSpec(
            candidate_id=f"linear-l1-alpha{alpha_name}",
            family="linear",
            parameters=(("alpha", alpha),),
        ))
    return result


CQR_CANDIDATES = tuple(candidate_specs())
_CANDIDATE_BY_ID = {candidate.candidate_id: candidate for candidate in CQR_CANDIDATES}


def build_summary_features(
    log_age: Sequence[float],
    endpoint_score: Sequence[float],
    ols_level_at_cutoff: Sequence[float],
    ols_slope_per_30: Sequence[float],
    residual_sd: Sequence[float],
) -> np.ndarray:
    """Stack the documented summary order into an (n, 5) matrix."""
    columns = [
        np.asarray(values, dtype=float)
        for values in (log_age, endpoint_score, ols_level_at_cutoff, ols_slope_per_30, residual_sd)
    ]
    if any(column.ndim != 1 for column in columns):
        raise ValueError("Summary inputs must be one-dimensional vectors.")
    if len({len(column) for column in columns}) != 1:
        raise ValueError("Summary vectors must have equal lengths.")
    matrix = np.column_stack(columns)
    if not np.isfinite(matrix).all():
        raise ValueError("Summary features must be finite.")
    if np.any(matrix[:, 4] < 0):
        raise ValueError("Residual SD must be nonnegative.")
    return matrix


def build_full_sequence_features(
    log_age: Sequence[float],
    observed_sequences: Sequence[Sequence[float]],
) -> np.ndarray:
    """Build [log_age, 30 interpolated points] without extrapolating history."""
    age = np.asarray(log_age, dtype=float)
    if age.ndim != 1 or not np.isfinite(age).all():
        raise ValueError("log_age must be a finite one-dimensional vector.")
    if len(age) != len(observed_sequences):
        raise ValueError("One observed sequence is required for each log_age value.")
    rows = []
    grid = np.linspace(0.0, 1.0, 30)
    for index, sequence in enumerate(observed_sequences):
        values = np.asarray(sequence, dtype=float)
        if values.ndim != 1 or len(values) < 1 or len(values) > 30:
            raise ValueError(f"Observed sequence {index} must contain 1..30 values.")
        if not np.isfinite(values).all():
            raise ValueError(f"Observed sequence {index} contains a non-finite value.")
        if len(values) == 1:
            sampled = np.full(30, values[0], dtype=float)
        else:
            source_grid = np.linspace(0.0, 1.0, len(values))
            sampled = np.interp(grid, source_grid, values)
        rows.append(np.concatenate(([age[index]], sampled)))
    if not rows:
        return np.empty((0, FULL_FEATURE_COUNT), dtype=float)
    return np.vstack(rows)


def ordered_endpoints(lower: Sequence[float], upper: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """Sort raw endpoints to prevent quantile crossing before scoring/calibration."""
    lo = np.asarray(lower, dtype=float)
    hi = np.asarray(upper, dtype=float)
    if lo.shape != hi.shape:
        raise ValueError("Lower and upper predictions must have the same shape.")
    if not np.isfinite(lo).all() or not np.isfinite(hi).all():
        raise ValueError("Endpoint predictions must be finite.")
    return np.minimum(lo, hi), np.maximum(lo, hi)


def mean90_interval_score(
    target_rul: Sequence[float],
    lower: Sequence[float],
    upper: Sequence[float],
    alpha: float = DEFAULT_ALPHA,
) -> float:
    """Mean uncapped-cycle interval score; caller supplies uncalibrated endpoints."""
    y = np.asarray(target_rul, dtype=float)
    lo = np.asarray(lower, dtype=float)
    hi = np.asarray(upper, dtype=float)
    if y.ndim != 1 or lo.shape != y.shape or hi.shape != y.shape:
        raise ValueError("Target and endpoint vectors must be one-dimensional and aligned.")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1.")
    if not (np.isfinite(y).all() and np.isfinite(lo).all() and np.isfinite(hi).all()):
        raise ValueError("Target and endpoints must be finite.")
    if np.any(y <= 0) or np.any(lo > hi):
        raise ValueError("RUL targets must be positive and endpoints ordered.")
    score = hi - lo + (2.0 / alpha) * np.maximum(lo - y, 0.0) + (2.0 / alpha) * np.maximum(y - hi, 0.0)
    return float(np.mean(score))


def _validated_arrays(
    Xsummary: Sequence[Sequence[float]],
    Xfull: Sequence[Sequence[float]],
    target_rul: Sequence[float] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    summary = np.asarray(Xsummary, dtype=float)
    full = np.asarray(Xfull, dtype=float)
    if summary.ndim != 2 or summary.shape[1] != SUMMARY_FEATURE_COUNT:
        raise ValueError("Xsummary must have 5 columns: log age, endpoint, OLS level, slope/30, residual SD.")
    if full.ndim != 2 or full.shape[1] != FULL_FEATURE_COUNT:
        raise ValueError("Xfull must have 31 columns: log age followed by 30 sequence values.")
    if summary.shape[0] != full.shape[0]:
        raise ValueError("Xsummary and Xfull must have the same number of engines.")
    if not np.isfinite(summary).all() or not np.isfinite(full).all():
        raise ValueError("Feature matrices must be finite.")
    if not np.allclose(summary[:, 0], full[:, 0], rtol=0.0, atol=1e-12):
        raise ValueError("The first summary and full-sequence columns must contain the same log age.")
    target = None
    if target_rul is not None:
        target = np.asarray(target_rul, dtype=float)
        if target.ndim != 1 or len(target) != len(summary):
            raise ValueError("R must be a one-dimensional vector aligned with the feature rows.")
        if not np.isfinite(target).all() or np.any(target <= 0):
            raise ValueError("R must contain finite, positive, uncapped RUL values in cycles.")
    return summary, full, target


def fit_linear_scaler(Xfull_fit: Sequence[Sequence[float]]) -> StandardScaler:
    """Fit the reusable linear-candidate scaler on fitting rows only."""
    full = np.asarray(Xfull_fit, dtype=float)
    if full.ndim != 2 or full.shape[1] != FULL_FEATURE_COUNT or not np.isfinite(full).all():
        raise ValueError("Xfull_fit must be a finite (n, 31) fitting-only matrix.")
    if len(full) == 0:
        raise ValueError("Cannot fit the linear scaler on zero rows.")
    return StandardScaler(with_mean=True, with_std=True).fit(full)


def _candidate(value: CandidateSpec | str) -> CandidateSpec:
    if isinstance(value, CandidateSpec):
        return value
    try:
        return _CANDIDATE_BY_ID[value]
    except KeyError as exc:
        raise ValueError(f"Unknown CQR candidate ID: {value!r}.") from exc


def _estimator(spec: CandidateSpec, quantile: float, random_state: int) -> Any:
    if spec.family == "gradient_boosting":
        return GradientBoostingRegressor(
            loss="quantile",
            alpha=quantile,
            n_estimators=int(spec.get("n_estimators")),
            max_depth=int(spec.get("max_depth")),
            min_samples_leaf=int(spec.get("min_samples_leaf")),
            learning_rate=float(spec.get("learning_rate")),
            random_state=int(random_state),
        )
    return QuantileRegressor(
        quantile=quantile,
        alpha=float(spec.get("alpha")),
        fit_intercept=True,
        solver="highs",
    )


def fit_candidate(
    Xsummary: Sequence[Sequence[float]],
    Xfull: Sequence[Sequence[float]],
    R: Sequence[float],
    candidate: CandidateSpec | str,
    *,
    linear_scaler: StandardScaler | None = None,
    random_state: int = CQR_RANDOM_STATE,
) -> CandidateFit:
    """Fit one fixed CQR candidate's tau=.05/.95 endpoints on fitting rows only."""
    spec = _candidate(candidate)
    summary, full, target = _validated_arrays(Xsummary, Xfull, R)
    if len(target) == 0:
        raise ValueError("Cannot fit a candidate on zero engines.")
    scaler = linear_scaler
    if spec.family == "linear":
        scaler = scaler if scaler is not None else fit_linear_scaler(full)
        if getattr(scaler, "n_features_in_", None) != FULL_FEATURE_COUNT:
            raise ValueError("Reusable linear scaler must be fitted on 31-column Xfull fitting rows.")
        features = scaler.transform(full)
    else:
        features = summary
    try:
        lower_model = _estimator(spec, LOWER_QUANTILE, random_state)
        upper_model = _estimator(spec, UPPER_QUANTILE, random_state)
        lower_model.fit(features, target)
        upper_model.fit(features, target)
        return CandidateFit(spec, "completed", lower_model, upper_model, scaler, len(target))
    except Exception as exc:
        return CandidateFit(
            spec=spec, status="failed", linear_scaler=scaler, train_size=len(target),
            failure_type=type(exc).__name__, failure_message=str(exc),
        )


def predict_endpoints(
    fitted: CandidateFit,
    Xsummary: Sequence[Sequence[float]],
    Xfull: Sequence[Sequence[float]],
) -> tuple[np.ndarray, np.ndarray]:
    """Predict and order the raw, pre-calibration CQR cycle endpoints."""
    if fitted.status != "completed" or fitted.lower_model is None or fitted.upper_model is None:
        raise RuntimeError(f"Candidate {fitted.spec.candidate_id} is unavailable: {fitted.failure_message}")
    summary, full, _ = _validated_arrays(Xsummary, Xfull)
    features = summary
    if fitted.spec.family == "linear":
        if fitted.linear_scaler is None:
            raise RuntimeError("Completed linear candidate has no reusable scaler.")
        features = fitted.linear_scaler.transform(full)
    lower = fitted.lower_model.predict(features)
    upper = fitted.upper_model.predict(features)
    return ordered_endpoints(lower, upper)


def fit_median_candidate(
    Xsummary: Sequence[Sequence[float]],
    Xfull: Sequence[Sequence[float]],
    R: Sequence[float],
    selected_candidate: CandidateSpec | str | SelectionDecision,
    *,
    linear_scaler: StandardScaler | None = None,
    random_state: int = CQR_RANDOM_STATE,
) -> MedianFit:
    """Fit a separate tau=.50 point model; no conformal shift is applied."""
    spec = selected_candidate.candidate if isinstance(selected_candidate, SelectionDecision) else _candidate(selected_candidate)
    summary, full, target = _validated_arrays(Xsummary, Xfull, R)
    if len(target) == 0:
        raise ValueError("Cannot fit the median model on zero engines.")
    scaler = linear_scaler
    if spec.family == "linear":
        scaler = scaler if scaler is not None else fit_linear_scaler(full)
        if getattr(scaler, "n_features_in_", None) != FULL_FEATURE_COUNT:
            raise ValueError("Reusable linear scaler must be fitted on 31-column Xfull fitting rows.")
        features = scaler.transform(full)
    else:
        features = summary
    try:
        model = _estimator(spec, MEDIAN_QUANTILE, random_state)
        model.fit(features, target)
        return MedianFit(spec, "completed", model, scaler, len(target))
    except Exception as exc:
        return MedianFit(
            spec=spec, status="failed", linear_scaler=scaler, train_size=len(target),
            failure_type=type(exc).__name__, failure_message=str(exc),
        )


def predict_median_candidate(
    fitted: MedianFit,
    Xsummary: Sequence[Sequence[float]],
    Xfull: Sequence[Sequence[float]],
) -> np.ndarray:
    if fitted.status != "completed" or fitted.model is None:
        raise RuntimeError(f"Median model for {fitted.spec.candidate_id} is unavailable: {fitted.failure_message}")
    summary, full, _ = _validated_arrays(Xsummary, Xfull)
    features = summary
    if fitted.spec.family == "linear":
        if fitted.linear_scaler is None:
            raise RuntimeError("Completed linear median model has no reusable scaler.")
        features = fitted.linear_scaler.transform(full)
    predictions = np.asarray(fitted.model.predict(features), dtype=float)
    if predictions.ndim != 1 or not np.isfinite(predictions).all():
        raise ValueError("Median predictions must be a finite vector.")
    return predictions


def _tie_complexity_key(spec: CandidateSpec) -> tuple[float, ...]:
    if spec.family == "linear":
        # Stronger L1 penalty is the predeclared lower-complexity tie preference.
        return (0.0, -float(spec.get("alpha")))
    # Fixed tree count: prefer shallow trees, larger leaves, then smaller steps.
    return (1.0, float(spec.get("max_depth")), -float(spec.get("min_samples_leaf")), float(spec.get("learning_rate")))


def select_candidate(
    mean_score_by_candidate: Mapping[str, float | None],
    *,
    tie_tolerance: float = 0.5,
    failure_reasons: Mapping[str, str] | None = None,
) -> SelectionDecision:
    """Select on tuning mean raw 90% interval score; ties within .5 cycles prefer linear then simpler."""
    if not np.isfinite(tie_tolerance) or tie_tolerance < 0:
        raise ValueError("tie_tolerance must be finite and nonnegative.")
    unknown = set(mean_score_by_candidate) - set(_CANDIDATE_BY_ID)
    if unknown:
        raise ValueError(f"Scores contain unknown candidate IDs: {sorted(unknown)}.")
    scored = {}
    for candidate_id, value in mean_score_by_candidate.items():
        if value is None:
            continue
        score = float(value)
        if not np.isfinite(score) or score < 0:
            raise ValueError(f"Candidate score must be a finite nonnegative cycle value: {candidate_id}.")
        scored[candidate_id] = score
    if not scored:
        raise ValueError("No completed candidate has a tuning score.")
    best = min(scored.values())
    tied_ids = tuple(sorted(candidate_id for candidate_id, score in scored.items() if score <= best + tie_tolerance))
    chosen_id = min(tied_ids, key=lambda cid: _tie_complexity_key(_CANDIDATE_BY_ID[cid]))
    failures = failure_reasons or {}
    return SelectionDecision(
        candidate=_CANDIDATE_BY_ID[chosen_id],
        best_observed_score=best,
        selected_candidate_score=scored[chosen_id],
        tie_candidate_ids=tied_ids,
        unscored_candidate_ids=tuple(sorted(set(_CANDIDATE_BY_ID) - set(scored))),
        failure_reasons=tuple(sorted((str(key), str(value)) for key, value in failures.items())),
    )




def fit_gaussian_logr_reference(
    Xsummary: Sequence[Sequence[float]],
    R: Sequence[float],
) -> GaussianLogRReferenceFit:
    """Fit OLS to log(R), retaining SVD factors for predictive parameter uncertainty."""
    summary = np.asarray(Xsummary, dtype=float)
    target = np.asarray(R, dtype=float)
    if summary.ndim != 2 or summary.shape[1] != SUMMARY_FEATURE_COUNT:
        raise ValueError("Xsummary must have five documented summary columns.")
    if target.ndim != 1 or len(target) != len(summary) or not np.isfinite(target).all() or np.any(target <= 0):
        raise ValueError("R must be aligned, finite, positive, uncapped RUL in cycles.")
    if not np.isfinite(summary).all() or len(target) == 0:
        raise ValueError("Reference fit requires finite features and at least one engine.")
    design = np.column_stack((np.ones(len(summary)), summary))
    u, singular, vh = np.linalg.svd(design, full_matrices=False)
    if singular.size == 0 or singular[0] <= 0:
        raise ValueError("Reference design has zero rank.")
    tolerance = np.finfo(float).eps * max(design.shape) * singular[0]
    rank = int(np.sum(singular > tolerance))
    if rank < 1:
        raise ValueError("Reference design has zero numerical rank.")
    ur, sr, vhr = u[:, :rank], singular[:rank], vh[:rank, :]
    coefficients = vhr.T @ ((ur.T @ np.log(target)) / sr)
    residual = np.log(target) - design @ coefficients
    degrees = len(target) - rank
    if degrees <= 0:
        raise ValueError("Reference fit needs positive residual degrees of freedom.")
    variance = float(np.dot(residual, residual) / degrees)
    return GaussianLogRReferenceFit(
        coefficients=coefficients,
        right_singular_vectors=vhr,
        singular_values=sr,
        residual_variance=variance,
        degrees_of_freedom=degrees,
        rank=rank,
    )


def predict_gaussian_logr_reference(
    fitted: GaussianLogRReferenceFit,
    Xsummary: Sequence[Sequence[float]],
    alpha: float = DEFAULT_ALPHA,
) -> PredictiveIntervals:
    """Return exp Student-t predictive quantiles and the predictive median in cycles."""
    summary = np.asarray(Xsummary, dtype=float)
    if summary.ndim != 2 or summary.shape[1] != fitted.feature_count or not np.isfinite(summary).all():
        raise ValueError("Xsummary must be a finite matrix with five documented columns.")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie strictly between 0 and 1.")
    design = np.column_stack((np.ones(len(summary)), summary))
    projected = design @ fitted.right_singular_vectors.T @ fitted.right_singular_vectors
    if np.any(np.linalg.norm(design-projected,axis=1)>1e-8*np.maximum(1.,np.linalg.norm(design,axis=1))):
        raise ValueError("New design has nonestimable contrasts under a rank-deficient training reference.")
    location = design @ fitted.coefficients
    coordinates = (design @ fitted.right_singular_vectors.T) / fitted.singular_values
    leverage = np.sum(coordinates * coordinates, axis=1)
    scale = np.sqrt(fitted.residual_variance * (1.0 + leverage))
    lower_log = location + student_t.ppf(alpha / 2.0, fitted.degrees_of_freedom) * scale
    upper_log = location + student_t.ppf(1.0 - alpha / 2.0, fitted.degrees_of_freedom) * scale
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        lower, upper, median = np.exp(lower_log), np.exp(upper_log), np.exp(location)
    if not (np.isfinite(lower).all() and np.isfinite(upper).all() and np.isfinite(median).all()):
        raise FloatingPointError("Exponentiated reference predictions are outside finite numeric range.")
    lower, upper = ordered_endpoints(lower, upper)
    return PredictiveIntervals(lower=lower, upper=upper, median=median)

