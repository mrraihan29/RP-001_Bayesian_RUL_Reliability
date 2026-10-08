# Candidate Mathematical Model Specification v0.2

Status: proposal matematis principal; belum implemented/fitted. Scope: probabilistic prediction pada selected alive landmark, bukan generative survival model untuk seluruh lifespan.

## Target dan unit likelihood

Satu engine i menyediakan satu selected cutoff c_i<T_i, satu y_i=log(R_i(c_i)), dan satu ordered sequence sensor score z_i dari w_i=min(30,c_i) observed cycles terakhir. R_i=T_i-c_i>0. Tidak ada repeated y_i pada likelihood primary.

Target ideal p(R|H,T>c,D_fit) didekati p(R|z,a,T>c,S_C=1,D_fit) dengan a=(1,log(c/100)). S_C menandai sampled alive landmarks. Conditioning survival dipenuhi oleh definisi cohort/response; ini tidak mengestimasi hazard atau membuktikan transportability ke selection mechanism lain. Continuous lognormal adalah approximation terhadap integer cycles.

## Frozen observation representation

Drop channel dengan empirical SD≤10^-8 di allowed fitting prefixes. Standardize setiap retained sensor memakai equal-engine-weighted fitting mean/SD. PCA pada covariance yang juga equal-engine-weighted; retain tepat satu PC untuk principal model. Orient sign dengan largest-absolute loading positif; normalize PC score agar fit-weighted variance satu. Operational settings FD001 tidak dimodelkan sebagai latent operating modes.

PCA/scaling hanya memakai rows sampai predefined fitting cutoff, tidak full post-cutoff trajectories. PCA diperlakukan frozen plug-in representation; uncertainty preprocessing bukan fully Bayesian. Pilot memeriksa apakah PC1 berinformasi dan apakah PC2 sensitivity diperlukan. PCA bukan bukti adanya physical health state.

Age dan sequence yang sama tersedia bagi comparator. Bila c<30, pakai seluruh available history tanpa future padding; principal covariance menyesuaikan length. Tidak mengeluarkan short official test engines sesudah melihat performance.

## Hierarchical sensor + response model

Definisikan g_i=(h_i,v_i)' sebagai latent score level pada cutoff dan slope per 30 cycles. Baris B_ij=(1,(t_ij-c_i)/30).

g_i | a_i,θ ~ N_2(Γ a_i,Σ_g),
z_i | g_i,θ ~ N_w(B_i g_i,σ_z² K_ρ),
y_i | g_i,a_i,θ ~ N(a_i'β+γ'g_i,σ_r²),

dengan K_ρ[j,k]=ρ^|t_ij-t_ik|, -1<ρ<1. Sensor error, outcome residual, dan engine effects independen conditional θ. Engines independen conditional global parameters. AR(1) modelling adalah working assumption untuk dependence sensor setelah local linear trend.

Satu y menghindari pseudo-replication dari identity R(t+1)=R(t)-1. Tidak memakai independent RUL residual per overlapping window. Tidak mengklaim g_i adalah physical degradation state yang benar.

## Marginalization dan unseen-engine prediction

Gaussian latent effects dapat diintegrasikan analitis. Untuk training engine, joint (z_i,y_i) mempunyai mean:

m_z=B_iΓa_i,
m_y=a_i'β+γ'Γa_i,

dan covariance:

C_zz=B_iΣ_gB_i'+σ_z²K_ρ,
C_zy=B_iΣ_gγ,
C_yy=γ'Σ_gγ+σ_r².

Gunakan likelihood engine-joint, bukan array flattened univariate normals. Cholesky solves, tanpa explicit matrix inverse; float64. Model implementasi boleh memakai p(z_i|a_i,θ)p(y_i|z_i,a_i,θ), aljabar ekuivalen joint likelihood.

Untuk unseen engine hanya dengan sensor z_*:

μ_g=Γa_*+Σ_gB_*' C_zz^-1(z_*-B_*Γa_*),
V_g=Σ_g-Σ_gB_*'C_zz^-1B_*Σ_g.

Lalu y_*|z_*,a_*,θ ~ N(a_*'β+γ'μ_g, σ_r²+γ'V_gγ).
Integrasikan θ dengan posterior draws; draw residual dan engine uncertainty atau gunakan mixture CDF untuk quantiles. R_*=exp(y_*). Endpoints primary adalah predictive quantiles 0,05 dan 0,95 dari mixture distribusi, bukan average parameter quantiles atau interval β.

**Prediksi θ perlu mengikuti joint model:** jika sensor marginal untuk engine baru dianggap sebagai informasi tambahan tentang global θ, weight posterior training draws dengan p(z_*|a_*,θ) sebelum marginalization atau refit/update θ memakai sensors saja. Primary implementation memilih full joint sensor-only update per unseen engine; jangan diam-diam memakai fixed θ weights dan menyebutnya exact joint posterior predictive. Untuk efisiensi, stabilized raw importance weights dapat diuji pada pilot. Proposed floor ESS_weight=1/sum(w_norm²)≥1.000 untuk8.000 retained draws, dengan maximum normalized weight dan chain-specific disagreement dilaporkan. Weight ESS adalah degeneracy diagnostic, bukan pengganti MCMC ESS. Tails quantile MC error dinilai melalui chain/batch uncertainty, proposed≤0,5 cycle; exact sensor-update fits pada synthetic/development engines menjadi oracle. Threshold/method final dikunci setelah pilot. Bila weight collapse belum terselesaikan sebelum lock, gunakan validated exact per-engine update atau revisi principal; jangan mengklaim full conditioning dari fixed weights. Di antara test engines, prediction dilakukan sendiri-sendiri dari frozen training posterior; tidak memanfaatkan other test-engine sensors untuk transductive fitting.

Bila dipilih modular/cut predictive menggunakan θ~p(θ|D_fit) dengan fixed weights, tulis estimand model tersebut sebagai modular approximation dan bandingkan sensitivitasnya. Pilihan full versus modular adalah keputusan pre-lock, tidak sesudah test.

## Priors proposed, di standardized scale

- β_intercept ~ N(log(100),1); β_age ~ N(0,0,75).
- γ_level,γ_slope ~ N(0,0,5), independent.
- Γ intercept entries ~ N(0,1); Γ age entries ~ N(0,0,5).
- Σ_g = diag(τ) Ω diag(τ), τ_h,τ_v ~ HalfNormal(0,5); Ω~LKJ(η=2).
- σ_z~HalfNormal(0,5), σ_r~HalfNormal(0,5).
- η_ρ~N(0,0,75), ρ=tanh(η_ρ).

Angka ini working regularization, bukan domain-informed physical prior. Prior-predictive checks pada age 30/100/250 wajib memeriksa plausible RUL quantiles dan sensor trends menggunakan fitting-only/domain evidence. Sensitivity half/double scale dan LKJ(1/4) tercatat; tidak memilih prior dari test score.

Primary Gaussian residual log-RUL. Robustness proposed finite contamination-normal mixture pada log scale, fixed mixture weight 0,05 dan residual scale multiplier 3; specification changes dijadikan exploratory. Hindari exp(Student-t) tanpa mengakui tidak adanya finite predictive mean; log-Student-t punya exponential moments tak berhingga. Point prediction primary memakai predictive median.

## Identifiability dan acceptance

g scale di-anchor pada observed PCA units dan B. Seluruh engine hanya satu y, sehingga outcome random intercept tambahan tidak teridentifikasi terpisah dari σ_r dan dilarang. Σ_g versus σ_z/ρ bisa confounded pada histories pendek; γ versus weak score signal bisa prior-dominated.

Sebelum principal diterima: prior checks; numerical covariance identity; synthetic recovery pada regime ρ=0/0,5/0,9 dan weak/strong slopes; parameter posterior contraction yang relevan; predictive recovery; stability terhadap prior; posterior correlations/boundary fits. Limited recovery tidak otomatis membuktikan global identifiability. Jika marginal covariance ill-conditioned, simplifikasi sebelum test; jitter numerical≤10^-8 pada standardized diagonal dicatat dan sensitivitas diperiksa.

MCMC proposed: 4 independent chains, 1.000 warmup+2.000 retained draws/chain; target_accept 0,95; max_treedepth 12. Require rank/folded R-hat<1,01, bulk/tail ESS≥400 bagi global parameters dan relevant predictive quantities, zero divergences, no persistent saturation, E-BFMI>0,3 heuristic, dan predictive quantile MC error yang kecil. ESS floor tidak mengganti precision check. Maksimal dua documented computational repairs sebelum principal dinyatakan unavailable; tidak melanjutkan claim dengan posterior unreliable.

RQ5 ablation: ρ=0 dengan priors/data/engine effects sama. Ini menguji sensor correlation contribution, bukan general claim semua dependence sudah teratasi. Repeated forecast diagnostics development-only memakai equal-engine weighting dan cluster resampling.

Alternative yang lebih sederhana: nonhierarchical lognormal landmark regression pada age, OLS score level/slope, dengan one outcome per engine. Alternative survival/state-space first-passage model membutuhkan generative degradation dan failure mechanism baru; deferred, bukan automatic upgrade.

[S09 diagnostics](https://sites.stat.columbia.edu/gelman/research/published/Vehtari_etal_2020_rhat_ess.pdf), [PyMC posterior predictive semantics](https://www.pymc.io/projects/docs/en/stable/api/generated/pymc.sample_posterior_predictive.html).
