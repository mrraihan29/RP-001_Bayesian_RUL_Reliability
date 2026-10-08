# RP-001 | RESEARCH OWNER DIRECTIVE v0.4
## Targeted Scientific Remediation & Pre-Lock Verification

**To:** GPT 6.1 SOL Extra High  
**Role:** AI Lead Research & Principal Mathematical Verifier  
**Workers:** GPT 6 LUNA MAX  
**From:** Raihan × Rei, Research Owners  
**Decision:** CONDITIONAL APPROVAL FOR v0.4 REMEDIATION  
**Current Status:** REVISE AGAIN / PROTOCOL_DRAFTED

---

## 1. Research Owner Decision

Research Owners telah meninjau sembilan laporan RP-001 v0.3 dan menerima rekomendasi **REVISE AGAIN**.

Kami menyetujui kelanjutan penelitian ke tahap **targeted scientific remediation v0.4**, tetapi belum mengizinkan final protocol lock maupun confirmatory evaluation.

Kami menilai pekerjaan v0.3 menunjukkan kemajuan metodologis yang baik. Namun, sejumlah persoalan terkait numerical precision, Bayesian prior plausibility, identifiability, cutoff transportability, dan inferential validity masih memerlukan penyelesaian.

**Tujuan v0.4 bukan memastikan Bayesian mengungguli CQR. Tujuannya adalah memastikan penelitian mempunyai fondasi matematis, statistik, dan komputasional yang cukup kuat untuk dievaluasi secara ilmiah.**

Jangan mengejar PASS dengan menurunkan standar atau mengubah keputusan setelah melihat hasil yang tidak menguntungkan.

## 2. Project Workspace

Gunakan workspace yang sudah ada:

`C:\Coding\Project\NAOBI RESEARCH\RP-001_Bayesian_RUL_Reliability`

Baca seluruh dokumen v0.3, kode, experimental registry, test logs, mathematical verification records, dan provenance sebelum melakukan perubahan.

Hasil revisi harus ditempatkan pada:

`docs/v0.4/`

Pertahankan dokumen v0.1–v0.3, experimental histories, failed runs, dan semua provenance material.

Jangan menghapus, menimpa, atau mengubah evidence historis secara diam-diam.

Gunakan Git untuk seluruh perubahan. Catat commit hash dan exact executed source state pada setiap experiment run.

## 3. P0 — Numerical Precision Remediation

Pada v0.3, maksimum approximate predictive quantile MCSE sebesar **0.728972 cycle**, melebihi acceptance criterion **0.5 cycle**.

Ini merupakan unresolved blocking issue.

Lakukan investigasi terhadap:

- Validitas metode estimasi quantile Monte Carlo uncertainty.
- Jumlah posterior draws dan chain dependence.
- Effective sample size untuk importance-weighted prediction.
- Stabilitas estimasi mixture CDF quantiles.
- Perbedaan antara MCMC parameter diagnostics dan predictive quantile accuracy.
- Ketidakpastian dari estimasi MCSE itu sendiri.
- Kesesuaian importance integration dengan exact sensor-only posterior conditioning.

Susun **prospective numerical precision plan** sebelum eksperimen tambahan.

Pertimbangkan peningkatan posterior draws, multiple independent replications, batch-based precision checks, atau sensor-only oracle apabila metodologis dan komputasional layak.

Verifikasi tidak hanya kasus terbaik, tetapi seluruh required calibration cases, termasuk engine 86 yang sebelumnya menghasilkan kegagalan maksimum.

Pertahankan threshold 0.5 cycle sebagai acceptance criterion yang sudah disetujui. Jangan merelaksasinya secara retrospektif.

Jika estimator MCSE sebelumnya tidak cukup valid, dokumentasikan keterbatasannya, tetapkan estimator pengganti yang dapat dipertanggungjawabkan, dan evaluasi ulang melalui prosedur yang dibekukan sebelum menghasilkan bukti baru.

**Required outcome:** Verified precision PASS atau documented unresolved FAIL. Jangan memaksakan PASS.

## 4. P0 — Bayesian Prior Plausibility

Laporan v0.3 menunjukkan prior predictive tails yang sangat luas dan sensitivitas upper predictive quantiles terhadap spesifikasi prior.

Lakukan:

1. Prior predictive plausibility assessment berdasarkan skala dan sifat RUL pada dataset.
2. Justifikasi setiap prior material, termasuk scale, correlation, residual noise, dan hierarchical effects.
3. Evaluasi implikasi prior terhadap predictive distribution.
4. Sensitivity assessment terhadap prior alternatives yang memiliki dasar ilmiah.
5. Pemeriksaan apakah posterior cukup diinformasikan data atau terlalu dipengaruhi prior.

Jangan memilih prior berdasarkan nilai interval score yang menguntungkan pada development calibration outcomes yang sudah terinspeksi.

Apabila prior awal tidak dapat dipertahankan, usulkan revisi dengan alasan metodologis independen. Catat revisi tersebut sebagai development adaptation.

**Required outcome:** Prior Specification & Mathematical Justification Report.

## 5. P0 — Identifiability and Synthetic Validation

Empat synthetic recovery experiments sebelumnya mendukung kebenaran implementasi pada skenario terbatas, tetapi belum membuktikan practical atau structural identifiability secara memadai.

Lakukan targeted validation terhadap:

- High sensor autocorrelation.
- Weak latent signal.
- Confounding antara age effects, latent effects, dan residual variance.
- Posterior correlations.
- Sensitivitas parameter terhadap noise assumptions.
- Recovery of scientifically material parameters and predictive quantities.

Pertimbangkan simulation-based calibration, repeated parameter recovery, dan prior-to-posterior information analysis dengan jumlah simulasi yang sesuai computational budget.

Bedakan secara eksplisit:

- Structural identifiability.
- Practical identifiability.
- Computational convergence.
- Predictive accuracy.
- Predictive uncertainty calibration.

Keberhasilan R-hat, ESS, atau parameter recovery pada beberapa synthetic datasets tidak otomatis membuktikan semua aspek tersebut.

Jika model terlalu sulit diidentifikasi, prioritaskan model yang lebih sederhana dan defensible. Jangan menambah kompleksitas hanya untuk mempertahankan arsitektur awal.

Fallback model wajib ditentukan secara prospektif sebelum final test evaluation.

**Required outcome:** Identifiability and Synthetic Validation Report dengan explicit unresolved limitations.

## 6. P0 — Statistical Estimand and Cutoff Transportability

Tetapkan secara formal target utama penelitian sebagai:

**Finite-benchmark comparative evaluation pada official NASA FD001 unseen-engine endpoints.**

Pertahankan proposed primary endpoint:

**Mean 90% Prediction Interval Score**

Pertahankan proposed primary comparison:

**Bayesian principal model versus calibrated CQR**

Namun, bedakan secara matematis:

1. Exact finite-benchmark mean score difference.
2. Superpopulation inference dengan asumsi sampling tertentu.
3. Marginal conformal coverage guarantee.
4. Conditional coverage dan realized calibration-cohort coverage.
5. Generalization kepada mesin nyata.

Jangan menyatakan bahwa engine-disjoint splitting membuktikan exchangeability antara pseudo-cutoff calibration dan official test endpoints.

Review survivor eligibility C<T, cutoff distribution, selection bias, dan population restrictions.

Jika official cutoff mechanism tidak dapat diidentifikasi dari informasi yang diizinkan, gunakan restricted scientific claim yang eksplisit.

**Kami lebih memilih klaim empiris yang terbatas tetapi valid daripada klaim generalisasi yang tidak memiliki dasar matematis.**

## 7. P0 — Statistical Inference and Uncertainty

Tinjau ulang proposed paired engine-level bootstrap-t procedure.

Periksa:

- Sampling assumptions.
- Skewed atau heavy-tailed paired score differences.
- Influential engine observations.
- Degenerate bootstrap standard errors.
- Interval-score outliers.
- One-sided hypothesis-test operating characteristics.
- Coverage dan type-I error pada simulation scenarios yang relevan.
- Numerical failures, infinite intervals, dan missing predictions.

Dalam v0.3, simulation-based false-positive behavior pada beberapa distribusi menunjukkan sensitivitas yang perlu ditinjau.

Jangan memilih statistical procedure berdasarkan official test results.

Predefine primary inference method, failure handling, dan fallback policy sebelum protected data diakses.

Selain itu, pisahkan:

**Conditional fitted-pipeline uncertainty** dari **whole-pipeline uncertainty**.

Rancang bounded training-only sensitivity experiments untuk menilai pengaruh:

- Engine resampling.
- PCA representation.
- Model fitting.
- Hyperparameter selection.
- Calibration cohort selection.
- Cutoff realization.

Jika full-pipeline study tidak feasible dalam medium research budget, jelaskan secara kuantitatif batas kemampuan dan konsekuensi inferensinya. Jangan menyatakan total pipeline uncertainty telah terukur apabila hanya sebagian komponen dianalisis.

## 8. Comparator Fairness

Pertahankan CQR sebagai primary comparator.

Audit:

- Informasi yang tersedia bagi masing-masing metode.
- Feature representation.
- Training engine allocation.
- Hyperparameter search freedom.
- Computational budgets.
- Calibration procedures.
- Model-selection procedures.

Bayesian + post-hoc conformal calibration boleh digunakan sebagai secondary ablation untuk membantu menjelaskan efek calibration.

Jangan mengganti primary comparison berdasarkan hasil secondary experiments.

Laporkan perbedaan metodologi yang dapat membatasi atribusi hasil kepada Bayesian inference itu sendiri.

Threshold 5 interval-score cycles tetap tidak disetujui sebagai practical superiority margin.

## 9. Mathematical Verification Authority

Seluruh material mathematics harus diverifikasi secara langsung oleh **GPT 6.1 SOL Extra High**.

Worker GPT 6 LUNA MAX boleh:

- Mengembangkan implementasi.
- Menyiapkan derivasi.
- Menjalankan synthetic experiments.
- Menghasilkan independent numerical checks.
- Menyusun scientific artifacts.

Namun, SOL wajib melakukan independent mathematical review terhadap:

- Likelihood derivation.
- Posterior conditioning.
- Hierarchical covariance structure.
- Mixture predictive CDF.
- Quantile computation.
- Importance weighting.
- Monte Carlo uncertainty estimation.
- Conformal rank correction.
- Statistical estimands.
- Primary inference procedure.

Setiap mathematical verification harus mencatat assumption, derivation/reference, numerical or independent cross-check, limitations, serta verdict PASS / REVISE / REJECT.

Worker agreement atau successful unit tests tidak menggantikan direct lead verification.

## 10. Scientific Scope and Computational Budget

Penelitian tetap berskala MEDIUM.

Gunakan CPU lokal sebagai default berdasarkan hasil pilot v0.3.

Google Colab Pro hanya digunakan apabila ada justifikasi berbasis measured runtime atau memory requirement.

Jangan melakukan exhaustive hyperparameter search, uncontrolled architecture expansion, atau eksperimen tambahan yang tidak mempunyai research purpose yang jelas.

Tetapkan batas jumlah experiment runs, compute budget, stopping criteria, dan rules for failed runs sebelum eksekusi tambahan.

Jika suatu eksperimen tidak materially meningkatkan scientific confidence, jangan jalankan hanya demi menambah jumlah hasil.

## 11. Protected Data and Adaptive Development

**STRICT DATA ACCESS RESTRICTION**

Di tahap v0.4:

- Synthetic data: AUTHORIZED.
- Official FD001 training data: AUTHORIZED.
- Official test sensors: NOT AUTHORIZED.
- Official test RUL labels: NOT AUTHORIZED.
- Confirmatory evaluation: NOT AUTHORIZED.

Development calibration outcomes yang telah diinspeksi pada v0.3 tidak boleh kembali diperlakukan sebagai untouched validation evidence.

Catat seluruh methodological adaptation setelah exposure tersebut.

Jangan menggunakan hasil development berulang untuk mengklaim confirmatory superiority.

Keputusan mengenai pemakaian test sensors, pembekuan predictions, dan pembukaan test labels akan diberikan secara terpisah setelah protocol lock disetujui Research Owners.

## 12. Required Deliverables v0.4

Serahkan paket berikut:

1. Updated Research Protocol v0.4.
2. Numerical Precision Remediation Report.
3. Bayesian Prior Plausibility Report.
4. Identifiability and Synthetic Validation Report.
5. Estimand and Cutoff Transportability Assessment.
6. Statistical Inference and Full-Pipeline Uncertainty Plan.
7. Comparator Fairness and Evaluation Audit.
8. Independent Mathematical Re-Verification Report.
9. Reproducibility, Environment, and Compute Report.
10. Updated Risk, Assumption, and Decision Registers.
11. Research Lead Pre-Lock Readiness Recommendation.

Sertakan supporting artifacts berupa source code, exact configurations, test logs, synthetic datasets/seeds atau generator specifications, experiment registry, posterior diagnostics, mathematical test results, reproducibility instructions, dan hashes.

Buat `docs/v0.4/README.md` sebagai entry point dan evidence index.

Untuk setiap critical risk, tetapkan salah satu status:

- RESOLVED.
- MITIGATED BY CLAIM RESTRICTION.
- STILL BLOCKED.

Jelaskan evidence dan remaining uncertainty untuk setiap status tersebut.

## 13. Mandatory Exit Criteria

Sebelum merekomendasikan PROTOCOL_READY, pastikan:

- Predictive precision gate terpenuhi melalui prosedur yang sah.
- Material equations memperoleh direct SOL verification.
- Principal model mempunyai prior policy dan justifikasi yang defensible.
- Identifiability limitations telah dievaluasi dan dibatasi.
- Primary estimand didefinisikan secara tepat.
- Inferential failure policy ditetapkan sebelum official test access.
- Comparator dan model-selection procedures terkunci.
- Calibration exposure dan development adaptations terdokumentasi.
- Reproducibility evidence cukup untuk memeriksa experimental claims.
- Tidak terdapat unresolved critical issue yang membatalkan interpretasi primary scientific claim.

Jika syarat tersebut belum terpenuhi, jangan merekomendasikan protocol lock.

## 14. Final Handoff and Decision

Setelah penyelesaian v0.4, lakukan scientific self-audit dan adversarial methodological review.

Kritisi penelitian seolah-olah kamu adalah reviewer independen yang berusaha menemukan kelemahan identifiability, inference, model specification, leakage, dan unsupported statistical claims.

Kemudian berikan satu rekomendasi:

**A. READY FOR OWNER PROTOCOL-LOCK REVIEW**

Seluruh blocking issues teratasi atau dibatasi dengan scientifically defensible claim restrictions.

**B. REVISE AGAIN**

Masih ada masalah yang realistis diselesaikan tanpa mengubah research question utama.

**C. RE-SCOPE RECOMMENDED**

Model atau desain saat ini tidak cukup layak untuk menghasilkan klaim yang valid dalam batas medium research.

Jangan menganggap pilihan A sebagai target yang harus dicapai. B dan C merupakan scientific outcomes yang sah.

### Final Instruction

Jalankan remediation sesuai Rei Research Engineering Suite, gunakan seluruh evidence v0.3 sebagai baseline, pertahankan scientific integrity, dan dokumentasikan setiap decision serta deviation.

Delegasikan implementation tasks kepada GPT 6 LUNA MAX secara terkontrol. Semua mathematical conclusions material wajib diverifikasi sendiri oleh SOL Extra High.

**Do not optimize for a positive research result. Optimize for valid, reproducible, mathematically defensible evidence.**

Research Owners tetap memegang final protocol authorization.

**Proceed with v0.4 targeted remediation only.**