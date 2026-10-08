# Identifiability and synthetic validation report v0.4

Structural identification is generically established under fixed full-rank age/basis, w>=6, positive sensor noise/covariance and |rho|<1; the direct lead proof and numerical covariance inversion are in report08. This says population moments uniquely determine model coordinates. It does not ensure accurate finite-sample estimates, good MCMC, prediction accuracy or interval coverage.

## Targeted repeated recovery

Four fixed-truth datasets per regime use56 training engines and20 independently generated assessment engines. Regimes:regularrho.5; highrho.95; weakgamma[-.03,.02]; confoundedrho.8 with stronger age-linked latent effects and sensor noise.6/response noise.15. Seeds and all arrays/truths are saved. Local integer IDs are namespaces within independent generated datasets, not reused physical engines or model covariates. No official data enter synthetic recovery.

| Regime | completed | MCMC pass | minimum coordinate recovery95 fraction | maximum standardized error | predictive covered/n |
| --- | --- | --- | --- | --- | --- |
| regular | 4 | 4 | 0.750000 | 2.576322 | 75/80 |
| high_rho | 4 | 3 | 0.750000 | 2.135404 | 76/80 |
| weak | 4 | 4 | 0.750000 | 2.451135 | 73/80 |
| confounded | 4 | 4 | 0.750000 | 2.899677 | 69/80 |

**High-rho acceptance caveat:** the 76/80 predictive tally and minimum 0.75 parameter-recovery fraction include `v04_syn_high_rho_3`, which failed physical and auxiliary convergence (maximum Rhat 1.013598). Its 18/20 predictive tally is diagnostic-only, not accepted posterior calibration or model-adequacy evidence. The aggregate is a retained raw diagnostic summary, not a successful four-fit validation. No failed fit was rerun, removed or replaced.

Recovery fractions use only four repeats per regime. Their Wilson intervals are broad (even4/4 has a lower95% limit around.51), so neither apparent95% agreement nor a miss certifies calibration or nonidentification. The reported maximum standardized error preserves poor cases. Every14-coordinate estimate/interval and parameter-coupling assessment is retained, including every prior/posterior SD ratio. Independent20-engine predictive checks integrate the full per-engine sensor update and report coverage/Wilson, median RMSE and mean interval score. Synthetic score values are model diagnostics, not evidence of Bayesian superiority over CQR or official benchmark performance; they still include finite MCMC approximation error.

## Practical identification and fallback

Second-difference covariance c2=sigma_z²(1-rho)^4 becomes tiny as rho approaches1; inversion is ill-conditioned. Small gamma, limited age spread, Gamma/beta/gamma coupling and nearly singular S can leave nuisance effects weakly informed even when sampling diagnostics pass. A compact model can support transparent benchmark predictions while remaining unsuitable for physical-state interpretation. Report uncertainty and coupling; do not equate posterior contraction or Rhat with identification.

SBC was considered but not performed. The bounded16-fit plan targets specified difficult fixed truths rather than prior-wide algorithmic calibration. Four repeats do not supply precise recovery coverage. A future SBC study would need a separately authorized plan and broader prior/parameter draws; this package makes no SBC claim.

The predeclared fallback fixesrho0 andr_g0 under anchored priors; it is not automatically fitted or substituted after these results. If principal prediction precision/model interpretation remains blocking, returnB/C for owner review before a new principal procedure. Fixed sensitivityrho0 alone is not evidence accepting that two-correlation fallback.

## Sampling evidence and posterior predictive checks

| Run | Rhat max | bulkESS min | tailESS min | diagnostic |
| --- | --- | --- | --- | --- |
| v04_main_r1 | 1.000331 | 16730.728554 | 18257.035307 | PASS |
| v04_main_r2 | 1.000410 | 19122.526775 | 20126.198462 | PASS |
| v04_main_r3 | 1.000248 | 17093.518135 | 19012.860652 | PASS |
| v04_oracle_e11 | 1.000246 | 34071.428112 | 39102.369783 | PASS |
| v04_oracle_e61 | 1.000195 | 39218.924582 | 42202.814592 | PASS |
| v04_oracle_e86 | 1.000094 | 34585.573066 | 38054.416454 | PASS |
| v04_broader | 1.001777 | 4188.407011 | 4518.124487 | PASS |
| v04_rho_zero | 1.001351 | 4628.399746 | 4948.910507 | PASS |
| v04_contamination | 1.000807 | 4272.210175 | 4939.083472 | PASS |
| v04_syn_regular_1 | 1.000717 | 5011.582769 | 3299.703864 | PASS |
| v04_syn_regular_2 | 1.001403 | 4215.704544 | 2872.436902 | PASS |
| v04_syn_regular_3 | 1.001343 | 2377.571308 | 1194.208122 | PASS |
| v04_syn_regular_4 | 1.002045 | 4029.592786 | 1931.232939 | PASS |
| v04_syn_high_rho_1 | 1.003812 | 573.266546 | 1318.300412 | PASS |
| v04_syn_high_rho_2 | 1.004809 | 669.925409 | 850.153036 | PASS |
| v04_syn_high_rho_3 | 1.013598 | 519.183093 | 690.169316 | FAIL |
| v04_syn_high_rho_4 | 1.005674 | 697.375768 | 947.834344 | PASS |
| v04_syn_weak_1 | 1.001846 | 5408.059950 | 3785.821475 | PASS |
| v04_syn_weak_2 | 1.002385 | 5320.875404 | 4923.455704 | PASS |
| v04_syn_weak_3 | 1.001604 | 5106.623938 | 4238.417083 | PASS |
| v04_syn_weak_4 | 1.001161 | 2585.145160 | 1401.739516 | PASS |
| v04_syn_confounded_1 | 1.001864 | 1081.270357 | 1571.286680 | PASS |
| v04_syn_confounded_2 | 1.006740 | 1486.851864 | 1675.937161 | PASS |
| v04_syn_confounded_3 | 1.003066 | 1604.527776 | 1931.525686 | PASS |
| v04_syn_confounded_4 | 1.003296 | 1660.116858 | 1923.894705 | PASS |
| v04_pipeline_1_canonical_infra1 | 1.001535 | 3080.694529 | 2653.525872 | PASS |
| v04_pipeline_1_alternate | 1.000528 | 3762.142527 | 4901.940003 | PASS |
| v04_pipeline_2_canonical_infra1 | 1.001061 | 4534.483582 | 4753.297209 | PASS |
| v04_pipeline_2_alternate | 1.001111 | 4564.274886 | 5061.702406 | PASS |
| v04_pipeline_3_canonical_infra1 | 1.002251 | 4465.218108 | 4524.236155 | PASS |
| v04_pipeline_3_alternate | 1.000818 | 2966.625013 | 4045.290308 | PASS |
| v04_pipeline_4_canonical_infra1 | 1.001472 | 3334.377334 | 4219.021444 | PASS |
| v04_pipeline_4_alternate | 1.000871 | 3116.870030 | 4150.696569 | PASS |

All convergence thresholds were set before the runs. Auxiliary variables gcor_u/eta_rho, divergences, BFMI and depth saturation are in each immutable run record. Posterior-predictive checks use1,000 parameter draws from principal fit1 and assess conditional response and joint sensor/response moments with seed51001. These are fitted-model checks, not external validity or independent calibration. Report every observed statistic and replicated quantile/tail area; a PPC discrepancy remains a modeling limitation, not a reason to tune on the calibration cohort.

The principal fitted-data PPC observed mean/log-RUL SD/90th percentile were 4.42746/0.77301/5.18172; conditional replica 95% ranges were [4.30083,4.55454]/[0.62280,0.86910]/[5.04766,5.52408], with tail areas 0.471/0.273/0.792. Observed sensor SD/end-minus-start were 1.12636/0.51530; joint replica 95% ranges were [0.81874,1.24930]/[0.29313,0.65044], with tail areas 0.178/0.323. No gross discrepancy appears in these selected summaries, but they do not validate omitted features, residual tails, transport or coverage.

Evidence: [summary and coordinate recovery](../../experiments/v0.4/analysis/summary.json), all `experiments/v0.4/analysis/v04_syn_*_checks.json`, [PPC](../../experiments/v0.4/analysis/posterior_predictive.json), exact synthetic NPZ/NC arrays and seeds in the run registry, [direct verification](08_independent_mathematical_reverification.md).

