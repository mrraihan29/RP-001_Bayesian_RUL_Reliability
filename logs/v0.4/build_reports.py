"""Assemble v0.4 owner reports from recorded scientific results; no model selection."""
import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
R=Path.cwd();D=R/'docs/v0.4';A=R/'experiments/v0.4/analysis'
def read(p):return json.loads((R/p).read_text(encoding="utf8"))
def doc(name,text):(D/name).write_text(text+'\n',encoding='utf8')
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(x) for x in r)+' |' for r in rows])
def f(x):return f'{x:.6f}' if isinstance(x,(float,np.floating)) else str(x)
s=read('experiments/v0.4/analysis/summary.json');precision=s['precision'];mc=read('experiments/v0.4/precision/v04_precision_mcse_validation.json');groups=mc['summary']['groups'];mcpass=all(g['plan_criterion_checks']['both'] for g in groups)
records=[read(f"experiments/v0.4/registry/{r['run_id']}.json") for r in read('configs/v0.4/remediation_plan.json')['runs']]
records=[read('experiments/v0.4/registry/'+r['run_id']+'_infra1.json') if r['status']=='failed' and (R/'experiments/v0.4/registry'/f"{r['run_id']}_infra1.json").exists() else r for r in records]
num_pass=precision is not None and precision['numerical_gate']=='PASS' and mcpass
rec='A. READY FOR OWNER PROTOCOL-LOCK REVIEW' if num_pass and not s['failed_run_ids'] and not s['mcmc_failed_diagnostics'] else 'B. REVISE AGAIN'
summary_status=dict(version='0.4',recommendation=rec,numerical_precision_pass=num_pass,mcse_estimator_validation_pass=mcpass,confirmatory_authorized=False,official_test_access=False,protocol_lock_authorized=False,protocol_status='PROTOCOL_DRAFTED')
(R/'research/v0.4').mkdir(parents=True,exist_ok=True)
(R/'research/v0.4/gate_summary.json').write_text(json.dumps(summary_status,indent=2)+'\n')
qrows=read('experiments/v0.4/analysis/principal_precision_all25.json')['results']
summaryrows=[]
for e in sorted(set(r['engine'] for r in qrows)):
    row=[r for r in qrows if r['engine']==e]
    summaryrows.append([e]+[f(max(b['approximate_upper_quantile_rul_mcse'] for b in r['batch_size_results'])) for r in row]+[f(min(r['weight_ess'] for r in row)),all(r['gate_pass'] for r in row)])
vg=[[g['rho'],g['probability'],g['batch_size'],f(g['rms_actual_error_over_rms_estimated_mcse']),f(g['empirical_1p96_mcse_coverage']),g['plan_criterion_checks']['both']] for g in groups]
doc('02_numerical_precision_remediation.md',f'''# Numerical precision remediation report v0.4

The historical v0.3 maximum approximate quantile MCSE **0.728972 cycles** exceeded **0.5**. That failure remains unchanged. The v0.4 numerical gate is **{'PASS' if num_pass else 'FAIL'}** after the prospectively fixed study; no threshold relaxation, winning-subset selection, extra draws or seed retry occurred.

Principal fits use three independent seeds, four chains each and8,000 retained draws/chain:96,000 total/12 independent chains. All25 original eligible calibration engines, including86, and all75 .05/.50/.95 quantiles are assessed at250 and500 batch sizes. This is a sensor-only training-development precision study, without official test predictions or comparative performance evaluation.

Maximum approximate upper MCSE: **{f(precision['max_upper_mcse_cycles'])} cycles**. Minimum weight ESS {f(precision['min_weight_ess'])}; minimum influence ESS {f(precision['min_influence_ess'])}. The separate all-quantile estimator/replication/oracle gate is {precision['numerical_gate']}; known-target estimator validation is {'PASS' if mcpass else 'FAIL'}. An overall acceptance requires both, not just a favorable maximum.

{table(['Engine','upperMCSE p.05','upperMCSE p.50','upperMCSE p.95','weightESS','engine gate'],summaryrows)}

## Estimator and uncertainty of its uncertainty

The weighted mixture CDF is solved directly. The ratio influence w(F_theta(q)-p) incorporates importance-weight normalization. Chain-wise nonoverlapping batch means estimate serial long-run variance, divided by squared predictive density; exponentiation converts log-scale error to cycles. Weight ESS is not autocorrelation-adjusted; influence ESS is quantity-specific. Satterthwaite degrees of freedom and a lower chi-square quantile at.05/(25×3×2) provide an approximate upper variance guard. Both250/500 guards must satisfy.5, along with weightESS>=1000,influenceESS>=400 and MCMC criteria.

This upper MCSE is an asymptotic approximation, not a finite-sample absolute-error bound or a rigorous simultaneous confidence limit. The guard assumes stable chains, adequate moments/mixing, positive smooth density and sufficiently independent Gaussian batch means. Estimated density and normalizer bring additional approximation. The lead derived the formula and independently checked variance/density algebra in [report08](08_independent_mathematical_reverification.md).

## Independent replication and sensor oracles

All225 pairwise seed/engine/quantile comparisons use the prespecified Bonferroni normal threshold z={f(precision['replication_z_threshold'])}, with each pair's combined MCSE. Compatible comparisons: {sum(r['compatible'] for r in precision['replication_comparisons'])}/225. Maximum observed standardized difference: {f(max(r['z'] for r in precision['replication_comparisons']))}.

Three joint-posterior sensor oracles were selected before results:engine11(first deterministic),61(lowest historical weightESS),86(worst historical MCSE). Each uses4chains×16,000 draws, adds that engine's sensors only to the56-engine likelihood, then predicts without double-weighting theta. All9 comparisons use z={f(precision['oracle_z_threshold'])}; compatible {sum(r['compatible'] for r in precision['oracle_comparisons'])}/9. Their full MCSE and MCMC diagnostics are retained, including every quantile, in precision_summary.json. This cannot establish accuracy for every possible future sensor prefix.

## Known-target correlated-chain validation

The stationary AR(1) base has theta~N(0,1); observing z1 with unit variance gives theta|z~N(.5,.5). Predictive logR~N(log100+.1,.11) supplies exact lognormal quantiles. Each rho has200 independent replicates, four chains×2,000 draws, rootseed48001. The prospective criteria are RMSactualerror/RMSreportedMCSE in[.75,1.33] and normal95%MC interval coverage>=.90, checked at both batch sizes, for every rho/quantile. Empirical coverage has binomial uncertainty, with Wilson95% intervals in the full evidence; a200-replicate point pass does not certify universal calibration.

{table(['rho','p','batch','RMSerror/MCSE','MC95%coverage','both criteria'],vg)}

The retrospective batch-means analysis of the historical refit remains explicitly retrospective and cannot erase its historical failed decision. Current numerical PASS/FAIL applies to the new prior and the specified96,000-draw procedure, not retrospectively to v0.3 or to any future official endpoint.

Evidence: [all25 precision records](../../experiments/v0.4/analysis/principal_precision_all25.json), [independent replications](../../experiments/v0.4/analysis/principal_replication_precision.json), [oracle comparisons](../../experiments/v0.4/analysis/precision_summary.json), [600 known-target replications](../../experiments/v0.4/precision/v04_precision_mcse_validation.json), [historical retrospective diagnostic](../../experiments/v0.4/analysis/v03_retrospective_precision.json).
''')
priors=read('experiments/v0.4/analysis/prior_predictive.json')['policies'];pr=[]
for name,p in priors.items():
    for i,c in enumerate(p['ages']):pr.append([name,c,f(p['rul_quantiles'][3][i]),f(p['rul_quantiles'][4][i]),f(p['prob_gt1000'][i]),f(p['prob_gt5000'][i]),f(p['log_rul_variance'][i]),f(p['analytic_log_rul_variance'][i])])
check=read('experiments/v0.4/analysis/v04_main_r1_checks.json');info=[[v['parameter'],f(v['prior_sd']),f(v['posterior_sd']),f(v['sd_ratio'])] for v in check['prior_posterior_sd']]
doc('03_bayesian_prior_plausibility.md',f'''# Bayesian prior plausibility report v0.4

The principal anchored_v04 policy was committed before any new scientific predictions. Its development change follows v0.3 calibration exposure and is explicitly adaptive; it was not selected by new calibration scores. The broader and noise policies are robustness diagnostics, never a winner search.

## Working scale policy and elicitation limits

beta=[intercept,log-age effect] has mean[log100,0] and SD[.6,.5]. At zero latent contribution, beta0 alone has median95% range about31–324cycles. The100-cycle center represents a hundreds-of-cycles engineering scale, consistent with the prior project convention and training lifetime128–362cycle scale; it does not identify a population RUL median. Age is dimensionless log(C/100); SD.5 allows meaningful directionally symmetric age effects without treating age as causal.

Gamma row SD[.5,.35] expresses moderate PC-level/per30cycle-slope changes with age. tau half-normal.35 describes between-engine random level/slope scales in a unit-PC representation. gamma SD.25 expresses logR coupling to those nuisance latent coordinates and permits either sign. sigma_z half-normal.4 describes standardized sensor residual scale; sigma_r half-normal.4 represents multiplicative response noise on logR. These scales are proper regularizing assumptions, not physical support limits or expert-certified reliability priors. No latent state has a physiological interpretation.

rho=tanh(N(0,.75²)) permits positive/negative residual autocorrelation with no exact boundary mass. LKJeta2 in dimension2 is2Beta(2,2)-1, a symmetric proper latent correlation policy with variance.2. Correlation priors stay fixed under the1.5× broad sensitivity, which broadens beta/gamma/Gamma/tau/sigma_z/sigma_r scale priors. High-rho and confounding stress regimes challenge inference beyond typical prior central mass. Full domain elicitation remains absent; this is defensible only as a transparent benchmark-model working policy.

## Actual prior predictive distribution

12,000 draws per fixed policy use roots49001–49003, ages30/100/250, independent latent and residual draws. Marginal logR is a product/mixture distribution; its tails are simulated, not inferred from a Gaussian variance shortcut. The lead-derived analytic log variance supplies an independent moment oracle. Finite Monte Carlo fluctuations are retained; the table is an assessment of scale, not a hard accept/reject support bound.

{table(['Policy','age','R95','R99','P R>1000','P R>5000','empirical Var logR','analytic Var logR'],pr)}

The prior still places mass on RUL outside the training lifetime range; RUL positivity is structural, whereas an upper bound is not. A narrower principal prior does not establish that its intervals are calibrated or superior. The historical broader tails are shown for comparison without erasing the earlier lack of elicitation.

## Data information and parameter coupling

The following information assessment uses the first principal fit and compares posterior SD with the same principal prior SD. It is not a measure of causal identifiability, and ratios near1 can signal weak information; ratios above1 can also reflect posterior geometry or prior-data conflict. Correlations and all per-run contraction records are retained.

{table(['coordinate','prior SD','posterior SD','ratio'],info)}

Largest posterior couplings: {', '.join(v['a']+' ↔ '+v['b']+' ('+f(v['correlation'])+')' for v in check['strongest_correlations'][:5])}. Assess those alongside repeated recovery and the structural/practical distinction in report04. The model's predictive distribution may be more informed than individual nuisance parameters; this does not authorize interpreting weak parameters as physical health effects.

## Prespecified sensitivity

The fixed broader/rho0/contamination runs retain their own convergence, predictive maps and all failures. Compare endpoint changes descriptively without using the original25 calibration RULs to select a prior. Bayesian+posthoc calibration is secondary and exploratory. Numerical precision of these smaller sensitivity fits is not automatically the principal96,000-draw precision; small differences cannot be interpreted as scientifically resolved effects.

Evidence: [full prior checks](../../experiments/v0.4/analysis/prior_predictive.json), [information and coupling](../../experiments/v0.4/analysis/v04_main_r1_checks.json), [prediction sensitivity](../../experiments/v0.4/analysis/sensitivity_prediction_maps.json), [frozen policy](../../configs/v0.4/remediation_plan.json).
''')
rows=[]
for regime,v in s['synthetic'].items():
    ps=v['parameter_summary'];rows.append([regime,v['n_completed'],v['n_mcmc_pass'],f(min(p['covered95']['proportion'] for p in ps.values())),f(max(p['max_abs_z'] for p in ps.values())),f'{v["predictive_covered"]}/{v["n_predictive"]}'])
rows2=[[r['run_id'],f(r.get('diagnostics',{}).get('rhat_max')),f(r.get('diagnostics',{}).get('bulk_ess_min')),f(r.get('diagnostics',{}).get('tail_ess_min')),r.get('diagnostics',{}).get('acceptance',r['status'])] for r in records]
doc('04_identifiability_synthetic_validation.md',f'''# Identifiability and synthetic validation report v0.4

Structural identification is generically established under fixed full-rank age/basis, w>=6, positive sensor noise/covariance and |rho|<1; the direct lead proof and numerical covariance inversion are in report08. This says population moments uniquely determine model coordinates. It does not ensure accurate finite-sample estimates, good MCMC, prediction accuracy or interval coverage.

## Targeted repeated recovery

Four fixed-truth datasets per regime use56 training engines and20 independently generated assessment engines. Regimes:regularrho.5; highrho.95; weakgamma[-.03,.02]; confoundedrho.8 with stronger age-linked latent effects and sensor noise.6/response noise.15. Seeds and all arrays/truths are saved. Local integer IDs are namespaces within independent generated datasets, not reused physical engines or model covariates. No official data enter synthetic recovery.

{table(['Regime','completed','MCMC pass','minimum coordinate recovery95 fraction','maximum |mean-truth|/posteriorSD','predictive covered/n'],rows)}

Recovery fractions use only four repeats per regime. Their Wilson intervals are broad (even4/4 has a lower95% limit around.51), so neither apparent95% agreement nor a miss certifies calibration or nonidentification. The reported maximum standardized error preserves poor cases. Every14-coordinate estimate/interval and parameter-coupling assessment is retained, including every prior/posterior SD ratio. Independent20-engine predictive checks integrate the full per-engine sensor update and report coverage/Wilson, median RMSE and mean interval score. Synthetic score values are model diagnostics, not evidence of Bayesian superiority over CQR or official benchmark performance; they still include finite MCMC approximation error.

## Practical identification and fallback

Second-difference covariance c2=sigma_z²(1-rho)^4 becomes tiny as rho approaches1; inversion is ill-conditioned. Small gamma, limited age spread, Gamma/beta/gamma coupling and nearly singular S can leave nuisance effects weakly informed even when sampling diagnostics pass. A compact model can support transparent benchmark predictions while remaining unsuitable for physical-state interpretation. Report uncertainty and coupling; do not equate posterior contraction or Rhat with identification.

SBC was considered but not performed. The bounded16-fit plan targets specified difficult fixed truths rather than prior-wide algorithmic calibration. Four repeats do not supply precise recovery coverage. A future SBC study would need a separately authorized plan and broader prior/parameter draws; this package makes no SBC claim.

The predeclared fallback fixesrho0 andr_g0 under anchored priors; it is not automatically fitted or substituted after these results. If principal prediction precision/model interpretation remains blocking, returnB/C for owner review before a new principal procedure. Fixed sensitivityrho0 alone is not evidence accepting that two-correlation fallback.

## Sampling evidence and posterior predictive checks

{table(['Run','Rhat max','bulkESS min','tailESS min','diagnostic'],rows2)}

All convergence thresholds were set before the runs. Auxiliary variables gcor_u/eta_rho, divergences, BFMI and depth saturation are in each immutable run record. Posterior-predictive checks use1,000 parameter draws from principal fit1 and assess conditional response and joint sensor/response moments with seed51001. These are fitted-model checks, not external validity or independent calibration. Report every observed statistic and replicated quantile/tail area; a PPC discrepancy remains a modeling limitation, not a reason to tune on the calibration cohort.

Evidence: [summary and coordinate recovery](../../experiments/v0.4/analysis/summary.json), all `experiments/v0.4/analysis/v04_syn_*_checks.json`, [PPC](../../experiments/v0.4/analysis/posterior_predictive.json), exact synthetic NPZ/NC arrays and seeds in the run registry, [direct verification](08_independent_mathematical_reverification.md).
''')
# Risk IDs and severities remain immutable; scoped dispositions do not erase risks.
old=read('research/pilot_risk_register_v0.3.json');risks=[]
choices={'R01':('MITIGATED BY CLAIM RESTRICTION','Exact finite-benchmark target; no transported population/conformal claim. Official cutoff mechanism remains unaudited.','05_estimand_cutoff_transport.md'),
'R02':('STILL BLOCKED' if s['mcmc_failed_diagnostics'] else 'MITIGATED BY CLAIM RESTRICTION','Generic identification proof does not remove high-rho sampling failure. Nuisance interpretation is restricted; one failed stress fit prevents claiming robust sampler behavior and requires prospective remedy.','04_identifiability_synthetic_validation.md'),
'R03':('RESOLVED' if num_pass else 'STILL BLOCKED','Prespecified all25/75 quantile MCSE, dependence-adjusted upper guards, independent replications/oracles and known-target validation. Only tested training cases; future endpoints require own guard.' if num_pass else 'At least one prespecified precision/validation criterion failed; cannot recommend lock. No threshold change or favorable retry.','02_numerical_precision_remediation.md'),
'R06':('MITIGATED BY CLAIM RESTRICTION','Train-only guarded imports and prefix tests; calibration exposure disclosed; official data unopened. Future official integrity/overlap audits require separate access and remain deferred.','01_updated_research_protocol.md'),
'R17':('STILL BLOCKED','Owner authorization for final protocol/test/confirmatory work absent. This is a governance gate, not permission supplied by scientific review.','11_prelock_recommendation.md')}
for r in old['risks']:
    row=dict(r)
    status,disp,evidence=choices.get(r['risk_id'],('MITIGATED BY CLAIM RESTRICTION',r['disposition']+'; benchmark-development scope retained.','10_risks_assumptions_decisions.md'))
    row.update(status=status,disposition=disp,evidence=evidence,remaining_uncertainty='Original risk and severity retained; scope qualification does not prove a excluded claim.')
    risks.append(row)
register=dict(version='0.4',owner='Raihan × Rei',risk_id_policy=old['risk_id_policy'],risks=risks,recommendation=rec)
(R/'research/v0.4/risk_register.json').write_text(json.dumps(register,indent=2,ensure_ascii=False)+'\n')
riskrows=[[r['risk_id'],r['severity'],r['statement'],r['status'],r['disposition']] for r in risks]
doc('10_risks_assumptions_decisions.md',f'''# Risk, assumption and decision registers v0.4

OriginalR01–R15 and their severities are preserved; v0.3R16/R17 are retained. Status applies to the proposed restricted primary claim, not a claim that every broader risk vanished. Recommendation: **{rec}**. Governance remains PROTOCOL_DRAFTED.

{table(['ID','severity','risk','status','evidence / remaining uncertainty'],riskrows)}

The original A01–A11 and D01–D07 tables remain authoritative historical records in [v0.3](../v0.3/08_risks_assumptions_decisions.md); their IDs are not reused. Current updates: A01 engine independence remains unproved and is not required for finite enumeration; A02 terminal cycle is a dataset convention; A03 alive/positive/uncapped training targets verified; A04 prefix availability tested, official checks deferred; A05 AR/local-linear are working models; A06 PC effects have no physical-state meaning; A07 bootstrap-t is a secondary conditional diagnostic with demonstrated stress limits; A08 canonical split/salts/seeds fixed, outer perturbations not winner search; A09 development authorized/final stage unauthorized; A10 owner reports ColabPro/localCPU sufficient; A11 literature is not independent benchmark replication.

D01 exact question/90%IS/Bayesian-versusCQR retained with owner-directed finite benchmark clarification; D02 anchored compact hierarchy remains principal, fallback is unactivated; D03 survivor cutoff rule preserved, no transport guarantee; D04 no5cycle practical margin/effect-size only; D05 localCPU/no additional spending; D06 final access and lock require owner authorization; D07 FD003 extension deferred.

New decisions: V04-D01 freeze plan before new science; V04-D02 disclose all calibration-informed development context and fix anchored prior independently of new score ranking; V04-D03 use dependence-adjusted ratio-CDF MCSE and uncertainty guards without relaxing.5; V04-D04 limit primary to finite benchmark and remove primary directional population test; V04-D05 suppress degenerate/nonfinite diagnostics without favorable replacement; V04-D06 repeat all relevant pipeline stages in eight conditional empirical perturbations, no unconditional-variance claim; V04-D07 adopt direct structural proof with practical/physical claim restrictions; V04-D08 retain every result and recommend {rec}.

Deviations: pre-experiment PowerShell launcher case-insensitive JSON parsing was corrected before any scientific run; no scientific record/seed/dataset existed for those launch attempts. Independently reviewed CQR upper support projection was corrected in commit6aab208 before any affected pipeline run; initial principal fits preserve their earlier exact executed source snapshots. No scientific refit was repeated, no output overwritten, no official data accessed. Any further analysis-only corrections must be individually disclosed in the final compute report. The hard-timeout record bypasses final artifact hashing; if that path occurs its partial payload is bound by the final delivery manifest and must remain scientifically failed. It is not silently treated as successful.

Residual scientific risks: cutoff mechanism/exchangeability unknown; n25 calibration variability; n13 CQR tuning instability; working-prior/domain elicitation limits; weak nuisance identification and fitted-model adequacy; eight perturbations are not whole-pipeline uncertainty; synthetic-to-official and official-to-real gaps; incomplete novelty claim; future endpoint precision and integrity unknown. There is no performance/superiority, nominal official coverage, real-engine reliability, practical margin or confirmatory result in this package.
''')
# Package index is updated after adversarial review; current recommendation remains machine-readable.
reportnames=['01_updated_research_protocol.md','02_numerical_precision_remediation.md','03_bayesian_prior_plausibility.md','04_identifiability_synthetic_validation.md','05_estimand_cutoff_transport.md','06_statistical_inference_pipeline_uncertainty_plan.md','07_comparator_fairness_audit.md','08_independent_mathematical_reverification.md','09_reproducibility_environment_compute.md','10_risks_assumptions_decisions.md','11_prelock_recommendation.md']
index='\n'.join(f'{i+1}. [{name}]({name})' for i,name in enumerate(reportnames))
doc('README.md',f'''# RP-001 v0.4 — owner review evidence index

Recommendation: **{rec}**. Status PROTOCOL_DRAFTED. No official test sensors/labels, endpoint evaluation, protocol lock or confirmatory work authorized or executed. Research Owners Raihan × Rei retain final authorization.

{index}

Additional evidence: [owner directive](owner_directive.md), [prospective plan](prospective_remediation_plan.md), [exact configurations/seeds](../../configs/v0.4/remediation_plan.json), [preserved v0.3 registry](../../research/experiment_registry_v0.3.jsonl), per-run records in `experiments/v0.4/registry`, complete posterior/synthetic arrays in `experiments/v0.4/fits`, analysis records in `experiments/v0.4/analysis`, and final fingerprint manifest/verification in `logs/v0.4`.

The native reports are Markdown. Read report11 first for disposition, report02 for numerical acceptance, and report08 for direct lead mathematics. Positive sampling/precision evidence is not research authorization or a result on official endpoints. Historical v0.3 failure and payload are retained.
''')
print(json.dumps(summary_status,indent=2))