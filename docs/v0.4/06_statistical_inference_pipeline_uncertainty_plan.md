# RP-001 v0.4 — Statistical inference and pipeline uncertainty plan

**Status: the frozen synthetic operating-characteristic run and eight-run training-only pipeline-perturbation summary are complete; the primary comparative claim remains unresolved.** The remediation plan was frozen in commit `1f01ef5c576094e3564172f03a22b1f172e37f27`. Research mode: `dataset-benchmark`. The primary comparative claim remains unresolved. This document does not authorize official test access, confirmatory evaluation, or final protocol lock. The current study gate remains `PROTOCOL_DRAFTED`.

The v0.3 development calibration outcomes were seen after the initial freeze. New v0.4 analyses remain exploratory; none may be presented as untouched confirmation.

## Research question and claim boundary

The research question remains whether the fixed hierarchical Bayesian predictor is competitive with calibrated CQR in 90% interval score at the official FD001 unseen-engine endpoint. The planned score difference is Bayesian minus CQR in cycles; lower is better. The primary question, outcome, and comparison are unchanged from v0.3. No practical superiority margin is set, and the v0.4 remediation plan does not authorize a primary p-value or an unconditional superpopulation superiority claim.

The primary finite-benchmark quantity and the two uncertainty analyses answer different questions:

| Quantity | Definition | Claim it supports |
| --- | --- | --- |
| Exact finite-benchmark effect | Arithmetic mean of the paired stored-prediction score differences over the complete planned set of official engine endpoints | Exact descriptive effect for those evaluated endpoints and those stored predictions |
| Conditional engine-pair inference | Paired bootstrap-t over complete engine-level score differences, with the fitted, tuned, and calibrated pipeline held fixed | A qualified diagnostic for an assumed engine-pair population; it excludes pipeline refitting and requires its sampling assumptions |
| Pipeline perturbation sensitivity | Changes across the eight planned training-only pipeline perturbations | Descriptive sensitivity to resampling, cutoffs, preprocessing, selection, refitting, and calibration; it is not a total-variance estimate or independent performance comparison |

For engine `i`, let `d_i = IS90_B(i) - IS90_CQR(i)`. The finite-benchmark effect is `D_F = (1/N) * sum_i d_i`, using all planned endpoints and their stored predictions. When every `d_i` is finite, this is the exact mean for that realized benchmark; it has no sampling interval for the fixed set of endpoints. It does not estimate performance on new engines by itself.

A missing paired score, NaN, or infinite score is retained with its engine identity and reason. No engine is dropped, replaced, imputed, capped, or given a favorable value. If all planned paired differences are not finite, the finite numerical mean is unavailable and the failure is reported. A finite `D_F` remains reportable even when a secondary bootstrap diagnostic is unavailable.

## Conditional paired bootstrap-t diagnostic

The separate future official-benchmark diagnostic is planned for 20,000 engine-pair resamples, after owner lock and any required authorization. It is secondary. It must not replace the exact finite-benchmark effect, create a primary p-value, or support an unconditional superiority statement. Its interpretation conditions on the realized pipeline and assumes a target population of exchangeable engine-level pairs under the frozen prediction procedure. Distinct IDs do not, by themselves, establish independent sampling or transport to operational engines and cutoffs.

For finite paired differences `d_1, ..., d_n`, use `SE = s_d / sqrt(n)`, with `s_d` the sample standard deviation using `ddof=1`. Resample the paired engine differences as complete units. Define each bootstrap pivot as:

```text
T_star = (mean(d_star) - mean(d)) / (sd(d_star, ddof=1) / sqrt(n))
```

This pivot is centered at the observed sample mean, not at the null value. With empirical pivot quantiles `q_.025`, `q_.05`, and `q_.975`, report the two-sided 95% interval and one-sided 95% upper bound as:

```text
lower_95 = mean(d) - q_.975 * SE
upper_95 = mean(d) - q_.025 * SE
upper_one_sided_95 = mean(d) - q_.05 * SE
```

The one-sided diagnostic null is `H0: population mean >= 0` versus `H1: population mean < 0`. A negative observed mean alone does not establish superiority.

Suppress this diagnostic if an input score is missing or nonfinite, if the observed SE is zero, or if any bootstrap pivot has a zero/nonfinite denominator or nonfinite value. Preserve the raw engine records, all invalid-resample counts, and the suppression reason. Do not remove invalid draws, switch to a percentile or normal interval, trim/winsorize differences, or choose another test after seeing the result. The finite benchmark mean remains separate and may still be reported when its inputs are finite.

A conditional interval does not account for variation in the training cohort, PCA, tuning, cutoff realization, or calibration cohort. Bayesian posterior uncertainty conditional on the fitted data does not supply those omitted repeated-pipeline components. Formal conformal coverage for the official endpoint distribution is not established: cutoff transport is unresolved, and duplicated calibration engines in a bootstrap sample do not satisfy a formal exchangeability guarantee.

## Frozen synthetic operating-characteristic run

The synthetic diagnostic evaluates the behavior of this paired bootstrap-t procedure under eight fixed mean-zero laws. It is not a simulation of the FD001 score-difference distribution and is not evidence about Bayesian-versus-CQR performance. Each scenario has 500 independent datasets of size `n=100`, with 1,999 paired bootstrap resamples per dataset. The total planned workload is 4,000 datasets and 7,996,000 bootstrap resamples. These settings are fixed by the frozen remediation plan; they will not be changed after seeing results.

| Plan scenario | Implementation law | Population mean | Variance / stress feature | Root seed |
| --- | --- | ---: | --- | ---: |
| `normal` | `N(0,1)` | 0 | 1 | 50001 |
| `lognormal1` | `Lognormal(0,1) - exp(1/2)` | 0 | Finite; right-skewed | 50002 |
| `lognormal1p5` | `Lognormal(0,1.5) - exp(1.125)` | 0 | Finite; more strongly right-skewed | 50003 |
| `t3` | Student-t, df 3, location 0, scale 1 | 0 | 3; heavy tails | 50004 |
| `rare_outlier` | `0.99*N(0,1) + 0.01*N(0,30^2)` | 0 | 9.99; rare extreme values | 50005 |
| `t1p5` | Student-t, df 1.5, location 0, scale 1 | 0 | Infinite variance; mean exists | 50006 |
| `sparse_discrete` | `P(-1)=0.01, P(0)=0.98, P(+1)=0.01` | 0 | 0.02; ties and degeneracy | 50007 |
| `all_zero` | Point mass at zero | 0 | Zero variance; bootstrap-t denominator unavailable | 50008 |

For each scenario, report the fraction of available intervals that cover the true mean zero and the fraction of available one-sided upper bounds that reject `H0: mean >= 0`. Include Wilson 95% intervals and binomial Monte Carlo standard errors, plus interval availability, zero-SE fractions, nonfinite/input failures, per-scenario runtime, and every dataset-level record. Wilson intervals and binomial MCSE quantify outer simulation-count uncertainty; they do not include the inner bootstrap quantile Monte Carlo error. Coverage/rejection rates conditional on interval availability must be shown together with availability and failure counts.

Any zero observed/bootstrap standard error or nonfinite pivot suppresses that replicate's interval. Failures remain in the raw output and in the denominator diagnostics; no scenario or failed dataset is silently removed. In particular, the all-zero family is expected to expose non-estimability, and sparse-discrete failures are adverse diagnostics. The Student-t(1.5) family has a defined mean but infinite variance, so its rates are stress behavior outside the standard finite-variance justification for ordinary bootstrap-t coverage. They are not grounds for replacing this method with a post hoc alternative.

The run entry writes all replicate results to `experiments/v0.4/inference/v04_paired_bootstrap_t_oc.json` and its provenance record to `experiments/v0.4/registry/v04_inference_oc.json`. It binds the results to the frozen plan, executed source hashes, Git snapshot, environment fingerprint, seeds, and measured wall/process CPU time. This synthetic run uses 1,999 bootstrap draws per dataset. The distinct 20,000-resample conditional diagnostic above is a future official-benchmark analysis and is not run here.

## Whole-pipeline variance and empirical perturbations

For a hypothetical new-engine estimand and a random fitted pipeline `P`, the law of total variance separates conditional engine variation from pipeline variation:

```text
Var(D_hat) = E_P[Var_E(D_hat | P)] + Var_P[E_E(D_hat | P)]
```

A paired engine bootstrap with `P` fixed addresses only the first component, under the engine-pair sampling assumptions. The completed v0.4 sensitivity run does not estimate the second term: it contains four dependent canonical/alternate perturbation pairs, not repeated independent pipeline draws with assessment outcomes. It does not provide a total-pipeline confidence interval.

The frozen sensitivity plan used eight pipeline executions arranged as four canonical/alternate cutoff pairs. Within each pair, the same role-stratified engine-bootstrap seed is used; one deterministic alternate cutoff salt is paired with the canonical cutoffs. The run seeds were:

| Pair | Shared role-bootstrap seed | Alternate cutoff salt | Canonical run seed | Alternate run seed |
| --- | ---: | ---: | ---: | ---: |
| 1 | 45001 | 46001 | 47001 | 47002 |
| 2 | 45002 | 46002 | 47003 | 47004 |
| 3 | 45003 | 46003 | 47005 | 47006 |
| 4 | 45004 | 46004 | 47007 | 47008 |

Each role was resampled with replacement within its original 55/15/30 fit/tune/calibration roster, at its original draw size. A drawn engine has one cutoff per replicate, shared across repeated copies. Eligibility is `C < T`; ineligible draws are recorded and excluded without redrawing. The minimum distinct eligible counts are 20 fit, 5 tune, and 9 calibration. All eight pipeline records and all eight CQR records completed. All 24 role stages met their applicable distinct-engine minimum, and each retained all ineligible-draw records. Within each of the four pairs, the raw fit, tune, and calibration bootstrap draw IDs match exactly between canonical and alternate runs; changing cutoff salts changes eligibility and downstream fitted data. The same 25 fixed anchor IDs are present in all eight results. The artifact records no official test or protected-archive access and is marked nonconfirmatory.

| Run | Cutoff | Fit eligible multiplicity / unique (ineligible draws) | Tune eligible multiplicity / unique (ineligible draws) | Calibration eligible multiplicity / unique (ineligible draws) | Fitted preprocessor/PCA SHA-256 prefix (selection / refit) |
| --- | --- | --- | --- | --- | --- |
| `1C` (`canonical_infra1`) | Canonical | 43 / 26 (12) | 14 / 10 (1) | 24 / 15 (6) | `e9aa5dc35789` / `a6462c7782ba` |
| `1A` | Alternate | 44 / 25 (11) | 13 / 9 (2) | 26 / 16 (4) | `370e93f9c7fe` / `6d89bfe54c6f` |
| `2C` (`canonical_infra1`) | Canonical | 47 / 31 (8) | 15 / 7 (0) | 25 / 13 (5) | `9f9c05121fe1` / `75b2c9ebb96b` |
| `2A` | Alternate | 50 / 32 (5) | 9 / 5 (6) | 19 / 9 (11) | `175e5b824d1f` / `c3e1e31ff6ae` |
| `3C` (`canonical_infra1`) | Canonical | 42 / 27 (13) | 11 / 7 (4) | 23 / 16 (7) | `8fb495ac32ba` / `4df75bf2de58` |
| `3A` | Alternate | 42 / 25 (13) | 8 / 5 (7) | 23 / 14 (7) | `ef7478aaa984` / `9a4e7a116252` |
| `4C` (`canonical_infra1`) | Canonical | 42 / 25 (13) | 14 / 9 (1) | 26 / 15 (4) | `b05a0cd2d2ee` / `e2881d7e875e` |
| `4A` | Alternate | 36 / 22 (19) | 12 / 9 (3) | 23 / 15 (7) | `6d52581678b9` / `6173ee574d69` |

Here `multiplicity / unique` counts eligible bootstrap rows and distinct eligible engine IDs; excluded counts are the ineligible draws retained from the role sample. All fit/tune/calibration minima (20/5/9) passed. The full fingerprints are in the raw artifact; all eight selection-stage hashes are distinct, as are all eight refit-stage hashes.

| Run | Selected CQR candidate (selected tuning score, cycles) | CQR calibration correction (cycles; rank / score rows) | Bayesian posthoc correction `q_B` (cycles) |
| --- | --- | ---: | ---: |
| `1C` | `linear-l1-alpha0p01` (156.490) | 34.939 (23 / 24) | 2.635 |
| `1A` | `gb-depth1-leaf10-lr0p03` (159.816) | 27.387 (25 / 26) | 3.276 |
| `2C` | `linear-l1-alpha0p01` (122.160) | 15.380 (24 / 25) | 10.820 |
| `2A` | `linear-l1-alpha0p1` (208.221) | 0.000 (18 / 19) | 0.000 |
| `3C` | `gb-depth1-leaf10-lr0p1` (198.133) | 62.981 (22 / 23) | 7.343 |
| `3A` | `linear-l1-alpha0p01` (293.058) | 13.115 (22 / 23) | 13.166 |
| `4C` | `gb-depth2-leaf5-lr0p1` (149.570) | 4.000 (25 / 26) | 3.552 |
| `4A` | `linear-l1-alpha0p01` (110.171) | 9.746 (22 / 23) | 0.000 |

Every canonical/alternate pair selected a different CQR candidate; eight runs selected five distinct candidates. In `1A`, the selected score 159.816 was 0.123 cycles above the best candidate score 159.692 and reflects the frozen deterministic simplicity rule. The CQR corrections use the duplicated bootstrap calibration rows and have no formal conformal exchangeability guarantee. Bayesian `q_B` is the stored nonshrinking posthoc correction calculated from its calibration predictions; it widens the lower and upper 90% quantile endpoints and was not used for model or prior selection. CQR calibration outcomes likewise supplied the correction only, not candidate selection. The two correction sequences vary across the paired cutoff perturbations: CQR `q` ranges from 0.000 to 62.981 cycles, and Bayesian `q_B` ranges from 0.000 to 13.166 cycles.

The existing fixed-anchor outputs allow a descriptive paired endpoint comparison, without assessing anchor outcomes. For each Bayesian run, the corrected endpoints are calculated from the stored raw quantiles as `lower=max(0, q05 - q_B)` and `upper=max(0, q95 + q_B)`; `q50` is unchanged. CQR anchor endpoints are already stored after its calibration correction. Aligning the same 25 anchor IDs within each of the four pairs gives 100 alternate-minus-canonical endpoint differences per column:

| Fixed-anchor endpoint | Mean absolute paired change (cycles) | 95th percentile of absolute change | Maximum absolute change |
| --- | ---: | ---: | ---: |
| Bayesian corrected `q05` | 7.6 | 15.8 | 23.0 |
| Bayesian `q50` | 8.3 | 25.2 | 45.5 |
| Bayesian corrected `q95` | 23.0 | 75.1 | 178.7 |
| CQR calibrated lower endpoint | 34.2 | 89.6 | 110.0 |
| CQR calibrated upper endpoint | 56.1 | 155.1 | 174.4 |

These summaries are ranges and absolute shifts on the fixed anchor set, not a variance estimate, confidence interval, engine-level score, or independent comparison. No assessment score or cross-perturbation performance winner was calculated. The four pairs share bootstrap draws within pair and are not independent pipeline replicates; their results do not identify `Var_P[E_E(D_hat | P)]` or total-pipeline uncertainty.

Across the 33 MCMC result records in the frozen campaign, all completed; 32 passed their configured diagnostics and `v04_syn_high_rho_3` failed. That failure remains visible and does not trigger a model switch. The four separate original records `v04_pipeline_{1..4}_canonical` preserve preparation-only failures: `ValueError("cutoff_salt is only valid with cutoff_mode='alternate'.")`. No HPO, NPZ data artifact or MCMC started in those attempts. Infrastructure campaign 1 corrected that helper call and executed the four originally planned fits with unchanged configurations/seeds/draws under `_infra1` IDs; their successful records are distinct from the original failures. Campaign 2 serialized the 600 already retained precision-validation records and rebuilt their summaries without resampling or reinvoking the validation runner. Both campaigns are accounted for in report09. No MCMC diagnostic failure was rerun or replaced.

The raw pipeline-variation artifact is [`pipeline_variation.json`](../../experiments/v0.4/analysis/pipeline_variation.json), SHA-256 `dbde56623335db020179f671e08533b55897de05f550a183b0b63ec6b92e47ab`. It records Git commit `87a0083314daafb79f7ae3c67e23abd5979bc82a`, clean executed sources, the frozen plan SHA-256 `0c6a7e1e924636cec6196295eac19b29a6bd7faa85e18b081549f8287ab0b99b`, and environment fingerprint `f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c`. No fit or simulation was rerun to produce the descriptive summaries above.

## Historical evidence and completed v0.4 synthetic results

The v0.3 exploratory check used 1,000 datasets per law, `n=100`, and 1,000 bootstrap resamples under Normal and centered lognormal with sigma 1. It reported 95% coverage estimates 0.951 (binomial MCSE 0.006826) and 0.942 (MCSE 0.007392), and one-sided false-rejection estimates 0.056 (MCSE 0.007271) and 0.066 (MCSE 0.007851), respectively. This is limited historical synthetic evidence; it does not cover the v0.4 stress families or establish validity for real score differences. The v0.3 Bayesian predictive-quantile precision gate also failed at 0.728972 cycles against its 0.5-cycle criterion. The v0.4 results do not waive that earlier failure.

**v0.4 synthetic OC status: completed under the frozen configuration.** The run attempted 4,000 datasets and 7,996,000 bootstrap resamples (500 datasets per scenario, `n=100`, 1,999 resamples each). All 4,000 dataset-level records were retained. There were 3,001 available intervals and 999 unavailable replicates: 565 terminal `zero_observed_standard_error` failures and 434 terminal `zero_bootstrap_standard_error` failures. There were no input/nonfinite failures and no unexpected errors. These terminal failure counts are mutually exclusive; the zero-bootstrap-SE draw fractions below also include zero-SE draws within datasets whose terminal status was zero observed SE.

The table reports rates conditional on an available interval. Parentheses give the Wilson 95% interval and the binomial outer-simulation MCSE in percentage points. These MCSEs do not include inner bootstrap quantile Monte Carlo error. For `sparse_discrete`, only one interval was available, so its conditional rates are not meaningful evidence of operating performance. For `all_zero`, no interval was available and both rates are not estimable.

| Scenario | Available intervals | 95% coverage (Wilson 95%; MCSE, pp) | One-sided rejection of `H0: mean >= 0` (Wilson 95%; MCSE, pp) |
| --- | ---: | --- | --- |
| Normal | 500/500 | 95.8% [93.7, 97.2]; 0.90 | 5.0% [3.4, 7.3]; 0.97 |
| Centered lognormal, sigma=1 | 500/500 | 94.6% [92.3, 96.3]; 1.01 | 8.2% [6.1, 10.9]; 1.23 |
| Centered lognormal, sigma=1.5 | 500/500 | 91.4% [88.6, 93.6]; 1.25 | 11.2% [8.7, 14.3]; 1.41 |
| Student-t, df=3 | 500/500 | 93.4% [90.9, 95.3]; 1.11 | 7.0% [5.1, 9.6]; 1.14 |
| Rare-outlier mixture | 500/500 | 92.6% [90.0, 94.6]; 1.17 | 6.8% [4.9, 9.4]; 1.13 |
| Student-t, df=1.5 (infinite variance; stress only) | 500/500 | 90.4% [87.5, 92.7]; 1.32 | 10.0% [7.7, 12.9]; 1.34 |
| Sparse discrete | 1/500 | 100.0% [20.7, 100.0]; 0.00 (only 1 interval) | 0.0% [0.0, 79.3]; 0.00 (only 1 interval) |
| All zero | 0/500 | Not estimable (0 available) | Not estimable (0 available) |

| Scenario | Interval availability (Wilson 95%; MCSE, pp) | Bootstrap draws with zero SE | Unavailable replicates by terminal status | Runtime (s) |
| --- | --- | ---: | --- | ---: |
| Normal | 500/500; 100.0% [99.2, 100.0]; 0.00 | 0/999,500 (0.000%) | None | 1.590 |
| Centered lognormal, sigma=1 | 500/500; 100.0% [99.2, 100.0]; 0.00 | 0/999,500 (0.000%) | None | 1.594 |
| Centered lognormal, sigma=1.5 | 500/500; 100.0% [99.2, 100.0]; 0.00 | 0/999,500 (0.000%) | None | 1.478 |
| Student-t, df=3 | 500/500; 100.0% [99.2, 100.0]; 0.00 | 0/999,500 (0.000%) | None | 1.323 |
| Rare-outlier mixture | 500/500; 100.0% [99.2, 100.0]; 0.00 | 0/999,500 (0.000%) | None | 1.314 |
| Student-t, df=1.5 (stress only) | 500/500; 100.0% [99.2, 100.0]; 0.00 | 0/999,500 (0.000%) | None | 1.311 |
| Sparse discrete | 1/500; 0.2% [0.04, 1.12]; 0.20 | 270,027/999,500 (27.016%) | 65 zero observed SE; 434 zero bootstrap SE | 1.286 |
| All zero | 0/500; 0.0% [0.00, 0.76]; 0.00 | 999,500/999,500 (100.000%) | 500 zero observed SE | 1.231 |

Across the nondegenerate finite-variance cases, the 95% Wilson intervals for coverage exclude 95% for centered lognormal sigma=1.5 (undercoverage) and the rare-outlier mixture (undercoverage). The one-sided rejection intervals exclude 5% for centered lognormal sigma=1, centered lognormal sigma=1.5, and Student-t df=3 (elevated rejection in this run). These are adverse diagnostics from a fixed 500-dataset Monte Carlo study, not confirmatory tests of the method; outer Wilson intervals omit inner-bootstrap quantile error. For Student-t df=1.5, the mean exists but variance is infinite, so its 90.4% coverage and 10.0% rejection are stress behavior only. No nominal 95% coverage or 5% rejection control is certified across the stress domain.

The sparse-discrete results show the failure mode directly: 65 samples had zero observed SE, 499 samples had at least one zero-SE bootstrap resample, and only one of 500 datasets yielded an available interval. The all-zero family had zero available intervals, 500 zero observed SEs, and all 999,500 bootstrap resamples had zero SE. No invalid resample was discarded and no alternate interval, trimming, winsorization, imputation, or favorable fallback was used. Nonfinite/input failures were zero in every scenario.

The frozen remediation plan specified no numerical acceptance threshold for these synthetic coverage or rejection rates. They are therefore descriptive diagnostics, not a pass/fail certification gate. The study gate remains `PROTOCOL_DRAFTED`; this run does not authorize official test access, confirmatory evaluation, final protocol lock, or a superpopulation superiority claim. The future 20,000-resample official-benchmark conditional diagnostic remains unrun and requires its separate authorization. The completed eight-run perturbation results are reported above; their four paired outcomes cannot be converted into a total-pipeline variance estimate.

Run provenance: run ID `v04_inference_oc_500x1999_n100_seed50001`; start `2026-10-08T14:49:28.747578Z`; finish `2026-10-08T14:49:40.004383Z`; scientific wall time 11.256835 s; process CPU time 11.140625 s. The raw result is [`v04_paired_bootstrap_t_oc.json`](../../experiments/v0.4/inference/v04_paired_bootstrap_t_oc.json), SHA-256 `1d91e53ea6c44f5ebc5d86a3c846b4e152a9542dc2fd3aa80bdb729c429b425a`, with 4,000 replicate records. Its registry entry is [`v04_inference_oc.json`](../../experiments/v0.4/registry/v04_inference_oc.json). The frozen plan SHA-256 is `0c6a7e1e924636cec6196295eac19b29a6bd7faa85e18b081549f8287ab0b99b`; Git HEAD at run start was `7a824ed0fe8346d3d65412de042dcaf2055894c1`, with scientific sources and plan clean. The executed inference module SHA-256 is `dc05f013b9c9bf05463269b4bd6c6ece74505467e5a4c2125a0ed0690ded1d64`, the run entry SHA-256 is `36be33a5637e9b0c0d7f0ea8164b3a7f70beb0c54a2cbb1c71ba0aa35def7af1`, and the environment fingerprint is `f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c` (Python 3.12.14, NumPy 2.4.6, Windows 11). The pipeline-variation artifact and its provenance are summarized above; no mean, standard error, confidence interval, or variance estimate is assigned to the four pairs.

## Reproducibility and unresolved validity threats

The frozen remediation plan limits aggregate compute to six CPU-hours and artifacts to 2 GiB, with at most two parallel processes, no additional spending, and retained failures. Both the synthetic OC run and the pipeline perturbations used their assigned compute slots and retained adverse results. The synthetic result/registry and pipeline-variation artifact record their configuration, source and plan fingerprints, Git snapshot, environment fingerprint, and available runtime/provenance fields.

- Frozen plan: [`configs/v0.4/remediation_plan.json`](../../configs/v0.4/remediation_plan.json), SHA-256 `0c6a7e1e924636cec6196295eac19b29a6bd7faa85e18b081549f8287ab0b99b`.
- Plan-freeze commit: `1f01ef5c576094e3564172f03a22b1f172e37f27`. Run source snapshot: `7a824ed0fe8346d3d65412de042dcaf2055894c1`.
- Paired inference module SHA-256: `dc05f013b9c9bf05463269b4bd6c6ece74505467e5a4c2125a0ed0690ded1d64`; run entry SHA-256: `36be33a5637e9b0c0d7f0ea8164b3a7f70beb0c54a2cbb1c71ba0aa35def7af1`; shared provenance helper SHA-256: `6c353d14140d9af2c1a20935751fb0218b8e7312da8490f3a743d92bc5e11933`.
- Validated environment fingerprint: `f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c`.
- Historical evidence: [v0.3 comparative evaluation design](../v0.3/06_comparative_evaluation_design.md), [v0.3 mathematical verification](../v0.3/02_mathematical_verification_report.md), and [v0.3 risk register](../v0.3/08_risks_assumptions_decisions.md).

Cutoff transport to official endpoints, engine-pair independence, repeated-pipeline uncertainty, duplicate-calibration exchangeability, working-prior/domain limits, practical Bayesian identification and future-endpoint numerical precision remain material validity threats. The original 25 development cases pass their prospective numerical gate; the high-rho synthetic convergence failure remains unresolved. This plan supports no maintenance-safety or operational-deployment claim. Final authorization remains with the research owners.
