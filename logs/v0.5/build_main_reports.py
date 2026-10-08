from pathlib import Path
import json,hashlib
R=Path('.');D=R/'docs/v0.5';D.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads((R/p).read_text(encoding='utf8'))
p=read('configs/v0.5/resolution_plan.json');fit=read('experiments/v0.5/registry/v05_highrho_innovation.json')
pre=read('experiments/v0.5/analysis/math_preflight.json');score=read('experiments/v0.5/analysis/score_propagation.json')
g=read('experiments/v0.5/analysis/highrho_geometry.json');disp=read('research/v0.5/blocker_disposition.json')
assert fit['diagnostics']['acceptance']=='PASS' and pre['status']=='PASS' and score['numerical_policy_result']=='PASS'
sha=lambda path:hashlib.sha256((R/path).read_bytes()).hexdigest()
def save(n,s):(D/n).write_text(s.strip()+'\n',encoding='utf8')
short={'R01':'Cutoff transport','R02':'High-rho identification / sampling','R03':'Conditioning / precision','R04':'Population precision at N=100','R05':'Small calibration','R06':'Leakage / adaptive test access','R07':'Representation adequacy','R08':'Features / unequal budgets','R09':'Novelty','R10':'Redistribution rights','R11':'Bootstrap inference','R12':'Compute failure','R13':'Real-fleet generalization','R14':'Outcome-driven selection','R15':'Whole-pipeline uncertainty','R16':'Working-prior justification','R17':'Final owner authorization'}
classes={'OUTSIDE_BENCHMARK_GENERALIZATION':'External generalization','ACCEPT_WITH_RESTRICTED_CLAIMS':'Accept with restricted claims','FIXED_NUMERICAL_FAILURE_POLICY':'Fixed numerical failure policy','PRIMARY_VALIDITY_PRECONDITION':'Primary validity precondition','PUBLICATION_REQUIREMENT':'Publication requirement','OWNER_AUTHORIZATION_GATE':'Owner authorization'}
rows=[f"| {r['risk_id']} ({r['severity_retained']}) | {short[r['risk_id']]} | {classes[r['impact_class']]} |" for r in disp['risks']]
memo=f"""
# RP-001 | Pre-Lock Resolution Memo v0.5

**Recommendation: READY FOR OWNER LOCK REVIEW.** Accept the principal model for the restricted descriptive finite-benchmark comparison under the proposed numerical failure policy. Close the bounded investigation; do not activate a fallback or start another campaign. This is a scientific recommendation for Raihan x Rei, **not protocol authorization**.

Owner-reviewed baseline:61b4c2c63cbad6c1b9bd99168e33d1367aa180bc. The v0.5 plan/inquiry source was committed at304d8e76d03fe7d69dc7f8f9bb6de3c600a219dd before preflight/sampling; score-demo source at{score['provenance']['git_commit']} before execution. Final delivery commit is in [receipt](../../logs/v0.5/delivery_receipt.json). No official sensors/labels, confirmation, fallback, Colab/GPU, or additional spending were used.

## 1. Critical blocker disposition

The restricted claim compares **specified complete procedures on every endpoint of one fixed benchmark**, conditional on the realized pipeline. Population significance, transported conformal coverage, physical nuisance identification, and universal sampler robustness are outside that claim. Original severities are retained; the [prospective matrix](../../research/v0.5/blocker_disposition.json) records all seventeen risks.

| Risk (original severity) | Issue | Disposition |
|---|---|---|
"""+"\n".join(rows)+f"""

Actual invalidators remain unresolved mathematical/implementation error, prohibited leakage or official-outcome adaptation, unauthorized data use, or incomplete/nonfinite paired scores. Claim restriction cannot excuse them. Future integrity/numerical audits are execution preconditions; development does not certify them. Computational failure stops evaluation and stays in the endpoint ledger.

## 2. One high-rho investigation, closed

Preserve the exact failed-case data hash and truths, including rho=0.95. Frozen inquiry:seed54103,4chains,4,000retained+2,000warmup each,target0.95,depth12,600second cap. Exactly **one sampler invocation**, **{fit['wall_seconds']:.2f} wall / {fit['cpu_seconds']:.3f} process-CPU seconds**.

Investigate nu=sigma_z*sqrt(1-rho^2); restoring the original scale prior with its Jacobian preserves the exact posterior. This is no new model or fallback. Independent dense joint-Gaussian density, transformed posterior equality, and gradients pass predefined tolerances at12points through rho=0.999.

Bounded fit **PASS**: physical maximum Rhat **{fit['diagnostics']['rhat_max']:.8f}**, minimum bulk/tailESS **{fit['diagnostics']['bulk_ess_min']:.1f}/{fit['diagnostics']['tail_ess_min']:.1f}**, auxiliary maximumRhat **{fit['diagnostics']['auxiliary_rhat_max']:.8f}**, zero divergences, minimumBFMI **{min(fit['diagnostics']['bfmi']):.3f}**, no depth saturation. Original v04_syn_high_rho_3 **FAIL remains unchanged**.

Original diagnostic correlation(log sigma_z,eta_rho)=**{g['old_failed_diagnostic_only']['correlations'][0][1]:.4f}**, versus correlation(log nu,eta_rho)=**{g['old_failed_diagnostic_only']['correlations'][2][1]:.4f}**. New physical parameters remain strongly coupled. Nu is concentrated while stationary scale, autocorrelation, and latent variance have weak practical separation. Evidence supports difficult sampling geometry; no implementation discrepancy was found in the tested domain. Parameterization/warmup/retained budget changed together, so the cause cannot be uniquely isolated. No universal robustness, SBC, or physical-identification claim follows. Principal training fits already passed; this fit never replaces them.

## 3. Final mathematical validity and numerical policy

SOL directly verified Jacobian/density, likelihood, score derivatives, aligned quantile influence, joint covariance projection, and Lipschitz sensitivity. **59 tests pass**; independent dense/gradient checks supplement worker tests. See [mathematical assessment](03_mathematical_validity.md).

Score propagation reused only25already-exposed training calibration endpoints and saved12x8,000draws. Maximum approximate upper scoreMCSE **{max(b['approximate_upper_quantile_score_mcse_cycles'] for b in score['batch_size_results']):.5f}cycles**, no label-kink flags, independent-fit score range **{score['replicate_range_cycles']:.4f}cycles**. No CQR contrast was computed; this is no performance evidence.

Future quantile/MCMC/replication guards apply **before labels**. Score influence preserves shared-draw dependence across engines/endpoints. Undefined score uncertainty, upperMCSE>0.5cycles, or a label within3endpoint-upperMCSEs of a boundary qualifies the ideal posterior-score interpretation. The complete stored-prediction contrast remains descriptive. No post-label repair without owner review. The0.5cycle guard is numerical resolution, not practical significance.

## 4. Final inferential claim boundary

Research question unchanged. **Competitive means descriptive comparative characterization**: method means, Bayesian-minus-CQR difference in cycles, ratio when defined, per-engine width/miss decomposition. No binary competitiveness, equivalence, noninferiority, or practical-superiority decision. Difference sign identifies only which stored procedure scored lower here.

Omit populationbootstrap tests/CIs from proposed lock. Preserve adverse v0.4 findings:999/4,000unavailable diagnostics; lognormal sigma1.5coverage0.914/one-sided rejection0.112. Complete finite enumeration has no engine-samplingSE. PosteriorMCSE is conditional computational uncertainty; eight dependent pipeline perturbations describe sensitivity, not total variance. Unknown cutoff transport, small calibration, exposed development outcomes, unequal budgets/features, and synthetic-to-real gap prohibit broader inference.

## 5. Contract, reproducibility, and owner decision

[Proposed locked contract](02_proposed_locked_analysis_contract.md) fixes estimand,complete evaluation,principal/prior,CQR,cutoffs,failures,uncertainty,disclosures,and protected phases. No favorable secondary substitution.

Remaining requirements: owner acceptance of the restricted contract; separately authorized sensor/label phases; future schema/overlap/numerical audits; accessible hash-matched historical payload for full replay; publication novelty and redistribution review. NASA's [catalog](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data) specifies no license. Private custody is not redistribution clearance. Reproduction is component/source-and-retained-artifact based, not a certified one-command clean replay.

Environment:{p['environment_fingerprint']}; training:{pre['dataset_sha256']}; split:{pre['split_manifest_sha256']}; v0.5plan:{pre['plan_sha256']}. Exact source/artifact chain and compute are in [custody report](04_compute_reproducibility.md).

**READY FOR OWNER LOCK REVIEW.** A qualified negative or limited benchmark conclusion is admissible. No further remediation experiment is necessary for this recommendation. Final lock/test authorization remains with Raihan x Rei.
"""
save('01_prelock_resolution_memo.md',memo)
contract=r"""
# RP-001 | Proposed Locked Analysis Contract v0.5

**PROPOSED FOR OWNER LOCK REVIEW; PROTOCOL_DRAFTED.** Raihan x Rei retain final authorization. No official sensor/label access, confirmation, fallback, or public release is authorized now. This contract supersedes older prospective population-inference wording only upon owner acceptance; historical evidence/failures remain unchanged.

## Question, primary estimand, and competitive

Retain: “Is a compact hierarchical Bayesian predictor competitive in 90% interval score with calibrated CQR at the official FD001 unseen-engine endpoint, with engine-level uncertainty and audited dependence?”

For complete official cohort F (metadata expects N=100), one last-observed endpoint per engine, positive uncapped RUL y in cycles and pre-label stored intervals:
IS90(y,L,U)=U-L+20max(L-y,0)+20max(y-U,0).
D_F=(1/N)sum_F[IS90(y,L_B,U_B)-IS90(y,L_C,U_C)].
Lower is better. This estimand describes these realized stored predictions, dataset bytes, and fixed training/calibration procedures. Ideal exact-posterior score is a separate approximation target.

Competitive is descriptive: report both mean scores,signed D_F,ratio mean(B)/mean(C) when denominator>0,and paired decomposition. Negative D_F means only lower stored Bayesian mean score on this benchmark. No general superiority,equivalence,noninferiority,causal benefit of Bayesian inference,or practical utility. No5cycle margin;0.5cycle numerical tolerance and CQR tie tolerance are separate rules.

## Exact training split, eligibility, and cutoff

Authorized FD001 training fingerprint:100engines,20,631rows,26fields. IDs are metadata, never predictors. Seed RP001-20261008-v0.2; sort IDs by hex SHA256(seed+'|split|'+engine):first55fit,next15tune,last30calibration. One assigned C=30+int(SHA256(seed+'|cutoff|'+engine),16)%221. Eligible iff C<T, training terminal cycleT. No redraw,replace,cutoff search,or resampling for the canonical pipeline. Eligible43/13/25; refit56fit+tune; one target log(T-C) per engine. Disclose survival selection and historical100salt sensitivity; outcome-blind hashing is no stochastic-independence proof.

Use sensors only through C. Tuning preprocessing fits43eligible fitting prefixes; final preprocessing fits56eligible fit+tune prefixes. Equal total weight1/n per engine and1/(n*C) per row. Drop SD<=1e-8channels; PC1 sign largest-absolute loading positive; scale by sqrt(top eigenvalue). Bayes/CQR share saved refit maps. No calibration/test row fits global preprocessing. Input is log(age/100),PC sequence last min(30,C) actual observed cycles.

Official C is its last observed cycle, not a new pseudo-cutoff. No label-based C<Tfilter,min-history exclusion,or30..250restriction. Bayesian w=min(30,C),B=[1,t/30],t=-(w-1),...,0. Include short histories:w1level only,summary slope/residualSD0. CQR interpolation spans available observed positions only; repeat a single observation,never extrapolate. Unsupported input retains its engine and stops evaluation. No pooled test preprocessing.

## Bayesian principal model and prior

g|a~N(Gamma a,S), S=diag(tau)[[1,r_g],[r_g,1]]diag(tau).
z|g,theta~N(Bg,sigma_z^2K_rho),K_jk=rho^|j-k|.
log RUL|g,a,theta~N(a beta+gamma'g,sigma_r^2).
Integrate g exactly in full joint p(z,y|theta).

Freeze anchored_v04 independent working priors:
beta~N([log100,0],diag([.6,.5]^2));gamma_j~N(0,.25^2).
Every Gamma row has independent intercept/age SDvector[.5,.35], shared across rows.
tau_j~HalfNormal(.35);sigma_z/sigma_r~HalfNormal(.4).
eta_rho~N(0,.75^2);rho=tanh(eta_rho).
gcor_u~Beta(2,2);r_g=2gcor_u-1.
Adaptation followed exposed v0.3calibration and preceded v0.4science; no untouched-calibration claim or score-selected prior change.

Reuse exactly saved v04_main_r1/r2/r3:each4chainsx8,000retained;pool12chains/96,000equal-weight training-posterior draws. NC hashes in evidence manifest authoritative. The new high-rho fit is diagnostic, never a replacement. Each new engine updates theta separately:weights proportional p(z_i|theta);predict from exact conditional Gaussian y_i|z_i,a_i,theta mixture. No joint conditioning on other test engines. Quantiles .05/.50/.95 on log scale then exponentiate. This is uncertainty under fitted model, not whole-pipeline uncertainty.

No fresh training,newdraws,oracle,seed substitution,sampler substitution,or fallback is automatic. Any such material change requires reviewed pre-label amendment.

## CQR selection, calibration, and secondary ablations

Original twelve candidates:8GradientBoostingRegressor endpoint pairs,.05/.95,200trees,depth{1,2},leaf{5,10},rate{.03,.10},random_state20261008;4linear QuantileRegressor pairs,L1alpha{.001,.01,.1,1},fit-only StandardScaler.

Boost features [log age,endpointPC,OLSlevel,OLSslope per30,residualSD];linear [log age,30interpolatedPCs]. Same allowed prefixes, different maps/budgets. Select minimum uncalibrated meanIS90 on13tune;within.5cycle minimum forms ties. Prefer linear then strongerpenalty;boost shallowerdepth/largerleaf/smallerrate. Preserve all candidate failures and scores. Canonical selected gb-depth1-leaf10-lr0p1; no reselection/grid expansion.

Reuse saved selected endpoint/median refits on56 with refit maps (results/pilot/selected_comparator.joblib). Sort endpoint crossing prospectively. Median no conformalshift;report negative median limitation without label-informed repair.

Calibration25:s_i=max(rawL_i-y_i,y_i-rawU_i),k=ceil(26*.9)=24,q=max(0,s_(24));freeze correction in results/pilot/comparator_calibration.json (about19.987559cycles).
Final CQR [max(0,rawL-q),max(0,rawU+q)];finite/ordered required, zero lower allowed. This support projection is prespecified. No other clipping,capping,winsorization,or score truncation.

Secondary Bayesian+posthoc calibration uses existing pooled calibration quantiles and same nonnegative rank24expansion;freeze q in experiments/v0.4/analysis/principal_posthoc_calibration.json and lower projection0. Cannot replace primary. Saved broader1.5scale,rho0,contamination sensitivities remain development disclosures, no official-model tournament. Existing GaussianlogR reference optional secondary only;nonestimable/unavailable prediction retained. No fallback activation.

CQR theorem requires exchangeable compatible calibration/new scores with appropriate separation ([Romano et al.](https://arxiv.org/html/1905.03222v1)); not established for official cutoffs. Calibration exposure is disclosed. No guaranteed official90% or conditional coverage certificate.

## Protected phases and complete finite-benchmark evaluation

1. Owner approves exact contract/source/input manifest,numerical qualification,and omission of population inference;create signed/date-stamped lock record. Until then draft.
2. Separately authorized sensor phase:extract sensors only;check source/hash,26fields,finite data,positive contiguous cycles,unique engine-cycle keys,expected100engine IDs/namespaces. Train-test prefix duplication/overlap audit and existing near-duplicate heuristic (>=30common cycles,mean normalizedRMSE<=.02,maxchannel<=.10),with heuristic limitations. Possible overlap/schema/count mismatch stops for owner review;never drop engine/redefine cohort. No label-member access.
3. Apply fixed procedures perengine;retain completeNrow ledger including failures. Pass prediction/numerical guards;hash/freeze intervals,medians,IDs,corrections,posterior/source/diagnostic digests and sensor audit before label authorization.
4. Separately authorized labels only after prediction freeze:validate exactN alignment,source/hash,and finite positive uncapped RUL. No label-driven feature,selection,model,cutoff,prediction,or numerical remediation.
5. Score all pairs float64;store widths,20xmiss penalties,fullpaired differences. Compensated sum for D_F;finite scores/sum required. Missing/nonfinite primary pair makes **UNAVAILABLE**, with full failure ledger. No subset primary mean,drop/imputation/replacement/capping.

Public label availability does not override owner separation. Protection is procedural; independent encrypted vault is not established. All future stages remain unauthorized now.

## Prospectively fixed numerical policy

Before labels,principal physical/auxiliary diagnostics finite:Rhat<1.01,bulk/tailESS>=400,divergences0,BFMI>.3,depth12saturation<=.01. AllNengine x3quantiles require weightESS>=1000,influenceESS>=400,approximate upperMCSE<=.5cycles at both250/500batches;tail=.05/(N*3*2). Positive finite mixture variance/density/normalization;weighted CDF root residual<=1e-10;finite ordered cycle endpoints. Brent bracket min(mu-12SD)..max(mu+12SD),xtol1e-10;failure retained with no result-selected bracket/draw repair.

All3independent-fit pair comparisons xNengine x3quantiles must satisfy absdifference<=z*sqrt(MCSE_a^2+MCSE_b^2),MCSE=max across2batches,z=Phi^-1(1-.05/(2*9*N)). Zero/nonfinite denominator fails. Any input,prediction,MCMC,or quantile-guard failure stops before labels;retain ledger, no extra draws,seeds,drop/impute/cap.

After labels, for logquantileq,Q=exp(q),componentCDF F_theta,positive mixture log-densityf,and shared chain/draw/engine indices:
X_ij=-Q_ij*w_i*(F_theta_i(q_ij)-p_j)/(mean(w_i)*f_i).
g_L=-1+20I[y<L],g_U=1-20I[y>U].
H=(1/N)sum_i(g_Li X_iL+g_Ui X_iU).
Use joint chainwise nonoverlapping batch covariance250/500 and pooled projection, preserving cross-engine/endpoint dependence. CQR has no posterior MC error conditional on fixed fit/correction;H propagates posterior approximation to D_F. Satterthwaite upperMCSE uses tail.05/2.

Report both scoreMCSE/uppers,batch sensitivity,three exact independent-fit contrasts/spread. Undefined/nonfinite upper,upper>.5cycles,or any label within3endpoint-upperMCSEs of either endpoint yields **NUMERICALLY_QUALIFIED** ideal posterior-score/ranking interpretation. Retain complete stored-prediction D_F and flags;no post-label rerun/repair without owner review.

At kink, delta approximation may fail. Conditional sensitivity abs(changeD_F)<=19/Nsum(epsilon_L+epsilon_U) holds **if actual endpoint errors lie within those radii**. Approximate MCSE is no absolute-error radius/finite coverage guarantee; substituting MCSE radii illustrates sensitivity without certified probabilistic coverage. .5cycle criterion is numerical resolution.

## Uncertainty reporting, disclosures, and publication limits

Report exact finite means,D_F,ratio when defined,perengine differences,widths,miss penalties,descriptive medianMAE/RMSE/bias,and exact empirical coverage fraction. No Wilson/binomialCI,engine-samplingSE,populationbootstrap,p-value,or practical equivalence claim for finite enumeration.

Fitted-model uncertainty,numericalMCSE,and observed pipeline sensitivity are distinct. None estimates unconditional repeated-training/calibration variation. Engine iid assumptions are unnecessary for the finite sum; shared posterior dependence is retained in computational uncertainty.

Always disclose original highrho3FAIL/bounded inquiryPASS;physical ridge/weak nuisance separation;v0.3precisionFAIL;25cal/13tune;calibration exposure/prior adaptation;8dependent fullpipeline perturbations and CQRwinner changes;bootstrap999unavailable/adverse OC;unequal features/search/compute;unknown official cutoff exchangeability;synthetic-to-real gap;approximate guards;all failures. Poor or limited results are admissible.

No novelty/operational reliability claim. Primary-source novelty review and data-rights/redistribution clearance before publication. [NASA catalog](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data) specifies no license;private custody is no public rights certification. Supply exact source/environment64package lock,input/artifact hashes,retained raw diagnostics/failures.33historical ignored payloads remain necessary for complete historical replay;one-command clean replay not certified. No new experiment automatically authorized.
"""
save('02_proposed_locked_analysis_contract.md',contract)
save('README.md',"""
# RP-001 v0.5 | Owner pre-lock review

**READY FOR OWNER LOCK REVIEW**, restricted descriptive finite-benchmark claim. Protocol draft; no official sensors/labels or confirmatory evaluation authorized.

Start with [Resolution Memo](01_prelock_resolution_memo.md) and [Proposed Locked Contract](02_proposed_locked_analysis_contract.md). Support: [direct mathematics](03_mathematical_validity.md), [compute/custody](04_compute_reproducibility.md), [prospective plan](prospective_resolution_plan.md), [risk matrix](../../research/v0.5/blocker_disposition.json), [fit](../../experiments/v0.5/registry/v05_highrho_innovation.json), [preflight](../../experiments/v0.5/analysis/math_preflight.json), [score propagation](../../experiments/v0.5/analysis/score_propagation.json), [59tests](../../logs/v0.5/verification_tests.xml), [handoff](research_lead_handoff.json), [delivery receipt](../../logs/v0.5/delivery_receipt.json).

One equivalent-posterior inquiry, no fallback/extra campaign. Historical FAILs remain. Owner-reviewed scientific baseline61b4c2c63cbad6c1b9bd99168e33d1367aa180bc.
""")
print(json.dumps(dict(memo_words=len(memo.split()),contract_words=len(contract.split()),plan_sha256=sha('configs/v0.5/resolution_plan.json'))))
