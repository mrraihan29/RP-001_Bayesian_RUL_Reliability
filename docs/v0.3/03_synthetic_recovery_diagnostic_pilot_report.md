# RP-001 — Synthetic Recovery and Diagnostic Pilot Report v0.3

**Development completed; REVISE AGAIN. Sampling diagnostics pass, predictive precision fails.** All results are synthetic or training-only exploratory evidence.

## Fixed design and retained failures

Four independent fixed synthetic datasets use n=56 engines, 30 sensor observations, ages uniformly drawn as integer cutoffs30..250, and seeds3101/3102/3103/3104: ρ=0/.5/.9, plus weak γ=[−.03,.02] at ρ=.5. Truth for other cases is β=[log100,−.4], γ=[−.35,.15], Γ=[[.1,.5],[−.1,−.25]], τ=[.45,.30], r_g=.2, σ_z=.30, σ_r=.25. These simulate the specified conditional landmark hierarchy. They do not simulate complete degradation-to-failure trajectories or verify the lifetime-selection mechanism.

The official training fits are principal fit43, prior SD half/double, fixed ρ=0, contamination residual, principal refit56, and sensor-only oracle on refit56 plus the first deterministic eligible calibration engine11. Four chains each use 1,000 warmup and 2,000 retained draws, two active CPU cores, target acceptance.95, maximum depth12 and nutpie NUTS.

The first synthetic ρ0 run and its first serialization repair failed when saving nested backend metadata. Both failed records remain. The second repair handles InferenceData and DataTree root/group attributes; it changes storage handling only. Successful `syn_r0_repair2` uses the same generated data, seed, model and sampler settings. Failed attempts are not replaced by favorable-seed reruns. Two infrastructure repairs have been consumed; no additional attempt was run to erase the predictive precision failure.

## Sampling diagnostics

Predefined gates: Rhat<1.01, bulk/tail ESS≥400, zero divergences, every-chain BFMI>.3 and depth saturation≤1%. The following physical-parameter summaries pass. Auxiliary sampled variables eta_rho and gcor_u also pass; values are retained in `logs/auxiliary_diagnostics.json`.

| Run | Max Rhat | Min bulk ESS | Min tail ESS | Divergences | Min BFMI | Status |
| --- | --- | --- | --- | --- | --- | --- |
| syn_r0_repair2 | 1.00128 | 6714 | 5414 | 0 | 0.944 | PASS |
| syn_r05 | 1.00214 | 1826 | 1498 | 0 | 0.856 | PASS |
| syn_r09 | 1.00383 | 804 | 479 | 0 | 0.815 | PASS |
| syn_weak | 1.00282 | 1622 | 1511 | 0 | 0.849 | PASS |
| base | 1.00117 | 4341 | 4812 | 0 | 0.977 | PASS |
| prior_half | 1.00066 | 4800 | 4777 | 0 | 0.974 | PASS |
| prior_double | 1.00152 | 3935 | 4196 | 0 | 0.907 | PASS |
| rho_zero | 1.00106 | 4323 | 4496 | 0 | 0.959 | PASS |
| contamination | 1.00126 | 4415 | 5348 | 0 | 0.974 | PASS |
| refit | 1.00094 | 4134 | 4643 | 0 | 0.970 | PASS |
| sensor_oracle | 1.00064 | 4405 | 5287 | 0 | 0.933 | PASS |

All observed depth-saturation fractions are zero. Good diagnostics do not prove exploration of every possible posterior mode or domain validity.

## Parameter recovery and identifiability

| Synthetic run | Truth in 95% intervals /14 | Max |posterior mean−truth|/posterior SD |
| --- | --- | --- |
| syn_r0_repair2 | 14/14 | 1.620 |
| syn_r05 | 14/14 | 1.555 |
| syn_r09 | 12/14 | 2.984 |
| syn_weak | 13/14 | 2.172 |

There are only four fixed datasets. Counting covered coordinates within a correlated vector is not a repeated-sampling coverage experiment; these counts do not certify 95% posterior calibration. No run triggered the gross >3 posterior-SD discrepancy flag. The high-ρ and weak-signal scenarios recover some coordinates less precisely. Recovery is consistent with an implemented finite-dimensional target, while global/practical identifiability remains qualified.

Fixing PC sign/scale and the intercept/slope basis removes arbitrary latent rotations and representation scale choices. It does not prove every residual/covariance parameter uniquely identified by 56 engines. When sensor noise is high or γ is weak, age effects, γ and σ_r can trade off. In principal fit43 the largest absolute measured posterior correlation is γ[1] versus β[0]=−.6630; γ components correlate−.4825, and σ_r versus γ[1]=.4098. These show coupled uncertainty rather than a cleanly separated mechanism. No formal structural-identifiability proof, repeated simulation-based calibration or prior-to-posterior information analysis has been completed.

## Prior predictive checks

4,000 prior draws per scale at ages30/100/250 show very broad RUL support. Principal prior median RUL is approximately100/100/107 cycles and its .95 quantiles are1534/871/1284 cycles. Prob(RUL>1000)=.08025/.041/.070. Half-scale .95 quantiles are339/259/311; double-scale .95 quantiles are139377/46670/93283, with Prob(RUL<1)=.139/.0955/.1205. These are actual simulated summaries in `results/pilot/prior_predictive.json`, not calibrated physical failure probabilities. Proper priors alone do not make these tails defensible. Their plausibility requires a domain-based policy before lock; priors must not be chosen by favorable observed calibration performance.

## Posterior predictive checks

1,000 replicated draws check log-RUL mean, SD and q90, plus PC-sequence SD and mean first-to-last change. Principal fit43 observed log-RUL statistics are4.49915/.75324/5.15636. Conditional replicate tail areas are.514/.464/.839; observed PC SD1.10554 and mean change.46616 have joint replicate tail areas.359/.448. Observed summaries fall inside the central95% replicate ranges. These coarse, in-sample checks do not establish prediction coverage, tail adequacy, correct stage dependence or transport to official test cutoffs. Every successful run retains both conditional and joint PPC summaries.

## Prior and error sensitivity

For the same13 tuning prefixes, these are maximum absolute predictive-quantile changes from the principal fit43, in cycles. They are sensitivity diagnostics, not a method-selection contest.

| Variant | Max |Δ lower| | Max |Δ median| | Max |Δ upper| | Max approx quantile MCSE |
| --- | --- | --- | --- | --- |
| base | 0.000 | 0.000 | 0.000 | 1.272 |
| prior_half | 5.493 | 7.954 | 20.979 | 1.024 |
| prior_double | 1.684 | 2.881 | 5.588 | 0.798 |
| rho_zero | 0.544 | 0.739 | 2.179 | 0.605 |
| contamination | 3.223 | 5.566 | 19.981 | 0.564 |

Upper endpoints can change by about21 cycles under half-scale priors or20 under contamination residuals. Fixed ρ0 yields smaller changes here; this does not establish that serial dependence can generally be ignored. The principal candidate remains unchanged. Some tuning predictions also have approximate MCSE>.5; sensitivity numbers therefore have numerical uncertainty and are not precise effect-size conclusions.

## New-engine integration and predefined failure

On the 25 calibration sensor prefixes after refit56, minimum importance ESS=3711.54/8000 passes the ≥1000 gate. Maximum approximate four-chain quantile MCSE=.728972 cycle fails the ≤.5 gate. This occurs at the upper endpoint for engine86; other failures include upper endpoints for engines listed in the raw predictive results. Approximate between-chain MCSE itself has uncertainty with only four chains and is not a bound.

For engine11, independently sampling the posterior with its sensors included, without its RUL, agrees with the importance-integrated lower/median/upper endpoints to .01870/−.00859/−.02215 cycle. This supports the full global sensor update for one case. It does not override the cohort precision gate. Bayesian+post-hoc calibration computes a development q=0 but is marked `accepted_for_inference=false`.

Retained failure and success records, configuration hashes, seeds, dataset payload hashes and posterior hashes are in `research/experiment_registry.jsonl` and `results/pilot/`. Posterior stores are local ignored scientific artifacts, bound by the delivery manifest. A revised prospective precision plan and a stronger identifiability/prior policy are needed before final lock. No test labels or confirmatory evaluation were used.
