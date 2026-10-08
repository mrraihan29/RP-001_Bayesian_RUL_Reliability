# RP-001 v0.4 precision worker contract

This module estimates Monte Carlo uncertainty for the sensor-only, self-normalized importance-weighted posterior predictive quantile. For each supplied chain and draw, conditional log RUL is Gaussian with mean mu_ct and variance v_ct; the target is the quantile of the weighted mixture CDF. It solves that CDF directly and reports the log-RUL quantile plus its exponentiated RUL value. It does not average draw-level quantiles.

For a target probability p, log-RUL quantile q, and globally max-scaled importance weights w_ct, the influence sequence is

h_ct = w_ct * [F_ct(q) - p].

At each requested batch size, chain-specific long-run variance is estimated from non-overlapping batch means. The log-scale variance estimator is

sum_c n_c * LRV_c / (N^2 * mean(w)^2 * f(q)^2),

where f(q) is the normalized weighted mixture density on log RUL. The exponentiated quantile delta-method MCSE is exp(q) times the log-scale MCSE. Weight ESS is reported separately from influence/autocorrelation ESS.

The per-chain batch-mean variance uses K_c - 1 degrees of freedom for K_c complete batches. Its estimated contribution to quantile variance is combined with the Satterthwaite approximation

df = V^2 / sum_c(V_c^2 / df_c).

For caller-supplied lower-tail probability alpha, the approximate upper variance is V * df / chi2.ppf(alpha, df), giving an approximate upper MCSE with nominal level 1-alpha. The caller must provide tail_probability; no acceptance threshold or gate is embedded in the helper. The first of two batch sizes supplies the primary estimate and both are included in an explicit stability comparison.

The normal model uses one component. The optional residual-contamination model follows the existing 95/5 parameterization: 0.95 N(mu, v) + 0.05 N(mu, v + 8*sigma_r^2), equivalent to a broad residual variance of 9*sigma_r^2 when v contains ordinary residual variance plus latent variance.

Assumptions: chains are independent, stationary, and ergodic for the base posterior; importance weights satisfy the moment conditions for a self-normalized ratio central limit theorem; the mixture density is positive and smooth at the quantile; enough complete batches are available; and the delta method is adequate at the supplied Monte Carlo size.

Limitations: batch-means long-run variance and the Satterthwaite chi-square upper MCSE are finite-sample approximations, not rigorous bounds. They may be inaccurate with few batches, poor mixing, nonstationarity, unstable weights, or low density at the target. Repeating the calculation with two batch sizes is a sensitivity diagnostic only. The result quantifies numerical integration error conditional on supplied chains and model; it does not address model/prior/data uncertainty, chain convergence, calibration, or prospective prediction performance.

Tests cover a conjugate Gaussian importance-sampling oracle, IID and AR(1) influence-series long-run variance scales, contamination-component variance, shape/domain validation, and finite output diagnostics. These are synthetic known-quantity unit checks, not a scientific simulation study or a replacement for a prospective v0.4 plan.
