# RP-001 | Proposed Locked Analysis Contract v0.5

**PROPOSED FOR OWNER LOCK REVIEW; PROTOCOL_DRAFTED.** Raihan x Rei retain final authorization. No official sensor/label access, confirmation, fallback, or public release is authorized now. This contract supersedes older prospective population-inference wording only upon owner acceptance; historical evidence/failures remain unchanged.

## Question, primary estimand, and competitive

Retain: “Is a compact hierarchical Bayesian predictor competitive in 90% interval score with calibrated CQR at the official FD001 unseen-engine endpoint, with engine-level uncertainty and audited dependence?”

For complete official cohort F (metadata expects N=100), one last-observed endpoint per engine, positive uncapped RUL y in cycles and pre-label stored intervals:
IS90(y,L,U)=U-L+20max(L-y,0)+20max(y-U,0).
D_F=(1/N)sum_F[IS90(y,L_B,U_B)-IS90(y,L_C,U_C)].
Lower is better. This estimand describes these realized stored predictions, dataset bytes, and fixed training/calibration procedures. Ideal exact-posterior score is a separate approximation target.

Competitive is descriptive: report both mean scores,signed D_F,ratio mean(B)/mean(C) when denominator>0,and paired decomposition. Negative D_F means only lower stored Bayesian mean score on this benchmark. No general superiority,equivalence,noninferiority,causal benefit of Bayesian inference,or practical utility. No5cycle margin;0.5 cycles numerical tolerance and CQR tie tolerance are separate rules.

## Exact training split, eligibility, and cutoff

Authorized FD001 training fingerprint:100 engines,20,631 rows,26 fields. IDs are metadata, never predictors. Seed RP001-20261008-v0.2; sort IDs by hex SHA256(seed+'|split|'+engine):first 55 fit,next 15 tune,last 30 calibration. One assigned C=30+int(SHA256(seed+'|cutoff|'+engine),16)%221. Eligible iff C<T, training terminal cycleT. No redraw,replace,cutoff search,or resampling for the canonical pipeline. Eligible 43/13/25; refit 56 fit+tune; one target log(T-C) per engine. Disclose survival selection and historical 100 salt sensitivity; outcome-blind hashing is no stochastic-independence proof.

Use sensors only through C. Tuning preprocessing fits 43 eligible fitting prefixes; final preprocessing fits 56 eligible fit+tune prefixes. Equal total weight1/n per engine and1/(n*C) per row. Drop SD <= 1e-8 channels; PC1 sign largest-absolute loading positive; scale by sqrt(top eigenvalue). Bayes/CQR share saved refit maps. No calibration/test row fits global preprocessing. Input is log(age/100),PC sequence last min(30,C) actual observed cycles.

Official C is its last observed cycle, not a new pseudo-cutoff. No label-based C<T filter,minimum history exclusion,or30..250 restriction. Bayesian w=min(30,C),B=[1,t/30],t=-(w-1),...,0. Include short histories:w=1 level only,summary slope/residual SD=0. CQR interpolation spans available observed positions only; repeat a single observation,never extrapolate. Unsupported input retains its engine and stops evaluation. No pooled test preprocessing.

## Bayesian principal model and prior

g|a~N(Gamma a,S), S=diag(tau)[[1,r_g],[r_g,1]]diag(tau).
z|g,theta~N(Bg,sigma_z^2K_rho),K_jk=rho^|j-k|.
log RUL|g,a,theta~N(a beta+gamma'g,sigma_r^2).
Integrate g exactly in full joint p(z,y|theta).

Freeze anchored_v04 independent working priors:
beta~N([log100,0],diag([.6,.5]^2));gamma_j~N(0,.25^2).
Every Gamma row has independent intercept/age SD vector[.5,.35], shared across rows.
tau_j~HalfNormal(.35);sigma_z/sigma_r~HalfNormal(.4).
eta_rho~N(0,.75^2);rho=tanh(eta_rho).
gcor_u~Beta(2,2);r_g=2gcor_u-1.
Adaptation followed exposed v0.3 calibration and preceded v0.4 science; no untouched-calibration claim or score-selected prior change.

Reuse exactly saved v04_main_r1/r2/r3:each4 chainsx8,000retained;pool 12 chains/96,000 equal-weight training-posterior draws. NC hashes in evidence manifest authoritative. The new high-rho fit is diagnostic, never a replacement. Each new engine updates theta separately:weights proportional p(z_i|theta);predict from exact conditional Gaussian y_i|z_i,a_i,theta mixture. No joint conditioning on other test engines. Quantiles .05/.50/.95 on log scale then exponentiate. This is uncertainty under fitted model, not whole-pipeline uncertainty.

No fresh training,new draws,oracle,seed substitution,sampler substitution,or fallback is automatic. Any such material change requires reviewed pre-label amendment.

## CQR selection, calibration, and secondary ablations

Original twelve candidates:8 GradientBoostingRegressor endpoint pairs,.05/.95,200 trees,depth {1,2},leaf {5,10},rate {.03,.10},random_state20261008;4 linear QuantileRegressor pairs,L1 alpha{.001,.01,.1,1},fit-only StandardScaler.

Boost features [log age,endpoint PC,OLS level,OLS slope per30,residual SD];linear [log age,30 interpolated PCs]. Same allowed prefixes, different maps/budgets. Select minimum uncalibrated mean IS90 on13 tune engines;within 0.5 cycles minimum forms ties. Prefer linear then stronger penalty;boost shallower depth / larger leaf / smaller rate. Preserve all candidate failures and scores. Canonical selected gb-depth1-leaf10-lr0p1; no reselection/grid expansion.

Reuse saved selected endpoint/median refits on 56 with refit maps (results/pilot/selected_comparator.joblib). Sort endpoint crossing prospectively. Median no conformalshift;report negative median limitation without label-informed repair.

Calibration 25:s_i=max(rawL_i-y_i,y_i-rawU_i),k=ceil(26*.9)=24,q=max(0,s_(24));freeze correction in results/pilot/comparator_calibration.json (about19.987559 cycles).
Final CQR [max(0,rawL-q),max(0,rawU+q)];finite/ordered required, zero lower allowed. This support projection is prespecified. No other clipping,capping,winsorization,or score truncation.

Secondary Bayesian+posthoc calibration uses existing pooled calibration quantiles and same nonnegative rank 24 expansion;freeze q in experiments/v0.4/analysis/principal_posthoc_calibration.json and lower projection0. Cannot replace primary. Saved broader 1.5 scale,rho0,contamination sensitivities remain development disclosures, no official-model tournament. Existing Gaussian log R reference optional secondary only;nonestimable/unavailable prediction retained. No fallback activation.

CQR theorem requires exchangeable compatible calibration/new scores with appropriate separation ([Romano et al.](https://arxiv.org/html/1905.03222v1)); not established for official cutoffs. Calibration exposure is disclosed. No guaranteed official 90% or conditional coverage certificate.

## Protected phases and complete finite-benchmark evaluation

1. Owner approves exact contract/source/input manifest,numerical qualification,and omission of population inference;create signed/date-stamped lock record. Until then draft.
2. Separately authorized sensor phase:extract sensors only;check source/hash,26 fields,finite data,positive contiguous cycles,unique engine-cycle keys,expected 100 engine IDs/namespaces. Train-test prefix duplication/overlap audit and existing near-duplicate heuristic (≥30 common cycles,mean normalizedRMSE<=.02,max channel<=.10),with heuristic limitations. Possible overlap/schema/count mismatch stops for owner review;never drop engine/redefine cohort. No label-member access.
3. Apply fixed procedures per engine;retain complete N row ledger including failures. Pass prediction/numerical guards;hash/freeze intervals,medians,IDs,corrections,posterior/source/diagnostic digests and sensor audit before label authorization.
4. Separately authorized labels only after prediction freeze:validate exact N alignment,source/hash,and finite positive uncapped RUL. No label-driven feature,selection,model,cutoff,prediction,or numerical remediation.
5. Score all pairs float64;store widths,20 x miss penalties,fullpaired differences. Compensated sum for D_F;finite scores/sum required. Missing/nonfinite primary pair makes **UNAVAILABLE**, with full failure ledger. No subset primary mean,drop/imputation/replacement/capping.

Public label availability does not override owner separation. Protection is procedural; independent encrypted vault is not established. All future stages remain unauthorized now.

## Prospectively fixed numerical policy

Before labels,principal physical/auxiliary diagnostics finite:Rhat<1.01,bulk/tail ESS>=400,divergences0,BFMI>.3,depth 12saturation<=.01. All N engines x 3 quantiles require weightESS>=1000,influenceESS>=400,approximate upper MCSE<=0.5 cycless at both 250/500 batches;tail=.05/(N*3*2). Positive finite mixture variance/density/normalization;weighted CDF root residual<=1e-10;finite ordered cycle endpoints. Brent bracket min(mu-12SD)..max(mu+12SD),xtol=1e-12 (frozen v0.4 precision implementation);failure retained with no result-selected bracket/draw repair.

All 3 independent-fit pair comparisons x N engines x 3 quantiles must satisfy absdifference<=z*sqrt(MCSE_a^2+MCSE_b^2),MCSE=max across2batches,z=Phi^-1(1-.05/(2*9*N)). Zero/nonfinite denominator fails. Any input, prediction,MCMC,or quantile-guard failure stops before labels;retain ledger, no extra draws,seeds,drop/impute/cap.

After labels, for logquantileq,Q=exp(q),componentCDF F_theta,positive mixture log-densityf,and shared chain/draw/engine indices:
X_ij=-Q_ij*w_i*(F_theta_i(q_ij)-p_j)/(mean(w_i)*f_i).
g_L=-1+20I[y<L],g_U=1-20I[y>U].
H=(1/N)sum_i(g_Li X_iL+g_Ui X_iU).
Use joint chainwise nonoverlapping batch covariance250/500 and pooled projection, preserving cross-engine/endpoint dependence. CQR has no posterior MC error conditional on fixed fit/correction;H propagates posterior approximation to D_F. Satterthwaite upper MCSE uses tail.05/2.

Report both score MCSE/uppers,batch sensitivity,three exact independent-fit contrasts/spread. Undefined/nonfinite upper,upper>0.5 cycless,or any label within3 endpoint upper MCSEs of either endpoint yields **NUMERICALLY_QUALIFIED** ideal posterior-score / ranking interpretation. Retain complete stored-prediction D_F and flags;no post-label rerun/repair without owner review.

At kink, delta approximation may fail. Conditional sensitivity abs(changeD_F)<=19/Nsum(epsilon_L+epsilon_U) holds **if actual endpoint errors lie within those radii**. Approximate MCSE is no absolute-error radius/finite coverage guarantee; substituting MCSE radii illustrates sensitivity without certified probabilistic coverage. 0.5 cycles criterion is numerical resolution.

## Uncertainty reporting, disclosures, and publication limits

Report exact finite means,D_F,ratio when defined,per engine differences,widths,miss penalties,descriptive medianMAE/RMSE/bias,and exact empirical coverage fraction. No Wilson/binomialCI,engine-samplingSE,populationbootstrap,p-value,or practical equivalence claim for finite enumeration.

Fitted-model uncertainty,numericalMCSE,and observed pipeline sensitivity are distinct. None estimates unconditional repeated-training/calibration variation. Engine iid assumptions are unnecessary for the finite sum; shared posterior dependence is retained in computational uncertainty.

Always disclose original high-rho3 FAIL/bounded inquiry PASS;physical ridge/weak nuisance separation;v0.3 precision FAIL;25 calibration / 13 tuning engines;calibration exposure/prior adaptation;8 dependent fullpipeline perturbations and CQR winner changes;bootstrap 999 unavailable/adverse OC;unequal features/search/compute;unknown official cutoff exchangeability;synthetic-to-real gap;approximate guards;all failures. Poor or limited results are admissible.

No novelty/operational reliability claim. Primary-source novelty review and data-rights/redistribution clearance before publication. [NASA catalog](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data) specifies no license;private custody is no public rights certification. Supply exact source/environment64 package lock,input/artifact hashes,retained raw diagnostics/failures.33 historical ignored payloads remain necessary for complete historical replay;one-command clean replay not certified. No new experiment automatically authorized.
