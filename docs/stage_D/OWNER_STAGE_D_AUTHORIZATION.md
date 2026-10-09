# RP-001 | FORMAL RESEARCH OWNER AUTHORIZATION
## STAGE D: OFFICIAL LABEL RELEASE, CONFIRMATORY BENCHMARK SCORING & SCIENTIFIC RESULT AUDIT

**To:** GPT 6.1 SOL Extra High  
**Research Workers:** GPT 6 LUNA MAX  
**Research Owners:** Raihan × Rei

**DECISION: AUTHORIZE STAGE D UNDER THE LOCKED G3 CONTRACT**

**Research status:** PROTOCOL_LOCKED  
**Stage B:** COMPLETED  
**Stage C:** ACCEPTED  
**Stage D:** AUTHORIZED BY THIS DIRECTIVE, SUBJECT TO PRE-LABEL INTEGRITY GATES

---

## 1. Formal Research Owner Decision

Research Owners menerima Stage C Formal Prediction Freeze Acceptance Report dan bukti pendukung pada:

`62892ff054a967daa28f5314dbd2e5981f902268`

Stage C acceptance payload commit:

`3f582c2935fec286b5576467b3b5d367bd467c00`

The accepted frozen prediction bundle is:

`96084deb61336367b48f19251f0cd529e5deb98c754eb09a05dca5f52ef4263e`

Protokol ilmiah tetap:

`RP-001-G3-v0.5-AM1`

Scientific lock commit:

`fc7083d23d3cff5e4ee9a9f5d0af9036ec32e26d`

Research Owners kini mengotorisasi **Stage D**, yaitu official FD001 RUL label release, evaluasi lengkap terhadap frozen Bayesian dan CQR predictions, serta analisis numerik dan pelaporan berdasarkan locked contract.

Ini merupakan first authorized official-outcome exposure.

**Tidak ada perubahan metode yang diizinkan sebagai akibat dari melihat hasil.**

## 2. Mandatory Pre-Label Verification

Sebelum mengakses `RUL_FD001.txt`:

1. Verifikasi bahwa G3 tetap PROTOCOL_LOCKED dan Stage C tetap ACCEPTED.
2. Rehash exact accepted bundle beserta tiga protected manifests.
3. Verifikasi exact hashes dari Bayesian predictions, CQR predictions dan 100-row engine ledger.
4. Cocokkan frozen posterior, calibration, model, preprocessing, scientific source dan environment identities.
5. Pastikan tidak ada perubahan pada prediksi setelah Stage C acceptance.
6. Siapkan dan bekukan scoring implementation serta execution plan sebelum labels dibuka.
7. Jalankan deterministic mathematical tests dengan synthetic fixtures untuk memverifikasi formula interval score, paired difference, missing-value handling, coverage indicator dan numerical influence calculations.
8. Lakukan direct SOL review terhadap source scoring dan failure rules.
9. Commit pre-execution plan, scoring code, tests, serta source hashes ke Git sebelum label access.
10. Siapkan event registry dan immutable failure logging.

Synthetic fixtures hanya boleh digunakan untuk memverifikasi implementasi aritmetika yang telah ditentukan, bukan untuk memilih metode evaluasi atau mengubah scientific hypotheses.

**Jika salah satu pre-label integrity gate gagal, STOP sebelum official label access.**

Tidak boleh mengganti accepted prediction bundle atau melakukan perbaikan prediksi.

## 3. Official Test-Label Release

Setelah seluruh pre-label checks PASS:

Akses hanya official FD001 RUL labels yang telah ditentukan dalam locked data policy.

Catat:

- Original NASA archive provenance.
- Exact source/archive/member identities.
- Extracted label file SHA-256.
- Timestamp dan owner authorization.
- Label extraction and access events.
- Frozen scoring source identity.

Validasi:

- Exactly 100 official RUL values.
- Complete one-to-one correspondence dengan frozen engine IDs.
- Correct ordering/alignment sesuai declared official schema.
- Finite, positive, uncapped RUL values.
- No duplicate, missing, ambiguous, atau unmatched engine records.

Jangan memodifikasi labels berdasarkan hasil prediksi.

Jika ditemukan schema/alignment/identity anomaly, STOP dan kembalikan kepada Research Owners tanpa melakukan subset scoring.

## 4. Primary Scientific Evaluation

Gunakan hanya frozen Bayesian dan calibrated CQR predictions yang diterima pada Stage C.

Primary endpoint:

**90% Prediction Interval Score**

Untuk setiap engine i:

`IS90_i = (U_i - L_i) + 20 max(L_i - y_i, 0) + 20 max(y_i - U_i, 0)`

Primary comparison:

`D_F = mean(IS90_Bayesian - IS90_CQR)`

Gunakan seluruh 100 official engines, satu official endpoint per engine.

Lower interval score is better.

Hitung dan simpan:

1. Mean Bayesian 90% interval score.
2. Mean calibrated CQR 90% interval score.
3. Exact paired benchmark score difference.
4. Score ratio apabila denominator valid.
5. Per-engine interval widths.
6. Below-interval and above-interval miss penalties.
7. Complete paired score decomposition.
8. Exact empirical 90% interval coverage fractions.
9. Descriptive median prediction errors, MAE, RMSE dan bias sesuai locked contract.

Gunakan float64 dan compensated summation untuk primary contrast.

Jika ada satu engine dengan primary prediction/label/score yang missing, invalid atau nonfinite, status primary evaluation harus **UNAVAILABLE**, bukan menghitung rata-rata dari subset.

Jangan drop, impute, cap, winsorize, replace, atau memilih ulang observations.

## 5. Numerical Uncertainty Propagation

Wajib jalankan locked score-level numerical uncertainty procedure.

Gunakan existing aligned 12-chain Bayesian conditional terms, quantile influence dan fixed model states.

Pertahankan:

- Shared posterior draw alignment across engines.
- Endpoint lower/upper covariance.
- Chain-wise batch covariance estimates.
- Batch sizes 250/500.
- Satterthwaite approximate upper MCSE.
- Frozen multiplicity and numerical acceptance rules.
- Independent-fit score sensitivity disclosures.
- Exact numerical failure handling.

Untuk interval score derivatives gunakan rumus yang dikunci:

`g_L = -1 + 20 I(y < L)`

`g_U = 1 - 20 I(y > U)`

Periksa prediction-boundary kinks dan label proximity terhadap endpoint uncertainty.

Jika score upper MCSE undefined/nonfinite, melebihi 0.5 cycles, atau label berada dalam tiga endpoint upper MCSE dari interval boundary, gunakan status:

`NUMERICALLY_QUALIFIED`

sesuai locked policy.

Status tersebut membatasi interpretasi ideal-posterior score atau ranking. Jangan menghapus complete stored-prediction benchmark contrast apabila tetap valid dan finite.

**No post-label rerun, additional draws, or numerical repair without separate Research Owner approval.**

MCSE merupakan approximate computational uncertainty, bukan confidence interval untuk generalisasi populasi.

## 6. Strict Scientific Interpretation

Hasil penelitian adalah:

**Descriptive finite-benchmark comparison of two frozen predictive procedures on official FD001 endpoints.**

Jangan melakukan atau mengklaim:

- Population-level hypothesis testing.
- Primary bootstrap confidence intervals.
- General Bayesian superiority.
- Practical equivalence or noninferiority.
- Guaranteed conformal coverage pada official cutoff distribution.
- Causal superiority of Bayesian inference.
- Validated real-engine maintenance utility.
- Whole-pipeline unconditional uncertainty quantification.

Jika Bayesian menghasilkan interval score lebih rendah, simpulkan hanya bahwa Bayesian frozen procedure mendapat lower mean score pada benchmark yang diamati.

Jika CQR menghasilkan interval score lebih rendah, simpulkan hal yang sama untuk CQR.

Jika ada numerical qualification, jelaskan dampaknya secara eksplisit.

**Negative, null, mixed atau qualified results sama-sama scientific outcomes yang valid.**

## 7. Mandatory Robustness and Limitations Disclosure

Pertahankan semua adverse evidence historis, termasuk:

- v0.3 numerical precision failure.
- Original high-rho synthetic MCMC failure.
- Bounded v0.5 high-rho remediation.
- 13 Stage B individual-fit precision exceedances.
- Small tuning and calibration cohorts.
- Exposed development calibration outcomes.
- Prior adaptation during development.
- Eight pipeline sensitivity perturbations.
- CQR winner instability.
- Bootstrap operating-characteristic limitations.
- Unequal model feature representation/search budgets.
- Unknown official cutoff exchangeability.
- Synthetic-to-real generalization limitations.

Jangan mengubah research narrative agar terlihat bahwa seluruh ketidakpastian telah terselesaikan.

Secondary analyses hanya boleh dijalankan sebagaimana telah ditetapkan dalam locked contract. Tidak boleh menggantikan primary comparison atau dipakai untuk outcome-driven selection.

## 8. Independent Numerical and Result Verification

SOL wajib melakukan direct independent mathematical review terhadap:

- Official label/engine alignment.
- Interval score formula and implementation.
- Compensated mean difference.
- Complete score vector and decomposition.
- Empirical coverage arithmetic.
- Per-engine result consistency.
- Score-level MCSE implementation.
- Correlation-preserving influence projection.
- Numerical qualification flags.
- Results interpretation and claim boundaries.

Worker LUNA MAX boleh menjalankan independent implementation checks dari frozen inputs, tetapi jangan mengklaim external replication jika pemeriksaan hanya dilakukan oleh tim internal.

Buat immutable result and verification artifacts dengan full failure provenance.

Jika arithmetic mismatch ditemukan setelah label release, dokumentasikan tanpa mengubah predictions; hentikan dan minta keputusan owner jika koreksi memerlukan perubahan material pada prosedur terkunci.

## 9. Protected Results and Repository Policy

Research repository tetap public.

Namun, authorization Stage D **tidak otomatis memberikan izin mempublikasikan official labels, raw sensor data, per-engine restricted predictions atau label-derived result payloads**.

Simpan data dan hasil rinci dalam protected local research storage.

Public GitHub boleh memuat administrative provenance, executable code, hash fingerprints dan laporan status yang tidak membocorkan restricted outcomes.

Jangan mempublikasikan scientific performance results atau hasil per-engine ke repository public sebelum Research Owners melakukan result-release, data-rights dan publication review.

Pastikan Git history dan staged files diperiksa sebelum push.

Pertahankan exact source/manifest/receipt provenance untuk semua scientific computations.

## 10. Required Stage D Deliverables

Serahkan:

**RP-001 | STAGE D OFFICIAL BENCHMARK EVALUATION & SCIENTIFIC RESULTS PACKAGE**

Paket wajib mencakup:

1. Official label access and provenance report.
2. Pre-label freeze/integrity verification receipt.
3. Complete 100-engine label alignment report.
4. Primary Bayesian versus CQR interval-score evaluation.
5. Per-engine paired score and miss/width decomposition.
6. Empirical coverage and descriptive error metrics.
7. Score-level numerical uncertainty assessment.
8. Numerical qualification and failure ledger.
9. Independent SOL mathematical re-verification.
10. Scientific limitations and claim-boundary assessment.
11. Protected result payload manifest and hashes.
12. Research Lead final Stage D recommendation.

Untuk handoff kepada Research Owners, gunakan salah satu status:

**A. COMPLETE AND READY FOR OWNER SCIENTIFIC RESULT REVIEW**

Seluruh required inputs/scores finite dan lengkap, dengan seluruh numerical qualification dilaporkan secara jujur.

**B. NUMERICALLY QUALIFIED RESULT**

Stored benchmark result valid, tetapi ideal-posterior numerical interpretation memerlukan qualification sesuai kontrak.

**C. STAGE D BLOCKED / PRIMARY RESULT UNAVAILABLE**

Terdapat failure atau ambiguity material yang membatalkan evaluasi lengkap.

Jangan menyembunyikan kategori B atau C demi menghasilkan status A.

## 11. Final Authorization Boundary

Stage D authorization hanya berlaku untuk official label release, frozen-procedure scoring, numerical assessment, verification dan protected result packaging.

Tidak termasuk:

- Retraining.
- Model reselection.
- New posterior sampling.
- Threshold changes.
- Post-outcome adaptation.
- Public scientific release.
- Declaring general predictive superiority.
- Declaring `RESEARCH_VALIDATED`.

Setelah Stage D selesai:

**STOP AND RETURN TO RESEARCH OWNERS.**

Research Owners akan memutuskan validitas kesimpulan, kebutuhan koreksi terbatas, serta kesiapan manuscript dan publication review dalam gate berikutnya.

**FINAL DECISION: AUTHORIZE STAGE D ONLY UNDER THE EXACT ACCEPTED STAGE C FREEZE AND LOCKED G3 CONTRACT.**

**Do not optimize the result. Execute the protocol exactly as frozen.**