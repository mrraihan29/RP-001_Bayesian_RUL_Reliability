# RP-001 | RESEARCH OWNER AUTHORIZATION
## STAGE B: OFFICIAL TEST-SENSOR ACCESS, PREDICTION GENERATION & NUMERICAL VERIFICATION

**To:** GPT 6.1 SOL Extra High  
**Role:** AI Lead Research & Principal Mathematical Verifier  
**Research Workers:** GPT 6 LUNA MAX  
**Research Owners:** Raihan × Rei

**Decision: AUTHORIZE STAGE B ONLY**

### 1. Research Owner Decision

Research Owners menerima laporan penyelesaian Formal G3 Protocol Lock.

Approved protocol version:

`RP-001-G3-v0.5-AM1`

Locked scientific commit:

`fc7083d23d3cff5e4ee9a9f5d0af9036ec32e26d`

Final administrative receipt checkpoint:

`da4da0bd51b86239a36effcb92a1106490835c6b`

Authoritative documents:

- `docs/protocol_lock/LOCKED_RESEARCH_PROTOCOL.md`
- `docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md`
- `docs/protocol_lock/PROTECTED_EVALUATION_ACCESS_POLICY.md`
- `docs/protocol_lock/LOCK_RECEIPT.json`

Kami sekarang memberikan otorisasi untuk **Stage B: official FD001 test-sensor access, input integrity audit, frozen-model prediction generation, numerical verification, dan preparation of immutable prediction evidence**.

Persetujuan ini tidak mencakup official test labels atau primary outcome scoring.

### 2. Strict Protected-Data Boundary

**AUTHORIZED:**

- Mengakses dan mengekstrak `test_FD001.txt` sesuai locked data policy.
- Melakukan sensor-only integrity dan overlap audits.
- Menghasilkan Bayesian dan CQR predictions menggunakan frozen procedures.
- Menjalankan numerical diagnostics tanpa mengetahui true RUL.
- Menyimpan dan membekukan prediction artifacts untuk Stage C review.

**STRICTLY PROHIBITED:**

- Membuka, membaca, mengekstrak, mem-preview, atau menganalisis `RUL_FD001.txt`.
- Menghitung interval score, prediction coverage, MAE, RMSE, atau metrik lain yang membutuhkan official RUL labels.
- Mengubah priors, posterior, CQR, preprocessing, hyperparameters, cutoff rules, atau numerical thresholds.
- Melakukan training ulang atau posterior resampling tanpa approved amendment.
- Mengganti model, memperbaiki predictions berdasarkan outcomes, atau menjalankan confirmatory scoring.
- Mengaktifkan Stage C atau D secara otomatis.

### 3. Pre-Execution Lock Verification

Sebelum membuka sensor data:

1. Verifikasi final G3 lock receipt dan scientific source hashes.
2. Cocokkan environment, dependency lock, model states, preprocessing maps, dan comparator artifacts.
3. Pastikan canonical quantile implementation menggunakan `rp001.v04_precision`, sesuai G3-AM-001.
4. Periksa integritas source data tanpa mengakses protected label members.
5. Catat Git commit, working-tree state, environment fingerprint, serta data-access authorization.
6. Siapkan immutable Stage B experiment registry dan failure ledger.

Jika terdapat mismatch material, STOP dan laporkan kepada Research Owners.

### 4. Official Sensor Integrity Audit

Akses official test sensors saja.

Lakukan pemeriksaan terhadap:

- Expected 100 engine trajectories.
- Schema 26 fields dan urutan kolom.
- Missing, NaN, infinite, atau invalid values.
- Engine identifiers dan uniqueness.
- Positive, contiguous observation cycles.
- Duplicate engine-cycle keys.
- Observed endpoint cycle untuk setiap engine.
- Prefix overlap dan near-duplicate screening terhadap training data.
- Tidak adanya target labels atau future information dalam features.

Gunakan aturan dan ambang overlap yang sudah dikunci. Jangan mengubahnya setelah melihat data.

Jika count, schema, overlap, atau integrity check menghasilkan material warning, STOP dan return to owners.

Jangan menghapus engine atau mendefinisikan ulang evaluation cohort.

### 5. Frozen Bayesian Prediction

Gunakan hanya approved production posterior:

- `v04_main_r1`
- `v04_main_r2`
- `v04_main_r3`

Total 12 chains dan 96.000 retained draws sesuai locked contract.

Untuk setiap official unseen engine:

1. Gunakan sensor history hingga official last-observed cycle.
2. Terapkan frozen PCA dan preprocessing.
3. Lakukan sensor-only posterior importance update untuk engine tersebut.
4. Hitung conditional predictive mixture CDF.
5. Peroleh quantiles 0.05, 0.50, dan 0.95 melalui canonical approved precision helper.
6. Simpan RUL-scale quantiles, importance diagnostics, numerical diagnostics, dan provenance.

Tidak diperbolehkan pooled conditioning menggunakan sensors dari engine official lain untuk mengubah global posterior secara kolektif.

### 6. Frozen CQR Prediction

Gunakan selected dan refitted CQR objects yang telah dikunci.

Pertahankan:

- Frozen selected candidate.
- Frozen preprocessing.
- Existing calibration cohort dan correction.
- Rank 24 finite-sample rule.
- Nonshrinking conformal expansion.
- Nonnegative RUL support projection.

Jangan melakukan hyperparameter search, refitting, atau recalibration menggunakan official test data.

Simpan lower, median, upper predictions dan seluruh identitas artifact.

### 7. Numerical Acceptance Gates

Verifikasi seluruh official endpoint predictions menggunakan locked numerical policy.

Termasuk:

- MCMC convergence requirements.
- Weight ESS dan influence ESS.
- Approximate upper quantile MCSE maksimum 0.5 cycle.
- Batch-size diagnostics 250/500.
- Multiplicity adjustment untuk seluruh official endpoints dan quantiles.
- Independent-fit replication compatibility.
- Weighted mixture CDF root residual.
- Finite and ordered predictive intervals.
- Complete engine coverage dan source consistency.

Pastikan semua endpoint dievaluasi menggunakan aturan yang identik.

**Jika satu mandatory numerical gate gagal, STOP.**

Pertahankan seluruh failure records. Jangan menghapus kasus sulit, mengganti seed, menambah draws, mengubah threshold, atau mengaktifkan fallback.

Kegagalan Stage B adalah hasil audit yang sah, bukan alasan memaksakan PASS.

### 8. Prediction Freeze Preparation

Jika seluruh mandatory Stage B checks PASS:

Buat immutable prediction package berisi:

1. Complete official engine-ID ledger.
2. Official observed cutoff cycles.
3. Bayesian lower/median/upper predictions.
4. Calibrated CQR lower/median/upper predictions.
5. Numerical precision dan convergence diagnostics.
6. Independent replication consistency records.
7. Input and overlap integrity audit.
8. Source, model, calibration, dan environment fingerprints.
9. Prediction artifact SHA-256 hashes.
10. Full execution provenance dan failure history.

Seluruh predictions harus dibekukan dan di-hash sebelum official labels diotorisasi.

Simpan protected scientific payloads sesuai repository data policy. Jangan mengunggah raw official sensor data atau restricted payloads ke public repository tanpa clearance.

Stage B boleh menghasilkan paket kandidat freeze, tetapi **acceptance of prediction freeze tetap milik Research Owners pada Stage C**.

### 9. Required Stage B Handoff

Serahkan:

**RP-001 | STAGE B OFFICIAL SENSOR & PREDICTION COMPLETION REPORT**

Laporan harus mencakup:

- Exact locked protocol version.
- Official sensor access provenance.
- Number of assessed engines.
- Input integrity and overlap results.
- Complete Bayesian/CQR prediction status.
- All mandatory numerical gate results.
- Prediction package manifest and hashes.
- Reproducibility/environment evidence.
- Deviations, warnings, and retained failures.
- Formal recommendation for Stage C readiness.

Rekomendasi akhir harus salah satu:

**A. READY FOR OWNER STAGE C REVIEW**

Semua required checks PASS dan seluruh prediksi telah dibekukan untuk acceptance review.

**B. STAGE B BLOCKED**

Ada integrity, numerical, source, atau execution failure yang memerlukan keputusan owner.

Jangan menggunakan kategori A kecuali seluruh mandatory gates benar-benar terpenuhi.

### 10. Final Authorization Boundary

Setelah Stage B selesai:

**STOP AND RETURN TO RESEARCH OWNERS.**

Jangan membuka test labels.

Jangan menghitung primary interval-score comparison.

Jangan mengubah scientific pipeline.

Jangan menganggap Stage B completion sebagai izin Stage C atau Stage D.

**AUTHORIZED: EXECUTE STAGE B ONLY UNDER THE LOCKED G3 CONTRACT.**

**NOT AUTHORIZED: STAGE C ACCEPTANCE OR STAGE D LABEL RELEASE AND SCORING.**

Scientific integrity, reproducibility, complete endpoint accountability, dan protection against outcome-driven adaptation harus diutamakan daripada mendapatkan hasil yang menguntungkan Bayesian.

**Proceed with Stage B only.**