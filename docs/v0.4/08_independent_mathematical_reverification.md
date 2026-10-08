# Independent mathematical re-verification — v0.4

Verifier: Rei / SOL lead. Worker implementations were inspected; their tests alone are not mathematical approval. This report records the lead's derivations and independent numerical oracles. Scope is synthetic and official FD001 training data only. The scientific status remains PROTOCOL_DRAFTED.

## Integrated likelihood and new-engine conditioning

Fix the fitted preprocessing, age vector a=(1,log(C/100)), and B=[1,t/30], t=-29,...,0. Let g~N(Gamma a,S), S=diag(tau) Omega diag(tau); z|g~N(Bg,sigma_z² K_rho); logR|g~N(a beta+gamma'g,sigma_r²). K has entries rho^|j-k|. Therefore Czz=B S B'+sigma_z²K, latent V=(S^-1+B'K^-1 B/sigma_z²)^-1 and latent conditional mean Gamma a+V B'K^-1(z-B Gamma a)/sigma_z². Predictive logR conditional on theta and z has mean a beta+gamma'm_g and variance sigma_r²+gamma'V gamma. The marginal sensor likelihood is the Gaussian N(B Gamma a,Czz). The joint log density factors into that likelihood and the conditional response density. AR whitening uses first row unchanged and subsequent differences divided by sqrt(1-rho²); determinant is sigma_z^(2w)(1-rho²)^(w-1) det(S) det(S^-1+J). The Woodbury quadratic subtracts b'Vb. All factors and dimensions were checked independently against dense covariance solves, including rho=.99.

A new engine's theta posterior is proportional to its sensor-only likelihood times the fitted training posterior. Each engine is updated separately: no response enters the weight and there is no pooled target-cohort update. Integrating conditional quantiles separately is incorrect; solve the weighted mixture CDF. Three oracle fits add just one engine's sensor likelihood to the joint training posterior; their logR predictions then integrate conditional distributions without weighting that sensor again. The oracle may reuse the same observed z to condition that engine's g; this is the conditional factorization, not double likelihood weighting of theta. The contamination alternative changes only response residuals: .95 N(0,sigma_r²)+.05 N(0,9sigma_r²). Its broad predictive component has variance gamma'V gamma+9sigma_r², not nine times the entire predictive variance.

## Generic structural identification, and its limits

This is an identification argument for the model's population joint moments under a fixed, known representation, not a guarantee about finite data or physical health. Require age design full column rank, B full column rank, w>=6, sigma_z>0, S positive definite and |rho|<1. E(z|a)=B Gamma a identifies Gamma using left inverses. Let D be the second-difference matrix, whose row coefficients are (1,-2,1). DB=0, so D Czz D'=sigma_z² D K_rho D'. For differences at lag h>=2 (lag2 shares one endpoint), its covariance is

    c_h = sigma_z² rho^(h-2) (1-rho)^4.

Thus c_2>0 and rho=c_3/c_2, including rho=0; sigma_z²=c_2/(1-rho)^4. Recover S=B⁺(Czz-sigma_z²K)B⁺'. Next Czy=B S gamma identifies gamma=S^-1 B⁺ Czy. The residual response variance is sigma_r²=Cyy-gamma'Sgamma. E(logR|a) identifies beta_total=beta+Gamma'gamma, hence beta=beta_total-Gamma'gamma. Known B and the fixed PCA sign/scale remove arbitrary latent rotations. Labels such as level and slope describe this parameterization; they are not causal or physiological states.

The lead numerically recovered covariance components and gamma at rho=-.5,0,.5,.9,.95,.99. This inversion exposes fragility: c_2 shrinks as (1-rho)^4, making high-rho recovery extremely sensitive to moment error. Weak gamma and finite age variation confound response effects and beta/Gamma couplings in finite samples. w<6 is outside this proof; short target windows can still be predicted under an identified fitted model, with weaker information. S near singular or sigma_z near zero are boundary cases not covered. Structural identification, practical precision, MCMC convergence, prediction accuracy and calibration are separate questions. Four fixed-truth repeats per regime provide targeted practical evidence; they are not SBC or a proof of frequentist coverage.

## Self-normalized weighted MCMC quantile error

For log-scale q_p, define F(q)=E_pi[w F_theta(q)]/E_pi[w], with w=p(z_new|theta) under the fitted posterior pi. At F(q_p)=p, linearization gives influence h=w(F_theta(q_p)-p); the normalizer fluctuation is included in this ratio influence. Arbitrary global weight scaling cancels. For independent stationary chains of length n_c, N=sum n_c, long-run variance v_c=sum_{k=-infinity}^{infinity} Cov(h_c0,h_ck),

    Var(qhat_log) ≈ sum_c n_c v_c / (N² mean(w)² f_log(q_p)²).

Estimate v_c=b Var(complete nonoverlapping batch means), using sample variance with ddof=1. Convert to cycles by exp(q_p), so MCSE_R=exp(q_p) sqrt(Var(qhat_log)). Density f_log is the weighted conditional normal-mixture density. The lead independently recomputed the variance from arrays and checked density by a central finite difference. Weight-only ESS=(sum w)²/sum w² ignores serial dependence. Influence ESS=Var_marginal(h)/Var(mean h) is quantity-specific, not an independent-engine count.

At each batch size, write each log-quantile variance contribution as V_c with d_c=(batch count-1). Approximate Satterthwaite degrees of freedom d=(sum V_c)²/sum(V_c²/d_c); upper variance=(sum V_c)d/chi²_alpha(d). alpha=.05/(25×3×2) covers a prospective collection of 150 approximate variance guards. It does **not** create a rigorous simultaneous finite-sample error bound: Gaussian independent batch behavior, consistent long-run variance estimation, ratio CLT, positive density and adequate mixing are assumptions; density and normalizer are themselves estimated. The two batch sizes 250/500, known correlated-chain targets, independent fits and joint-posterior oracles probe that approximation. The .5-cycle criterion is an upper-MCSE criterion, not a claim that absolute errors are below .5 in every result.

General MCMC quantile CLTs and variance estimation require dependence and regularity conditions; see [Doss et al., Markov Chain Monte Carlo Estimation of Quantiles](https://arxiv.org/pdf/1207.6432). Its sample-quantile theory is background, not a theorem automatically certifying this self-normalized smoothed-mixture estimator. The ratio/density derivation above is directly verified here. Known conjugate validation uses theta~N(0,1), sensor z=1 with variance1, giving theta|z~N(.5,.5); logR|theta~N(log100+.2theta,.09), hence marginal logR~N(log100+.1,.11). Exact quantiles follow by exponentiating its normal quantiles. AR(1) chains retain a stationary N(0,1) marginal and test serial correlations 0,.8,.95 independently of the prediction target.

## Prior moments and support

All proposed priors are proper. Half-normal scales exclude negative SDs, LKJ eta2 in dimension2 is r_g=2 Beta(2,2)-1 (mean0, variance1/5); rho=tanh(eta), eta~N(0,.75²), lies in (-1,1). Broadening leaves correlation priors unchanged. With independent zero-mean Gamma/gamma, symmetric r_g and age x=log(C/100), the lead derived

    E(logR)=log100,
    Var(logR)=b0²+b1²x²+2 s_gamma²(G0²+G1²x²+s_tau²)+s_sigma_r².

At sensor basis [1,t], Var(z)=(1+t²)(G0²+G1²x²+s_tau²)+s_sigma_z². Products and mixtures make marginal logR nonnormal; these moments do not justify Gaussian marginal tail approximations. Prior predictive simulation assesses its actual tails, including above1000/5000 cycles. The center100 is an engineering-scale anchor, not an empirical RUL population law or an externally validated elicitation. Its latent-zero beta intercept alone has median95% prior range exp(log100±1.96*.6)≈31..324 cycles. Changes after historical calibration exposure are disclosed; no new calibration interval-score ranking selects priors.

## Conformal rank, calibration precision and interval score

For nominal90%, k=ceil((n+1)*.9); n25 gives k24. Use the kth order statistic directly, no interpolated percentile; k>n entails an infinite correction. q=max(0,s_(k)) with score max(L-y,y-U) cannot shrink. Sort raw endpoints and project both calibrated endpoints onto nonnegative RUL support. Under exchangeability of fitted-procedure calibration and target scores, the usual marginal conformal statement applies; the pseudo-cutoff/official-endpoint transport assumption is unverified. [Romano, Patterson and Candès, Conformalized Quantile Regression](https://arxiv.org/abs/1905.03222) supplies the underlying CQR method. Under the stronger iid continuous score law conditional on a fixed fit, F(s_(k))~Beta(k,n+1-k). With k24,n25 its mean is24/26=.923077, SD=.051282; P(F(s24)<.9)=.271206. These are hypothetical calibration-cohort precision calculations, not official FD001 coverage.

IS90=(U-L)+20(L-y)1[y<L]+20(y-U)1[y>U]. For ordered endpoints its coordinate slopes are -1 or19 in L and1 or-19 in U, so |delta IS|<=19(|delta L|+|delta U|). This connects endpoint error to score sensitivity. MCSE is not an absolute error bound; .5 per endpoint does not establish a small score difference or a five-cycle practical margin. Future score error can be assessed by propagation of the joint quantile influence covariances and independent posterior fits; report it separately from any engine-population diagnostic. Current primary comparison is not executed.

## Estimand and inference

The future finite-benchmark mean of all paired stored-prediction scores is a deterministic enumerated contrast for that complete endpoint set. No engine-sampling SE is required to describe that finite set; posterior approximation error still matters. The secondary bootstrap-t pivot is (mean(D*)-mean(D))/[sd(D*)/sqrt(N)]. Its two-sided interval is [mean(D)-q_.975 SE, mean(D)-q_.025 SE]; one-sided upper uses q_.05. Missing/nonfinite scores, zero original SE or any zero/nonfinite bootstrap pivot suppress that diagnostic. No engine deletion or favorable fallback is allowed. Bootstrap conditional on a realized pipeline does not account for changing PCA, tuning, fitted parameters, calibration cohort or cutoffs. For a genuine stochastic pipeline P, Var(D)=E[Var(D|P)]+Var(E[D|P]); eight observed-data perturbations illustrate variation but do not estimate this unconditional law precisely. Bayesian parameter integration does not integrate every pipeline selection step. Finite benchmark, hypothetical superpopulation, conformal marginal coverage, conditional cohort coverage and external engine validity are distinct claims.

## Direct lead verdicts

These verdicts concern the equations/procedure within the stated scope. PASS does not approve protocol lock or model adequacy.

| Material mathematics | Direct lead verdict | Cross-check / limitation |
| --- | --- | --- |
| Integrated likelihood and hierarchical covariance | PASS | Dense Gaussian likelihood/conditional solves, AR determinant and covariance dimensions; working Gaussian/AR model |
| Sensor-only theta update and predictive mixture CDF | PASS | Ratio factorization, independent dense conditional values, three sensor-only oracles; target response absent |
| Quantile solution and self-normalized importance weighting | PASS | Exact conjugate target, density finite differences, independent fits; positive density and adequate importance support assumed |
| Quantile Monte Carlo uncertainty | PASS for prospective development diagnostic | Direct influence/LRV/delta derivation and 600 known-target replications; Satterthwaite upper guard remains approximate |
| Structural identifiability | PASS under explicit interior/full-rank assumptions | Second-difference inversion and numerical recovery; high-rho practical identification/sampling remains REVISE |
| Material prior moments/support | PASS as working-prior mathematics | Analytical variance and prior predictive simulation; domain elicitation remains unverified |
| CQR finite-sample rank correction | PASS | n25/k24 direct order statistic, support projection, hypothetical Beta precision; official exchangeability unproved |
| Finite-benchmark estimand and interval score | PASS | Enumeration, coordinate slope19 bound; no population superiority or practical margin |
| Secondary bootstrap-t and total-variance distinction | PASS for formulas/failure policy; REVISE broad validity claims | Direct pivot/variance derivation and retained stress outcomes; no nominal stress-domain or whole-pipeline certification |

## Evidence and decision boundary

Lead preflight: [19 tests passed](../../logs/v0.4/lead_preflight.xml), including independent dense/vectorized likelihood, covariance inversion, weighted MCSE/density, rank and interval-score derivative checks. Historical 36 tests and all prior mathematical evidence are retained. Numerical simulation, posterior fits and independent review must be read alongside this report; neither algebra nor schema validation alone establishes readiness. Final owner authorization remains required, and no official test data or confirmatory evaluation is authorized.