# RP-001 | FORMAL RESEARCH OWNER AUTHORIZATION
## G3: Protocol Lock, Scientific Freeze & Pre-Evaluation Readiness

**To:** GPT 6.1 SOL Extra High  
**Role:** AI Lead Research & Principal Mathematical Verifier  
**Research Workers:** GPT 6 LUNA MAX  
**Research Owners:** Raihan × Rei  
**Decision:** APPROVE FORMAL PROTOCOL LOCK ONLY  
**Authorization Scope:** G3 Scientific Protocol Lock and Preparation for Protected Evaluation

---

## 1. Formal Research Owner Decision

Research Owners telah meninjau paket RP-001 v0.5, termasuk:

- Pre-Lock Resolution Memo v0.5.
- Proposed Locked Analysis Contract v0.5.
- Mathematical Validity Assessment.
- High-rho investigation.
- Numerical precision and score uncertainty verification.
- Reproducibility and provenance records.
- Research risk dispositions.

Kami menerima rekomendasi Research Lead:

**READY FOR OWNER LOCK REVIEW**

Berdasarkan bukti tersebut, Research Owners memberikan:

**APPROVAL TO EXECUTE FORMAL G3 PROTOCOL LOCK**

Persetujuan ini berlaku khusus untuk research protocol dengan cakupan:

**Descriptive finite-benchmark comparison of hierarchical Bayesian predictive intervals versus calibrated CQR on NASA C-MAPSS FD001.**

Persetujuan ini bukan izin untuk menjalankan official evaluation.

Research question, primary endpoint, primary model, comparison procedure, uncertainty policy, dan scientific claim boundaries harus mengikuti kontrak v0.5 yang telah ditinjau.

## 2. Authoritative Research Baseline

Project root:

`C:\Coding\Project\NAOBI RESEARCH\RP-001_Bayesian_RUL_Reliability`

Repository:

`https://github.com/mrraihan29/RP-001_Bayesian_RUL_Reliability`

Owner-reviewed v0.5 commit:

`c583ce62eac9a6b3dcd29c1929cc07c17569beb7`

Authoritative contract:

`docs/v0.5/02_proposed_locked_analysis_contract.md`

Supporting decision:

`docs/v0.5/01_prelock_resolution_memo.md`

Verified baseline identities reported by the research team:

Environment SHA-256:

`f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c`

FD001 training SHA-256:

`963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8`

Split/cutoff SHA-256:

`6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b`

v0.5 resolution-plan SHA-256:

`6046cd808d6a4b68ed42fd7d3458f0f142273aa323f64bb077cb8c0bc7dc0745`

Sebelum melakukan lock, verifikasi identitas file dan snapshot aktual, termasuk final delivery receipt lokal yang sebelumnya tidak tersedia melalui GitHub.

Jangan menganggap nilai hash yang tertulis sebagai verifikasi otomatis. Jika terdapat mismatch yang material, hentikan lock dan laporkan kepada Research Owners.

## 3. Formal Protocol Lock Procedure

Buat folder:

`docs/protocol_lock/`

Siapkan immutable, auditable protocol lock package berisi:

1. `LOCKED_RESEARCH_PROTOCOL.md`
2. `LOCKED_ANALYSIS_CONTRACT.md`
3. `LOCK_DECISION_RECORD.md`
4. `FROZEN_MODEL_AND_CONFIGURATION_MANIFEST.json`
5. `FROZEN_CODE_AND_ENVIRONMENT_MANIFEST.json`
6. `FROZEN_DATA_AND_SPLIT_MANIFEST.json`
7. `SCIENTIFIC_CLAIM_BOUNDARIES.md`
8. `PROTECTED_EVALUATION_ACCESS_POLICY.md`
9. `LOCK_VERIFICATION_REPORT.md`
10. `LOCK_RECEIPT.json`

Nama file dapat disesuaikan jika diperlukan untuk konsistensi sistem, tetapi seluruh informasi tersebut wajib tersedia.

Dokumen terkunci harus merepresentasikan kontrak v0.5 yang telah disetujui, bukan menulis ulang metode dengan perubahan substantif.

Jangan mengubah persamaan, prior, preprocessing, hyperparameter, candidate selection, correction rule, statistical estimand, atau failure policy ketika melakukan packaging.

Jika ditemukan ambiguitas atau kontradiksi material yang memengaruhi output, **jangan diam-diam memperbaikinya**. Kembalikan amendment request kepada Research Owners.

## 4. Freeze the Scientific Methods

Secara eksplisit bekukan seluruh aspek berikut.

### Bayesian principal model

- Hierarchical latent level/slope Gaussian model.
- AR(1) sensor measurement-error structure.
- Log-RUL Gaussian conditional response.
- Analytically integrated latent engine effects.
- `anchored_v04` principal prior.
- Frozen posterior states from `v04_main_r1/r2/r3`.
- New-engine sensor-only global posterior update.
- Weighted posterior predictive mixture-CDF quantiles.
- Existing numerical and convergence acceptance criteria.

High-rho v0.5 reparameterization experiment tetap merupakan diagnostic evidence dan **tidak menggantikan principal production posterior**.

Tidak ada sampler rerun, prior modification, additional draws, atau automatic fallback tanpa reviewed pre-label amendment.

### CQR comparator

- Original fixed 12-candidate search space.
- Original tuning criteria and deterministic tie-breaking.
- Frozen selected gradient boosting configuration.
- Frozen refitted model and preprocessing.
- Original 25-engine development calibration cohort.
- Corrected conformal quantile rank 24.
- Frozen nonshrinking conformal correction.
- Fixed nonnegative RUL support projection.

Tidak diperbolehkan melakukan re-selection setelah protocol lock.

### Primary evaluation

- Dataset: official NASA C-MAPSS FD001.
- Unit evaluasi: satu official endpoint untuk setiap unseen engine.
- Target: uncapped RUL dalam cycles.
- Primary endpoint: mean 90% interval score.
- Primary contrast: Bayesian minus calibrated CQR.
- Complete-engine finite-benchmark evaluation.
- No primary population p-value.
- No claim of general superiority, equivalence, noninferiority, or validated maintenance utility.

Secondary ablations tetap exploratory dan tidak boleh menggantikan primary comparison.

## 5. Scientific Claim Boundary

Definisi operasional *competitive* adalah comparative characterization, bukan binary hypothesis acceptance.

Hasil akhir wajib memungkinkan pelaporan:

- Mean Bayesian interval score.
- Mean CQR interval score.
- Signed paired mean difference.
- Score ratio apabila terdefinisi.
- Interval-width and miss-penalty decompositions.
- Complete per-engine prediction and scoring records.
- Observed empirical coverage as a descriptive benchmark statistic.
- Numerical uncertainty and its limitations.
- Pipeline sensitivity and development limitations.

Tidak boleh mengklaim:

- Universal Bayesian superiority.
- Distribution-free coverage pada official endpoint population.
- Validated operational maintenance predictions.
- Unconditional whole-pipeline confidence interval.
- Practical equivalence or safety certification.
- Physical identification of latent degradation states.

Semua adverse development findings harus dipertahankan dan dilaporkan.

## 6. Protected Evaluation Separation

**CRITICAL: PROTOCOL LOCK IS NOT DATA-ACCESS AUTHORIZATION.**

Tahap penelitian selanjutnya harus dipisahkan menjadi empat keputusan:

**Stage A: Protocol Lock**

AUTHORIZED BY THIS DIRECTIVE.

Bekukan protokol, konfigurasi, model states, scientific code, data identities, dan policy. Verifikasi lock package dan serahkan receipt.

**Stage B: Official Test-Sensor Access**

NOT YET AUTHORIZED.

Hanya dapat dilakukan setelah Research Owners memberikan instruksi terpisah.

Tahap ini nantinya mencakup authorized extraction of test sensors, dataset-integrity checks, overlap screening, fixed-model predictions, numerical diagnostics, dan prediction freezing.

**Stage C: Prediction Freeze Acceptance**

NOT YET AUTHORIZED.

Research Owners harus memeriksa completion ledger, numerical gate status, prediction hashes, dan source/config identities sebelum memberikan izin pembukaan labels.

**Stage D: Official Test-Label Release and Scoring**

NOT YET AUTHORIZED.

Label release harus merupakan keputusan terpisah setelah frozen predictions diterima.

Public availability dari NASA benchmark tidak menggantikan owner authorization.

Jangan membaca protected test members dari archive, baik untuk preprocessing, statistik deskriptif, eksperimen, maupun preview.

## 7. Numerical Failure and Scientific Integrity Policy

Pertahankan seluruh numerical acceptance rules dari kontrak v0.5.

Semua future official endpoints harus melewati prospective numerical checks sebelum test labels dibuka.

Pastikan:

- Complete endpoint inclusion.
- Valid finite predictions.
- Fixed sampling diagnostic acceptance.
- Quantile MCSE and importance-weight diagnostics.
- Cross-replication consistency.
- Correct mixture CDF root evaluation.
- Proper chain/draw alignment untuk joint score-uncertainty propagation.
- Immutable prediction identity and hashes.
- Defined handling of score kinks and numerical qualification.

Jika terjadi kegagalan:

**STOP, RETAIN EVIDENCE, REPORT TO OWNERS.**

Jangan membuang engine yang sulit, mengubah seed, mengganti posterior, memperbesar jumlah draws, atau melakukan post-result repair tanpa persetujuan perubahan protokol.

## 8. Reproducibility and Repository Governance

Gunakan Git untuk mencatat formal lock.

Pastikan:

- Locked contract mempunyai exact content hash.
- Approved scientific source files terikat ke exact Git snapshot atau content hashes.
- Environment dan dependency lock dicatat.
- Model/posterior states terikat pada stored artifact hashes.
- Training data dan split identities diverifikasi.
- Historical failures tidak dihapus.
- Lock receipt dapat diverifikasi kembali.
- Working tree bersih setelah final lock commit, kecuali ignored research payloads yang sudah tercatat dan diverifikasi.

Repository saat ini public.

Sebelum push:

- Periksa Git history dan file yang akan dipublikasikan.
- Pastikan tidak ada credentials, private paths containing secrets, raw NASA archives, protected test data, atau restricted scientific payloads yang tanpa sengaja dipublikasikan.
- Jangan menganggap repository public berarti dataset memiliki izin redistribusi.
- Tetap dokumentasikan kebutuhan novelty dan data-rights review sebelum publikasi ilmiah.

Tidak perlu melakukan independent full MCMC rerun hanya untuk membuat lock package jika existing frozen evidence dan artifact identities dapat diverifikasi.

## 9. Mathematical Verification and Delegation

GPT 6 LUNA MAX dapat membantu penyusunan manifest, automated consistency checks, hashing, dan packaging.

Namun, **GPT 6.1 SOL Extra High wajib melakukan direct final verification** terhadap:

- Model specification consistency.
- Prior consistency.
- Posterior prediction contract.
- CQR quantile/calibration specification.
- Primary score definition.
- Numerical acceptance gates.
- Score-uncertainty propagation.
- Finite-benchmark estimand.
- Protected evaluation procedures.

Periksa bahwa tidak ada mathematical or methodological change antara approved v0.5 contract dan locked documents.

Catat sign-off SOL untuk setiap material scientific component.

## 10. Required Final Lock Handoff

Setelah seluruh verification checks selesai, berikan:

**RP-001 | G3 FORMAL PROTOCOL LOCK COMPLETION REPORT**

Laporan harus menyatakan:

1. Apakah protocol lock berhasil dilaksanakan.
2. Exact locked protocol version.
3. Lock commit hash.
4. Contract and scientific source hashes.
5. Dataset, split, environment dan posterior artifact fingerprints.
6. Verification results.
7. Preserved historical failure references.
8. Current authorization status.
9. Outstanding execution-stage risks.
10. Recommended first action untuk separately authorized Stage B.

Jika semua gate lulus, perbarui project state menjadi:

`PROTOCOL_LOCKED`

Catat owner directive ini sebagai dasar otorisasi formal, beserta tanggal, identitas pengirim yang dapat diverifikasi, dan commit sumber. Jangan membuat tanda tangan kriptografis atau identitas persetujuan yang tidak benar-benar tersedia.

Jika verifikasi gagal, status tetap:

`PROTOCOL_DRAFTED`

dan laporkan alasan kegagalan tanpa memaksakan lock.

## 11. Final Authorization Boundary

**AUTHORIZED NOW:**

Formal G3 protocol lock, scientific artifact freezing, source/configuration fingerprinting, lock integrity verification, documentation, dan Git recording.

**NOT AUTHORIZED NOW:**

Official test sensors, official RUL labels, confirmatory scoring, model reselection, numerical threshold relaxation, new science experiments, automatic fallback activation, atau scientific publication.

### Final Research Owner Instruction

Selesaikan formal G3 protocol lock berdasarkan kontrak v0.5.

Jangan mengoptimalkan hasil penelitian, jangan mengubah metode agar lebih menguntungkan salah satu model, dan jangan membuka protected evaluation data.

Setelah lock berhasil, **berhenti pada gate berikutnya** dan serahkan Lock Completion Report untuk keputusan owner.

**PROCEED WITH FORMAL PROTOCOL LOCK ONLY.**