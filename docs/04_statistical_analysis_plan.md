# Statistical Analysis Plan v0.2

Status: DRAFT; owner approval dan validated numerical preflight diperlukan sebelum lock. Interval nominal α_PI=0,10 dibedakan dari α_test=0,05.

## Estimand dan primary endpoint

Satu official endpoint per test engine i=1,...,100. Freeze fitted pipelines A_B dan A_C, termasuk training split, representation, priors, fitting, sensor-only unseen-engine inference, dan calibration layer. Untuk intervals [L_ji,U_ji] dan uncapped target r_i:

IS_0.10(L,U;r)=(U-L)+20(L-r)1{r<L}+20(r-U)1{r>U}.

Mean score engine-weighted. d_i=IS_B,i-IS_C,i; dbar=mean(d_i), cycles. Negative berarti Bayesian lower loss.

Finite-benchmark estimand D_100=dbar adalah descriptive quantity untuk 100 engines yang tersedia. Population counterpart D=E[d|frozen pipelines, FD001 engine generator, official cutoff mechanism] membutuhkan sampling/independence assumptions yang tidak sepenuhnya terverifikasi. Confidence interval tidak menyulap benchmark tetap menjadi random representative sample. Primary inference qualified sebagai engine-superpopulation approximation, conditional pada fitted pipelines.

Satu directional hypothesis proposed: H0:D≥0 vs H1:D<0. Primary null threshold zero. SESOI proposed 5 score-cycles digunakan hanya bila owner menerima sebagai decision scale; tidak otomatis healthcare/maintenance utility. Tidak ada equivalence/noninferiority claim.

## Inference procedure yang dikunci sebelum final evaluation

Paired engine bootstrap-t, B=20.000, seed 8102026. Resample 100 complete engine pairs with replacement. t_b*=(dbar_b*-dbar)/(s_b*/sqrt(100)); original se=s_d/sqrt(100).

Two-sided 95% CI: [dbar-q_0.975(t*)se, dbar-q_0.025(t*)se].
One-sided 95% upper bound: U_95=dbar-q_0.05(t*)se.
Evidence for directional superiority hanya bila U_95<0 dan inferential assumptions/diagnostics memadai. Report two-sided CI bersama one-sided bound, jangan menyamakan two-sided 95% CI dengan α=0,05 one-sided decision.

Optional bootstrap p-value=(1+sum(t_b*≤dbar/se))/(B_valid+1), approximate dan bukan exact randomization p-value. Tidak gunakan sign-flip permutation sebagai exact mean-null test; symmetry/exchangeability null tidak otomatis berlaku.

Pipeline tidak direfit dalam primary test bootstrap. Jadi CI mengukur held-out-engine uncertainty conditional pipeline, bukan general performance seluruh class Bayesian, training-set variability, atau prior-selection variability. Semua engines memakai training fit/calibration yang sama; conditioning ini harus dinyatakan.

Jika s_d=0, nonfinite losses, >1% zero-variance bootstrap replicates, atau materially unstable quantiles (pre-lock pilot akan menetapkan numerical tolerance): jangan pilih CI lain berdasarkan significance. Report descriptive difference, failure, diagnostic distribution, dan qualified uncertainty. Working stability rule: split bootstrap draws menjadi dua blocks10.000; jika relevant bound berbeda>max(0,5 cycles,10% CI width), perlu convergence-of-resampling review sebelum inferential decision. Pilot harus memverifikasi tolerance dan menetapkan final rule sebelum lock; tidak boleh memperluas B hanya untuk mengubah significance.

Mathematical design simulations sebelum lock harus mengecek normal/skew/contamination regimes dengan same estimator, n=100, dan type-I coverage. Bootstrap adalah approximate; extreme tails/influential engines dapat membatasi interpretasi. Student t CI dan percentile paired bootstrap adalah sensitivity, bukan alternative decision oracle.

## Practical interpretation

Report absolute difference, ratio of mean scores (secondary), distribution d_i, individual misses, dan sensitivity ke influential engines tanpa menghapusnya. “Statistical direction supported” terpisah dari practical improvement. Jika upper bound tidak negatif: superiority not established; bukan evidence of equivalence. Untuk approved SESOI δ, practical superiority memerlukan U_95<−δ. Tanpa approved δ, tidak gunakan practical-superiority label.

## Secondary outcomes dan tail orientation

- PICP dan signed gap=PICP−0,90; Wilson 95% interval per model.
- Mean width, MAE, RMSE, bias=mean(point forecast−R). Point forecast Bayesian/reference adalah predictive median; CQR adalah separately fitted τ=0,50 estimated conditional quantile (docs/05), tanpa conformal shift.
- Lower misses R<L; rate dan total lower penalty 20Σ(L-R)_+/n. Ini overestimation risk: engine dapat gagal lebih cepat dari lower predicted bound.
- Upper misses R>U; upper penalty 20Σ(R-U)_+/n.
- Median overestimation rate dan 95th percentile positive median error.
- Posterior predictive checks pada fit/tune; calibration response hanya untuk fixed score computation.
- CRPS tidak primary: CQR interval saja tidak menentukan distribution. Omit common CRPS kecuali ada full-distribution comparator yang dikunci.

Unconditional pooled PICP tidak membuktikan conditional calibration. Bayesian credible parameter interval tidak sama dengan posterior predictive interval atau frequentist empirical coverage.

## Stage, sensitivity, dan multiplicity

Only one confirmatory hypothesis. Semua baselines, calibrated Bayesian ablation, correlation ablation, prior variants, likelihood variants, FD003, dan stage analyses exploratory dengan effect sizes/intervals tanpa secondary confirmatory claims. Jangan memilih “winner” dari seluruh comparisons lalu memakai primary p-value.

Stage bins proposed pada observable age: <100, 100–199, ≥200; predicted median RUL <50, 50–99, ≥100 cycles, dengan classification menggunakan frozen age-only reference median yang sama untuk semua models. Ini observable prediction-time stratification; true-RUL bins hanya retrospective diagnostics. Bila n_bin<20, tampilkan counts dan descriptive results tanpa inferential subgroup claim. Bins tidak dipindahkan sesudah melihat test outcomes.

Development repeated forecasts tidak dicampur ke primary endpoint. Predefine cycles {50,100,150,200,250} bila alive; mean per engine dahulu, kemudian mean fleet, engine bootstrap dengan seluruh forecasts tetap bersama. RQ5 primary ablation tetap satu official endpoint, dan repeated-development analysis terpisah.

## Missing, failed models, dan stopping

No test-engine exclusions untuk memperbaiki metrics. Short histories memakai rule predefined. Tidak impute target atau menghapus extreme errors. Incomplete predictions/diagnostic failure berarti principal comparison unavailable, dilaporkan lengkap. Software bug boleh diperbaiki transparan; label exposure mengubah confirmatory status dan dicatat. Setelah single final evaluation, tidak memilih prior/calibration/features lagi. Tambahan dataset tidak menggantikan FD001 setelah unfavorable result.

Formulas diverifikasi menurut [S06 §6.2](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf); planning computation tersimpan dalam logs/sample_precision.json.
