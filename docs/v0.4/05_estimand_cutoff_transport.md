# Estimand and cutoff transport assessment (v0.4)

**Status:** Prospective claim boundary; no official test sensors or labels have been accessed, no test predictions have been made, and no confirmatory evaluation is authorized. The frozen v0.4 target is the exact finite-benchmark mean 90% interval-score difference for stored predictions at all official FD001 endpoints. The primary comparison is the Bayesian principal procedure versus calibrated CQR. See the [owner directive](owner_directive.md), [frozen remediation plan](prospective_remediation_plan.md), and [machine-readable configuration](../../configs/v0.4/remediation_plan.json).

## Primary finite-benchmark estimand

For each official endpoint i, let L and U be a method's stored lower and upper prediction limits and y_i the uncapped official RUL label. The 90% interval score is

    IS90_i = (U_i - L_i) + 20(L_i - y_i) I(y_i < L_i) + 20(y_i - U_i) I(y_i > U_i).

After authorized predictions have been frozen and hashed, and labels are separately authorized, the primary contrast is

    D_FD001 = (1/N) sum_i [IS90_Bayes,i - IS90_CQR,i],

over every official FD001 endpoint, with N equal to the complete official endpoint count. Negative values favor Bayesian. This is a deterministic descriptive contrast for that fixed benchmark and those stored predictions. With all endpoint labels observed, it is not an estimate of a sampling parameter for that same finite set; no primary p-value, confidence interval, equivalence claim, or practical-superiority decision follows from it. The v0.4 plan adopts no primary population test or practical margin. The earlier proposed five-cycle margin remains unapproved; interval-score cycles are not maintenance-cost cycles. The score's factor 20 makes that distinction material. The v0.3 protocol and comparator design make the same finite-versus-population distinction ([protocol](../v0.3/01_updated_research_protocol.md); [comparison design](../v0.3/06_comparative_evaluation_design.md)).

The complete paired endpoint set is the unit of this contrast. Every planned engine must appear once with both methods' stored limits and its label. Sensor cycles, repeated bootstrap copies, or multiple model draws do not increase N. A missing, NaN, infinite, or otherwise unscorable endpoint is retained with its identity and failure reason; it is never dropped, imputed, capped, or trimmed to produce a favorable mean. If a complete finite score vector cannot be formed, the primary scalar result is unavailable under the frozen policy ([inference worker contract](worker_inference_contract.md)).

No such contrast currently exists. The v0.4 owner directive withholds test-sensor and label access, and the worker has not opened the test archive. Any later test-sensor prediction phase and label release require separate owner authorization. Predictions must be frozen before labels are opened.

## Five distinct inferential statements

| Statement | Target and assumptions | What v0.4 permits |
|---|---|---|
| Finite-benchmark effect | The exact paired mean above for all official endpoints and the particular frozen predictions. No engine-sampling model is needed to describe this set. | Primary target after separate data authorizations. Report the complete paired mean and endpoint records; do not attach a superpopulation interpretation. |
| Hypothetical engine-population effect | Expected paired score difference for a specified population of engines under an assumed engine and cutoff sampling law, conditional on the realized fitted, tuned, and calibrated pipeline. An engine-level paired bootstrap requires exchangeable or iid engine pairs and adequate tail behavior. | No primary population claim. The frozen paired bootstrap-t is only a secondary conditional diagnostic; its assumptions and failures must be reported. It cannot account for refitting, selection, calibration-cohort, or cutoff variation. |
| Marginal conformal coverage | Long-run coverage averaged over exchangeable calibration and target scores, conditional on a fixed fitted procedure and the conformal sampling assumptions. | No official coverage guarantee is claimed. Engine-disjoint roles and outcome-blind hashing alone do not establish score exchangeability across pseudo-cutoff calibration cases and official endpoints. Bootstrap multiplicities are repeated observations of the same engines, not new independent engines, and provide no conformal guarantee. |
| Conditional or realized-cohort coverage | Coverage for a particular realized calibration cohort, potentially conditional on its fitted model and observed scores. | Describe the observed calibration cohort only as development evidence. Marginal rank validity does not ensure that this cohort's conditional coverage is 90%. |
| Real-engine generalization | Performance or coverage on operating engines outside the FD001 benchmark, under a field population and operating process. | No such claim. A finite FD001 result is benchmark-specific; no external real-engine validation is included. |

These statements answer different questions. In particular, a paired uncertainty interval for an assumed engine population is not a conformal coverage statement, and neither turns the exact finite-benchmark contrast into evidence about real-engine reliability. The [v0.3 mathematical verification](../v0.3/02_mathematical_verification_report.md) and [risk register](../v0.3/08_risks_assumptions_decisions.md) already distinguish these issues.

## Survivor eligibility and cutoff transport

The v0.3 pseudo-cutoff was assigned as C = 30 + hash(engine ID, salt) mod 221, giving cycles 30 through 250. A training engine entered a role's eligible set only when C < T, where T is its terminal cycle. Thus the analysis cohort consists of engines that survived to their assigned cutoff. The hash rule is outcome-blind in construction, but conditioning on survival changes the cohort composition and does not establish that cutoff and lifetime are independent among eligible cases.

In the canonical training audit, 81 of 100 assigned engines were eligible: 43 of 55 fit, 13 of 15 tune, and 25 of 30 calibration. Among all 100 assigned engines, cutoff-lifetime correlations were Pearson r = -0.015 and Spearman rho = -0.067; among the 81 survivors they were r = +0.244 and rho = +0.180. These are descriptive associations in one training assignment, not tests of independence, causal effects, or estimates of official-test transport. The lifetime-quartile eligibility rates rose from 14/25 in Q1 to 25/25 in Q4, consistent with the direct consequence of C < T ([cutoff audit](../v0.3/04_dataset_split_eligibility_cutoff_audit.md); [calibration report](../v0.3/05_calibration_feasibility_precision_report.md)).

A historical audit evaluated 100 deterministic salt scenarios while retaining the canonical role assignments. Total eligible count ranged from 69 to 85 (median 78); eligible calibration count ranged from 18 to 29 (median 23), with role-specific ranges of 34–51 fit, 8–15 tune, and 18–29 calibration. Eighty-three engine IDs changed eligibility in at least one scenario. The audit measured counts and membership only: it did not fit models, compute scores, or choose a salt by performance. These overlapping deterministic scenarios are not 100 independent samples from a cutoff population, do not estimate a sampling distribution, and did not refit the pipeline.

For reference, the split-conformal finite rank at nominal 90% is k = ceil(0.9(n+1)). Applied to the unique eligible calibration counts seen in those salt scenarios, this gives:

| Unique eligible calibration engines n | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Rank k | 18 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 27 |

This is rank arithmetic, not evidence that any of the cohorts are exchangeable with official endpoints. The v0.3 canonical cohort used rank 24 of 25 and a nonshrinking correction q = max(0, s_(24)); the recorded CQR correction was 19.987559 cycles. Bootstrap duplicate multiplicities must not be substituted for independent engine count or used to claim a new conformal guarantee. See the [direct rank verification and calibration analysis](../v0.3/02_mathematical_verification_report.md) and [calibration feasibility report](../v0.3/05_calibration_feasibility_precision_report.md).

The official cutoff audit cannot be performed before test-sensor access is authorized: even reading the observed test endpoints to reconstruct cutoff cycles would cross the current data boundary. Checking survival eligibility against terminal lifetime also requires outcome information not available from the authorized training metadata. No official cutoff histogram, lifetime association, selection mechanism, or transport comparison is asserted here. If owners later authorize the required data, a descriptive audit may be considered before any label-based comparison; an observed histogram still cannot prove the data-generating mechanism or exchangeability. Until then, population and coverage transport remain blocked.

## Bounded v0.4 training-only perturbations

The frozen plan schedules eight empirical pipelines: four paired engine-bootstrap multiplicity seeds, each run with canonical and alternate cutoff variants. Each repeats PCA, the fixed 12-candidate CQR selection, refit, Bayesian fitting, and calibration. Resampling is stratified within the frozen fit/tune/calibration roles. A unique sampled engine gets one cutoff per replicate; repeated draws are represented as multiplicity, not as distinct independent engines. Eligibility is C < T with no redraw. A replicate below the minimum distinct eligible counts (20 fit, 5 tune, or 9 calibration) is a recorded failure.

These perturbations vary several observed-data pipeline stages together. They can describe sensitivity of predictions and calibration to these specified perturbations; eight runs cannot estimate total pipeline sampling uncertainty or identify a precise variance decomposition. The fixed 25 original eligible calibration sensor prefixes are prediction-map anchors only. Their RUL outcomes must not select a prior or algorithm, and the anchors are not independent performance cases. Calibration duplicates remain multiplicities and receive no formal conformal guarantee. The numerical seeds and rules are frozen in the [remediation configuration](../../configs/v0.4/remediation_plan.json) and [prospective plan](prospective_remediation_plan.md).

## Claim disposition

- **Finite-benchmark estimand — defined at design level.** Its numerical value remains unavailable until test predictions are separately authorized, frozen, and matched to separately authorized labels.
- **Cutoff transport to official endpoints — STILL BLOCKED as a population or exchangeability claim.** The official cutoff and lifetime process have not been audited and cannot be audited under the current access restriction.
- **Primary scientific interpretation — MITIGATED BY CLAIM RESTRICTION.** If the official finite-benchmark comparison is later completed, describe that benchmark and those stored predictions only. Do not infer an iid engine population, official marginal conformal coverage, conditional cohort reliability, or real-engine performance without additional evidence and authorization.

This restriction is the v0.4 scientifically supportable path. It does not retroactively validate the historical calibration cohort or resolve any still-blocked transport claim.
