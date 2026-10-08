# RP-001 — Owner Return: Development Pilot v0.3

**Recommendation: REVISE AGAIN. Do not lock the final protocol yet.**

Research Owners: **Raihan × Rei**. Conditional development authorization was executed with synthetic and official FD001 training only. Test covariates and labels were not inspected; no confirmatory evaluation. The primary question, proposed90% interval-score endpoint and Bayesian-versus-CQR comparison remain.

## Evidence established

- Direct lead verification:36 final implementation/conditioning/comparator/storage test cases passed within tested scope. CQR25 rank24, integrated likelihood, sensor-only conditioning and score calculations were independently checked.
- Four fixed synthetic recovery cases plus seven training fits passed MCMC diagnostics:11 completed fits,4 chains/8,000 retained draws each. Two failed storage attempts remain, with two disclosed infrastructure repairs.
- Split/eligibility/cutoff audit and lead reconstruction completed. Eligible43 fit/13 tune/25 calibration; refit56. Future-sensor isolation tested.
- All12 CQR candidates and freeze recorded. Calibration correction19.987559cycles; cohort/influence sensitivity reported without independent performance claims. Bayesian+post-hoc calibration examined as secondary feasibility.
- Local CPU sufficient: logged sampler CPU623.016seconds (~.173CPU-hours) including failures. No Colab or paid expansion.

## Observed blocking failure

Bayesian refit56 on25 calibration sensor prefixes has minimum importance ESS3711.54, but **maximum approximate quantile MCSE .728972cycle exceeds the fixed .5cycle criterion**. Fitting diagnostics do not certify quantile precision. A sensor-only MCMC oracle agrees within .022155cycle for one deterministic engine, but does not override cohort failure. Bayesian calibration q=0 is not accepted for inference.

## Revisions needed before lock

1. Fix a prospective numerical precision plan: valid quantile MC uncertainty, fixed extra draws or exact sensor-only strategy, non-cherry-picked case coverage, budget/stopping and retained failures. Do not retrospectively relax .5cycle.
2. Defend prior tails and identifiability limits. Four fixed recoveries do not establish repeated-sampling calibration or a physical mechanism. Disclose all adaptation after development calibration exposure.
3. Decide calibration claim scope. Official cutoff exchangeability is unknown; survivor eligibility changes population. Qualified finite empirical benchmarking may be defensible; formal transported coverage is unsupported.
4. Finalize conditional-pipeline estimand, influential/degenerate-case inference policy and full fitting/selection/calibration sensitivity design. The illustrative variance simulation is not that full study.
5. Disclose information, representation/search-budget limitations and secondary calibration ablations. Report effect sizes without a5cycle practical-superiority/equivalence margin unless a defensible utility mapping is separately approved.

Novelty/current-method and redistribution reviews remain open before publication. Synthetic evidence cannot support operational-engine safety claims. Report08 and the handoff retain every open risk; none is silently closed.

## Nine-item return package

1. [Updated Research Protocol v0.3](01_updated_research_protocol.md)
2. [Mathematical Verification](02_mathematical_verification_report.md)
3. [Synthetic Recovery and Diagnostic Pilot](03_synthetic_recovery_diagnostic_pilot_report.md)
4. [Dataset Split, Eligibility and Cutoff Audit](04_dataset_split_eligibility_cutoff_audit.md)
5. [Calibration Feasibility and Precision](05_calibration_feasibility_precision_report.md)
6. [Comparative Evaluation Design](06_comparative_evaluation_design.md)
7. [Compute and Environment](07_compute_environment_report.md)
8. [Risk, Assumption and Decision Registers](08_risks_assumptions_decisions.md)
9. [Owner Return and Recommendation](09_owner_return_recommendation.md)

Supporting evidence: dependency lock, run registry, source/protocol snapshots, test logs, posterior/data hashes, candidate freeze and design simulations. Full software/data fingerprints: report07. Git checkpoint and artifact identities: [delivery provenance](delivery_provenance.json), `logs/v0.3_delivery_manifest.json`.

The development return is complete. This is a scientific recommendation, **not final research authorization**. Final approval remains with Raihan × Rei; official test labels and confirmatory evaluation remain unapproved.
