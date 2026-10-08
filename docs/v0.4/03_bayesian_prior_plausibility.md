# Bayesian prior plausibility report v0.4

The principal anchored_v04 policy was committed before any new scientific predictions. Its development change follows v0.3 calibration exposure and is explicitly adaptive; it was not selected by new calibration scores. The broader and noise policies are robustness diagnostics, never a winner search.

## Working scale policy and elicitation limits

beta=[intercept,log-age effect] has mean[log100,0] and SD[.6,.5]. At zero latent contribution, beta0 alone has median95% range about31–324cycles. The100-cycle center represents a hundreds-of-cycles engineering scale, consistent with the prior project convention and training lifetime128–362cycle scale; it does not identify a population RUL median. Age is dimensionless log(C/100); SD.5 allows meaningful directionally symmetric age effects without treating age as causal.

Each of the two Gamma rows uses the same independent intercept/age-coefficient SD vector [.5,.35] expresses moderate PC-level/per30cycle-slope changes with age. tau half-normal.35 describes between-engine random level/slope scales in a unit-PC representation. gamma SD.25 expresses logR coupling to those nuisance latent coordinates and permits either sign. sigma_z half-normal.4 describes standardized sensor residual scale; sigma_r half-normal.4 represents multiplicative response noise on logR. These scales are proper regularizing assumptions, not physical support limits or expert-certified reliability priors. No latent state has a physiological interpretation.

rho=tanh(N(0,.75²)) permits positive/negative residual autocorrelation with no exact boundary mass. LKJeta2 in dimension2 is2Beta(2,2)-1, a symmetric proper latent correlation policy with variance.2. Correlation priors stay fixed under the1.5× broad sensitivity, which broadens beta/gamma/Gamma/tau/sigma_z/sigma_r scale priors. High-rho and confounding stress regimes challenge inference beyond typical prior central mass. Full domain elicitation remains absent; this is defensible only as a transparent benchmark-model working policy.

## Actual prior predictive distribution

12,000 draws per fixed policy use roots49001–49003, ages30/100/250, independent latent and residual draws. Marginal logR is a product/mixture distribution; its tails are simulated, not inferred from a Gaussian variance shortcut. The lead-derived analytic log variance supplies an independent moment oracle. Finite Monte Carlo fluctuations are retained; the table is an assessment of scale, not a hard accept/reject support bound.

| Policy | age | R95 | R99 | P R>1000 | P R>5000 | empirical Var logR | analytic Var logR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| anchored_v04 | 30 | 497.045817 | 1035.116742 | 0.010500 | 0.000167 | 0.953880 | 0.951146 |
| anchored_v04 | 100 | 342.933271 | 627.058677 | 0.001917 | 0.000000 | 0.566657 | 0.566563 |
| anchored_v04 | 250 | 438.040762 | 825.659655 | 0.006167 | 0.000000 | 0.771782 | 0.789316 |
| broader1p5 | 30 | 1221.472739 | 3642.819393 | 0.064250 | 0.005833 | 2.359487 | 2.333463 |
| broader1p5 | 100 | 681.862843 | 1719.163009 | 0.025167 | 0.001417 | 1.386116 | 1.405723 |
| broader1p5 | 250 | 986.299208 | 2753.443896 | 0.049250 | 0.003333 | 1.929971 | 1.943076 |
| historical_v03 | 30 | 1528.076045 | 5576.486066 | 0.082500 | 0.011417 | 2.810291 | 2.871566 |
| historical_v03 | 100 | 968.310531 | 2791.892900 | 0.047083 | 0.003583 | 1.879429 | 1.875000 |
| historical_v03 | 250 | 1345.791012 | 4819.471595 | 0.072417 | 0.009667 | 2.478503 | 2.452217 |

The prior still places mass on RUL outside the training lifetime range; RUL positivity is structural, whereas an upper bound is not. A narrower principal prior does not establish that its intervals are calibrated or superior. The historical broader tails are shown for comparison without erasing the earlier lack of elicitation.

## Data information and parameter coupling

The following information assessment uses the first principal fit and compares posterior SD with the same principal prior SD. It is not a measure of causal identifiability, and ratios near1 can signal weak information; ratios above1 can also reflect posterior geometry or prior-data conflict. Correlations and all per-run contraction records are retained.

| coordinate | prior SD | posterior SD | ratio |
| --- | --- | --- | --- |
| beta[0] | 0.601622 | 0.074872 | 0.124450 |
| beta[1] | 0.495398 | 0.111354 | 0.224776 |
| gamma[0] | 0.250341 | 0.053517 | 0.213778 |
| gamma[1] | 0.249764 | 0.131614 | 0.526952 |
| Gamma[0] | 0.502120 | 0.126891 | 0.252710 |
| Gamma[1] | 0.354093 | 0.211654 | 0.597738 |
| Gamma[2] | 0.503669 | 0.061225 | 0.121558 |
| Gamma[3] | 0.348784 | 0.114836 | 0.329246 |
| tau[0] | 0.214413 | 0.086771 | 0.404692 |
| tau[1] | 0.212634 | 0.045996 | 0.216316 |
| r_g[0] | 0.444550 | 0.108626 | 0.244350 |
| sigma_z[0] | 0.244647 | 0.004829 | 0.019737 |
| sigma_r[0] | 0.240529 | 0.045508 | 0.189199 |
| rho[0] | 0.540512 | 0.026488 | 0.049005 |

Largest posterior couplings: beta[0] ↔ gamma[1] (-0.657196), gamma[1] ↔ sigma_r[0] (0.502914), gamma[0] ↔ gamma[1] (-0.477906), Gamma[0] ↔ Gamma[2] (0.434600), beta[1] ↔ gamma[0] (-0.413310). Assess those alongside repeated recovery and the structural/practical distinction in report04. The model's predictive distribution may be more informed than individual nuisance parameters; this does not authorize interpreting weak parameters as physical health effects.

## Prespecified sensitivity

The fixed broader/rho0/contamination runs retain their own convergence, predictive maps and all failures. Compare endpoint changes descriptively without using the original25 calibration RULs to select a prior. Bayesian+posthoc calibration is secondary and exploratory. Numerical precision of these smaller sensitivity fits is not automatically the principal96,000-draw precision; small differences cannot be interpreted as scientifically resolved effects.

Evidence: [full prior checks](../../experiments/v0.4/analysis/prior_predictive.json), [information and coupling](../../experiments/v0.4/analysis/v04_main_r1_checks.json), [prediction sensitivity](../../experiments/v0.4/analysis/sensitivity_prediction_maps.json), [frozen policy](../../configs/v0.4/remediation_plan.json).

