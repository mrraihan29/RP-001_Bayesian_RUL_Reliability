# Fair Comparator Design v0.2

Status: DRAFT. Comparison adalah end-to-end probabilistic pipelines. Perbedaan Bayesian versus comparator tidak mengisolasi inferential philosophy saja; representation dan model structure juga berbeda.

## Common information dan data budgets

Semua families memakai engine namespaces, cutoff, uncapped target, age, dan causal history identik. Shared PCA/scaler fitted dari fitting prefixes saja, lalu refit pada fitting+tuning ketika selection selesai. Principal representation satu PC; PCA2 limited sensitivity exploratory. Primary test tidak dipakai memilih channel, feature, model, atau prior.

Shared input: age dan last min(30,c) PC sequence. Bayesian memakai sensor likelihood sequence. Comparator mempunyai deterministic summaries: endpoint score, OLS-estimated level pada cutoff, OLS slope per 30 cycles, residual SD, log(c/100). Direct sequence features untuk CQR linear candidates tersedia sebagai alternative representation. Tidak ada label engine ID feature, true lifetime feature, bidirectional future filtering, atau centered smoother yang mengintip future readings.

## Families dan selection

| Family | Specification | Role / selection |
|---|---|---|
| Reference | Gaussian log-RUL regression pada shared summaries, predictive interval dengan observation residual dan parameter uncertainty | Simple probabilistic reference; belum calibrated |
| CQR | Quantile regressors τ=0,05/0,95 plus split calibration pada cycles | Primary comparator |
| Bayesian principal | Model docs/03, fixed priors dan sensor-only new-engine prediction | Primary principal; no post-hoc calibration |
| Bayesian+CQR-style calibration | Fixed Bayesian raw quantiles conformalized | Exploratory calibration ablation |
| Matched Gaussian plugin | Same hierarchical sensor/response equations with likelihood fit + parametric uncertainty bootstrap | Optional mechanism diagnostic, bila identifiability/compute feasible |

Reference tidak boleh mengutip parameter CI sebagai prediction interval. Lognormal regression harus propagate residual uncertainty dan transform predictive quantiles; point forecast median, bukan exp(mean y) yang disebut predictive mean.

CQR candidate budget: delapan gradient-boosting quantile configurations pada summary inputs: depth∈{1,2}, min_leaf∈{5,10}, learning_rate∈{0,03;0,10}, 200 estimators. Empat L1-regularized linear quantile configurations pada standardized full sequence+age, penalty∈{0,001;0,01;0,1;1}. Full-sequence linear candidate menggunakan fixed 30-cycle window untuk development eligible; short test history diatasi oleh predeclared feature interpolation within observed history, tanpa future synthesis. Interpolation tidak memperpanjang c atau memberi future data. Principal partial-history strategy tetap likelihood native.

Tiap configuration merupakan dua quantile fits; seed tetap; sorted raw lower/upper values mencegah crossing sebelum scoring/calibration. Pilih configuration dengan lowest uncalibrated 90% interval score pada 13 tuning engines. Tie dalam 0,5 cycle: pilih linear lalu complexity lebih kecil; failure/timeout dicatat sebagai failed candidate, tidak diganti dengan extra favorable trial. Hasil 13 engines mempunyai high selection noise; repeated group-CV di fit adalah optional development sensitivity, tidak mengubah selector tanpa recorded pre-lock revision.

Bayesian principal satu model dengan fixed priors; prior variants bukan search untuk memilih favorable winner. Fairness tidak berarti jumlah fits sama: comparator mendapat tuning terstruktur yang cukup, Bayesian mendapat inference reliability budget. Jika target adalah kontribusi Bayesian inference murni, matched Gaussian diagnostic wajib, dan scope primary berubah melalui owner-approved revision.

Setelah selection, fit selected methods pada 56 fit+tune eligible engines. Semua common preprocessing diulang hanya pada cohort itu. Calibration 25 engines masih reserved. Setiap global θ sensor update untuk calibration/test engines mengikuti policy yang identik dan tidak melihat RUL.

## Calibration contract

Dari fixed raw cycle endpoints qL(x),qU(x), compute satu score per calibration engine:

s_i=max(qL(x_i)−r_i, r_i−qU(x_i)).
k=ceil((n_cal+1)×0,90); q_raw=s_(k); q=max(0,q_raw).
C(x)=[max(0,qL(x)−q), max(0,qU(x)+q)].

Nonnegative correction adalah conservative nonshrinking CQR variant yang dipilih untuk ordered positive intervals. Laporkan variant tersebut; jangan sebut persis shrinking original CQR. Support projection [0,∞) benar hanya karena target nonnegative. Tidak cap upper bound atau actual labels. Pada n_cal<9, order statistic finite tidak tersedia; use infinite interval mathematically atau stop comparator feasibility, bukan interpolate quantile diam-diam. Proposed study minimum n_cal19, observed eligible25.

Calibration layer di-estimate sekali; tidak memilih score function, alpha, subgroup weights, normalizer, or recalibration rule dari calibration losses. Post-hoc Bayesian ablation memakai calibration units sama, tetapi tidak memperoleh confirmatory comparator-selection status. Bootstrap primary mempertahankan layer fixed.

CQR theorem mensyaratkan exchangeable engine-level landmark pairs; cutoff-distribution mismatch belum diselesaikan. Karena itu report empirical official-test coverage; jangan menjanjikan distribution-free conditional stage coverage atau simultaneous trajectory coverage. Ties, nonshrinking correction, dan finite rank dapat menyebabkan overcoverage.

## Validation dan failure accounting

Before freeze: check quantile crossing, support, exact order-statistic index, preprocessing scope, short history behavior, every engine's cutoff, posterior predictive construction, dan train/cal separation. Check baseline performance pada development termasuk chance that simple reference dominates; model tidak disembunyikan hanya karena menang terhadap principal.

Track time, effective fits, preprocessing info, calibration access, and failures untuk setiap family. Optional deep models perlu research question tambahan/compute amendment; Colab Pro tidak menjadi alasan memperbesar architecture tanpa evidence.

Guarantee yang dipakai berasal dari [S05 Theorem 1](https://arxiv.org/pdf/1905.03222), dengan limits dari [S07](https://arxiv.org/html/2202.13415v5). Tidak mengklaim CP mengidentifikasi aleatoric uncertainty terpisah dari epistemic uncertainty.
