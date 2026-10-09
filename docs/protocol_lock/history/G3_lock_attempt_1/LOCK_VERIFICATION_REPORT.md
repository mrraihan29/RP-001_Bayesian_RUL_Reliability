# RP-001 | G3 Lock Verification Report

**Overall: FAIL FOR FORMAL LOCK. Baseline integrity: PASS. State: PROTOCOL_DRAFTED.**

Verification UTC: 2026-10-08T17:18:03.859503+00:00; local calendar date 2026-10-09 Asia/Jakarta.
Owner-reviewed scientific commit: c583ce62eac9a6b3dcd29c1929cc07c17569beb7.
Administrative baseline HEAD: 2eca96034ccb69877b16f601f05c85fcda9fc40c.

## Actual identity verification

All 593 v0.5 manifest entries match actual byte lengths/SHA-256: 560 also match exact Git blobs at the approved snapshot; 33 are retained verified local-only payloads. No missing/mismatching baseline artifact. Actual final local delivery receipt matches its manifest hash and scientific commit. [Complete audit](../../logs/protocol_lock/baseline_verification.json).

Fresh interpreter, platform and installed-package metadata matches saved environment. Float64/nutpie/one-thread labels identify preserved execution policy; no sampler or BLAS workload was run to recapture them. The 64-package lock is hash-bound. Actual authorized input files were hashed. Whole opaque archive bytes were hashed only; no archive listing/member reads.

| Identity | Actual SHA-256 |
|---|---|
| Approved v0.5 contract | 1e03e072682878fde6ced8c00ddcde44594af59e56129e65db1127a0166fa598 |
| Scientific source map (sorted compact JSON) | 0967e8db64935764b5c34fb35b15978739c6a2d536f6ea13bb05fd0540681d5d |
| Environment stable fingerprint | f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c |
| FD001 training | 963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8 |
| Split/cutoff | 6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b |
| v0.5 resolution plan | 6046cd808d6a4b68ed42fd7d3458f0f142273aa323f64bb077cb8c0bc7dc0745 |
| Dependency lock bytes | 0a11fa76ae3648ebc6277850deddc8c7990eeb47eca8d3f3566119de62ddbc99 |
| Local final v0.5 receipt | 9c2f278b233d2f147e5086c8540c219274f158fa58051844b88fd2c5d7f6dd8c |
| Selected CQR fitted object | 85027f22fc1c4f4d20748412d6072ad7b23e493f0b008fffc15cb0800683458f |
| Refit preprocessing | f23b7fdd1c354d92468cdff02b056d7cda603cfc00d52d3ba24917dcd5c01b9e |

| Principal state | SHA-256 | Chains x retained draws | Saved diagnostics |
|---|---|---|---|
| v04_main_r1 | 750157b158f665d2c962202813f2cfd11a0152730956743dc434b6b47db75415 | 4 x 8000 | PASS |
| v04_main_r2 | bce67cd39c38c54271ab59d1a9922795ff62524aac25bd09f64eed3a3f99fe3b | 4 x 8000 | PASS |
| v04_main_r3 | 805ec463ea94b565c536fc39dcc3d95a784d9fd1527f15ab106a4b2acf23cb96 | 4 x 8000 | PASS |

Saved posterior dimensions/finite physical and auxiliary values were inspected without sampling/recomputing diagnostics. Selected CQR endpoint/median objects are completed 56-engine refits: 200 trees, depth 1, leaf 10, learning rate .1, seed 20261008. Saved refit maps match all three principal preprocessor maps exactly. Eligibility remains 43/13/25; calibration rank 24 and q=19.987558518873357. [Saved-state audit](../../logs/protocol_lock/saved_state_verification.json).

## Direct SOL scientific sign-off by component

| Component | Disposition | Finding |
|---|---|---|
| MODEL_SPECIFICATION | CONSISTENT | Direct SOL review: joint Gaussian g/z/logR marginal, covariance and AR1/Woodbury source match; prior dense-oracle evidence retained. |
| PRIOR | CONSISTENT | anchored_v04 priors and saved fit policy match; exposed development adaptation remains disclosed. |
| POSTERIOR_PREDICTION | CONSISTENT_WITH_ROUTE_BLOCKER | Separate sensor-only importance update/conditional Gaussian mixture match; 3 x 4 x 8000 principal states verified. Quantile route pending. |
| CQR | CONSISTENT | 12 fixed candidates/ties/refit agree; ceil(26*.9)=24, q=19.987558518873357; support projection retained. No official exchangeability guarantee. |
| PRIMARY_SCORE | CONSISTENT | IS90=U-L+20max(L-y,0)+20max(y-U,0); Bayesian-minus-CQR on complete uncapped finite cohort. Future contrast requires compensated aggregation. |
| NUMERICAL_GATES | FAIL | Other guard thresholds/influence formulas agree; bracket/tolerance/helper identity conflicts (G3-AM-001). No threshold relaxed. |
| SCORE_UNCERTAINTY | CONSISTENT | X=-Q*w*(F-p)/(mean(w)*f), indicator score gradients, aligned joint covariance/projection, Satterthwaite approximation, kink qualification and 19/N conditional sensitivity agree. Prior saved-draw check retained. |
| FINITE_ESTIMAND | CONSISTENT | Exact complete stored prediction comparison only; no population inference, binary competitive decision, practical margin, superiority/equivalence/noninferiority or operational certification. |
| PROTECTED_ACCESS | CONSISTENT_AND_HONORED | A lock authorized but unsuccessful; B sensors, C freeze acceptance and D labels/scoring separate and unauthorized. No protected member reads/predictions. |

CONSISTENT is a scoped static consistency sign-off using already archived numerical evidence; it does not grant PROTOCOL_LOCKED or RESEARCH_VALIDATED or guarantee future endpoint success. [Full sign-off/source hashes](../../logs/protocol_lock/direct_SOL_component_review.json).

## Material inconsistency and halt

Contract line 70 combines the legacy +/-12 SD bracket with precision-helper 1e-12 tolerance. Precision source actually uses a larger probability-dependent radius and deterministic bracket expansion; legacy source uses 1e-10 tolerance. Neither exactly matches the combined description. [G3-AM-001](AMENDMENT_REQUEST_G3_AM_001.md) supplies exact locations, a direct uniqueness/bracketing argument, materiality assessment and minimal unexecuted replacement.

The mismatch concerns exact numerical procedure/failure behavior. It does not demonstrate changed posterior target, invalid historical sampling or a material historical score difference. No future endpoint computation quantified its effect. G3 section 3 prohibits silently choosing between the rules.

No final ten-file lock package is certified, no locked research/analysis contract is manufactured, no lock timestamp is assigned, and successful lock commit is null. Receipt is an unsuccessful-attempt receipt. Original scientific source/configuration/results remain unchanged. Seven advanced administrative aliases have byte-preserved archives.

## Historical failures and evidence preserved

- Original v04_syn_high_rho_3 remains FAIL; bounded v05 diagnostic inquiry PASS is not a production posterior replacement.
- v0.3 quantile precision FAIL (.728972 versus .5 cycles) remains; v0.4 calibration precision PASS is not official endpoint certification.
- Eight dependent pipeline perturbations/four paired contrasts and CQR winner changes remain; no unconditional pipeline variance estimate.
- Adverse bootstrap operating characteristics and 999 unavailable replicates remain; no primary population bootstrap.
- Existing 59-test XML was hash-verified, not rerun. Registry remains 73 records; original 71-record prefix unchanged. G3 appended no scientific run.

## Authorization and next gate

Stage A formal lock is authorized, but consistency failed. B official sensors, C prediction-freeze acceptance and D labels/scoring remain separately unauthorized. No official members were extracted/read/previewed/predicted/scored. No MCMC, new experiment, reselection, fallback, threshold relaxation or spending.

After accepted amendment and successful resumed G3, the first action **only if separately authorized for B** is to record the exact instruction/source identities, extract sensors alone, and audit all expected endpoints for schema/IDs/finite contiguous cycles/overlap before fixed-model predictions. Stage C acceptance and Stage D labels remain separate decisions.

Outstanding execution risks: unknown cutoff transport/exchangeability, future numerical/input failures, weak physical nuisance identification, exposed calibration/prior adaptation, unequal features/search/compute, small tuning/calibration cohorts, approximate MCSE/kink qualification, incomplete cross-platform clean replay, 33 local-only historical payloads, unresolved novelty and lawful redistribution. Retained limitations are not additional automatic lock blockers; G3-AM-001 is the sole current freeze blocker.

Repository remains PUBLIC under explicit owner direction. [History audit](../../logs/protocol_lock/public_history_audit.json) found no forbidden raw/protected input paths or concrete credential signatures in its bounded scope; staged-file audit follows before push. This is not proof of absence of every possible secret. Public review access does not authorize scientific publication or raw-data redistribution.
