# RP-001 | SCIENTIFIC RESEARCH PROPOSAL

**Title:** A Rigorous Evaluation of Bayesian Predictive Uncertainty for Turbofan Remaining Useful Life Estimation: Calibration, Sharpness, and Reliability Under Engine-Level Dependence

**Version:** 0.1  
**Status:** Provisional Research Proposal  
**Research Mode:** Empirical Computational / Statistical Methodology  
**Dataset:** NASA C-MAPSS Turbofan Engine Degradation Simulation

---

## 1. Research Background

Remaining Useful Life (RUL) estimation merupakan komponen penting dalam prognostics and health management. Secara konvensional, banyak pendekatan mengevaluasi kualitas prediksi berdasarkan point estimation errors seperti MAE atau RMSE.

Akan tetapi, estimasi tunggal tidak menggambarkan seluruh ketidakpastian terkait proses degradasi, parameter model, pengamatan sensor, dan kondisi operasi.

Probabilistic prognostics memungkinkan prediksi berupa distribusi probabilitas atau prediction intervals. Kualitas prediksi tersebut perlu dinilai melalui calibration, sharpness, dan statistical reliability.

Studi ini menyelidiki kemampuan pendekatan Bayesian untuk menghasilkan predictive uncertainty yang dapat dipertanggungjawabkan secara statistik pada data degradasi mesin simulasi NASA C-MAPSS.

Penelitian tidak mengasumsikan bahwa Bayesian modeling akan mengungguli metode alternatif.

## 2. Research Problem

Masalah utama penelitian:

**Seberapa andal posterior predictive intervals dari model Bayesian untuk memperkirakan RUL mesin turbofan, apabila dievaluasi terhadap non-Bayesian probabilistic methods dengan mempertimbangkan calibration, interval sharpness, dan dependence antar-observasi dalam trajectory mesin?**

Perhatian utama bukan pencapaian predictive accuracy tertinggi, melainkan evaluasi konsistensi antara ketidakpastian yang diprediksi dan kenyataan empiris.

## 3. Research Objectives

### Primary Objective

Menentukan apakah pendekatan Bayesian mampu menghasilkan 90% RUL predictive intervals dengan kualitas probabilistik yang kompetitif dibandingkan comparator yang sudah dikalibrasi, menggunakan engine-level held-out evaluation.

### Secondary Objectives

- Mengukur empirical interval coverage terhadap nominal coverage.
- Membandingkan interval sharpness dan undercoverage penalties.
- Mengevaluasi bias dan point-prediction errors.
- Mengukur stabilitas model terhadap pemilihan prior.
- Menguji ketergantungan hasil pada stage degradasi.
- Mengevaluasi kualitas posterior computation dan posterior predictive fit.
- Menilai sejauh mana hasil dapat digeneralisasikan dalam batas dataset simulasi.

## 4. Research Questions

**RQ1:** Apakah model Bayesian menghasilkan 90% predictive intervals dengan mean interval score lebih baik daripada comparator probabilistik terkalibrasi?

**RQ2:** Seberapa besar perbedaan empirical coverage dan nominal coverage pada model-model yang dibandingkan?

**RQ3:** Bagaimana kualitas predictive uncertainty berubah terhadap observed age dan predicted degradation stage?

**RQ4:** Seberapa sensitif posterior predictive uncertainty terhadap spesifikasi prior dan distribusi error?

**RQ5:** Apakah kualitas inferensi berubah secara material ketika within-engine dependence ditangani secara eksplisit?

## 5. Hypothesis Framework

### Primary Confirmatory Hypothesis

Definisikan D sebagai expected difference in 90% interval score antara model Bayesian dan primary calibrated comparator, dihitung untuk target population yang telah ditentukan.

- H0: D ≥ 0 (Bayesian tidak mempunyai interval score lebih baik).
- H1: D < 0 (Bayesian mempunyai interval score lebih baik).

Lower interval score menunjukkan kualitas lebih baik.

Hypothesis direction ini merupakan usulan yang harus ditinjau SOL dan dikunci sebelum confirmatory evaluation. Keputusan akhir harus didasarkan pada effect size, uncertainty interval, dan practical significance, tidak semata-mata p-value.

### Secondary Hypotheses

Analisis calibration gap, point errors, prior sensitivity, dan subgroup performance diperlakukan sebagai secondary atau exploratory, kecuali secara eksplisit dipra-spesifikasikan sebagai confirmatory dengan multiplicity control.

Tidak semua research questions diwajibkan mempunyai directional hypothesis.

## 6. Dataset Specification

**Primary Source:** NASA Prognostics Center of Excellence Data Repository.

**Dataset Family:** C-MAPSS Turbofan Engine Degradation Simulation.

### Primary Study Population

FD001:

- 100 training trajectories.
- 100 testing trajectories.
- Single operating condition.
- Single high-pressure-compressor degradation mode.

Data meliputi engine identifier, operating cycle, tiga operational settings, dan 21 sensor measurements.

Training trajectories mencakup operasi sampai failure, sedangkan official testing trajectories berhenti sebelum failure dan mempunyai target RUL yang disediakan secara terpisah.

### Dataset Extension

FD003 dapat dipertimbangkan sebagai secondary robustness dataset karena mempunyai dua mode degradasi. Ekstensi hanya dilaksanakan setelah primary analysis dibekukan dan kelayakannya disetujui.

Tidak boleh memperlakukan FD003 sebagai validasi terhadap mesin nyata.

## 7. Mathematical Problem Formulation

Untuk engine i pada cycle t:

- T_i = cycle terjadinya failure.
- R_i(t) = T_i − t, dengan syarat mesin masih beroperasi pada t.
- H_i(t) = observed sensor and operating history sampai cycle t.
- θ = model parameters.

Target predictive quantity:

p(R_i(t) | H_i(t), T_i > t, D_train)

Prediction intervals harus dibangun dari distribusi predictive untuk engine baru, bukan hanya ketidakpastian posterior suatu parameter.

Parameter uncertainty dan predictive uncertainty wajib dibedakan.

Jika model menggunakan engine-specific latent effects, prediction untuk unseen engine harus mengintegrasikan ketidakpastian latent effect tersebut tanpa menggunakan future RUL labels.

### Mathematical Modeling Priority

Kandidat principal method:

**Bayesian Hierarchical Probabilistic RUL Model**

Spesifikasi final harus ditentukan setelah identifiability, dataset structure, dan computational feasibility review.

Pilihan implementasi dapat berupa hierarchical log-RUL regression dengan struktur dependence yang eksplisit, atau alternatif time-to-event formulation yang koheren terhadap survival conditioning.

Pemilihan likelihood, link function, error distribution, random effects, dan prior merupakan tanggung jawab langsung SOL.

Tidak boleh menyamakan ordinary regression on overlapping windows dengan valid survival inference tanpa membuktikan kecocokan likelihood dan struktur dependensinya.

## 8. Comparator Framework

Model family yang diusulkan:

| Model | Function |
|---|---|
| Simple probabilistic reference | Interpretability dan minimum benchmark |
| Quantile regression + conformal calibration | Primary calibrated comparator |
| Bayesian probabilistic model | Principal research model |
| Bayesian model + post-hoc calibration | Calibration ablation, bila feasible |

Primary comparison harus menggunakan evaluation cases yang identik.

Training, tuning, dan calibration information harus dipisahkan secara benar.

Comparator dan hyperparameter budgets harus cukup adil untuk menghasilkan interpretasi yang valid.

## 9. Experimental Design

### Splitting Principle

- Pembagian dilakukan berdasarkan engine identity, bukan random sensor rows.
- Official NASA test set diproteksi sebagai final held-out evidence.
- Training units dibagi menjadi fitting, tuning/validation, dan calibration units sesuai protokol yang dikunci.
- Per-engine data windows hanya boleh menggunakan informasi sampai prediction time.
- Test labels tidak boleh memengaruhi model selection, prior selection, preprocessing, atau calibration policy.

### Prediction Protocol

Primary evaluation mengikuti official test cutoff: satu prediction target per held-out engine.

Repeated within-engine forecast analysis dapat dilakukan pada development trajectories untuk mengevaluasi temporal behavior, tetapi harus menggunakan evaluation design terpisah yang menghormati dependence.

Jika study design menggunakan multiple landmarks per engine, jumlah landmark, selection rule, weighting, dan unit inferensi harus dipra-spesifikasikan.

### Sample Precision

SOL wajib menghitung uncertainty dan attainable precision berdasarkan jumlah independent engine units, bukan total sensor rows.

Jika statistical precision tidak memadai untuk klaim superioritas, penelitian harus menurunkan kekuatan klaim menjadi comparative evidence atau feasibility study.

## 10. Primary Statistical Endpoint

**Mean 90% Prediction Interval Score**

Primary metric harus mempertimbangkan:

- Lebar predictive interval.
- Penalti ketika actual RUL berada di bawah lower bound.
- Penalti ketika actual RUL berada di atas upper bound.

Primary comparator dan alpha = 0.10 ditentukan sebelum final testing.

### Secondary Metrics

- Empirical Prediction Interval Coverage Probability (PICP).
- Coverage gap terhadap nominal 90%.
- Mean Prediction Interval Width (MPIW).
- RMSE dan MAE untuk point predictions.
- Optional CRPS jika seluruh model menyediakan predictive distributions yang dapat dibandingkan.
- Lower-tail risk diagnostics untuk RUL overestimation.
- Bayesian posterior predictive checks.

Point metrics tidak boleh digunakan menggantikan primary probabilistic endpoint setelah melihat hasil.

## 11. Statistical Inference Plan

- Primary test set dianalisis pada level engine.
- Difference in interval score dievaluasi secara paired.
- Uncertainty estimation menggunakan engine-level resampling atau metode dependence-aware yang setara.
- Effect size dan confidence interval harus dilaporkan.
- Statistical testing harus mematuhi predeclared hypothesis dan multiplicity policy.
- Subgroup comparisons diperlakukan exploratory jika jumlah engine tidak cukup.
- Practical significance harus dibedakan dari statistical significance.

Untuk hasil Bayesian, posterior credible intervals dan frequentist empirical coverage harus dibahas dengan definisi yang benar.

## 12. Bayesian Model Diagnostics

Minimal:

- Multiple independent MCMC chains.
- Rank-normalized R-hat diagnostics.
- Bulk dan tail effective sample size.
- Divergence dan sampler efficiency diagnostics.
- Prior predictive checks.
- Posterior predictive checks.
- Sensitivity to prior specification.
- Posterior geometry dan identifiability assessment bila diperlukan.

Acceptance threshold untuk diagnostics harus ditentukan SOL pada protocol stage.

Model dengan posterior sampling yang tidak dapat dipercaya tidak boleh dipakai untuk mendukung klaim inferensial final.

## 13. Robustness and Sensitivity

Prioritas:

1. Alternative defensible prior specifications.
2. Alternative likelihood/error assumptions.
3. Model calibration versus uncalibrated predictions.
4. Limited feature-set sensitivity.
5. Prediction-stage heterogeneity.
6. Optional independent FD003 analysis.

Semua analisis robustness harus mempunyai tujuan jelas dan tidak boleh menjadi pencarian hasil yang menguntungkan.

## 14. Proposed Computational Stack

**Core:** Python, NumPy, SciPy, pandas.

**Bayesian Inference:** PyMC, ArviZ.

**Statistical Models:** statsmodels, scikit-learn.

**Probabilistic Comparators:** Quantile regression dan library conformal yang diverifikasi kesesuaiannya.

**Testing:** pytest, numerical unit tests, synthetic statistical tests.

**Visualization:** Matplotlib dan library plotting ilmiah yang sesuai.

**Reproducibility:** Git, lockfile atau pinned dependencies, environment manifest, experiment configurations, deterministic seeds where applicable.

Dependency versions wajib dikunci setelah environment feasibility review.

## 15. Expected Scientific Contributions

Potensi kontribusi:

- Comparative evidence mengenai kalibrasi Bayesian RUL predictive intervals.
- Quantitative trade-off antara coverage, sharpness, dan point accuracy.
- Dependency-aware evaluation pada engine-level prognostics.
- Mathematical dan computational audit terhadap Bayesian uncertainty estimates.
- Reproducible statistical evaluation framework bagi C-MAPSS.

Kontribusi tersebut merupakan target penelitian, bukan hasil yang sudah terbukti.

Publication novelty harus dikonfirmasi melalui prior-art review.

## 16. Threats to Validity

Risiko utama:

- Synthetic-to-real domain gap.
- Keterbatasan jumlah independent engine units.
- Temporal dependence dan pseudo-replication.
- Label atau future-information leakage.
- Informative selection of prediction landmarks.
- Misspecified likelihood.
- Weakly identifiable hierarchical effects.
- Prior sensitivity.
- Inaccurate posterior computation.
- Calibration-set scarcity.
- Adaptive reuse of the held-out test set.
- Limited transportability antar fault modes dan operating conditions.

Seluruh risiko harus memperoleh mitigation atau documented residual risk.

## 17. Expected Research Outcome

Hasil akhir berupa paper ilmiah yang menjelaskan:

1. Apa pertanyaan yang diuji.
2. Bagaimana probabilistic models didefinisikan.
3. Bagaimana inferensi Bayesian dilakukan dan diperiksa.
4. Bagaimana uncertainty dinilai secara empiris.
5. Apa hasil perbandingan beserta uncertainty-nya.
6. Apa yang didukung dan tidak didukung oleh bukti.
7. Di mana model gagal.
8. Seberapa jauh temuan dapat digeneralisasikan.

Penelitian tetap sah ketika Bayesian modeling tidak menunjukkan superioritas, sepanjang evaluasinya valid.

## 18. Immediate Instructions to Research Lead

Sebelum implementasi model, SOL Extra High harus menyerahkan:

- Literature Gap & Novelty Review.
- Dataset Feasibility and Sample Precision Assessment.
- Candidate Mathematical Model Specification.
- Statistical Analysis Plan.
- Fair Comparator Design.
- Proposed Protocol Lock.
- Compute Feasibility Estimate.
- Material Risks, Assumptions, and Decisions Required.

Tidak ada confirmatory experiment yang boleh dimulai sebelum protokol disetujui.

### 19. Local Project Workspace & Directory Standard

**Instruction to AI Lead Research (GPT 6.1 SOL Extra High)**

Sebelum memulai research execution, delegasikan pembuatan folder proyek kepada GPT 6 LUNA MAX pada direktori induk berikut:

`C:\Coding\Project\NAOBI RESEARCH`

**Required project directory:**

`C:\Coding\Project\NAOBI RESEARCH\RP-001_Bayesian_RUL_Reliability`

Buat struktur awal:

```text
RP-001_Bayesian_RUL_Reliability/
├── docs/
├── literature/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── src/
├── notebooks/
├── configs/
├── experiments/
├── results/
├── figures/
├── tests/
├── manuscript/
├── logs/
├── README.md
├── pyproject.toml
└── .gitignore
```

**Mandatory requirements:**

1. Semua pekerjaan dan research artifacts disimpan di dalam direktori proyek ini.
2. Jangan mengubah atau menghapus proyek lain di parent directory.
3. Periksa keberadaan folder sebelum membuatnya. Jangan menimpa file yang sudah ada tanpa pemeriksaan.
4. Gunakan relative paths dalam kode untuk meningkatkan reproducibility.
5. Gunakan Git untuk version control, dengan pengaturan `.gitignore` yang tepat untuk data, secrets, cache, dan large artifacts.
6. Dokumentasikan environment, dependencies, dataset provenance, dan execution instructions.
7. AI Lead wajib memverifikasi folder structure sebelum menyetujui dimulainya penelitian.

**Execution:** Pada fase Project Initialization (G0), setelah handoff kepada research team.

---

**Scientific Position:** Evaluate whether Bayesian predictive uncertainty is empirically trustworthy; do not presume that it is.

**Proposal Status:** Pending Research Lead Technical Review and Research Owner Approval.