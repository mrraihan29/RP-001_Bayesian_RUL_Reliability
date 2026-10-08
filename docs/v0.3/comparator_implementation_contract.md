# Comparator Implementation Contract

Status: implementation handoff; no empirical comparator or reference fit has been executed.

## CQR candidates and data contract

The module exposes the fixed 12-candidate search from docs/05: eight GradientBoostingRegressor quantile endpoint pairs with 200 trees over max depth {1,2}, minimum leaf {5,10}, and learning rate {0.03,0.10}; and four QuantileRegressor endpoint pairs with L1 alpha {0.001,0.01,0.1,1}. Endpoint models use tau=.05 and .95, then predictions are sorted before the uncalibrated tuning score or later calibration.

CQR targets raw, uncapped RUL R in cycles, equivalent to R=exp(log R); final-cycle landmarks are excluded upstream, so R must be positive. The Gaussian reference instead fits log(R) and maps its predictive quantiles back to cycles.

Input feature order is explicit:

- Xsummary: five columns [log(c/100), endpoint observed score, OLS level at cutoff, OLS slope per 30 cycles, residual SD].
- Xfull: 31 columns [log(c/100), 30 interpolated observed sequence values].

For Xfull, the 30-point grid spans only the observed sequence from first to last cycle. A one-value history repeats that observed value 30 times. There is no extrapolation. The existing data.features(..., full=False) currently returns four summary columns and therefore needs the owner-authorized data.py update described by the lead before integration; this module intentionally enforces the five-column docs/05 contract.

## Scaling, fitting, prediction, and selection

Linear candidates use one reusable StandardScaler fitted on fitting rows only. Pass the same scaler to each of the four linear candidates for that cohort. After selection, pass a scaler fitted on the 56 fit+tune rows, or omit it so fit_median_candidate fits its own on the supplied refit cohort. Do not reuse a fit-only scaler for refit+tune.

fit_candidate(Xsummary, Xfull, R, candidate) fits exactly two quantile estimators. Candidate failures are returned with status, exception type, and message; orchestration should preserve timeouts/failures and not add replacement trials. predict_endpoints returns sorted raw endpoints. Selection uses the lowest tuning mean 90% interval score; scores within 0.5 cycle of the minimum form the tie set, where linear is preferred and the lower-complexity proxy breaks remaining ties: stronger L1 penalty for linear; shallower depth, larger minimum leaf, then smaller learning rate for boosting. Missing scores are reported in the decision rather than silently retried.

The selected configuration gets one additional tau=.50 model fit on the fit+tune refit cohort for point metrics. Its output is an estimated conditional median and receives no conformal shift. No calibration responses are read or accepted by this module.

## Gaussian log-RUL reference

The reference is OLS on log(R) using an intercept and the five summary columns. It computes residual variance using residual degrees of freedom and returns a Student-t predictive distribution on log scale with scale s*sqrt(1 + xᵀ(XᵀX)^+x). This includes new-observation residual and coefficient uncertainty. Predictive interval quantiles are exponentiated to cycles; the point forecast is exp(xᵀβ), the predictive median. No finite predictive mean on the cycle scale is claimed for the exponentiated Student-t distribution.

## Verification boundary and risks

The module and tests target interface, deterministic transforms, selection tie handling, and a manually specified predictive-reference example. Tests do not call estimator.fit; no project training or tuning rows, calibration responses, or official test bytes are used. The caller still owns split enforcement, equal-engine one-row R inputs, run/failure provenance, and ensuring each preprocessing fit uses the permitted cohort. The five-summary-column integration point must be reconciled with the current data.features implementation before empirical fitting.




## Implementation default to confirm before protocol lock

GradientBoostingRegressor receives fixed random_state=20261008 for all eight candidates. docs/05 requires a fixed seed but does not state its numeric value; this literal is an implementation default, not a performance-selected choice, and should be confirmed in the final lock. QuantileRegressor is deterministic for a fixed input and solver.

