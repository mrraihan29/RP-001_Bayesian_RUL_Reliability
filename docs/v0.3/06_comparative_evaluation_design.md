# RP-001 — Comparative Evaluation Design v0.3

**Proposed design only. No official test predictions, label access, primary comparison or confirmatory decision was executed.**

## Comparison and fair information access

Retain Bayesian versus CQR, mean90% interval score primary. This compares complete procedures: a generative joint Gaussian hierarchy with posterior integration against a tuned non-Bayesian quantile regressor with conformal expansion. Differences can arise from representation, assumptions, regularization, interval construction or tuning, not Bayesian inference alone.

Both receive the same engine-role split, allowed prefixes, age, training labels, uncapped target, refit56 and calibration25 cohorts. Equal-engine weighted preprocessing uses fitting prefixes only. No future sensor values or test-population statistics enter selection. The Bayesian global sensor update uses only the current new engine's prefix, with no pooling of other test engines. CQR uses those sensors through fixed features. Equal information does not imply identical structural biases.

Report actual budgets: one fixed principal Bayesian candidate plus four exploratory sensitivities; CQR12 fixed configurations on13 tuning engines, with no grid extension after results. Search freedom and runtime are not equal. All candidates, criteria, failures, seeds and representations must be disclosed. Development CQR selection is gb-depth1-leaf10-lr0p1; the principal Bayesian prior/error structure is not selected by sensitivity scores. The small tuning sample gives imprecise selection and optimistic best tuning performance; tuning results are not assessment evidence.

Boosting uses five observed-prefix summaries: age, observed endpoint PC, OLS level/slope, residual SD. Linear quantile regression uses age and the30-position observed sequence. Bayesian uses the observed sequence itself. These are fixed representation choices and attribution limits. A matched representation/plugin control could help, but is not completed or substituted into the primary comparison.

## Secondary explanations

Propose Bayesian+the same rank-corrected post-hoc calibration as a secondary ablation, sharing reserved cohort and outcome-use policy. Report raw versus calibrated CQR as well. Within-method differences help explain interval-construction effects. Raw Bayesian versus calibrated CQR remains proposed primary; no secondary winner replaces it.

The Gaussian log-RUL reference has Student-t prediction intervals including coefficient/residual estimation. Removing serial correlation, half/double prior SD and contamination residuals remain exploratory. CRPS is omitted without a defined comparable CQR full predictive distribution. These comparisons do not establish an isolated benefit of Bayesian inference philosophy.

## Future endpoint analysis — final authorization required

For engine i, d_i=IS90_B,i−IS90_CQR,i in uncapped cycles. Its exact benchmark average is descriptive. Population inference conditions on the frozen pipeline and an assumed engine/cutoff sampling model. Resample complete engine pairs, never individual sensor cycles or methods separately. If repeated-cutoff secondary analysis is later approved, all forecasts stay within the same engine cluster.

Proposed primary inference: paired bootstrap-t20,000 resamples, two-sided95% interval and one-sided95% upper bound for H0:D≥0 versus D<0. Report SE, influence of extreme scores, missing/infinite predictions and degenerate bootstrap samples. Finalize the failure policy for dominant observations/unestimable SE before lock. Do not choose a favorable inferential fallback after labels. Power for a5cycle margin is not demonstrated and that margin is not adopted.

The executed synthetic check uses1,000 independent n100 datasets per distribution and1,000 bootstrap resamples each. Nominal95% coverage: Normal .951±.006826 Monte Carlo SE; centered lognormal .942±.007392. One-sided false-positive proportions .056±.007271 and .066±.007851. These are approximate operating characteristics under specified distributions, with skew sensitivity; they do not certify inference for unknown actual score differences or run the proposed primary analysis on official outcomes.

The future table should report absolute mean score difference and interval, mean width, lower/upper miss penalties, coverage/Wilson intervals, median MAE/RMSE/bias, and assessable independent engine count. One primary comparison prevents post-hoc multiplicity expansion; secondaries remain exploratory.

## Practical interpretation and uncertainty boundary

Do not use a fixed5cycle superiority/equivalence margin. Interval score is an interval loss, not maintenance cost; its20×miss penalty prevents interpreting five score cycles as five operation cycles. Without an agreed utility mapping, report effect sizes, precision and decompositions. Statistical evidence of lower expected score is distinct from practical superiority.

Engine-pair bootstrap conditions on realized fitting, tuning and calibration. It excludes cohort replacement and representation/selection variation. Report05's variance simulation is illustrative, not the primary confidence interval. Bayesian posterior variance does not close this distinction. A prospective training-only outer resampling plan must repeat PCA, allowed selection, fitting, calibration and prediction for a broader pipeline-robustness claim; this full exercise was not completed.

## Readiness

Final priors, numerical precision, inference-failure policy, calibration claim scope, frozen model states/code/environment and owner lock must precede test-label access. After a separate final authorization, authorized test sensor predictions must be stored/hashed before any separately authorized labels are used. Current state: **REVISE AGAIN**. Calibration responses were seen only after the development freeze; further redesign must disclose this exposure and cannot call the cohort untouched. Research Owners retain final authority.
