# RP-001 v0.4 — paired bootstrap-t worker contract

**Status: implementation contract only. No substantive operating-characteristic simulation or benchmark evaluation has been run.** The protocol remains `PROTOCOL_DRAFTED`; final protocol approval, official test access and confirmatory evaluation remain unauthorized in the v0.3 records.

## Purpose and estimand boundary

The primary benchmark estimand is the exact arithmetic mean of the complete set of stored per-engine paired prediction-score differences, with each engine represented once. `finite_benchmark_mean` returns that observed finite-benchmark value and makes no population claim. The paired bootstrap-t simulation is a secondary conditional diagnostic for a hypothetical engine-pair population under a named law. It does not alter the primary estimand, test whether the two methods are superior on the benchmark, or justify an unconditional FD001 population claim.

For a later paired score vector, `d_i` is the Bayesian interval score minus the CQR interval score for the same engine. The sample standard error is `sd(d, ddof=1)/sqrt(n)`. Each bootstrap draw resamples complete engine differences with replacement, preserving the method pairing. The bootstrap pivot is

`T* = (mean(d*) - mean(d)) / (sd(d*, ddof=1) / sqrt(n))`.

If its empirical quantiles are `q(.025)`, `q(.05)` and `q(.975)`, the two-sided 95% interval is `[mean(d)-q(.975)SE, mean(d)-q(.025)SE]`; the one-sided upper 95% bound for `H0: mean(d) >= 0` against `mean(d) < 0` is `mean(d)-q(.05)SE`. A negative point estimate alone does not establish superiority.

This interval conditions on the realized fitted, tuned and calibrated procedures. It does not include training-cohort, representation, selection, calibration-cohort, cutoff or full-pipeline variability. IID engine-pair sampling and finite, adequately regular tails are assumptions for the population interpretation; 100 distinct engine IDs alone do not establish them.

## Synthetic scenarios

Each scenario has population mean zero. The actual sample and bootstrap seeds must be supplied by the caller for every scenario. `n` defaults to 100; `nsim` and `bootstrap_count` have no substantive-run defaults. The worker always runs the full registered set, so a caller cannot silently omit an adverse family.

| Scenario | Fixed law | Mean | Variance / role |
| --- | --- | ---: | --- |
| `normal` | `N(0,1)` | 0 | 1 |
| `centered_lognormal_sigma1` | `Lognormal(0,1) - exp(1/2)` | 0 | `(exp(1)-1)exp(1)` |
| `centered_lognormal_sigma1p5` | `Lognormal(0,1.5) - exp(1.125)` | 0 | `(exp(2.25)-1)exp(2.25)` |
| `student_t3` | Student-t, df 3, loc 0, scale 1 | 0 | 3 |
| `rare_outlier_mixture` | `0.99*N(0,1) + 0.01*N(0,30^2)` | 0 | 9.99 |
| `student_t1p5_infinite_variance` | Student-t, df 1.5, loc 0, scale 1 | 0 | Infinite; stress case, mean exists |
| `sparse_discrete_pm1` | `P(-1)=.01, P(0)=.98, P(+1)=.01` | 0 | .02; ties/degeneracy stress |
| `all_zero` | Point mass at zero | 0 | 0; undefined t standardization |

The t(1.5) mean exists but its variance is infinite, so its coverage and rejection rates are stress diagnostics outside the ordinary finite-variance bootstrap-t justification. The discrete and all-zero cases expose zero-SE behavior. They remain in the run and are not pooled into a more favorable distribution family.

## Numerical and input policy

Calculations use float64. Sample and bootstrap standard deviations use `ddof=1`; the NumPy quantile method (default `linear`) and resampling chunk size are configurable and included in returned configuration. Chunking limits temporary resample-array memory. The exact zero-SE rule is `SE*=0`; there is no scale-dependent epsilon. Every zero bootstrap SE and nonfinite bootstrap draw is counted. Any such draw invalidates that replicate's interval; invalid draws are not discarded, replaced or assigned a favorable value. A zero observed SE also makes the t interval unavailable, after bootstrap denominator diagnostics have been recorded.

The finite-benchmark and inference helpers require a one-dimensional vector with at least two finite paired differences. A missing pair, NaN, positive/negative infinity, wrong shape, or arithmetic overflow fails the complete comparison input. Do not drop an engine, impute a score, cap an infinite interval score, trim or winsorize differences, or switch to a different interval/test after seeing results. On a future score run, require one-to-one engine IDs and both finite method scores for every planned endpoint. Preserve the engine identity, original prediction/score record and failure reason; mark the primary numerical result unavailable until its predeclared policy is resolved.

Synthetic replicates whose interval is unavailable stay in `simulation_records`. Conditional coverage/rejection summaries use only replicates with a defined interval, and the interval-availability rate, zero-SE rates and all failure counts are reported beside them. Thus conditional rates must never be presented alone as the method's unconditional success rate. A material unavailable fraction is an adverse operating characteristic, not permission to remove a scenario or its replicates.

## Reported operating characteristics and raw record

The returned object contains the full effective configuration, all per-scenario root seeds, derived sample/bootstrap seeds for each replicate, scenario definitions, every replicate row, source SHA-256, runtime and environment metadata. Each replicate row retains its sample mean/SE, interval and upper bound where defined, coverage/rejection indicators, influence diagnostics, zero/nonfinite draw counts, status and exception. No file is written automatically.

For each scenario, coverage and one-sided rejection are Bernoulli summaries across estimable simulation replicates. The worker returns the success count, denominator, rate, binomial MCSE `sqrt(p(1-p)/m)` and two-sided 95% Wilson interval. It also returns the same uncertainty summary for interval availability. These Wilson intervals and MCSE describe outer simulation counting uncertainty only; they do not include finite-bootstrap quantile noise. Keep small-run debug output distinct from planned operating-characteristic evidence.

Influence is computed for each simulated sample as (1) `max_i |d_i - mean(d)| / sum_j |d_j - mean(d)|`, and (2) the largest absolute leave-one-out mean change, divided by the original sample SE. The full per-replicate values remain in the raw rows; aggregate median, 95th percentile and maximum are descriptive only. Undefined influence values remain null with the replicate status and are not replaced.

## Review risks and limits

The finite benchmark consists of the exact engines in the test set; a superpopulation interval is a different claim. A paired bootstrap-t method can miscover under strong skew, extreme influence, sparse discrete laws, a very small usable-resample tail, or infinite variance. The rare-outlier and t(1.5) scenarios directly probe such failure. At `n=100`, scenario counts may still be too small to characterize rare extremes precisely; Wilson intervals show only simulation-count uncertainty. The all-zero law has no positive standard error, so t-based inference must fail there. IID synthetic engines do not reproduce cutoff-dependent survivor selection, benchmark dependence, model fitting or calibration variation. None of these simulations can repair the v0.3 predictive precision failure or establish official-cutoff transport.

## Verification boundary

`tests/test_v04_inference_worker.py` contains deterministic formula checks and a tiny debug run over the registered scenarios. Its output is software-debug evidence only, not a numerical operating-characteristic result. The root lead retains independent responsibility for mathematical review and for freezing a prospective substantive simulation plan before execution.
