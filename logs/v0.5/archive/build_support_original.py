import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
import xml.etree.ElementTree as ET
R=Path('.');D=R/'docs/v0.5';now=datetime.now(timezone.utc).isoformat()
read=lambda p:json.loads((R/p).read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,x):
    p=R/p;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,allow_nan=False,ensure_ascii=True)+'\n',encoding='utf8')
def save(n,s):(D/n).write_text(s.strip()+'\n',encoding='utf8')
p=read('configs/v0.5/resolution_plan.json');pre=read('experiments/v0.5/analysis/math_preflight.json')
fit=read('experiments/v0.5/registry/v05_highrho_innovation.json');score=read('experiments/v0.5/analysis/score_propagation.json');dem=read('experiments/v0.5/registry/v05_score_propagation.json')
max_grad_ratio=max(abs(a-b)/(1e-4+1e-4*abs(b)) for r in pre['grid'] for g in r['gradients'] for a,b in zip(g['autodiff'],g['dense_finite_difference']))
assert max_grad_ratio<=1
save('03_mathematical_validity.md',f"""
# SOL direct mathematical validity assessment v0.5

**Scoped PASS.** Direct lead derivations and independent numerical oracles supplement LUNA's pure-array score implementation. This is model/implementation verification, not proof of scientific superiority, transported coverage, or total-pipeline uncertainty.

## Equivalent high-rho posterior

Let eta=atanh(rho), nu=sigma_z*sech(eta), sigma_z=nu*cosh(eta). For original independent HalfNormal scale prior f_sigma and Normal eta prior f_eta, the joint density in (nu,eta) is f_sigma(nu*cosh(eta))*cosh(eta)*f_eta(eta). The Jacobian is cosh(eta). Reference HalfNormal(nu) is canceled by the potential log f_sigma(sigma_z)-log f_reference(nu)+log cosh(eta). No extra innovation-scale prior is introduced.

In unconstrained coordinates s=log(sigma_z),u=log(nu), s=u+log cosh(eta). The triangular Jacobian has determinant1. The original transformed log posterior at s equals the new one at u. This reasoning also verifies that the positive-variable log transform must be included; omitting the scale/Jacobian terms would change the model.

The direct oracle constructs the full31-dimensional marginal Gaussian of (z,logR) with Czz=B S B'+sigma_z^2 K, Czy=B S gamma, Cyy=sigma_r^2+gamma'S gamma; it uses dense Cholesky solves, not AR whitening/Woodbury. Independent Normal/HalfNormal/Beta densities and unconstrained Jacobians complete its joint log density. Both original and innovation automatic gradients are compared against this oracle's centered finite differences in two coordinates.

Frozen grid: rho .5/.95/.99/.999 x sigma_z .1/.3/.6, all other coordinates at exact failed-case truths;12density points/48gradient coordinates. Tolerances: density1e-7+1e-8*abs(reference), gradient1e-4+1e-4*abs(reference), step1e-5. All pass. Maximum density discrepancy against dense oracle **{max(r['original_vs_dense_abs'] for r in pre['grid']):.9g}**; original versus equivalent posterior **{max(r['original_vs_new_abs'] for r in pre['grid']):.9g}**. Maximum raw gradient discrepancy **{max(g['max_abs_difference'] for r in pre['grid'] for g in r['gradients']):.9g}**, maximum discrepancy divided by its prespecified absolute-plus-relative tolerance **{max_grad_ratio:.9g}**. The largest absolute gradient residual occurs on a large-gradient stress scale; the relative tolerance, not an absolute1e-4 assertion, defines acceptance. No claim of universal float64 stability at the boundary |rho|=1 or for all possible data.

## Quantile-to-score influence, dependence, and sensitivity

Conditional on a fixed posterior, importance-mixture CDF is Fhat(q)=mean(w F_theta(q))/mean(w). Its linearized ratio influence at target probabilityp is w(F_theta(q)-p)/mean(w); implicit quantile differentiation divides by -f_log(q). Exponentiating multiplies by Q=exp(q). Thus X=-Q*w*(F_theta(q)-p)/(mean(w)*f_log(q)). Scaling weights by a common positive factor within engine leaves X unchanged.

IS90 is piecewise linear in its endpoints: partial_L=-1+20I[y<L], partial_U=1-20I[y>U]. At equality the derivative is not unique; the strict indicator branch is algebraic bookkeeping and the kink flag restricts delta-method interpretation. The finite-mean influence H is the aligned mean of these derivative-weighted endpoint influences. Never discard engine dependence induced by shared posterior draws.

For independent equal-length chains of lengthn and M total draws, joint batch covariance estimate Lambda_c gives Cov_MC=sum_c n*Lambda_c/M^2. Project by a=[g_L/N,g_U/N]. V=sum_c v_c, v_c=n*a'Lambda_c*a/M^2. Satterthwaite degrees of freedom V^2/sum(v_c^2/(batches_c-1)); upperMCSE=sqrt(V*df/chi2_ppf(tail,df)). This is an **approximation**, conditional on stationarity/mixing, ratio CLT, positive smooth mixture density, and local score smoothness. Batch-means asymptotic background: [Flegal & Jones](https://arxiv.org/abs/0811.1729); the present nonlinear application and guard are directly checked here, not granted a finite-sample theorem by that source.

Maximum endpoint derivative magnitude is19. Therefore abs(change meanIS)<=19/N*sum(abs(changeL)+abs(changeU)), and it holds with supplied error radii only if actual errors lie within them. It also holds across score kinks. MCSE radii do not certify absolute error or coverage. CQR is deterministic conditional on its stored fit/calibration; H propagates only Bayesian posterior approximation to the primary difference. Repeated-data, calibration-estimation, prior/model misspecification, and full-pipeline uncertainty remain excluded.

## Computational verification and conformal rank

All **59 tests pass**, including the original55 and four deterministic worker tests. SOL's saved-draw check first projects to scalar H, then independently uses scalar chain-batch variance, matching the joint-matrix projection and chi-square upper formula at250/500. Dense mixture densities and root-CDF residuals match archived quantiles. Upper scoreMCSEs:{[b['approximate_upper_quantile_score_mcse_cycles'] for b in score['batch_size_results']]}; no training label-kink flags. This is a numerical demonstration, no primary CQR comparison.

Finite CQR rank is ceil((25+1)*.9)=24. Nonnegative correction expands rather than shrinks; lower projection0 preserves inclusion of positive outcomes. The exchangeable-rank theorem requires score exchangeability/training separation ([Romano et al.](https://arxiv.org/html/1905.03222v1)); official cutoff exchangeability and untouched development outcomes are not established. We do not infer guaranteed official coverage from the correct rank.

Generic latent structural identification uses covariance moments under full rank/interior assumptions; high-rho second differences are ill-conditioned. A bounded fitPASS and concentrated innovation scale do not establish practically separate physical nuisance effects. That is compatible with a restricted complete-procedure score comparison, provided actual prediction guards pass and all failures remain.

**Conclusion:** no unresolved material mathematical discrepancy found in tested implementation. Future endpoint guards remain mandatory. Restricted finite description is defensible; ideal-posterior numerical precision and population/physical/general robustness claims require qualifications.
""")
payload=sum(q.stat().st_size for q in (R/'experiments/v0.5').rglob('*') if q.is_file())
save('04_compute_reproducibility.md',f"""
# Compute, provenance, custody, and outstanding requirements v0.5

Exactly one new synthetic MCMC invocation, on the exact saved failed-case training data; no additional simulation, test data, fallback, or model search. The fixed saved-draw score demonstration performs no sampling. Local CPU default was sufficient; Google Colab Pro/GPU unused, no additional spending.

| Component | Wall seconds | Process CPU seconds |
|---|---:|---:|
| Single high-rho inquiry | {fit['wall_seconds']:.6f} | {fit['cpu_seconds']:.6f} |
| Saved-draw score propagation | {dem['wall_seconds']:.6f} | {dem['cpu_seconds']:.6f} |

Registered timed new scientific work totals **{fit['cpu_seconds']+dem['cpu_seconds']:.6f} CPU seconds**. Timers start after imports; direct preflight, tests, source review, packaging/Git are excluded and no OS-wide total/energy measurement is claimed. Fit remains below600wall seconds/oneCPUhour; new experiment payload is approximately{payload/1024**2:.3f}MiB, below128MiB. Peak fit RSS:{fit['peak_rss_bytes']}bytes. Hardware i7-10750H,6physical/12logical cores,15.776GiB RAM; float64,BLAS/OMP/MKL/NumExpr threads1,sampler cores2. Warnings about unavailable g++ and loop fusion were recorded; backend was frozen nutpie/Numba.

## Exact identities

- Owner-reviewed scientific snapshot:61b4c2c63cbad6c1b9bd99168e33d1367aa180bc.
- Pre-execution plan/source and high-rho run:304d8e76d03fe7d69dc7f8f9bb6de3c600a219dd.
- Saved-draw demo source:{dem['git_commit']}.
- Environment:{p['environment_fingerprint']}.
- Authorized train:{pre['dataset_sha256']}.
- Original split:{pre['split_manifest_sha256']}.
- v0.5plan:{pre['plan_sha256']}.
- Exact reused synthetic data:{p['investigation']['input_sha256']}.
- Direct preflight:{sha('experiments/v0.5/analysis/math_preflight.json')}.
- New posterior:{fit['posterior_sha256']}.
- Final snapshot/manifest identities:[delivery receipt](../../logs/v0.5/delivery_receipt.json).

The64package lock and environment remain unchanged. Per-run records bind every executed source hash, plan, commit, dataset, and no-test-access flag. Original high-rhoFAIL is preserved, not overwritten by the new run. No extra MCMC invocation or retry is permitted by its runner; a record already present prevents reexecution.

## Reproduction boundaries

Saved artifacts allow deterministic recomputation of the documented diagnostics and score-propagation check. For a fresh authorized scientific replay, use an isolated checkout at304d8e7, pinned CPython3.12.14/package lock, and exact historical failed-case data/required retained principal NCs. Set PYTHONPATH=src, float64, one BLAS thread, and forward-slash PyTensor cache directory. The entry points are python -m rp001.v05_highrho preflight then run; they require an empty v0.5 destination and refuse overwrite. The score-demo source is in60e9208; the historical source/provenance assertions intentionally require their own source snapshot. A new replay must record its own commit and identities rather than manufacture the original run receipt.

Complete historical replay still needs33Git-ignored local payload files bound in the v0.4manifest, including trusted comparator object/preprocessing stores; the private GitHub repository does not by itself supply every historical input. No one-command clean/new-platform replay or bit-identical cross-platform sampler claim is certified. Stage an authorized custodian bundle or document lawful fresh acquisition before a public reproducibility claim. Never extract protected official members while reproducing the training pilot.

The [baseline archive map](../../research/v0.5/baseline_alias_archive_map.json) preserves any advanced current metadata byte-for-byte. [QC](../../logs/v0.5/closure_qc.json) checks historical537file manifest custody via those aliases, unchanged old source/evidence, main registry prefix, all59tests, one invocation, exact fingerprints, and protected draft state. Manifests bind bytes, not scientific assumptions.

## Unresolved rights and publication requirements

[NASA catalog](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data), checked2026-10-08, describes100FD001test trajectories and explicitly reports unspecified license. Only catalog metadata was browsed; no archive sensor/label resource was opened. Acquisition/provenance, permission to use, and permission to redistribute are distinct. Preserve raw-data exclusion and private review visibility; obtain appropriate rights review before public release of data or derived payload. This report does not supply legal clearance.

Novelty remains unverified; CQR/Bayesian RUL are established families. Complete targeted primary-source novelty/evidence review before publication claims. Current disclosure/source custody is sufficient for owner contract review, not certified public research reproducibility. Future official schema/overlap/numerical audits and distinct owner lock/sensor/label permissions remain outstanding execution requirements.
""")
# Owner directive input is retained as a scope record, not a manufactured approval.
save('owner_response_scope.md',"""
# Owner response to v0.4: retained authorization boundary

Human source: Raihan x Rei response to scientific commit61b4c2c63cbad6c1b9bd99168e33d1367aa180bc in this conversation,2026-10-08.
Decision: ACCEPT REVISE AGAIN, WITH A BOUNDED PRE-LOCK RESOLUTION MANDATE.

Required: classify all risks for restricted finite-benchmark claim; one fixed-scope high-rho investigation or defensible restriction; define competitive; propagate numerical uncertainty to score difference; propose complete locked contract; return concise seven-part v0.5memo with READY FOR OWNER LOCK REVIEW / RE-SCOPE / STOP.
Owner permits bounded pre-lock remediation, not indefinite experimentation. Final protocol authorization remains Raihan x Rei. Official test sensors/labels, confirmation, and fallback activation are prohibited now.

This scope record summarizes the owner message; it does not replace the original human instruction or authorize subsequent phases.
""")
# Retain complete v04 state before advancing current aliases.
aliases=['research/protocol.json','research/state_manifest.json','research/gate_results.json','research/environment_manifest.json','research/experiment_registry.jsonl','research/decision_log.md']
archive_map={}
for path in aliases:
    dst=R/'research/v0.5/baseline_current_aliases'/path;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert dst.read_bytes()==(R/path).read_bytes(),'No archive overwrite'
    else:dst.write_bytes((R/path).read_bytes())
    archive_map[path]=dict(archive=str(dst).replace('\\','/'),sha256=sha(path))
write('research/v0.5/baseline_alias_archive_map.json',archive_map)
old=read('research/protocol.json');old.update(schema_version='0.5',artifact_version='0.5',updated_at=now,pilot_disposition='READY FOR OWNER LOCK REVIEW',status='PROTOCOL_DRAFTED',protocol_locked_at=None,owner_stage_b_approved=False)
old['analysis_plan']='Proposed owner-lock contract docs/v0.5/02_proposed_locked_analysis_contract.md: complete finite mean90%IS difference; no population inference; all failures retained.'
old['uncertainty_plan']='Joint posterior quantile-to-score MC influence; guards before labels; score/kink qualification after labels; no engine-sampling CI or total-pipeline variance.'
old['secondary_outcomes']=['Exact finite empirical coverage fraction','width','median MAE/RMSE/bias','lower/upper miss penalties','fixed Bayesian+posthoc calibration descriptive ablation']
old['secondary_population_hypothesis']=None
old['stopping_rule']='Bounded v0.5 mandate complete; one inquiry only. No further science without separately reviewed owner authorization.'
old['robustness_plan']='Disclose unchanged v0.4stressFAIL/OC/pipeline sensitivity and new one-inquiryPASS; no universal robustness/physical identification.'
old['primary_claims']=['Official comparison unresolved/unexecuted; restricted descriptive finite contract recommended for owner review.','One equivalent high-rho inquiry and direct numerical implementation checks PASS; old stressFAIL retained.']
old['practical_decision_rule']='Descriptive comparison only; no binary competitive, practical superiority, equivalence or noninferiority threshold.'
old['competitive_definition']=p['competitive_definition'];old['proposed_analysis_contract']='docs/v0.5/02_proposed_locked_analysis_contract.md'
old['compute_budget']='v0.5one MCMC cap600sec/1CPUhour/128MiB; observed fit90.125CPU seconds, demonstration9.453125; localCPU,noColab/spending.'
old['deviations'].append(dict(date='2026-10-08',phase='owner-authorized bounded pre-lock resolution',disclosed=True,held_out_labels_visible=False,change='Reassess risk relevance for finite claim; omit populationbootstrap from proposedlock; one exact-posterior innovation inquiry, oldFAIL preserved; fixed score numerical policy. RQ unchanged.'))
write('research/protocol.json',old);write('research/v0.5/protocol.json',old)
gates=[
('BOUNDED_AUTHORIZATION','PASS','Scope honored; one invocation; no official access.'),
('IMPLEMENTATION_MATHEMATICS','PASS','Direct SOL Jacobian/dense/gradient/influence/covariance verification in tested scope.'),
('PRINCIPAL_DEVELOPMENT_PRECISION','PASS','v04all25/75retained; v05jointscore demoPASS; futurecases untested.'),
('ORIGINAL_HIGH_RHO_STRESS','FAIL','Original immutable failed case remainsFAIL; no retroactive acceptance.'),
('BOUNDED_HIGH_RHO_INQUIRY','PASS','Single equivalent-posterior fitpasses; no general robustness certification.'),
('FULL_PIPELINE_UNCERTAINTY','DEFERRED','Excluded from restricted claim; observed8perturbations sensitivity only.'),
('CUTOFF_TRANSPORT','DEFERRED','Official exchangeability/generalization unproved and excluded.'),
('POPULATION_INFERENCE','DEFERRED','Omitted from proposedlock; adverse historical study preserved.'),
('FUTURE_ENDPOINT_INTEGRITY_PRECISION','DEFERRED','Mandatory authorized sensor-phase guard; no endpointsaccessed.'),
('OWNER_PROTOCOL_LOCK','BLOCKED','Owner approval absent; scientific readiness is for review only.'),
('CONFIRMATORY_EVALUATION','BLOCKED','Not authorized, no official results.')]
gate_rows=[dict(gate=a,state=b,owner='Rei SOL lead / Raihan x Rei final authorization',artifact_version='0.5',evidence_ids=['V05-MEMO'],rationale=c) for a,b,c in gates]
write('research/gate_results.json',dict(version='0.5',scope='Restricted contract owner review; not validated research',recommendation='READY FOR OWNER LOCK REVIEW',gates=gate_rows))
write('research/v0.5/gate_summary.json',read('research/gate_results.json'))
env=read('research/environment_manifest.json');env.update(schema_version='0.5',git_commit=dem['git_commit'],final_research_authorized=False,notes='Per-run exact source commits authoritative; final delivered snapshot in v05receipt. Local64package environment unchanged.')
write('research/environment_manifest.json',env)
state=read('research/state_manifest.json');state.update(schema_version='0.5',created_at=now,recommendation='READY FOR OWNER LOCK REVIEW',scientific_execution_source_commit=pre['git_commit'],analysis_source_commit=dem['git_commit'],final_artifact_manifest='logs/v0.5/delivery_manifest.json',final_commit_receipt='logs/v0.5/delivery_receipt.json',baseline_state_archive=archive_map['research/state_manifest.json']['archive'],note='Bounded evidence return complete; owner lock/test/confirmatory authorization absent.')
write('research/state_manifest.json',state)
base=(R/aliases[4]).read_bytes()
add=[]
for name,rec in [('v05_highrho_innovation',fit),('v05_score_propagation',dem)]:
    path=f'experiments/v0.5/registry/{name}.json'
    add.append(dict(run_id=name,phase='exploratory-v0.5-bounded',method='One authorized bounded inquiry' if name.startswith('v05_highrho') else 'Fixed saved-draw numerical demonstration',code_commit=rec['git_commit'],code_dirty=False,config_hash=pre['plan_sha256'],configuration=rec.get('configuration',{'scope':rec['scope']}),status=rec['status'],metrics_file=path,record_sha256=sha(path),environment_fingerprint=rec['environment_fingerprint'],data_fingerprint=rec.get('data_sha256',rec['dataset_sha256']),frozen_plan_sha256=rec['plan_sha256'],seed=rec.get('configuration',{}).get('seed'),cpu_seconds=rec['cpu_seconds'],wall_seconds=rec['wall_seconds'],protected_test_access=False,confirmatory=False))
# No old bytes/line altered, including historical failures.
with (R/aliases[4]).open('ab') as f:
    for x in add:f.write((json.dumps(x,ensure_ascii=True)+'\r\n').encode('utf8'))
assert (R/aliases[4]).read_bytes().startswith(base)
write('research/v0.5/registry_append_audit.json',dict(baseline_lines=len(base.splitlines()),baseline_sha256=hashlib.sha256(base).hexdigest(),added_records=2,current_lines=len((R/aliases[4]).read_bytes().splitlines()),old_prefix_unchanged=True))
with (R/'research/decision_log.md').open('a',encoding='utf8') as f:f.write('\n\n## v0.5 bounded pre-lock return\n\nREADY FOR OWNER LOCK REVIEW for restricted descriptive finite-benchmark contract. One inquiry PASS, original FAIL retained; population inference omitted; numerical failure policy fixed. No final lock, test access, fallback or confirmation authorized. Full disposition docs/v0.5/01_prelock_resolution_memo.md.\n')
# Scientific risk status retains severity, never turns external assertions into proven facts.
old_risks=read('research/v0.4/risk_register.json')['risks'];matrix=read('research/v0.5/blocker_disposition.json')['risks'];risks=[]
for before,new in zip(old_risks,matrix):
    r=dict(before);r.update(impact_class=new['impact_class'],disposition=new['pre_experiment_disposition'],status='RESTRICTED_CLAIM_DISPOSITION' if new['risk_id']!='R17' else 'OWNER_APPROVAL_PENDING',evidence='docs/v0.5/01_prelock_resolution_memo.md',remaining_uncertainty='Historical severity/evidence retained; broader claims unproved; future execution guards and owner permissions remain.')
    if new['risk_id']=='R02':r['disposition']+=' One bounded equivalent-posterior inquiryPASS; physicalcoupling persists; no automaticprincipal replacement.'
    risks.append(r)
write('research/v0.5/risk_register.json',dict(version='0.5',recommendation='READY FOR OWNER LOCK REVIEW',risks=risks))
# Handoff schema preserved from previously validated envelope.
h=read('docs/v0.4/research_lead_handoff.json')
h.update(handoff_id='RP001-V05-BOUNDED-PRELOCK-RETURN',artifact_type='bounded-prelock-resolution-memo-and-proposed-analysis-contract',artifact_version='0.5',scope='One bounded synthetic inquiry and saved-training scorenumerics; no officialaccess/confirmatory/lock/fallback.',claims_or_requirements='Bounded return complete; restricted descriptive contract ready for ownerlockreview.',gate_results=gate_rows,risks=risks,return_to_parent='COMPLETE',return_interpretation='Evidence handoffcomplete, PROTOCOL_DRAFTED; final authorization remains owners.',requested_decision='READY FOR OWNER LOCK REVIEW: accept/reject/amend proposed restricted contract; no further pilot requested.',unresolved=[short for short in ['Owner final protocol/sensor/label authorization','Futureendpointintegrity/precision','Physicalnuisancecoupling/highrhorobustness','Officialcutoffexchangeability','Smallcalibration/tuning and exposure','Wholepipelinevariance','Publicationnovelty/data-rights/cleanreplay']],worker_contribution='Existing GPT6LUNAMAX worker wrote pure-array scoreutility/tests; SOL directly derived and independently checked all materialmath.',deviations=['Exactposterior reparameterization and doubled retained/warmup budgets frozenbeforeonefit; cause notuniquely attributable.','Populationbootstrap omitted onlyin proposedcontract, historicaladverseresults retained.','No scientificretry orpostlabelrepair.'],report_only_clarification='None')
h['artifact_identity']=dict(path_or_uri='docs/v0.5/01_prelock_resolution_memo.md',sha256_or_version=sha('docs/v0.5/01_prelock_resolution_memo.md'),created_at=now,source_revision='Plan/inquiry304d8e7;score60e9208;final snapshot in v05receipt.')
sources=[('V05-MEMO','docs/v0.5/01_prelock_resolution_memo.md','DirectSOLbounded scientific disposition'),('V05-CONTRACT','docs/v0.5/02_proposed_locked_analysis_contract.md','Proposedfiniteanalysis/failure/phasecontract'),('V05-MATH','experiments/v0.5/analysis/math_preflight.json','Directdense/Jacobian/gradientverification'),('V05-FIT','experiments/v0.5/registry/v05_highrho_innovation.json','Exactlyone fixedtruthinquiry'),('V05-SCORE','experiments/v0.5/analysis/score_propagation.json','Dependencepreserving jointscoreMCSEandscalaroracle'),('V05-TESTS','logs/v0.5/verification_tests.xml','59testsPASS')]
h['evidence']=[dict(evidence_id=i,kind='bounded-evidence',location=path,sha256=sha(path),collected_at=now,method=m,supports='Restrictedclaim only;notfinalauthorization',provenance_chain='Owners -> preexecutionplan304d8e7 -> input/sourcehashes -> fixedrun -> independentSOLmath -> restrictedreturn') for i,path,m in sources]
h['assumptions']=['Futurelabels/sensorsare separateowner-authorizedphases.','Finitecompleteenumerationdoesnotrequireiidsamplinginference.','ApproximateMCSErequiresstationaryadequatemixing/positiveCDFdensity;crossengineindicespreserved.','Noofficialconformal/generalrobustness/physicalidentification/wholepipelinevarianceclaim.']
write('docs/v0.5/research_lead_handoff.json',h)
print(json.dumps(dict(max_gradient_tolerance_ratio=max_grad_ratio,payload_MiB=payload/1024**2,old_registry_lines=len(base.splitlines()),current_registry_lines=len((R/aliases[4]).read_bytes().splitlines()))))
