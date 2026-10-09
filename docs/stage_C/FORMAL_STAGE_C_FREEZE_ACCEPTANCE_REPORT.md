# RP-001 | FORMAL STAGE C FREEZE ACCEPTANCE REPORT

**Final decision: STAGE_C_ACCEPTED.** The Research Owners' conditional acceptance of B001 is now recorded after all final byte-integrity checks passed. Exact protocol version: **RP-001-G3-v0.5-AM1**. G3 remains PROTOCOL_LOCKED; Stage B is COMPLETED; Stage C is ACCEPTED; **Stage D is NOT_AUTHORIZED**.

Client date: 2026-10-09, Asia/Jakarta. Final verification completed 2026-10-09T03:15:14.626234+00:00; acceptance recorded 2026-10-09T03:18:18.894705+00:00. This acceptance concerns integrity and numerical readiness of previously frozen predictions. Predictive accuracy, empirical coverage and Bayesian-versus-CQR performance remain unknown.

## Owner authority and exact accepted freeze

The [owner directive](OWNER_STAGE_C_DECISION.md) was copied byte-for-byte from the human Raihan attachment in this conversation. SHA-256: 6799a82744a2f35564d204ab4dd0ab307c92d30cb3be27065f2d893d1734b5d2. The stated owners are Raihan × Rei. No cryptographic signature or independently verified legal identity is invented.

The accepted scientific lock commit is fc7083d23d3cff5e4ee9a9f5d0af9036ec32e26d. Stage B evidence commit is 97eccae2e41c48ab63ab263931b964cb5165c181; its administrative receipt checkpoint is e3ce076de4bd6e1eec4844f5c53dc4d3d15d03cd. These reviewed identities are preserved.

| Accepted identity | Exact SHA-256 |
|---|---|
| Prediction bundle | 96084deb61336367b48f19251f0cd529e5deb98c754eb09a05dca5f52ef4263e |
| Base protected payload manifest | 09ae59cb40c33af4170ae8b041550a9d1f8e49042b1ef8065e764c45e55fb7a1 |
| Existing mathematical verification manifest | 6090ea4a08eaffb758b48042c8629c42e18cc82e5729d94b08e8eb96a15116df |
| Existing review tables manifest | 2911bf37b68668584e1bf71564003ad5820a2073c32263cf048be456fd6404b3 |

The bundle is the unchanged SHA-256 of sorted compact UTF8 JSON mapping the three named manifests to their hashes. Mutable repository HEAD has no role in choosing accepted predictions.

| Frozen prediction/table identity | Rows | SHA-256 |
|---|---|---|
| Bayesian_predictions.csv | 100 | 3f2016c38dfa25268d40cb8522bbebba3b507a26db88eda18ecc335a4de3a9b5 |
| CQR_predictions.csv | 100 | 6dc96a60c40ee1a7a36c89b76cd9003395bd1f02783b239dbfdc93d994496593 |
| engine_ledger.csv | 100 | 5bec5804a31788995754e66114ffeeee35424815ebfcd813925b555585f47129 |

Per-engine identities and values remain in the protected local file maps and tables. Their numerical contents are not published. [Accepted identities](ACCEPTED_PREDICTION_IDENTITIES.json) records the model, calibration, source and table fingerprints.

## Bounded final integrity verification

The verification plan and source were committed at **48d1307473b16ba10247fd8d2d49ea712f3fc7ee** before the check. Verifier SHA-256: 2ac5c9ddca895606f440cca92f106d1981d35f0450565c0db87dcfad5ede1348. The standalone verifier uses existing artifacts and deterministic checks only, with no scientific prediction/root/fitting/sampling library calls.

| Final requirement | Result |
|---|---|
| Rehash all 3,016 base payload files, sizes and complete file inventory | PASS; every byte identity matches |
| Rehash 3 existing verification members and all 3 review tables | PASS |
| Reconstruct exact owner-specified manifest bundle identity | PASS |
| Verify Bayesian/CQR tables against individual sealed JSON records | PASS; all 100 rows per method, exact float64 hex equality |
| Verify complete engine/cutoff ledger and CSV alignment | PASS; 100/100, same namespace, status and values |
| Preserve G3 lock package and Stage B public artifacts | PASS; all 58 sealed G3 files and 18 tracked Stage B artifacts unchanged |
| Confirm scientific source/configuration, posterior, PCA and CQR/calibration identities | PASS |
| Confirm stored numerical acceptance logic and compatibility arithmetic | PASS; no new diagnostics/predictions generated |
| Confirm retained failure ledger and input/overlap audit | PASS; original mandatory failure ledger remains empty |
| Confirm available pre-label sealing/access evidence | PASS within procedural limits; 507 chained events unchanged, sealed flags consistent, labels remain unextracted |

No material discrepancy occurred. Verification took 14.69 s locally. Detailed read-only checks are retained under .protected/stage_C/C001; the new Stage C verification manifest has SHA-256 **072f7937ab0ca845cad3804352aac3afb791db4f46a36a5516995b30ef11a5cd**. The [final integrity summary](FINAL_INTEGRITY_VERIFICATION.json) records the complete result.

Scientific source-map fingerprint remains 0967e8db64935764b5c34fb35b15978739c6a2d536f6ea13bb05fd0540681d5d; environment fingerprint remains f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c. The live interpreter/packages match the frozen environment. No dependency or scientific configuration changed.

The approved production posterior is still v04_main_r1/r2/r3, 12 chains and 96,000 retained draws. Exact posterior hashes, frozen PCA, selected comparator and calibration hashes are in the accepted identity record. CQR remains the preselected/refitted gb-depth1-leaf10-lr0p1 with the original 25-engine cohort, rank 24 and nonshrinking correction 19.987558518873357. No recalibration occurred.

## Unchanged numerical acceptance and disclosures

Bayesian and CQR predictions remain complete for 100/100 engines. All **300 pooled production quantiles** and **900 independent-fit compatibility comparisons** retain PASS. Maximum pooled approximate upper MCSE remains **0.3976892271390135 cycles**, under the fixed 0.5-cycle limit. Mandatory numerical failures remain zero.

The **13 individual-fit batch upper-MCSE exceedances**, affecting 7 individual-fit quantiles, are mandatory disclosures and remain unchanged. Their maximum is 0.86495109 cycles. The owner explicitly accepts these disclosures under the preapproved pooled production rule, provided unchanged numerical logic and all compatibility checks. Those conditions passed. There is no retrospective threshold reinterpretation, predictor substitution, added draw or repair.

[Complete cohort/numerical summary](COHORT_AND_NUMERICAL_ACCEPTANCE_SUMMARY.json) binds the retained Stage B disclosure. All earlier development failures, selection/calibration exposure, identification, pipeline sensitivity, approximate MCSE, transport/exchangeability, data-rights, novelty and replay limitations remain applicable. This Stage C check does not reassess or erase them.

## Formal receipt, publication custody and current authority

The [Stage C acceptance receipt](STAGE_C_ACCEPTANCE_RECEIPT.json) records the owner's satisfied condition, exact accepted bundle, all manifest/table hashes and verification provenance. Acceptance payload and exact Git checkpoint are linked by the subsequent **GIT_ADMINISTRATIVE_RECEIPT.json**. That later receipt avoids circular commit/hash claims.

The [current protected phase state](CURRENT_PROTECTED_PHASE_STATUS.json) records G3 PROTOCOL_LOCKED, B COMPLETED, C ACCEPTED and D NOT_AUTHORIZED. Historical G3/Stage B phase-status files remain byte-preserved evidence of permissions at their earlier dates; they are not rewritten to manufacture prior acceptance.

Raw sensors, engine-level predictions, complete protected file maps and detailed Stage C checks remain local and Git-ignored. The public repository receives documentation, source and artifact identities only. Raw-data redistribution and scientific publication rights are not conferred by this acceptance.

Procedural evidence supports pre-label sealing and the documented access boundary. It does not prove independent encrypted custody, WORM immutability, external identity authentication or an exhaustive OS-level forensic history. These limits are explicitly retained.

## Readiness recommendation and stop boundary

**READY FOR SEPARATE OWNER STAGE D AUTHORIZATION REVIEW.** The exact pre-label prediction freeze is accepted and its integrity/numerical prerequisites are satisfied. Stage D execution still requires its own explicit owner directive. Future label alignment, complete finite scoring and the locked joint score-MCSE/kink qualification procedures remain future authorized-stage checks; no successful outcome is guaranteed here.

**Official labels were not opened and no interval score, Bayesian-minus-CQR contrast, empirical coverage, MAE, RMSE or other label-dependent metric was computed.** No new predictions, roots, draws, refits, recalibration, additional experiment or scientific change occurred. Native scientific status remains PROTOCOL_LOCKED, not RESEARCH_VALIDATED.

**STOP after Stage C. Stage D remains NOT_AUTHORIZED.**
