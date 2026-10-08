# RP-001 — Prospective targeted remediation plan v0.4

Frozen before additional scientific experiments,8October2026. Research Owners:Raihan×Rei; final authorization absent. Exact configurations/seeds/criteria are in configs/v0.4/remediation_plan.json. Historical data/documents/source/results are retained; baseline212-artifact hashes and30-record registry verified.

## Numerical precision

Three independent principal fits use4chains×8000retained draws each, pooled as12independent chains. Evaluate all25 original calibration sensor cases, all .05/.50/.95 quantiles, including86. Use self-normalized weighted-CDF influence h=w(Fθ(q)−p), batch-means long-run variance and delta-method division by predictive density. Batches250/500 account for serial dependence. Approximate Satterthwaite chi-square upper variance limits use Bonferroni tail .05/(25×3×2). Both approximate upperMCSE guards must be≤.5cycle; weightESS≥1000,influenceESS≥400, principal MCMC gates pass. The.5criterion is unchanged, and the uncertainty-of-MCSE guard is stricter. Its validity remains asymptotic, not a deterministic error bound. Independent replication and exact sensor-only oracles11/61/86 test computational agreement; no best-case selection. No extra draws or favorable-seed retry after the result.

Known-conjugate IID/AR1 synthetic validation uses200independent replications perρ=0/.8/.95,4chains×2000draws. Report RMSactualerror versus RMSestimatedMCSE and MC interval coverage with binomial uncertainty. This targets the estimator, not the scientific model's calibration. Historical four-chain MCSE is retained as a failed approximate point diagnostic with poorly estimated variance(df≈3), not relabeled as a rigorous bound.

## Prior and identifiability

Principal prior is changed prospectively to anchored_v04, with the same log100 intercept center and a.6log-scale intercept SD, ageSD.5,γSD.25,ΓSD[.5,.35],τSD.35, sensor/errorSD.4,ηρSD.75,LKJη2. These are proper weakly regularizing working priors on hundreds-of-cycles RUL and standardized PC units, not physical safety bounds. The intercept-only prior median95% range is31..324cycles; total predictive tails are separately evaluated. Broad1.5×prior sensitivity and two fixed noise alternatives never select a winner by interval score. This is disclosed development adaptation after calibration exposure.

Four targeted synthetic regimes each receive4new fixed seeds: regular,ρ.95,weak latent signal, and age/latent/noise confounding. Evaluate14working parameters, predictive quantities on20independent synthetic engines/run, correlations and information contraction. This is repeated fixed-parameter recovery, not simulation-based calibration; n4/regime cannot certify nominal95%coverage. Structural identification is separately proved for fullrank age/basis, positive covariance and w≥6 using second-difference covariance lag3/lag2=ρ, then recovering all Gaussian moments. Weak practical identification is not erased by that proof. LatentPC effects remain statistical nuisance structure, not a physical health mechanism.

## Estimand, inference and full-stage sensitivity

Primary target is exact finite-benchmark mean90%interval-score difference for stored predictions at all official endpoints. No primary population p-value, equivalence or practical-superiority rule is adopted. Pairedbootstrap-t is a secondary conditional diagnostic; its future numerical/degeneracy/outlier reporting policy is frozen now. Synthetic Normal,skewed lognormal,heavyfinitevariance,rareoutlier,infinitevariance and discrete/degenerate cases are all retained(500datasets×1999resamples). An unavailable diagnostic is suppressed, not replaced with a favorable test.

Eight observed-data perturbation pipelines use4paired stratified engine bootstraps, canonical versus alternate cutoff salts. Each repeats PCA,CQR12-candidate selection,refit,Bayesianfit and calibration. Fixed25sensor-prefix anchors measure prediction-map sensitivity; they are not an independent assessment set. Calibration duplicates are multiplicities, not new engines or a new conformal guarantee. All stages are varied but8perturbations cannot measure true total pipeline sampling uncertainty or support a precise variance decomposition.

## Budget, failures and authority

33scientific MCMC fits maximum, at most2 documented infrastructure-only repairs,6aggregate CPU-hours,2GiB scientific artifacts,10minutes perfit, at most2parallel CPU processes. Preserve failures and exact executed sources/configs/data/environment/seeds. No extra spending. Colab only if measured need. Proposed fallback: same compact hierarchy withρ0 anddiagonalΣ; no automatic replacement after failure, and owner review remains necessary. Official test sensors/labels and confirmatory evaluation are unauthorized. Lead directly verifies material mathematics and completes an adversarial review before returning A/B/C.
