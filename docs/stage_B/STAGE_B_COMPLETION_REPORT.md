# RP-001 | STAGE B OFFICIAL SENSOR & PREDICTION COMPLETION REPORT

**Recommendation: READY FOR OWNER STAGE C REVIEW.** Campaign B001 completed the authorized sensor-only phase under **RP-001-G3-v0.5-AM1**. Both primary methods produced complete predictions for 100 engines; all required production numerical, integrity and compatibility gates passed. This is a candidate prediction freeze for Research Owners Raihan × Rei. Stage C acceptance and Stage D label release/scoring remain unauthorized. Predictive performance is unknown.

Client date: 2026-10-09, Asia/Jakarta. Prediction sealing completed 2026-10-09T02:45:15.823085+00:00; direct arithmetic verification completed 2026-10-09T02:48:05.939475+00:00.

## Authority, source and pre-execution custody

The [owner directive](OWNER_AUTHORIZATION_STAGE_B.md) authorizes Stage B only. Its byte-exact attachment SHA-256 is 675cff9c457723b05f66edb8dc63bdfd5e3010cc6b55e05905b33bc4fc4e5bd1. Conversation/attachment provenance is recorded; no independent owner signature authentication is claimed.

The scientific lock remains fc7083d23d3cff5e4ee9a9f5d0af9036ec32e26d, with final receipt checkpoint da4da0bd51b86239a36effcb92a1106490835c6b. The prospective single-attempt plan and direct SOL source review were committed at 6d5098e93e3d08325d708f708500b95133e6761e before sensor access. The clean official execution checkout was a85412ba7c8ada34c5c284251ef05d35cfaf15ee.

[Preflight verification](PREFLIGHT_VERIFICATION.json) matched all 58 sealed G3 files, scientific sources/configurations, 64-package environment, dependency lock, opaque archive identities, all three retained posterior states, shared frozen PCA maps, selected CQR object and rank-24 calibration. The same checks ran again immediately before opening sensors. No scientific implementation, prior, model state, preprocessing fit, comparator selection or acceptance threshold changed.

The immutable local event registry started before sensors. Failure persistence and the immediate-stop policy were prospectively specified in the committed driver; the terminal empty failure_ledger.json was written at sealing. This distinction is retained in the direct verification disclosures.

## Sensor access and integrity

Only the named test_FD001.txt member of the already fingerprinted CMAPSSData.zip was opened and extracted. No archive-wide extraction, member preview, label-member content access or public upload occurred.

| Check | Observed result | Status |
|---|---|---|
| Official sensor cohort | Exactly 100 IDs, 1..100, separate FD001_test namespace | PASS |
| Schema | 13,096 rows, 26 finite fields; ID, cycle, 3 settings, 21 sensors | PASS |
| Observation integrity | Positive integer IDs/cycles, unique engine-cycle keys, ordered contiguous histories | PASS |
| Cutoffs/features | Actual last observed cycle for every engine; no label-based eligibility or exclusion | PASS |
| Exact-prefix overlap | 10,000 train–test pairs, 0 flags | PASS |
| Near-duplicate screen | 10,000 pairs, 0 flags under locked heuristic | PASS |

Sensor bytes: 2,228,855; SHA-256 **3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851**. The opaque nested archive retains SHA-256 74bef434a34db25c7bf72e668ea4cd52afe5f2cf8e44367c55a82bfd91a5a34f; original NASA archive retains c9c5dec12a945a82e8bb4446589d7fb3cc057b5e5d81fa1a12e25ee9912ad3b2.

The cross-dataset screen extends the locked training screen to all 100 authorized training trajectories and 100 observed test histories. It preserves cycle-aligned shared-prefix comparisons, 24 settings/sensor channels, ≥30 common cycles for the near screen, RMS channel-normalized error ≤0.02 and maximum channel error ≤0.10. Population SD normalization uses the existing 81 eligible training prefixes only, with the existing SD≤1e-12 fallback of 1; test rows never fit those scales. Exact-prefix comparisons also cover any shorter shared histories. Numeric IDs do not establish cross-dataset identity. This heuristic cannot certify semantic independence or exclude all contamination. Headerless column order is bound to the official archive and declared schema; physical sensor units have not been independently verified.

## Frozen predictions and numerical gates

Bayesian production uses exactly v04_main_r1/r2/r3: 12 chains × 8,000 retained draws, 96,000 total. Each engine is processed separately through frozen PCA, its own sensor-only importance weights and the exact conditional Gaussian mixture. Global parameters are never collectively updated using other official engines. The authoritative rp001.v04_precision helper supplies the same returned quantile to storage, CDF/density and precision checks. The historical prediction.mixture_quantile route was not used.

CQR reuses gb-depth1-leaf10-lr0p1 and its separately fitted median object, shared refit preprocessing and the existing 25-engine calibration correction 19.987558518873357 cycles, rank 24. Raw endpoint ordering, nonshrinking expansion, nonnegative support projection and unshifted median follow the frozen source. No search, fitting or recalibration occurred.

| Mandatory gate | Result | Locked requirement |
|---|---|---|
| Production posterior diagnostics | All 3 physical/auxiliary saved diagnostic sets PASS; states finite float64, 4×8,000 per fit | Rhat<1.01, bulk/tail ESS≥400, div=0, BFMI>0.3, depth12 saturation≤0.01 |
| Complete primary predictions | Bayesian 100/100, CQR 100/100; no dropped/pending engines | Complete cohort |
| Production quantile precision | All 300 pooled quantiles PASS at both batches; maximum upper MCSE 0.39768923 cycles | ≤0.5 cycle, batches 250/500 |
| Weight / influence ESS | Minimum pooled weight ESS 7,919.65; minimum influence ESS 56,496.70 | ≥1,000 / ≥400 |
| CDF root / density | Largest stored absolute pooled root residual 2.6057e-13; positive finite density and normalization | Residual≤1e-10 |
| Independent-fit compatibility | All 900 comparisons PASS; largest standardized difference 3.28232 | ≤4.03093437, positive finite denominator |
| Prediction validity / identity | Finite ordered primary intervals, exact IDs/cutoffs, unchanged sources and models | Mandatory |
| Failure retention | 0 mandatory failures; all 100 ledger rows retained | Stop at first failure |

Production upper-MCSE multiplicity tail is 0.05/(100×3×2)=1/12,000. Replication z is Φ⁻¹(1−0.05/(2×9×100)); each comparison uses the larger ordinary MCSE across the two batches for each fit. Maximum pooled upper MCSE occurs at engine 85, p=0.95, batch 500. CQR has zero negative-median flags.

**Individual-fit precision disclosure:** 13 of 1,800 individual-fit batch records exceed 0.5 cycles; maximum is 0.86495109 cycles for v04_main_r1, engine 85, p=0.95, batch 500. These records are preserved. The fixed production predictor is the preapproved 12-chain pool; the 0.5 production gate covers its 300 quantiles. Individual fits supply finite canonical diagnostic quantiles/MCSEs and the separately locked 900 compatibility comparisons. This follows the locked contract's pooled endpoint family and the frozen v04_analysis acceptance expression, which gates pooled precision plus independent-fit compatibility, rather than requiring every individual-fit diagnostic to have production precision. No pooled predictor was selected after observing this limitation.

[Direct SOL completion verification](DIRECT_SOL_COMPLETION_VERIFICATION.json) independently reconstructed weighted CDF/density, self-normalized weight ESS, influence processes, chain batch variance, Satterthwaite upper MCSE and replication inequalities from sealed conditional terms. All 1,200 quantile records, 2,400 batch calculations and 900 comparisons matched. No new root, prediction, draw or scientific experiment was generated for this verification. Its retained code was added after prediction sealing and is separately hashed. Agreement tolerance only verifies arithmetic correspondence; it does not relax official gates.

## Candidate package and fingerprints

[Candidate package receipt](CANDIDATE_PACKAGE_RECEIPT.json) binds three local protected manifests:

| Artifact | SHA-256 |
|---|---|
| Base prediction/custody manifest, 3,016 files | 09ae59cb40c33af4170ae8b041550a9d1f8e49042b1ef8065e764c45e55fb7a1 |
| Direct arithmetic verification manifest | 6090ea4a08eaffb758b48042c8629c42e18cc82e5729d94b08e8eb96a15116df |
| Combined candidate bundle identity | 96084deb61336367b48f19251f0cd529e5deb98c754eb09a05dca5f52ef4263e |

The base package contains the complete ID/cutoff ledger, all primary endpoints/medians, pooled and individual diagnostics, all replication comparisons, input/overlap audit, environment/model/source provenance, aligned conditional mixture terms for a separately authorized future score-MCSE calculation, 507 hash-chained events and empty failure history. Every file has an individual SHA-256 in the protected manifest. Supplementary 100-row Bayesian, CQR and ledger CSVs losslessly consolidate already-sealed values, with exact float64 round-trip checks; their hashes and review-table manifest are in the public receipt.

Protected locations are .protected/stage_B/B001, B001_verification and B001_review_tables. Raw sensors, per-engine cutoffs/predictions, detailed payloads and full file maps remain local and Git-ignored. Public Git contains code, owner authority, custody hashes and diagnostic summaries only.

Environment fingerprint remains **f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c**. CPython 3.12.14, pinned 64 packages and requirements lock SHA-256 0a11fa76ae3648ebc6277850deddc8c7990eeb47eca8d3f3566119de62ddbc99 match the lock. Scientific source-map fingerprint remains 0967e8db64935764b5c34fb35b15978739c6a2d536f6ea13bb05fd0540681d5d; canonical precision-module SHA-256 remains 396a5f55ca2e9c51fd21f02f50e59c57be7aedd38321a4a3123b0b955f1fde33. Exact posterior, PCA, CQR and calibration fingerprints remain in the unchanged G3 manifests and Stage B preflight.

Local CPU execution took 106.53 s wall / 103.34 s CPU, with recorded peak working set about 334.1 MiB. All observed BLAS/OpenMP pools used one thread. Direct verification took 12.42 s. Google Colab was unnecessary; no spending occurred. Runtime emitted the pinned ArviZ future-refactor notice and unavailable-g++ notice; prediction completed without compilation or sampling. These warnings did not indicate a mandatory input/source/numerical failure.

## Boundaries, residual risks and return to owners

No scientific deviation, retraining, posterior resampling, fallback, threshold change, outcome scoring or official label access occurred. Native scientific status remains PROTOCOL_LOCKED; this report does not declare RESEARCH_VALIDATED.

Preserve the original high-rho failure/bounded inquiry, v0.3 precision failure, weak physical identification, exposed calibration/prior adaptation, small calibration/tuning cohorts, observed pipeline sensitivity, unequal comparator representations/search/compute and bootstrap limitations. Official cutoff exchangeability and population transport remain unproved. Numerical MCSE is approximate and conditional on frozen fitted models; it does not quantify whole-pipeline uncertainty or certify absolute numerical error. No coverage/performance/superiority, novelty, operational reliability or generalization claim is available from Stage B.

Data redistribution rights, novelty review, complete historical/clean-machine replay, independent notarization and separately encrypted custody remain unresolved. Byte hashes plus exclusive-create discipline establish procedural traceability, not WORM storage or an independent identity system.

**Return: READY FOR OWNER STAGE C REVIEW. Stop here.** Owners must separately accept this exact candidate freeze. Official labels and primary interval-score comparison remain closed until a subsequent explicit Stage D authorization after Stage C acceptance.
