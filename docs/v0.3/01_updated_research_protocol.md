# RP-001 — Updated Research Protocol v0.3

**Status: PROTOCOL_DRAFTED. Development pilot returned; REVISE AGAIN. Final protocol is not locked.**
Research Owners: Raihan × Rei. Lead scientific and mathematical review: Rei, SOL Extra High role. Research worker: GPT-6 LUNA MAX; worker conclusions were reviewed and material mathematics reconstructed directly by the lead.

## Question, estimand and authorization

The primary question is unchanged from v0.2:

> Is a compact hierarchical Bayesian predictor competitive in 90% interval score with calibrated CQR at the official FD001 unseen-engine endpoint, with engine-level uncertainty and audited dependence?

The proposed primary endpoint is mean 90% interval score in cycles, using uncapped RUL and one forecast at the official endpoint per engine. The proposed primary comparison is Bayesian minus CQR score. Lower is better. A negative point estimate alone does not establish superiority. Current empirical work uses synthetic data and official FD001 **training** only. Official test covariates and test labels remain uninspected, and no primary confirmatory comparison has been run. The owner's conditional development approval does not authorize final evaluation or a change to the primary question.

For a future authorized run, distinguish (i) the exact finite-benchmark mean difference, and (ii) inference for an assumed engine/cutoff population conditional on the frozen fitted pipeline. The second requires assumptions beyond having 100 distinct engine IDs. This protocol does not claim applicability to operational engine maintenance.

## Data, cutoffs and representation

The NASA training file has 100 engines, 20,631 cycles and 26 fields. Engine roles are the unchanged SHA-256 ordering with seed `RP001-20261008-v0.2`: 55 fit, 15 tune, 30 calibration reserved. Each engine receives one outcome-blind hash cutoff, an integer in [30,250]; retain only C<T. No cutoff redraw is allowed. The observed eligible counts are 43 fit, 13 tune and 25 calibration; final fitting uses the 56 eligible fit+tune engines. All role assignments, lifetime-derived eligibility and prefix checks are retained in the split manifest and audit.

Eligibility conditions on survival and disproportionately retains longer-lived engines. Outcome-blind hashing is not a proof of stochastic independence. The official test cutoff distribution cannot be reconstructed from the allowed training information. Formal conformal coverage transported to official test endpoints is therefore not established.

At each cutoff use sensors observed through C only. Training-only, equal-engine weighted scaling drops channels with weighted SD≤1e-8. Retain PC1, orient its largest absolute loading positive, and scale to unit fitting variance. The Bayesian model uses the most recent min(30,C) PC values with age [1,log(C/100)] and fixed intercept/slope basis. Gradient boosting uses five prefix summary features; linear quantile regression uses age plus the 30-position observed sequence. No terminal sensor values, future sensors, or capped RUL enter preprocessing. The refit representation is learned again from the 56 fitting prefixes and frozen before calibration outcomes are used.

## Bayesian candidate and prediction

The fixed principal candidate is a conditional alive-landmark Gaussian hierarchy, not a physical failure-time model. Let g be a two-dimensional local level/slope, z the observed PC sequence, and y=log(T−C): g|a~N(Γa,Σ), z|g~N(Bg,σ_z²K_ρ), y|g,a~N(aᵀβ+γᵀg,σ_r²), K_ij=ρ^|i−j|. Latents are integrated analytically. Priors and exact conditional equations are specified in report 02 and implemented in `src/rp001/model.py`.

For each new engine separately, update the global posterior using that engine's sensor likelihood only. Then integrate its conditional log-RUL distribution over the updated global parameters and latent conditional distribution. Obtain mixture CDF quantiles at .05/.50/.95; averaging draw-level quantiles is prohibited. No other new engine's sensors are pooled in this forecast rule. Exact sensor-only MCMC provides a diagnostic oracle, not a replacement selected by observed test outcomes.

The predefined predictive precision gate failed: maximum approximate quantile MCSE 0.728972 cycles >0.5. The present posterior draws and Bayesian calibration correction are development evidence, not inference-ready predictions. A revised, prospectively specified numerical precision plan is required before lock.

## Comparator and calibration

The fixed CQR search contains eight gradient-boosting quantile configurations (depth 1/2, leaf 5/10, learning rate .03/.1, 200 estimators) and four linear quantile configurations (penalties .001/.01/.1/1). Both .05/.95 endpoints are fitted and sorted. Choose by uncalibrated mean interval score on the 13 tuning engines, with the specified ≤0.5-cycle score tie band and deterministic simplicity rule. This tie rule is a model-selection convention; it is not a practical-significance threshold.

The selected development configuration is `gb-depth1-leaf10-lr0p1`. Refit on 56 engines. Separately fit its .50 quantile. Freeze configuration and representation before accessing calibration outcomes. For each of 25 calibration engines compute s=max(L−R,R−U); choose k=ceil(26×.90)=24 and q=max(0,s_(24)). Output [L−q,U+q] intersected with nonnegative RUL support. If k>n the correction is infinite, never silently clipped to n. This deliberately nonshrinking CQR variant is fixed and disclosed.

The Gaussian log-RUL reference uses Student-t predictive intervals including coefficient and residual uncertainty, with estimability checks. Bayesian+the same post-hoc conformal calibration is a proposed **secondary** ablation. Raw versus calibrated CQR and Bayesian intervals can diagnose calibration effects. No diagnostic replaces the proposed primary comparison.

## Evaluation and uncertainty plan — proposed, not executed

After an explicit final owner authorization, freeze protocol, data-access policy, model states, priors, calibration corrections, environment and analysis code. Only then generate per-engine predictions from authorized test sensors, store and hash all predictions, and request or use the separately authorized test-label step. There is no authorization to do these steps in this development return.

For the future primary comparison let d_i=IS90_B,i−IS90_CQR,i and D=mean(d_i). Use paired engine bootstrap-t with 20,000 resamples for a two-sided 95% interval and a one-sided 95% upper bound under H0:D≥0. Keep all forecasts from an engine in the same resampling unit if any secondary repeated-cutoff analysis is later approved. Disclose infinite/undefined intervals, dominant influences and degenerate standard errors; do not select a favorable inferential fallback after labels are seen. Operating-characteristic diagnostics are in reports 05/06. A final failure policy for influential cases remains to be fixed before lock.

The primary interval conditions on the realized fitted/tuned/calibrated pipeline. It excludes variation in training engines, PCA, hyperparameter selection, cutoff realization and calibration cohort. Posterior parameter uncertainty conditional on observed fitting data does not supply this missing repeated-pipeline uncertainty. Full-pipeline sensitivity requires repeating all relevant stages on training-only resamples, and remains incomplete.

Report absolute score differences and intervals, width and miss-penalty decompositions, coverage with Wilson intervals, and median MAE/RMSE/bias. CRPS is not a comparable endpoint for CQR without a defined full predictive distribution. There is one proposed primary comparison; secondary ablations are exploratory. No fixed 5-cycle practical superiority or equivalence threshold is adopted because a defensible utility mapping is absent.

## Changes, stopping and lock requirements

The development plan and its initial snapshot preserve predefined likelihood, sampler, recovery and prediction criteria. Two documented serialization repairs retain failed runs with unchanged data/seeds/model/sampling settings. The existing proposed refit step and a sensor-only oracle were added as numerical validation, without changing the primary question or searching for a Bayesian winner. Calibration outcomes are now known under a frozen development policy; future retuning must disclose adaptive reuse and cannot call this cohort untouched.

Before lock: remedy predictive precision under a revised fixed plan; defend prior plausibility and identifiability limitations; decide the official-cutoff transport claim scope; predefine inference failure and whole-pipeline sensitivity policies; record fair information and tuning budgets. Publication additionally requires current novelty/full-method and data-redistribution reviews. Research Owners retain final authorization. The detailed open items and disposition are in reports 08/09.
