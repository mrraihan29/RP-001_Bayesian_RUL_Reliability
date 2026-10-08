# SOL direct mathematical validity assessment v0.5

**Scoped PASS.** Direct lead derivations and independent numerical oracles supplement LUNA's pure-array score implementation. This is model/implementation verification, not proof of scientific superiority, transported coverage, or total-pipeline uncertainty.

## Equivalent high-rho posterior

Let eta=atanh(rho), nu=sigma_z*sech(eta), sigma_z=nu*cosh(eta). For original independent HalfNormal scale prior f_sigma and Normal eta prior f_eta, the joint density in (nu, eta) is f_sigma(nu*cosh(eta))*cosh(eta)*f_eta(eta). The Jacobian is cosh(eta). Reference HalfNormal(nu) is canceled by the potential log f_sigma(sigma_z)-log f_reference(nu)+log cosh(eta). No extra innovation-scale prior is introduced.

In unconstrained coordinates s=log(sigma_z), u=log(nu), s=u+log cosh(eta). The triangular Jacobian has determinant1. The original transformed log posterior at s equals the new one at u. This reasoning also verifies that the positive-variable log transform must be included; omitting the scale/Jacobian terms would change the model.

The direct oracle constructs the full 31-dimensional marginal Gaussian of (z, logR) with Czz=B S B'+sigma_z^2 K, Czy=B S gamma, Cyy=sigma_r^2+gamma'S gamma; it uses dense Cholesky solves, not AR whitening/Woodbury. Independent Normal/HalfNormal/Beta densities and unconstrained Jacobians complete its joint log density. Both original and innovation automatic gradients are compared against this oracle's centered finite differences in two coordinates.

Frozen grid: rho .5/.95/.99/.999 x sigma_z .1/.3/.6, all other coordinates at exact failed-case truths; 12 density points/48 gradient coordinates. Tolerances: density1e-7+1e-8*abs(reference), gradient1e-4+1e-4*abs(reference), step 1e-5. All pass. Maximum density discrepancy against dense oracle **3.46975867e-07**; original versus equivalent posterior **1.16415322e-10**. Maximum raw gradient discrepancy **0.0404814444**, maximum discrepancy divided by its prespecified absolute-plus-relative tolerance **0.401717252**. The largest absolute gradient residual occurs on a large-gradient stress scale; the relative tolerance, not an absolute 1e-4 assertion, defines acceptance. No claim of universal float64 stability at the boundary |rho|=1 or for all possible data.

## Quantile-to-score influence, dependence, and sensitivity

Conditional on a fixed posterior, importance-mixture CDF is Fhat(q)=mean(w F_theta(q))/mean(w). Its linearized ratio influence at target probabilityp is w(F_theta(q)-p)/mean(w); implicit quantile differentiation divides by -f_log(q). Exponentiating multiplies by Q=exp(q). Thus X=-Q*w*(F_theta(q)-p)/(mean(w)*f_log(q)). Scaling weights by a common positive factor within engine leaves X unchanged.

IS90 is piecewise linear in its endpoints: partial_L=-1+20I[y<L], partial_U=1-20I[y>U]. At equality the derivative is not unique; the strict indicator branch is algebraic bookkeeping and the kink flag restricts delta-method interpretation. The finite-mean influence H is the aligned mean of these derivative-weighted endpoint influences. Never discard engine dependence induced by shared posterior draws.

For independent equal-length chains of length n and M total draws, joint batch covariance estimate Lambda_c gives Cov_MC=sum_c n*Lambda_c/M^2. Project by a=[g_L/N, g_U/N]. V=sum_c v_c, v_c=n*a'Lambda_c*a/M^2. Satterthwaite degrees of freedom V^2/sum(v_c^2/(batches_c-1)); upper MCSE=sqrt(V*df/chi2_ppf(tail, df)). This is an **approximation**, conditional on stationarity/mixing, ratio CLT, positive smooth mixture density, and local score smoothness. Batch-means asymptotic background: [Flegal & Jones](https://arxiv.org/abs/0811.1729); the present nonlinear application and guard are directly checked here, not granted a finite-sample theorem by that source.

Maximum endpoint derivative magnitude is 19. Therefore abs(change meanIS)<=19/N*sum(abs(changeL)+abs(changeU)), and it holds with supplied error radii only if actual errors lie within them. It also holds across score kinks. MCSE radii do not certify absolute error or coverage. CQR is deterministic conditional on its stored fit/calibration; H propagates only Bayesian posterior approximation to the primary difference. Repeated-data, calibration-estimation, prior/model misspecification, and full-pipeline uncertainty remain excluded.

## Computational verification and conformal rank

All **59 tests pass**, including the original 55 and four deterministic worker tests. SOL's saved-draw check first projects to scalar H, then independently uses scalar chain-batch variance, matching the joint-matrix projection and chi-square upper formula at250/500. Dense mixture densities and root-CDF residuals match archived quantiles. Upper score MCSEs:[0.055868001427118806, 0.05878074634522647]; no training label kink flags. This is a numerical demonstration, no primary CQR comparison.

Finite CQR rank is ceil((25+1)*.9)=24. Nonnegative correction expands rather than shrinks; lower projection0 preserves inclusion of positive outcomes. The exchangeable-rank theorem requires score exchangeability/training separation ([Romano et al.](https://arxiv.org/html/1905.03222v1)); official cutoff exchangeability and untouched development outcomes are not established. We do not infer guaranteed official coverage from the correct rank.

Generic latent structural identification uses covariance moments under full rank/interior assumptions; high-rho second differences are ill-conditioned. A bounded fitPASS and concentrated innovation scale do not establish practically separate physical nuisance effects. That is compatible with a restricted complete-procedure score comparison, provided actual prediction guards pass and all failures remain.

**Conclusion:** no unresolved material mathematical discrepancy found in tested implementation. Future endpoint guards remain mandatory. Restricted finite description is defensible; ideal-posterior numerical precision and population/physical/general robustness claims require qualifications.
