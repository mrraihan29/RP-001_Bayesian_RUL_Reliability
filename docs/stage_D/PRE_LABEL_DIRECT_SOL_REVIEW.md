# Stage D pre-label direct SOL source and mathematical review

Reviewer: Rei / SOL lead, direct review; internal team verification, not external replication. Prepared before any official label payload access. Governing sources are the locked G3-AM1 contract, Stage C accepted identities and current human owner Stage D directive.

## Assessment: PASS for the prescribed finite stored-prediction calculation

The interval score has derivatives (-1,1) inside, (19,1) below and (-1,-19) above. Equality follows the strict-miss branch and is separately flagged as a derivative kink. CQR lower zero is permitted; the frozen Bayesian-only score helper's strictly-positive interval check is not incorrectly imposed on CQR. Every primary vector has exact shape100 and declared IDs1..100; incomplete/nonfinite inputs cannot produce a subset mean. Predictions and labels are never clipped by the Stage D wrapper.

D_F is the compensated sum of per-engine float64 score differences divided by100. Full width and both 20-times-miss components are retained. Coverage uses L<=y<=U; median errors are median prediction minus observed RUL, with MAE/RMSE/bias reported descriptively. The independent stdlib scalar oracle checks all score/component values and the contrast; a 60-digit Decimal route checks arithmetic rounding on ordinary finite fixtures.

For a self-normalized weighted Gaussian log-RUL mixture, the CDF ratio influence is w(F-p)/mean(w). Implicit quantile differentiation gives minus this quantity divided by the positive log-scale density. Exponentiation multiplies by Q, yielding the pinned cycle influence. Each engine normalizes its own sensor likelihood weights; no joint test-engine likelihood or flattened engine sampling assumption is introduced.

The mean-score influence is the linear projection H of the concatenated 200 endpoint coordinates. Pooling independently sampled chain blocks of n=8000 gives covariance sum_c(n LRV_c)/M^2, M=96000. This retains all off-diagonal engine/endpoint terms. The scalar variance is the projection by [gL/100,gU/100]. Batch means with250/500 use32/16 batches per chain and all retained draws. The Satterthwaite degrees of freedom v^2/sum(v_c^2/df_c) and lower chi-square quantile at.025 give the pinned approximate upper MCSE. Zero variance produces undefined upper and qualification, not an invented exact-posterior certificate.

The independent verification uses Gaussian erfc CDF algebra, compensated full-draw projection, stdlib scalar batch moments and independently reconstructed joint covariance. Approximate MCSE and chi-square assumptions remain conditional/asymptotic; these checks validate implementation rather than proving finite-sample coverage. The 19/N Lipschitz bound requires actual endpoint errors within supplied radii; MCSE radii alone do not certify that premise.

Qualification is fixed: either batch upper undefined/nonfinite or maximum>.5 cycles, or any label within3 endpoint upper MCSEs at either batch. Qualification preserves a complete finite stored result. The three independent-fit contrasts are diagnostics from already-stored quantiles; 13 accepted individual-fit precision exceedances remain disclosed. Posthoc calibration has frozen correction0, so its secondary identity is predetermined.

## Source and failure-policy review

Reviewed core.py, common.py, integrity.py, preflight.py, run_stage_D.py, oracles.py, verify_results.py, the deterministic tests, and the pinned v05_score_numerics.py. Their exact hashes are in configs/stage_D_execution_plan.json. No fit, sampler, quantile root, comparator selection or prediction repair is invoked. Preflight/execute outputs use exclusive creation, a sequential hash-chain journal and immutable failure files; a second execution is refused.

An exception before access stops with labels unopened. Any schema/input/primary arithmetic/verification failure after exposure is preserved and blocks completion, with no retry or scientific modification. Undefined/nonfinite score upper is a numerical qualification if the complete stored score is otherwise valid. No outcome-dependent public payload selection is permitted: all performance metrics and per-engine results stay protected.

## Verification evidence and boundaries

19 deterministic tests passed, including the four pinned score-numerics tests. They cover interval scores/misses/coverage, positive label/schema/order validation, missing predictions and overflow rejection, compensated cancellation, influence normalization, covariance versus an incorrect diagonal-only approximation, exact-boundary kinks, threshold/undefined-upper handling. Exact test artifact hashes are frozen with the plan.

Prior G3/B/C records remain immutable. This review is not population validation, guaranteed numerical error certification, novelty review, data-rights clearance, independent custody certification or authorization for public scientific release. The owner-specified finite claim and all historical limitations remain controlling.
