# Proposed Protocol Lock v0.2

**Status: PROTOCOL_DRAFTED / REVISE BEFORE LOCK.** Owner: Raihan. Lock timestamp: absent by design. This is a reviewable proposal, not an approval record.

## Scope yang diusulkan untuk keputusan owner

Research mode computational/statistical methodology; primary skill mode dataset-benchmark. Primary FD001 only; one official endpoint per engine; uncapped RUL; Bayesian joint hierarchical landmark model versus CQR. Primary interval nominal90%; one directional test α_test0,05; paired engine bootstrap-t conditional pipeline. Secondary/exploratory analyses tidak mengubah primary winner atau endpoint.

Preserve question: apakah Bayesian predictive uncertainty kompetitif dalam interval score, coverage, sharpness, dan reliability? Klaim hasil tidak dijanjikan. Target engine generator/cutoff transport assumptions dicatat; tidak mewakili actual fleet safety.

## Items proposed, bukan locked

| Item | Proposal |
|---|---|
| Outcome / failure convention | R=T−c; training terminal cycle T; c<T; no cap |
| Split | Deterministic 55/15/30 engine reservation; hash seed RP001-20261008-v0.2 |
| Development cutoff | Ex-ante integer30..250; no redraw; survivors only |
| Primary model | docs/03 joint latent level/slope + AR(1), one RUL response/engine |
| New-engine prediction | Full sensor-only conditioning of θ and latent effects; algorithm pending pilot verification |
| Comparator | docs/05; 12 fixed CQR configurations; nonshrinking correction |
| Selection | Tuning13 eligible; refit56; calibration25 |
| Endpoint | Mean90% interval score in cycles |
| Primary inference | Paired engine bootstrap-t20.000; one upper95% bound |
| Practical scale | Proposed5 score-cycles, owner justification/approval required |
| Robustness | Prior half/double, rho0, contamination-normal residual, PCA2 limited, Bayesian calibration; exploratory |
| FD003 | Deferred until FD001 evidence/pipeline archived and explicit extension approval |
| Test policy | No test labels until final lock + prediction hashes + readiness signoff |
| Budget | Proposed32 aggregate CPU-hours,10 GiB artifact cap; pilot-driven estimate |
| Stopping | Fixed planned runs; diagnostic repairs max2; no test-driven redesign |

## Two-stage authorization

**Stage A — approve development-only work.** Owner accepts the research scope, proposed cutoff limitations, model/comparator design, compute envelope, and practical-effect interpretation. This permits code implementation, isolated dependency environment, synthetic recovery/design simulations, fitting/tuning diagnostic pilots, and refinement using allowed development information. Calibration residuals remain sealed until selection frozen; test labels remain sealed.

**Stage B — final protocol lock and held-out evaluation.** Lead supplies actual validated environment lock, code commit, split hash, artifact hashes, model recovery/diagnostics, measured runtime, exact prediction algorithm including full versus modular conditioning, calibration implementation, and model-selection outcome. Owner approves final protocol identity before official evaluation. Owner Stage A approval is not equivalent to Stage B.

This staged sequence satisfies source proposal §18: “Tidak ada confirmatory experiment yang boleh dimulai sebelum protokol disetujui.” It also lets a concrete final implementation be reviewed before permission to expose test labels.

## Required acceptance evidence before Stage B

- Dataset provenance, internal research terms, train/test namespaces, exact content/trajectory overlap audit, no future features.
- Candidate likelihood mathematically/numerically checked; parameter/predictive recovery under plausible generating regimes. Model not identified as physical mechanism.
- Reliable MCMC and out-of-engine predictive integration; explicit importance-weight ESS/MC precision or exact-update method if used.
- Empirical design-simulation reliability of planned bootstrap, especially skew/influence, with simulation Monte Carlo uncertainty.
- Every fit and failed candidate registered; preprocessing and selection scope validated.
- Exact calibration quantile and negative-correction convention verified; calibration never used to tune policy.
- Dependency lock, reproducible local/Colab execution, protected labels, hardware/runtime logs.
- Primary prediction contract includes engine ID, L/U, median, provenance, warnings; all engine targets forecasted.
- Claims reflect conditional pipeline evidence and synthetic scope; novelty wording remains provisional unless full-text review resolves it.

## Test access sequence

1. Freeze source/config/preprocessing/selected model/inference code and dependency manifest.
2. Commit code and record dirty-state; hash split/calibration outputs. Pre-register/timestamp primary SAP and protocol.
3. Extract official test sensor file into evaluation scope; generate per-engine predictions with past data only, full sensor conditioning as locked. No tuning/feedback from unlabeled official covariates beyond predefined per-engine prediction.
4. Write and hash all prediction tables for principal/comparators/sensitivity models.
5. Only after owner Stage B approval and readiness: expose final RUL vector to locked scoring process, verify label-ID positional mapping, score once.
6. Preserve all results, failures, deviations; test-informed changes become exploratory follow-up requiring fresh evidence.

Archive contains official label bytes already, but no label entry has been opened. “Sealed” is a policy boundary, not OS-level custody; execution code must enforce filenames/access logging and a separate scoring step.

## Deviations and contingencies

Minor code bugs: record time, affected artifacts, whether labels were visible, correction and rerun scope. Methods changes after labels visible invalidate original confirmatory claim; do not simply update protocol timestamp. If model fails, record principal unavailable and remaining descriptive baselines; never switch principal post-test.

Calibration/test cutoff exchangeability not demonstrable from current metadata. Residual risk is explicit empirical qualification; it is not silently marked resolved. Formal 90% guarantee at official cutoffs requires mechanism evidence or a separate matched population evaluation.

Current action requested: approve Stage A with accepted risks/decisions in docs/08, or revise those decisions. No implicit approval is inferred from this document, elapsed time, or Colab availability.
