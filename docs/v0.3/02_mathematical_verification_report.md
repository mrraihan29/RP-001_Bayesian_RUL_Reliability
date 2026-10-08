# RP-001 — Mathematical Verification Report v0.3

**Lead disposition: implementation checks PASS within the tested domain; predictive numerical precision FAIL; mathematical verification does not lock the protocol.** Material equations and numerical claims below were checked directly by the lead using independent dense covariance, conditional Gaussian, finite-difference and rank calculations. Worker output alone was not accepted as mathematical verification.

## Integrated likelihood

Write S=diag(τ)Ωdiag(τ), R_z=σ_z²K_ρ, μ₀=Γa, C_z=BSBᵀ+R_z. Integrating g gives z|a,θ~N(Bμ₀,C_z). Conditional on z:

V=(S⁻¹+BᵀR_z⁻¹B)⁻¹,
μ_g=μ₀+VBᵀR_z⁻¹(z−Bμ₀),
m_y=aᵀβ+γᵀμ_g,
v_y=σ_r²+γᵀVγ.

Thus log p(z,y|a,θ)=log N(z;Bμ₀,C_z)+log N(y;m_y,v_y). The NumPy reference uses dense C_z solves. The sampler implementation whitens the stationary AR(1) residual: first observation unchanged; later innovations (u_t−ρu_(t−1))/sqrt(1−ρ²). Since det(K_ρ)=(1−ρ²)^(w−1), Woodbury and the determinant lemma give:

A=S⁻¹+BᵀR_z⁻¹B,
log det C_z=w log σ_z²+(w−1)log(1−ρ²)+log det S+log det A,
uᵀC_z⁻¹u=uᵀR_z⁻¹u−bᵀA⁻¹b, b=BᵀR_z⁻¹u.

This reduces repeated engine calculations to a 2×2 inverse. The w=1 case uses determinant exponent zero. With the sensitivity residual mixture .95 N(0,σ_r²)+.05 N(0,9σ_r²), integrate both components: their variances are σ_r²+γᵀVγ and 9σ_r²+γᵀVγ. Multiplying the whole integrated variance by nine would be incorrect.

The fitting target is expressed in y=log R coordinates. If evaluating a density with respect to R, include the Jacobian 1/R; its −log R term is parameter-constant for observed fitting data, so omitting it in the y-coordinate fitting likelihood does not change the posterior. This model specifies an alive-landmark pair distribution; it does not derive a coherent survival process at all ages or a physical failure boundary.

## Priors and conditional prediction

β~N([log100,0],diag([1,.75]²)); γ_j~N(0,.5²); Γ row entries have SD[1,.5]; τ_j,σ_z,σ_r~HalfNormal(.5); η_ρ~N(0,.75²), ρ=tanh η_ρ. In dimension two LKJ(η=2) has density proportional to (1−r_g²), exactly represented by r_g=2u−1, u~Beta(2,2); Var(r_g)=1/5. Sensitivity scales multiply the normal/half-normal SDs by .5 or 2, including the η_ρ SD, while retaining LKJ shape. Priors are proper but their domain plausibility is unresolved.

For a new engine sensor prefix z*, p(θ|D,z*,a*) is proportional to p(z*|a*,θ)p(θ|D). Therefore the predictive CDF is a weighted mixture of Φ((log r−m_y(θ))/sqrt(v_y(θ))) with sensor-likelihood importance weights. For the contamination model use the corresponding two-component CDF. Solve F(r)=.05/.50/.95, rather than averaging conditional quantiles. Prediction does not use the new RUL, and the sensor likelihood is not applied twice after an exact global posterior update.

Independent conjugate-Gaussian testing verifies that a global sensor update changes the predictive distribution correctly. A lead dense likelihood oracle, not merely a second copy of the optimized formula, was used for likelihood and gradients. Exact sensor-only refitting for one deterministic training calibration engine agreed with importance integration within 0.022155 cycle; the planned 1-cycle/minimum oracle tolerance is much coarser and this one-engine success is not a universal certification. Weight ESS is not MCMC ESS. The four-chain quantile variability estimate is an approximate diagnostic, not a rigorous upper bound on Monte Carlo error.

## CQR finite-sample correction: n=25

At α=.10 and n=25, exact decimal arithmetic gives k=ceil((n+1)(1−α))=ceil(23.4)=24. Use the 24th ascending calibration score, without interpolation. A naive empirical .9 quantile can use rank23; under independent continuous scores and a fixed fit that corresponds to mean coverage 23/26=.884615, below .90. Correct rank24 corresponds to 24/26=.923077. The usual rank guarantee needs exchangeability of calibration and target scores conditional on the fitted procedure; independence is not proved by engine IDs or outcome-blind hashing. See the primary [CQR paper](https://arxiv.org/pdf/1905.03222) for the method and assumptions.

Raw scores can be negative. This protocol fixes q=max(0,s_(k)), so intervals only expand. Nonshrinking projection and ties can make the procedure more conservative. For R≥0, intersecting an interval with [0,∞) cannot remove a truly covered response. Sorting raw endpoints before scoring is mandatory. If ceil(.9(n+1))>n, use infinity. For integer n, the smallest finite cohort is n=9; n=8 must not manufacture a finite guarantee.

Under the stronger independent continuous-score model with score CDF F and fixed fit, U=F(s_(k))~Beta(k,n+1−k). At n25: E U=24/26, SD U=sqrt(24×2/(26²×27))=.0512821. Its central 95% repeated-cohort range is [.796483,.990160], and P(U<.90)=.271206. This is a distribution of realized conditional coverage across calibration cohorts, not a confidence interval for official test coverage and not a consequence of exchangeability alone. Direct order-statistic simulation (5,000 cohorts, fixed seed) agreed: mean .922995, MCSE .000720.

## Score, sample precision and uncertainty

IS90(L,U;R)=(U−L)+20(L−R)1{R<L}+20(R−U)1{R>U}. It has units cycles and balances width and misses. Five interval-score cycles could represent five width cycles or only .25 cycle of additional miss distance. Without a maintenance loss/utility relation, this does not justify a universal 5-cycle practical decision margin. Report effect sizes and uncertainty without practical-superiority/equivalence labels.

For a hypothetical 90 successes among 100 independent Bernoulli endpoints, the Wilson 95% interval is [.825634,.944771]. Approximate independent n for a .90 proportion with half-width .02 is 865, or .05 is 139; these are planning calculations, not observed results. A common fitted model does not make conditional-independent assessment engines multiple independent training replications. With shared pipeline P:

Var(estimated score)=E_P[Var(estimated score|P)]+Var_P[E(estimated score|P)].

Paired assessment-engine resampling with P frozen addresses the first component. Bayesian posterior uncertainty conditional on the observed fitting data addresses parameter integration under that model; it does not automatically cover fitting-data selection, PCA, HPO or conformal-cohort replacement. Report 05's synthetic illustration makes the distinction explicit without estimating RP-001's actual total uncertainty.

## Executed verification and limits

- `logs/pilot_math_tests.xml`: 21 tests passed. Dense joint-Gaussian oracle, NumPy factorization and optimized symbolic target agree to 1e−8 tolerance for w=1/2/30, ρ=−.5/0/.5/.9/.99 and both residual structures. Symbolic gradients agree with dense-oracle central differences under the 1e−4 relative criterion. CQR ranks/ties/infinity, known interval scores, support projection, LKJ prior moment and single-component lognormal quantiles are tested.
- `logs/backend_serialization_tests_v2.xml`: 2 tests passed for both supported trace container formats. They verify storage handling, not posterior correctness.
- `logs/lead_comparator_tests.xml`: 10 comparator/prediction tests passed, including independently computed Student-t reference intervals, estimability rejection, fixed five-feature contract and batch/dense predictive agreement.
- `logs/lead_cutoff_tests.xml`: 3 tests passed, including direct split/cutoff reconstruction, future-sensor isolation, and conjugate sensor conditioning. Correlation results are retained in `logs/lead_cutoff_verification.json`.

These 36 final test cases support specific implementation claims. They do not establish global identifiability, population exchangeability, prior plausibility, frequentist posterior calibration or predictive superiority. All 11 successful sampling fits pass the predefined MCMC criteria, but calibration-engine predictive precision fails: max approximate MCSE=.728972>.5 cycle. Lead recommendation: **REVISE AGAIN**.
