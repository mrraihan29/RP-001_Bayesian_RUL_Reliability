from pathlib import Path
import json, hashlib, datetime, subprocess
R=Path(__file__).resolve().parents[1]
D=R/'docs/v0.3'
def read(p): return json.loads((R/p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,s): (R/p).write_text(s.strip()+'\n',encoding='utf-8')
def dump(p,v): write(p,json.dumps(v,indent=2,ensure_ascii=False))
def table(headers,rows): return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,row))+' |' for row in rows])
runs=['syn_r0_repair2','syn_r05','syn_r09','syn_weak','base','prior_half','prior_double','rho_zero','contamination','refit','sensor_oracle']
fits={k:read('results/pilot/'+k+'.json') for k in runs}
env=read('logs/pilot_environment.json'); pred=read('results/pilot/predictive_integration.json'); stat=read('results/pilot/statistical_design.json'); cal=read('results/pilot/comparator_calibration.json'); aux=read('logs/auxiliary_diagnostics.json')
write('docs/v0.3/01_updated_research_protocol.md',r'''
# RP-001 — Updated Research Protocol v0.3

**Status: PROTOCOL_DRAFTED. Development pilot returned; REVISE AGAIN. Final protocol is not locked.**
Research Owners: Raihan × Rei. Lead scientific and mathematical review: Rei, SOL Extra High role. Research worker: GPT-6 LUNA MAX; worker conclusions were reviewed and material mathematics reconstructed directly by the lead.

## Question, estimand and authorization

The primary question is unchanged from v0.2:

> Is a compact hierarchical Bayesian predictor competitive in 90% interval score with calibrated CQR at the official FD001 unseen-engine endpoint, with engine-level uncertainty and audited dependence?

The proposed primary endpoint is mean 90% interval score in cycles, using uncapped RUL and one forecast at the official endpoint per engine. The proposed primary comparison is Bayesian minus CQR score. Lower is better. A negative point estimate alone does not establish superiority. Current empirical work uses synthetic data and official FD001 **training** only. Official test covariates and test labels remain uninspected, and no primary confirmatory comparison has been run. The owner's conditional development approval does not authorize final evaluation or a change to the primary question.

For a future authorized run, distinguish (i) the exact finite-benchmark mean difference, and (ii) inference for an assumed engine/cutoff population conditional on the frozen fitted pipeline. The second requires assumptions beyond having 100 distinct engine IDs. This protocol does not claim applicability to operational engine maintenance.

## Data, cutoffs and representation

The NASA training file has 100 engines, 20,631 cycles and 26 fields. Engine roles are the unchanged SHA-256 ordering with seed `RP001-20261008-v0.2`: 55 fit, 15 tune, 30 calibration reserved. Each engine receives one outcome-blind hash cutoff, an integer in [30,250]; retain only C<T. No cutoff redraw is allowed. The observed eligible counts are 43 fit, 13 tune and 25 calibration; final fitting uses the 56 eligible fit+tune engines. All role assignments, lifetime-derived eligibility and prefix checks are retained in the split manifest and audit.

Eligibility conditions on survival and disproportionately retains longer-lived engines. Outcome-blind hashing is not a proof of stochastic independence. The official test cutoff distribution cannot be reconstructed from the allowed training information. Formal conformal coverage transported to official test endpoints is therefore not established.

At each cutoff use sensors observed through C only. Training-only, equal-engine weighted scaling drops channels with weighted SD≤1e-8. Retain PC1, orient its largest absolute loading positive, and scale to unit fitting variance. The Bayesian model uses the most recent min(30,C) PC values with age [1,log(C/100)] and fixed intercept/slope basis. Gradient boosting uses five prefix summary features; linear quantile regression uses age plus the 30-position observed sequence. No terminal sensor values, future sensors, or capped RUL enter preprocessing. The refit representation is learned again from the 56 fitting prefixes and frozen before calibration outcomes are used.

## Bayesian candidate and prediction

The fixed principal candidate is a conditional alive-landmark Gaussian hierarchy, not a physical failure-time model. Let g be a two-dimensional local level/slope, z the observed PC sequence, and y=log(T−C): g|a~N(Γa,Σ), z|g~N(Bg,σ_z²K_ρ), y|g,a~N(aᵀβ+γᵀg,σ_r²), K_ij=ρ^|i−j|. Latents are integrated analytically. Priors and exact conditional equations are specified in report 02 and implemented in `src/rp001/model.py`.

For each new engine separately, update the global posterior using that engine's sensor likelihood only. Then integrate its conditional log-RUL distribution over the updated global parameters and latent conditional distribution. Obtain mixture CDF quantiles at .05/.50/.95; averaging draw-level quantiles is prohibited. No other new engine's sensors are pooled in this forecast rule. Exact sensor-only MCMC provides a diagnostic oracle, not a replacement selected by observed test outcomes.

The predefined predictive precision gate failed: maximum approximate quantile MCSE 0.728972 cycles >0.5. The present posterior draws and Bayesian calibration correction are development evidence, not inference-ready predictions. A revised, prospectively specified numerical precision plan is required before lock.

## Comparator and calibration

The fixed CQR search contains eight gradient-boosting quantile configurations (depth 1/2, leaf 5/10, learning rate .03/.1, 200 estimators) and four linear quantile configurations (penalties .001/.01/.1/1). Both .05/.95 endpoints are fitted and sorted. Choose by uncalibrated mean interval score on the 13 tuning engines, with the specified ≤0.5-cycle score tie band and deterministic simplicity rule. This tie rule is a model-selection convention; it is not a practical-significance threshold.

The selected development configuration is `gb-depth1-leaf10-lr0p1`. Refit on 56 engines. Separately fit its .50 quantile. Freeze configuration and representation before accessing calibration outcomes. For each of 25 calibration engines compute s=max(L−R,R−U); choose k=ceil(26×.90)=24 and q=max(0,s_(24)). Output [L−q,U+q] intersected with nonnegative RUL support. If k>n the correction is infinite, never silently clipped to n. This deliberately nonshrinking CQR variant is fixed and disclosed.

The Gaussian log-RUL reference uses Student-t predictive intervals including coefficient and residual uncertainty, with estimability checks. Bayesian+the same post-hoc conformal calibration is a proposed **secondary** ablation. Raw versus calibrated CQR and Bayesian intervals can diagnose calibration effects. No diagnostic replaces the proposed primary comparison.

## Evaluation and uncertainty plan — proposed, not executed

After an explicit final owner authorization, freeze protocol, data-access policy, model states, priors, calibration corrections, environment and analysis code. Only then generate per-engine predictions from authorized test sensors, store and hash all predictions, and request or use the separately authorized test-label step. There is no authorization to do these steps in this development return.

For the future primary comparison let d_i=IS90_B,i−IS90_CQR,i and D=mean(d_i). Use paired engine bootstrap-t with 20,000 resamples for a two-sided 95% interval and a one-sided 95% upper bound under H0:D≥0. Keep all forecasts from an engine in the same resampling unit if any secondary repeated-cutoff analysis is later approved. Disclose infinite/undefined intervals, dominant influences and degenerate standard errors; do not select a favorable inferential fallback after labels are seen. Operating-characteristic diagnostics are in reports 05/06. A final failure policy for influential cases remains to be fixed before lock.

The primary interval conditions on the realized fitted/tuned/calibrated pipeline. It excludes variation in training engines, PCA, hyperparameter selection, cutoff realization and calibration cohort. Posterior parameter uncertainty conditional on observed fitting data does not supply this missing repeated-pipeline uncertainty. Full-pipeline sensitivity requires repeating all relevant stages on training-only resamples, and remains incomplete.

Report absolute score differences and intervals, width and miss-penalty decompositions, coverage with Wilson intervals, and median MAE/RMSE/bias. CRPS is not a comparable endpoint for CQR without a defined full predictive distribution. There is one proposed primary comparison; secondary ablations are exploratory. No fixed 5-cycle practical superiority or equivalence threshold is adopted because a defensible utility mapping is absent.

## Changes, stopping and lock requirements

The development plan and its initial snapshot preserve predefined likelihood, sampler, recovery and prediction criteria. Two documented serialization repairs retain failed runs with unchanged data/seeds/model/sampling settings. The existing proposed refit step and a sensor-only oracle were added as numerical validation, without changing the primary question or searching for a Bayesian winner. Calibration outcomes are now known under a frozen development policy; future retuning must disclose adaptive reuse and cannot call this cohort untouched.

Before lock: remedy predictive precision under a revised fixed plan; defend prior plausibility and identifiability limitations; decide the official-cutoff transport claim scope; predefine inference failure and whole-pipeline sensitivity policies; record fair information and tuning budgets. Publication additionally requires current novelty/full-method and data-redistribution reviews. Research Owners retain final authorization. The detailed open items and disposition are in reports 08/09.
''')
write('docs/v0.3/02_mathematical_verification_report.md',r'''
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
''')
recovery_counts=[{'run':k,'covered95':sum(p['truth_in95'] for p in fits[k]['recovery']['parameters'])} for k in runs[:4]]
rows=[]
for k,v in fits.items():
 x=v['diagnostics']; rows.append([k,f"{x['rhat_max']:.5f}",f"{x['bulk_ess_min']:.0f}",f"{x['tail_ess_min']:.0f}",x['divergences'],f"{min(x['bfmi']):.3f}",x['acceptance']])
recovery=table(['Synthetic run','Truth in 95% intervals /14','Max |posterior mean−truth|/posterior SD'],[[x['run'],str(x['covered95'])+'/14',f"{fits[x['run']]['recovery']['max_abs_standardized_mean_error']:.3f}"] for x in recovery_counts])
sens=table(['Variant','Max |Δ lower|','Max |Δ median|','Max |Δ upper|','Max approx quantile MCSE'],[[x['variant']]+[f'{n:.3f}' for n in x['max_absolute_quantile_delta_cycles']]+[f"{max(x['max_between_chain_quantile_mcse_approx']):.3f}"] for x in pred['sensitivity_deltas']])
write('docs/v0.3/03_synthetic_recovery_diagnostic_pilot_report.md',r'''
# RP-001 — Synthetic Recovery and Diagnostic Pilot Report v0.3

**Development completed; REVISE AGAIN. Sampling diagnostics pass, predictive precision fails.** All results are synthetic or training-only exploratory evidence.

## Fixed design and retained failures

Four independent fixed synthetic datasets use n=56 engines, 30 sensor observations, ages uniformly drawn as integer cutoffs30..250, and seeds3101/3102/3103/3104: ρ=0/.5/.9, plus weak γ=[−.03,.02] at ρ=.5. Truth for other cases is β=[log100,−.4], γ=[−.35,.15], Γ=[[.1,.5],[−.1,−.25]], τ=[.45,.30], r_g=.2, σ_z=.30, σ_r=.25. These simulate the specified conditional landmark hierarchy. They do not simulate complete degradation-to-failure trajectories or verify the lifetime-selection mechanism.

The official training fits are principal fit43, prior SD half/double, fixed ρ=0, contamination residual, principal refit56, and sensor-only oracle on refit56 plus the first deterministic eligible calibration engine11. Four chains each use 1,000 warmup and 2,000 retained draws, two active CPU cores, target acceptance.95, maximum depth12 and nutpie NUTS.

The first synthetic ρ0 run and its first serialization repair failed when saving nested backend metadata. Both failed records remain. The second repair handles InferenceData and DataTree root/group attributes; it changes storage handling only. Successful `syn_r0_repair2` uses the same generated data, seed, model and sampler settings. Failed attempts are not replaced by favorable-seed reruns. Two infrastructure repairs have been consumed; no additional attempt was run to erase the predictive precision failure.

## Sampling diagnostics

Predefined gates: Rhat<1.01, bulk/tail ESS≥400, zero divergences, every-chain BFMI>.3 and depth saturation≤1%. The following physical-parameter summaries pass. Auxiliary sampled variables eta_rho and gcor_u also pass; values are retained in `logs/auxiliary_diagnostics.json`.

'''+table(['Run','Max Rhat','Min bulk ESS','Min tail ESS','Divergences','Min BFMI','Status'],rows)+r'''

All observed depth-saturation fractions are zero. Good diagnostics do not prove exploration of every possible posterior mode or domain validity.

## Parameter recovery and identifiability

'''+recovery+r'''

There are only four fixed datasets. Counting covered coordinates within a correlated vector is not a repeated-sampling coverage experiment; these counts do not certify 95% posterior calibration. No run triggered the gross >3 posterior-SD discrepancy flag. The high-ρ and weak-signal scenarios recover some coordinates less precisely. Recovery is consistent with an implemented finite-dimensional target, while global/practical identifiability remains qualified.

Fixing PC sign/scale and the intercept/slope basis removes arbitrary latent rotations and representation scale choices. It does not prove every residual/covariance parameter uniquely identified by 56 engines. When sensor noise is high or γ is weak, age effects, γ and σ_r can trade off. In principal fit43 the largest absolute measured posterior correlation is γ[1] versus β[0]=−.6630; γ components correlate−.4825, and σ_r versus γ[1]=.4098. These show coupled uncertainty rather than a cleanly separated mechanism. No formal structural-identifiability proof, repeated simulation-based calibration or prior-to-posterior information analysis has been completed.

## Prior predictive checks

4,000 prior draws per scale at ages30/100/250 show very broad RUL support. Principal prior median RUL is approximately100/100/107 cycles and its .95 quantiles are1534/871/1284 cycles. Prob(RUL>1000)=.08025/.041/.070. Half-scale .95 quantiles are339/259/311; double-scale .95 quantiles are139377/46670/93283, with Prob(RUL<1)=.139/.0955/.1205. These are actual simulated summaries in `results/pilot/prior_predictive.json`, not calibrated physical failure probabilities. Proper priors alone do not make these tails defensible. Their plausibility requires a domain-based policy before lock; priors must not be chosen by favorable observed calibration performance.

## Posterior predictive checks

1,000 replicated draws check log-RUL mean, SD and q90, plus PC-sequence SD and mean first-to-last change. Principal fit43 observed log-RUL statistics are4.49915/.75324/5.15636. Conditional replicate tail areas are.514/.464/.839; observed PC SD1.10554 and mean change.46616 have joint replicate tail areas.359/.448. Observed summaries fall inside the central95% replicate ranges. These coarse, in-sample checks do not establish prediction coverage, tail adequacy, correct stage dependence or transport to official test cutoffs. Every successful run retains both conditional and joint PPC summaries.

## Prior and error sensitivity

For the same13 tuning prefixes, these are maximum absolute predictive-quantile changes from the principal fit43, in cycles. They are sensitivity diagnostics, not a method-selection contest.

'''+sens+r'''

Upper endpoints can change by about21 cycles under half-scale priors or20 under contamination residuals. Fixed ρ0 yields smaller changes here; this does not establish that serial dependence can generally be ignored. The principal candidate remains unchanged. Some tuning predictions also have approximate MCSE>.5; sensitivity numbers therefore have numerical uncertainty and are not precise effect-size conclusions.

## New-engine integration and predefined failure

On the 25 calibration sensor prefixes after refit56, minimum importance ESS=3711.54/8000 passes the ≥1000 gate. Maximum approximate four-chain quantile MCSE=.728972 cycle fails the ≤.5 gate. This occurs at the upper endpoint for engine86; other failures include upper endpoints for engines listed in the raw predictive results. Approximate between-chain MCSE itself has uncertainty with only four chains and is not a bound.

For engine11, independently sampling the posterior with its sensors included, without its RUL, agrees with the importance-integrated lower/median/upper endpoints to .01870/−.00859/−.02215 cycle. This supports the full global sensor update for one case. It does not override the cohort precision gate. Bayesian+post-hoc calibration computes a development q=0 but is marked `accepted_for_inference=false`.

Retained failure and success records, configuration hashes, seeds, dataset payload hashes and posterior hashes are in `research/experiment_registry.jsonl` and `results/pilot/`. Posterior stores are local ignored scientific artifacts, bound by the delivery manifest. A revised prospective precision plan and a stronger identifiability/prior policy are needed before final lock. No test labels or confirmatory evaluation were used.
''')
print(json.dumps({'written_reports':[1,2,3],'recommendation':'REVISE AGAIN'}))
calrows=table(['n calibration','k','Ideal mean coverage','Ideal SD','Central95% cohort-coverage range'],[[x['n_calibration'],x['rank'],f"{x['coverage_mean_theory']:.4f}",f"{x['coverage_sd_theory']:.4f}",f"[{x['conditional_coverage95_range_theory'][0]:.4f}, {x['conditional_coverage95_range_theory'][1]:.4f}]"] for x in stat['calibration']['design_rows']])
subrows=table(['Subset n','k','Correction 2.5% / median /97.5% cycles'],[[x['n'],x['rank'],' / '.join(f'{a:.3f}' for a in x['correction_range95'])] for x in cal['subset_sensitivity']])
write('docs/v0.3/05_calibration_feasibility_precision_report.md',r'''
# RP-001 — Calibration Feasibility and Precision Report v0.3

**Finite-sample calculation verified; official-population coverage guarantee unresolved. Numerical Bayesian prediction gate FAIL.**

## What 25 engines can and cannot establish

At n25, corrected CQR uses rank24. Exchangeability of calibration and target scores from the fixed fitting procedure supports marginal coverage at least .90. It does not guarantee .90 conditional coverage for each engine age, degradation stage, fitted calibration cohort or an unverified shifted population. Under the stronger independent continuous-score idealization, mean rank coverage is .923077, but realized cohort conditional coverage has central95% range [.796483,.990160]. P(cohort conditional coverage<.90)=.271206. A repeated-cohort average guarantee is not a per-cohort assurance.

Analytic order-statistic calculations and 5,000 synthetic score cohorts per size yield the following. These are **idealized repeated-cohort coverage distributions**, not official data results or confidence intervals for test coverage.

'''+calrows+r'''

Rank rounding causes nonmonotone conservatism as n changes. Increasing n generally improves precision, but integer boundaries can change the realized mean and undercoverage probability. n25 cannot support precise .90 conditional calibration. Even with a fixed interval and100 independent assessment engines, hypothetical90/100 coverage has Wilson95% [.825634,.944771]. More sensor rows do not increase the number of independent endpoints.

## Training-only calibration feasibility

After the CQR candidate and refit representation were frozen, the25 reserved eligible training engines were used for calibration/influence diagnostics. Selected configuration: gb-depth1-leaf10-lr0p1; q_raw=q=19.987559cycles. No calibration-engine coverage or score was treated as independent assessment performance. All12 completed candidates and their tuning selection record remain available.

For500 draws of subsets at each fixed size within this cohort, correction distributions are:

'''+subrows+r'''

These without-replacement ranges are sensitivity summaries, not confidence intervals or evidence that a favorable cohort should be selected. Leaving one engine out gives correction9.612119..19.987559cycles. Fixed-model bootstrap resampling of25 scores gives quantiles[0,19.987559,21.999902]cycles. Sparse extreme order statistics and n25 make ordinary empirical-bootstrap tail precision fragile. This bootstrap excludes representation/model/hyperparameter refitting.

Bayesian+post-hoc calibration is feasible as a secondary development ablation: the same rank24 nonshrinking rule gives q=0. It is marked **not accepted for inference**, because quantile numerical precision failed. A zero correction does not validate raw Bayesian coverage on independent engines or establish superiority.

## Cutoff and selection sensitivity

The rule assigns C in30..250 without observing lifetime in its construction, then retains C<T. The survivor sample overrepresents long-lived engines: lifetime-rank quartile eligibility14/25,20/25,22/25,25/25. Lead reconstruction gives cutoff/lifetime Pearson−.014760 among all engines and+.243970 among survivors; Spearman−.067357 and+.180308. Descriptive sample correlations do not establish stochastic independence or causal selection effects.

One hundred fixed salt perturbations with the same reserved roles yield eligible totals69..85 (median78), calibration counts18..29 (median23). Eighty-three engines change eligibility in at least one perturbation. These are deterministic membership/count sensitivity analyses; no salt was chosen using performance. They do not estimate whole-pipeline score variability, and alternative pipelines were not all refitted.

The official cutoff mechanism/distribution are unknown from allowed training metadata. Distribution matching and exchangeability to official endpoint pairs are **unverified**. A future empirical finite benchmark may support explicitly qualified claims; this audit does not support distribution-free official-population coverage.

As a mathematical illustration only, synthetic target scores with SD1.5 times calibration-score SD reduce mean ideal coverage to .773826 (MCSE .001142). This is not an estimate of actual official shift. It illustrates why score-distribution mismatch matters.

## Conditional versus full-pipeline precision

The law-of-total-variance illustration uses400 synthetic Gaussian-regression+conformal training/calibration pipelines (fit56,cal25), each with40 independent assessment sets of100. Mean within-pipeline variance=122.432684; between-pipeline variance after finite-assessment Monte Carlo correction=136.092813; total=258.525497. Conditional assessment SD=11.064930 versus full illustrated pipeline SD=16.078728. These are synthetic score units, not empirical RP-001 uncertainties or a Bayesian-versus-CQR comparison.

It includes regressor refitting and calibration-cohort replacement, but excludes PCA, hyperparameter selection, Bayesian sampling and cutoff/data selection. The missing variance term is illustrated without completing a full-pipeline study. The proposed primary paired bootstrap conditions on all fitted/tuned/calibrated artifacts. Whole-pipeline claims require prospectively repeating every relevant stage on training-only resamples.

## Acceptance

Calibration computation and fixed-cohort influence checks are complete. Precise conditional coverage, official cutoff transport and whole-pipeline variability remain open. Bayesian integration has minimum importance ESS3711.54 but maximum approximate quantile MCSE .728972>.5cycle; this FAIL cannot be waived by a calibration correction or one-engine oracle. **REVISE AGAIN.**

Evidence: `results/pilot/statistical_design.json`, `results/pilot/comparator_calibration.json`, `results/pilot/predictive_integration.json`, `experiments/development_data_audit.json`, `logs/lead_cutoff_verification.json`. Direct verification: report02.
''')
write('docs/v0.3/06_comparative_evaluation_design.md',r'''
# RP-001 — Comparative Evaluation Design v0.3

**Proposed design only. No official test predictions, label access, primary comparison or confirmatory decision was executed.**

## Comparison and fair information access

Retain Bayesian versus CQR, mean90% interval score primary. This compares complete procedures: a generative joint Gaussian hierarchy with posterior integration against a tuned non-Bayesian quantile regressor with conformal expansion. Differences can arise from representation, assumptions, regularization, interval construction or tuning, not Bayesian inference alone.

Both receive the same engine-role split, allowed prefixes, age, training labels, uncapped target, refit56 and calibration25 cohorts. Equal-engine weighted preprocessing uses fitting prefixes only. No future sensor values or test-population statistics enter selection. The Bayesian global sensor update uses only the current new engine's prefix, with no pooling of other test engines. CQR uses those sensors through fixed features. Equal information does not imply identical structural biases.

Report actual budgets: one fixed principal Bayesian candidate plus four exploratory sensitivities; CQR12 fixed configurations on13 tuning engines, with no grid extension after results. Search freedom and runtime are not equal. All candidates, criteria, failures, seeds and representations must be disclosed. Development CQR selection is gb-depth1-leaf10-lr0p1; the principal Bayesian prior/error structure is not selected by sensitivity scores. The small tuning sample gives imprecise selection and optimistic best tuning performance; tuning results are not assessment evidence.

Boosting uses five observed-prefix summaries: age, observed endpoint PC, OLS level/slope, residual SD. Linear quantile regression uses age and the30-position observed sequence. Bayesian uses the observed sequence itself. These are fixed representation choices and attribution limits. A matched representation/plugin control could help, but is not completed or substituted into the primary comparison.

## Secondary explanations

Propose Bayesian+the same rank-corrected post-hoc calibration as a secondary ablation, sharing reserved cohort and outcome-use policy. Report raw versus calibrated CQR as well. Within-method differences help explain interval-construction effects. Raw Bayesian versus calibrated CQR remains proposed primary; no secondary winner replaces it.

The Gaussian log-RUL reference has Student-t prediction intervals including coefficient/residual estimation. Removing serial correlation, half/double prior SD and contamination residuals remain exploratory. CRPS is omitted without a defined comparable CQR full predictive distribution. These comparisons do not establish an isolated benefit of Bayesian inference philosophy.

## Future endpoint analysis — final authorization required

For engine i, d_i=IS90_B,i−IS90_CQR,i in uncapped cycles. Its exact benchmark average is descriptive. Population inference conditions on the frozen pipeline and an assumed engine/cutoff sampling model. Resample complete engine pairs, never individual sensor cycles or methods separately. If repeated-cutoff secondary analysis is later approved, all forecasts stay within the same engine cluster.

Proposed primary inference: paired bootstrap-t20,000 resamples, two-sided95% interval and one-sided95% upper bound for H0:D≥0 versus D<0. Report SE, influence of extreme scores, missing/infinite predictions and degenerate bootstrap samples. Finalize the failure policy for dominant observations/unestimable SE before lock. Do not choose a favorable inferential fallback after labels. Power for a5cycle margin is not demonstrated and that margin is not adopted.

The executed synthetic check uses1,000 independent n100 datasets per distribution and1,000 bootstrap resamples each. Nominal95% coverage: Normal .951±.006826 Monte Carlo SE; centered lognormal .942±.007392. One-sided false-positive proportions .056±.007271 and .066±.007851. These are approximate operating characteristics under specified distributions, with skew sensitivity; they do not certify inference for unknown actual score differences or run the proposed primary analysis on official outcomes.

The future table should report absolute mean score difference and interval, mean width, lower/upper miss penalties, coverage/Wilson intervals, median MAE/RMSE/bias, and assessable independent engine count. One primary comparison prevents post-hoc multiplicity expansion; secondaries remain exploratory.

## Practical interpretation and uncertainty boundary

Do not use a fixed5cycle superiority/equivalence margin. Interval score is an interval loss, not maintenance cost; its20×miss penalty prevents interpreting five score cycles as five operation cycles. Without an agreed utility mapping, report effect sizes, precision and decompositions. Statistical evidence of lower expected score is distinct from practical superiority.

Engine-pair bootstrap conditions on realized fitting, tuning and calibration. It excludes cohort replacement and representation/selection variation. Report05's variance simulation is illustrative, not the primary confidence interval. Bayesian posterior variance does not close this distinction. A prospective training-only outer resampling plan must repeat PCA, allowed selection, fitting, calibration and prediction for a broader pipeline-robustness claim; this full exercise was not completed.

## Readiness

Final priors, numerical precision, inference-failure policy, calibration claim scope, frozen model states/code/environment and owner lock must precede test-label access. After a separate final authorization, authorized test sensor predictions must be stored/hashed before any separately authorized labels are used. Current state: **REVISE AGAIN**. Calibration responses were seen only after the development freeze; further redesign must disclose this exposure and cannot call the cohort untouched. Research Owners retain final authority.
''')
print('Reports05/06 written')
all_sampler=[read('results/pilot/'+k+'.json') for k in ['syn_r0','syn_r0_repair1']+runs]
sampler_cpu=sum(x['process_cpu_seconds'] for x in all_sampler); sampler_wall=sum(x['wall_seconds'] for x in all_sampler); peak=max(x['peak_process_rss_gib'] for x in all_sampler)
compute_table=table(['Run','Wall seconds','Process CPU seconds','Peak process RSS GiB'],[[x['run_id'],f"{x['wall_seconds']:.2f}",f"{x['process_cpu_seconds']:.2f}",f"{x['peak_process_rss_gib']:.3f}"] for x in all_sampler])
write('docs/v0.3/07_compute_environment_report.md',f'''
# RP-001 — Compute and Environment Report v0.3

**Local CPU pilot completed. Colab Pro was not used; no paid compute or additional expenditure was authorized or incurred by this task.**

## Runtime and reproduction

Isolated runtime: CPython {env['python']}, {env['platform']}, float64, PyMC {env['packages']['pymc']}, PyTensor {env['packages']['pytensor']}, nutpie {env['packages']['nutpie']}, ArviZ {env['packages']['arviz']}, NumPy {env['packages']['numpy']}, SciPy {env['packages']['scipy']}, scikit-learn {env['packages']['scikit-learn']}. System packages were not replaced. Full exact versions: `configs/requirements-pilot.lock`; resolver wheel URLs/hashes: `logs/pilot_install_report.json`. Import smoke and dependency consistency checks passed. NUTS used the validated Numba/Rust nutpie backend; no unrecorded fallback.

Software environment SHA-256, computed from canonical JSON of Python implementation/version, platform, all package versions, float dtype, sampler and BLAS threads:

`{env['fingerprint']}`

Full metadata: `logs/pilot_environment.json`. The fingerprint identifies configuration; it does not guarantee bit-identical results across hardware/threading. The Windows lock is platform-specific. Colab would need a separately fingerprinted/validated environment.

Hardware: Intel i7-10750H, 6 physical/12 logical CPU cores, 15.776 GiB RAM. GTX1650Ti 4GiB present but unused. Four chains with two active cores, 1,000 warmup+2,000 retained draws per chain, one BLAS/OMP/MKL thread, maximum tree depth12, target_accept=.95. Per-run seeds/settings are preserved.

## Measured demand

{compute_table}

Sum of logged sampler **process CPU time**, including two failed storage attempts: {sampler_cpu:.6f} seconds ({sampler_cpu/3600:.4f} CPU-hours). Sum of individual wall times: {sampler_wall:.3f} seconds; this is not elapsed calendar time when runs overlap. Peak logged main-process RSS: {peak:.3f} GiB, not total simultaneous system memory. Predictive integration used15.349 wall/15.078 CPU seconds; comparator selection/refit/calibration4.515 wall/4.422 CPU seconds. Statistical design simulation6.387 wall seconds; CPU unmeasured. Dependency installation, tests, worker audits and drafting are excluded from sampler totals and must not be represented as zero-cost work.

Demand is far below the proposed32 aggregate CPU-hour envelope. Each successful fit took less than49 wall seconds in its logged call. Local CPU remains appropriate for numerical refinement. Colab Pro is available by owner report but not needed by these measurements. Broader repeated-pipeline studies require a new measured estimate; no extra spending is authorized.

## Run and storage provenance

The run registry preserves all fits, CQR candidates and development analyses. Sampling records include data payload hash, config hash, seed, software hash, start code commit and dirty-worktree flag. Most runs honestly retain `code_dirty=true`; a commit alone does not prove an executed dirty source state. Final delivery hashes retained sources/evidence/data/posteriors. This is an auditable reproduction specification, not a claim every historical run started clean or the entire project was independently rerun.

Two metadata-serialization repairs support both DataTree and InferenceData; failed runs remain, with unchanged scientific target/seeds/sampler. Windows configuration parsing also created a local compilation-cache directory with backslashes removed from its name. It contains generated cache only and is excluded from Git/scientific manifests. Use a forward-slash absolute cache path in PYTENSOR_FLAGS for future runs. This path issue does not alter likelihood or authorize protected data.

Create a fresh isolated Python3.12.14 environment, install/check the exact lock, verify the training hash, set project `src` as PYTHONPATH, float64 and one BLAS thread. Execute retained mathematical/conditioning/comparator tests before named synthetic/training runs. Freeze CQR selection before calibration responses, then refit56, sensor oracle and predictive integration. Preserve prior failures; use new IDs and a prospective revised precision plan for additional work. Exact Windows commands: `experiments/REPRODUCE_DEVELOPMENT.md`.

## Data and Git identities

Training SHA-256: `{sha('data/raw/train_FD001.txt')}`.

NASA original outer archive SHA-256: `{sha('data/raw/NASA_CMAPSS_original.zip')}`.

Source proposal SHA-256: `{sha('docs/proposal_v0.1.md')}`.

Split manifest SHA-256: `{sha('configs/proposed_split_manifest.json')}`.

The archive contains unopened test members; only training/readme were extracted. The barrier is procedural, not cryptographic. Final code/evidence checkpoint, delivery-commit convention and manifest identities: `docs/v0.3/delivery_provenance.json` and `logs/v0.3_delivery_manifest.json`. Raw data, .nc/.npz/.joblib scientific payloads remain local ignored artifacts, hash-bound without publishing. Redistribution rights remain unresolved before release.
''')
import runpy
runpy.run_path(str(R/'logs/update_pilot_registers.py'))
index=[('01_updated_research_protocol.md','Updated Research Protocol v0.3'),('02_mathematical_verification_report.md','Mathematical Verification'),('03_synthetic_recovery_diagnostic_pilot_report.md','Synthetic Recovery and Diagnostic Pilot'),('04_dataset_split_eligibility_cutoff_audit.md','Dataset Split, Eligibility and Cutoff Audit'),('05_calibration_feasibility_precision_report.md','Calibration Feasibility and Precision'),('06_comparative_evaluation_design.md','Comparative Evaluation Design'),('07_compute_environment_report.md','Compute and Environment'),('08_risks_assumptions_decisions.md','Risk, Assumption and Decision Registers'),('09_owner_return_recommendation.md','Owner Return and Recommendation')]
write('docs/v0.3/09_owner_return_recommendation.md',r'''
# RP-001 — Owner Return: Development Pilot v0.3

**Recommendation: REVISE AGAIN. Do not lock the final protocol yet.**

Research Owners: **Raihan × Rei**. Conditional development authorization was executed with synthetic and official FD001 training only. Test covariates and labels were not inspected; no confirmatory evaluation. The primary question, proposed90% interval-score endpoint and Bayesian-versus-CQR comparison remain.

## Evidence established

- Direct lead verification:36 final implementation/conditioning/comparator/storage test cases passed within tested scope. CQR25 rank24, integrated likelihood, sensor-only conditioning and score calculations were independently checked.
- Four fixed synthetic recovery cases plus seven training fits passed MCMC diagnostics:11 completed fits,4 chains/8,000 retained draws each. Two failed storage attempts remain, with two disclosed infrastructure repairs.
- Split/eligibility/cutoff audit and lead reconstruction completed. Eligible43 fit/13 tune/25 calibration; refit56. Future-sensor isolation tested.
- All12 CQR candidates and freeze recorded. Calibration correction19.987559cycles; cohort/influence sensitivity reported without independent performance claims. Bayesian+post-hoc calibration examined as secondary feasibility.
- Local CPU sufficient: logged sampler CPU623.016seconds (~.173CPU-hours) including failures. No Colab or paid expansion.

## Observed blocking failure

Bayesian refit56 on25 calibration sensor prefixes has minimum importance ESS3711.54, but **maximum approximate quantile MCSE .728972cycle exceeds the fixed .5cycle criterion**. Fitting diagnostics do not certify quantile precision. A sensor-only MCMC oracle agrees within .022155cycle for one deterministic engine, but does not override cohort failure. Bayesian calibration q=0 is not accepted for inference.

## Revisions needed before lock

1. Fix a prospective numerical precision plan: valid quantile MC uncertainty, fixed extra draws or exact sensor-only strategy, non-cherry-picked case coverage, budget/stopping and retained failures. Do not retrospectively relax .5cycle.
2. Defend prior tails and identifiability limits. Four fixed recoveries do not establish repeated-sampling calibration or a physical mechanism. Disclose all adaptation after development calibration exposure.
3. Decide calibration claim scope. Official cutoff exchangeability is unknown; survivor eligibility changes population. Qualified finite empirical benchmarking may be defensible; formal transported coverage is unsupported.
4. Finalize conditional-pipeline estimand, influential/degenerate-case inference policy and full fitting/selection/calibration sensitivity design. The illustrative variance simulation is not that full study.
5. Disclose information, representation/search-budget limitations and secondary calibration ablations. Report effect sizes without a5cycle practical-superiority/equivalence margin unless a defensible utility mapping is separately approved.

Novelty/current-method and redistribution reviews remain open before publication. Synthetic evidence cannot support operational-engine safety claims. Report08 and the handoff retain every open risk; none is silently closed.

## Nine-item return package

'''+ '\n'.join(f'{i}. [{label}]({name})' for i,(name,label) in enumerate(index,1))+r'''

Supporting evidence: dependency lock, run registry, source/protocol snapshots, test logs, posterior/data hashes, candidate freeze and design simulations. Full software/data fingerprints: report07. Git checkpoint and artifact identities: [delivery provenance](delivery_provenance.json), `logs/v0.3_delivery_manifest.json`.

The development return is complete. This is a scientific recommendation, **not final research authorization**. Final approval remains with Raihan × Rei; official test labels and confirmatory evaluation remain unapproved.
''')
write('docs/v0.3/README.md','# RP-001 — Development return v0.3\n\n**REVISE AGAIN. Final protocol not locked. Synthetic/FD001 training-only evidence.**\n\n'+'\n'.join(f'{i}. [{label}]({name})' for i,(name,label) in enumerate(index,1))+'\n\n[Exact data/software/Git provenance](delivery_provenance.json). Historical v0.2 and original proposal remain.\n')
print(json.dumps({'written_reports':[7,8,9],'sampler_cpu_seconds':sampler_cpu,'sampler_wall_seconds':sampler_wall}))