# Material Risks, Assumptions & Decisions v0.2

Owner decisions are requested only after the concrete review package is available. Dates use Asia/Jakarta, 8 October 2026. Statuses PASS/FAIL/BLOCKED/DEFERRED/NOT_APPLICABLE are not interchangeable.

## Risk register

| ID | Severity | Risk / mitigation / residual | Owner / disposition |
|---|---|---|---|
| R01 | Critical | Pseudo-cutoff and official-test mechanism may differ. Outcome-blind deterministic cutoff, one engine score, explicit transport qualification; no unproved conformal guarantee | Lead; unresolved but acceptable for empirical benchmark if owner accepts limited claim |
| R02 | Critical | Hierarchical covariance/latent effects weakly identified at 56 final engines. Anchored sensor units, compact model, marginalization, synthetic recovery, priors; can force pre-test simplification | Lead; blocks model acceptance until pilot |
| R03 | Critical | Unreliable posterior or new-engine θ conditioning error. Four-chain diagnostics, sensor-only update, importance-weight/recovery oracle; reject unreliable predictions | Lead; blocks inferential readiness |
| R04 | High | 100 test engines give broad coverage/effect uncertainty. Report CI/planning, avoid ±2pp calibration certification and equivalence | Quant lead; residual accepted only with scope |
| R05 | High | Calibration on 25 engine scores produce unstable/coarse tail threshold. Exact rank 24, no window inflation; disclose conditional layer variation | Lead; residual |
| R06 | Critical | Future features, ID leakage, or adaptive test access. Prefix-only transforms, separate namespace, locked labels/prediction hashes; original public labels historically exposed to community | Lead; current training audit partial, final checks deferred |
| R07 | High |One-PC/local-linear sensor representation misses early nonidentifiability or nonlinear health. Prior/PPC, held-out diagnostics, PCA2 exploratory, no physical-state claim | Lead; unresolved pilot |
| R08 | High |Comparison confounds structure, information compression and Bayesian inference. Same histories/cutoffs and strong CQR tuning; matched Gaussian diagnostic if inference-only contribution claimed | Lead; scope qualification |
| R09 | High |Novelty overlap and inaccessible recent full methods. Verified older prior art, targeted current search, explicitly provisional novelty; follow-up review before publication | Literature lead; unresolved novelty |
| R10 | Medium |Rights/license redistribution unclear. Source terms/metadata stored, NASA acknowledgment, raw data ignored; release-rights review before public distribution | Owner+lead; blocks data redistribution decision |
| R11 | High |Skew/influential misses challenge bootstrap approximation. Prespecified bootstrap-t, design simulation, t/percentile sensitivities; no favorable analysis switch | Quant lead; pilot required |
| R12 | Medium |Local dependency/runtime unavailable; Colab resources variable. Isolated env, lock, measured pilot, checkpoint persistence | Engineering lead; no compute evidence yet |
| R13 | High |Synthetic-to-real gap. FD001-only synthetic scope, FD003 separate simulation extension, no maintenance deployment/safety certification | Owner+lead; permanent scope boundary |
| R14 | Medium |Multiple exploration/prior searches cherry-pick wins. Single primary comparison, fixed candidate budgets, all failures/run ledger, full reporting | Lead; policy proposed |
| R15 | Medium |Training preprocessing uncertainty ignored in conditional pipeline CI. State frozen plug-in transforms; repeated development splits exploratory separately | Quant lead; explicit residual |

Likelihood probabilities tidak dapat ditentukan dari evidence yang tersedia; tidak diberi fake numerical probability. “Unresolved but acceptable for scoped benchmark” bukan menutup risk.

## Assumption register

A01: Engines are approximately independent conditional common simulator regime; row count is not n. A02: Last training cycle represents failure under operational label convention, not exact physical event timestamp. A03: R>0 at selected alive landmarks; no capping. A04: Sensor history until cutoff is available. A05: AR(1) and local linear score trends are working approximations. A06: PCA axis is a measured representation, not certified health state. A07: Bootstrap inference is conditional pipeline superpopulation approximation. A08: Deterministic seed/splits are chosen before model outcomes and never searched. A09: Private owner approval has not occurred. A10: Colab Pro availability is user-reported; account quotas/runtime not inspected. A11: Published FD001 studies share a benchmark and are not independent new-engine replications.

## Decisions required from Raihan

| Decision | Lead recommendation | Consequence |
|---|---|---|
| D01 research scope | Comparative probabilistic evidence on simulated FD001, with one planned superiority direction but no promised superiority | Limits interpretation and publication framing |
| D02 model route | Approve development of compact joint sensor/RUL model, conditional acceptance after recovery | If pilot fails, return revised principal before test |
| D03 cutoff policy | Accept outcome-blind 30–250 pseudo-cutoff with survivor counts 43/13/25 and explicit official-cutoff mismatch | No formal conformal 90% guarantee at official cutoffs |
| D04 practical importance | 5 score-cycles as provisional internal scale, or provide maintenance/scientific justification for another threshold | Without approved scale, report magnitude without practical-superiority/equivalence claim |
| D05 compute scope | Local isolated CPU first; Colab Pro if pilot shows benefit; proposed 32 CPU-hours/10 GiB, no added purchase | Colab transfer/runtime plan prepared after approval |
| D06 next authorization | Approve Stage A development-only; Stage B final test approval later on validated code/protocol | Leaves test outcomes protected |
| D07 optional extension | Defer FD003 until FD001 pipeline/evidence archived | Prevents favorable-dataset substitution |

These can be approved as a package with stated exceptions. There is no need to ask for permission again for already authorized directory initialization/review/audit. Request for protocol approval originates in user proposal §18, not an invented skill requirement.

## Completed versus outstanding

Completed: fixed-parameter numerical equation checks, G0, source preservation, focused evidence map, training audit/provenance, precision calculations, mathematical specification, SAP/comparator/lock drafts, local/Colab compute proposal, risks. Outstanding before final lock: owner Stage A, isolated dependencies, implemented model and implementation-specific numerical checks, synthetic/pilot diagnostics, exact predictive update policy, complete data integrity and calibration readiness. Outstanding before publication: current full-text novelty/status review, release rights, empirical claims/reproducibility and venue requirements.

No experiment output or scientific superiority claim exists. Formal downstream SCIENTIFIC_VALIDATED gate is DEFERRED.
