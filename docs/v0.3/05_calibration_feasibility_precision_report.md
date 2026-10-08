# RP-001 — Calibration Feasibility and Precision Report v0.3

**Finite-sample calculation verified; official-population coverage guarantee unresolved. Numerical Bayesian prediction gate FAIL.**

## What 25 engines can and cannot establish

At n25, corrected CQR uses rank24. Exchangeability of calibration and target scores from the fixed fitting procedure supports marginal coverage at least .90. It does not guarantee .90 conditional coverage for each engine age, degradation stage, fitted calibration cohort or an unverified shifted population. Under the stronger independent continuous-score idealization, mean rank coverage is .923077, but realized cohort conditional coverage has central95% range [.796483,.990160]. P(cohort conditional coverage<.90)=.271206. A repeated-cohort average guarantee is not a per-cohort assurance.

Analytic order-statistic calculations and 5,000 synthetic score cohorts per size yield the following. These are **idealized repeated-cohort coverage distributions**, not official data results or confidence intervals for test coverage.

| n calibration | k | Ideal mean coverage | Ideal SD | Central95% cohort-coverage range |
| --- | --- | --- | --- | --- |
| 9 | 9 | 0.9000 | 0.0905 | [0.6637, 0.9972] |
| 19 | 18 | 0.9000 | 0.0655 | [0.7397, 0.9870] |
| 25 | 24 | 0.9231 | 0.0513 | [0.7965, 0.9902] |
| 30 | 28 | 0.9032 | 0.0523 | [0.7793, 0.9789] |
| 50 | 46 | 0.9020 | 0.0412 | [0.8077, 0.9667] |
| 100 | 91 | 0.9010 | 0.0296 | [0.8360, 0.9510] |

Rank rounding causes nonmonotone conservatism as n changes. Increasing n generally improves precision, but integer boundaries can change the realized mean and undercoverage probability. n25 cannot support precise .90 conditional calibration. Even with a fixed interval and100 independent assessment engines, hypothetical90/100 coverage has Wilson95% [.825634,.944771]. More sensor rows do not increase the number of independent endpoints.

## Training-only calibration feasibility

After the CQR candidate and refit representation were frozen, the25 reserved eligible training engines were used for calibration/influence diagnostics. Selected configuration: gb-depth1-leaf10-lr0p1; q_raw=q=19.987559cycles. No calibration-engine coverage or score was treated as independent assessment performance. All12 completed candidates and their tuning selection record remain available.

For500 draws of subsets at each fixed size within this cohort, correction distributions are:

| Subset n | k | Correction 2.5% / median /97.5% cycles |
| --- | --- | --- |
| 9 | 9 | 0.000 / 19.988 / 22.000 |
| 19 | 18 | 0.000 / 19.988 / 19.988 |
| 24 | 23 | 9.612 / 19.988 / 19.988 |
| 25 | 24 | 19.988 / 19.988 / 19.988 |

These without-replacement ranges are sensitivity summaries, not confidence intervals or evidence that a favorable cohort should be selected. Leaving one engine out gives correction9.612119..19.987559cycles. Fixed-model bootstrap resampling of25 scores gives quantiles[0,19.987559,21.999902]cycles. Sparse extreme order statistics and n25 make ordinary empirical-bootstrap tail precision fragile. This bootstrap excludes representation/model/hyperparameter refitting.

Bayesian+post-hoc calibration is feasible as a secondary development ablation: the same rank24 nonshrinking rule gives q=0. It is marked **not accepted for inference**, because quantile numerical precision failed. A zero correction does not validate raw Bayesian coverage on independent engines or establish superiority.

## Cutoff and selection sensitivity

The rule assigns C in30..250 without observing lifetime in its construction, then retains C<T. The survivor sample overrepresents long-lived engines: lifetime-rank quartile eligibility14/25,20/25,22/25,25/25. Lead reconstruction gives cutoff/lifetime Pearson−.014760 among all engines and+.243970 among survivors; Spearman−.067357 and+.180308. Descriptive sample correlations do not establish stochastic independence or causal selection effects.

One hundred fixed salt perturbations with the same reserved roles yield eligible totals69..85 (median78), calibration counts18..29 (median23). Eighty-three engines change eligibility in at least one perturbation. These are deterministic membership/count sensitivity analyses; no salt was chosen using performance. They do not estimate whole-pipeline score variability, and alternative pipelines were not all refitted.

The official cutoff mechanism/distribution are unknown from allowed training metadata. Distribution matching and exchangeability to official endpoint pairs are **unverified**. A future empirical finite benchmark may support explicitly qualified claims; this audit does not support distribution-free official-population coverage.

As a mathematical illustration only, synthetic target scores with SD1.5 times calibration-score SD reduce mean ideal coverage to .773826 (MCSE .001142). This is not an estimate of actual official shift. It illustrates why score-distribution mismatch matters.

## Conditional versus full-pipeline precision

The law-of-total-variance illustration uses400 synthetic Gaussian-regression+conformal training/calibration pipelines (fit56,cal25), each with40 independent assessment sets of100. Mean within-pipeline variance=122.432684; between-pipeline variance after finite-assessment Monte Carlo correction=136.092813; total=258.525497. Conditional assessment SD=11.064930 versus full illustrated pipeline SD=16.078728. These are synthetic score units, not empirical RP-001 uncertainties or a Bayesian-versus-CQR comparison.

It includes regressor refitting and calibration-cohort replacement, but excludes PCA, hyperparameter selection, Bayesian sampling and cutoff/data selection. The missing variance term is illustrated without completing a full-pipeline study. The proposed primary paired bootstrap conditions on all fitted/tuned/calibrated artifacts. Whole-pipeline claims require prospectively repeating every relevant stage on training-only resamples.

## Acceptance

Calibration computation and fixed-cohort influence checks are complete. Precise conditional coverage, official cutoff transport and whole-pipeline variability remain open. Bayesian integration has minimum importance ESS3711.54 but maximum approximate quantile MCSE .728972>.5cycle; this FAIL cannot be waived by a calibration correction or one-engine oracle. **REVISE AGAIN.**

Evidence: `results/pilot/statistical_design.json`, `results/pilot/comparator_calibration.json`, `results/pilot/predictive_integration.json`, `experiments/development_data_audit.json`, `logs/lead_cutoff_verification.json`. Direct verification: report02.
