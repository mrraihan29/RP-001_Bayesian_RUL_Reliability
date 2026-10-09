from pathlib import Path
import json,hashlib,datetime,subprocess,difflib,csv,io,dataclasses,sys
R=Path.cwd();D=R/'docs/protocol_lock';L=R/'logs/protocol_lock/final_G3'
A=json.loads((L/'resume_baseline_verification.json').read_text(encoding='utf8'));assert A['status']=='PASS'
BASE=A['original_scientific_commit'];REVIEW=A['reviewed_amendment_commit'];VERSION='RP-001-G3-v0.5-AM1'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
local_date='2026-10-09';auth={'stage_A_formal_lock':True,'stage_B_official_test_sensors':False,'stage_C_prediction_freeze_acceptance':False,'stage_D_official_test_labels_and_scoring':False}
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def write(p,x):
 p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def md(p,x):
 p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(x.strip()+'\n',encoding='utf8')
# Exact owner-reviewed failed package is preserved before advancing its current aliases.
preserve={}
for row in A['prior_attempt_documents']:
 p=row['path'];dst='docs/protocol_lock/history/G3_lock_attempt_1/'+Path(p).name
 target=R/dst;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():raise FileExistsError(dst)
 data=(R/p).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256'];target.write_bytes(data)
 preserve[p]={'archive':dst,'sha256':row['sha256'],'bytes':len(data),'source_commit':REVIEW}
aliases=['README.md','GITHUB_REVIEW.md','research/protocol.json','research/state_manifest.json','research/gate_results.json','research/decision_log.md','research/artifact_map.csv','configs/protocol_lock_record.json']
for p in aliases:
 dst='research/protocol_lock/final_G3/baseline_current_aliases/'+p;target=R/dst;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():raise FileExistsError(dst)
 data=(R/p).read_bytes();target.write_bytes(data);preserve[p]={'archive':dst,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'source_commit':REVIEW}
write('research/protocol_lock/final_G3/preservation_map.json',preserve)
md('docs/protocol_lock/history/G3_lock_attempt_1/HISTORY_CONTEXT.md',f'''# Historical G3 lock attempt 1

All eight original top-level documents/receipt are byte-exact copies from owner-reviewed commit {REVIEW}. They retain their FAIL/PENDING captions and original relative links; read the original commit for its original link context. Current successful G3 documents are in docs/protocol_lock. This archive does not alter or retroactively accept the failed attempt.
''')
original_path='docs/v0.5/02_proposed_locked_analysis_contract.md';original=(R/original_path).read_bytes()
assert sha(original_path)=='1e03e072682878fde6ced8c00ddcde44594af59e56129e65db1127a0166fa598'
old=b'Brent bracket min(mu-12SD)..max(mu+12SD), xtol=1e-12 (frozen v0.4 precision implementation); failure retained with no result-selected bracket/draw repair.'
proposal=(R/'docs/protocol_lock/AMENDMENT_REQUEST_G3_AM_001.md').read_bytes()
replacement=next(line[2:] for line in proposal.splitlines() if line.startswith(b'> For principal official endpoints'))
assert original.count(old)==1
amended=original.replace(old,replacement)
amendpath='docs/protocol_lock/provenance/amended_v0.5_source_contract.md';(R/amendpath).parent.mkdir(parents=True,exist_ok=True);(R/amendpath).write_bytes(amended)
marker=b'## Question, primary estimand, and competitive';body=amended[amended.index(marker):]
cover=f'''# RP-001 | Locked Analysis Contract {VERSION}

**PROTOCOL_LOCKED.** Owners Raihan x Rei authorize formal G3 lock via the original G3 directive and approved G3-AM-001 decision reviewed at {REVIEW}. Observed lock record UTC: {now}; client date {local_date} Asia/Jakarta.

Only the approved quantile-procedure clause differs from original scientific v0.5 content. The administrative cover records current status and authority. The body below preserves original scientific bytes except that exact approved substitution, including historical typography. Canonical numerical source is src/rp001/v04_precision.py SHA-256 {A['authoritative_quantile_route']['module_sha256']}. No scientific implementation or threshold changed.

B test sensors, C prediction-freeze acceptance, and D labels/scoring remain separately unauthorized. The public repository is for review; scientific publication and raw-data redistribution remain uncleared. No cryptographic owner signature is claimed.

'''
(R/'docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md').write_bytes(cover.encode()+body)
diff=''.join(difflib.unified_diff(original.decode('utf8').splitlines(keepends=True),amended.decode('utf8').splitlines(keepends=True),fromfile=original_path,tofile=amendpath))
(R/'docs/protocol_lock/AMENDMENT_DIFF.patch').write_bytes(diff.encode())
change={'amendment':'G3-AM-001','decision':'APPROVED','owner_reviewed_commit':REVIEW,'observed_at_utc':now,'client_date':local_date,'source':'Current human Raihan user message; UTF-8 transcription stored, not an independently signed document','stated_research_owners':'Raihan x Rei','owner_decision_document':'docs/protocol_lock/OWNER_AMENDMENT_DECISION_G3_AM_001.md','owner_decision_document_sha256':sha('docs/protocol_lock/OWNER_AMENDMENT_DECISION_G3_AM_001.md'),'original_contract_path':original_path,'original_contract_sha256':sha(original_path),'amended_source_contract_path':amendpath,'amended_source_contract_sha256':sha(amendpath),'exact_diff_path':'docs/protocol_lock/AMENDMENT_DIFF.patch','exact_diff_sha256':sha('docs/protocol_lock/AMENDMENT_DIFF.patch'),'removed_clause':old.decode(),'approved_replacement_clause':replacement.decode(),'substitution_count':1,'inverse_substitution_recovers_original_bytes':amended.replace(replacement,old)==original,'locked_contract_path':'docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md','locked_contract_sha256':sha('docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md'),'locked_scientific_body_sha256':hashlib.sha256(body).hexdigest(),'administrative_cover_bytes':len(cover.encode()),'scientific_source_unchanged':True,'canonical_quantile_source':A['authoritative_quantile_route'],'historical_preservation_map':'research/protocol_lock/final_G3/preservation_map.json'}
assert change['inverse_substitution_recovers_original_bytes']
write('docs/protocol_lock/AMENDMENT_CHANGE_RECORD.json',change)
sys.path.insert(0,str(R/'src'))
from rp001.comparators import candidate_specs
grid=[dataclasses.asdict(c) for c in candidate_specs()];assert len(grid)==12
plan=read('configs/v0.4/remediation_plan.json')
model={'version':VERSION,'status':'FROZEN','approved_original_scientific_commit':BASE,'approved_amendment_review_commit':REVIEW,'model':'Hierarchical Gaussian level/slope g, AR1 Gaussian sensor error, Gaussian log-RUL conditional response; g analytically integrated in full joint likelihood','model_source':'src/rp001/v04_model.py','latent_joint_likelihood_source':'src/rp001/model.py','prior_policy':plan['prior'],'principal_prior_scale':1.0,'principal_error':'normal','rho_zero':False,'principal_posteriors':A['principal_posteriors'],'pooling':{'replications':['v04_main_r1','v04_main_r2','v04_main_r3'],'chains_per_replication':4,'retained_draws_per_chain':8000,'pooled_chains':12,'pooled_draws':96000,'order':'r1 chains then r2 chains then r3 chains; preserve original draw order','base_weights':'Equal training-posterior draw weights before separate sensor importance update'},'new_engine_prediction':{'sensor_terms_source':'src/rp001/v04_predict.py','conditioning':'Each engine separately weights theta by its own sensor likelihood; no joint conditioning on other test engines','predictive_law':'Conditional Gaussian logRUL mixture under full sensor-reweighted global theta posterior','probabilities':[.05,.5,.95],'authoritative_quantile_route':A['authoritative_quantile_route'],'legacy_quantile_helper':'rp001.prediction.mixture_quantile retained for historical provenance only; not official primary route','short_history':'w=min(30,C), actual positions B=[1,t/30]; w=1 level only; no engine exclusion'},'MCMC_policy':plan['mcmc_acceptance'],'quantile_numerical_policy':{'batch_sizes':[250,500],'upper_MCSE_cycles_max':.5,'weight_ESS_min':1000,'influence_ESS_min':400,'tail_probability':'.05/(N*3*2), N complete expected official cohort 100','root_CDF_residual_max':1e-10,'replication_comparisons':'3 pairs * N engines * 3 probabilities, z=Phi^-1(1-.05/(2*9*N)); MCSE=max of batches; zero/nonfinite denominator fails','failure':'Stop before labels; preserve every engine/failure; no draws/seeds/bracket-method modification/post-result repair'},'score_numerical_policy':{'source':'src/rp001/v05_score_numerics.py','tail_probability':.05/2,'batch_sizes':[250,500],'upper_MCSE_cycles_max':.5,'label_kink_flag':'Within 3 endpoint upper MCSEs at either endpoint','status_if_undefined_nonfinite_excess_upper_or_kink':'NUMERICALLY_QUALIFIED ideal-posterior score/ranking; stored complete finite score retained','no_post_label_repair':True,'dependence':'Preserve shared chain/draw/engine alignment through joint covariance projection'},'CQR':{'candidate_grid':grid,'endpoint_quantiles':[.05,.95],'n_tuning_eligible':13,'tie_tolerance_cycles':.5,'tie_order':'linear before boost; stronger linear L1; shallower boost/larger leaf/smaller rate','selected_id':'gb-depth1-leaf10-lr0p1','selected_fitted_object':{'path':'results/pilot/selected_comparator.joblib','sha256':sha('results/pilot/selected_comparator.joblib')},'fitted_parameters':A['CQR_fitted_parameters'],'refit_n_engines':56,'preprocessor':{'path':'results/pilot/refit_preprocessor.npz','sha256':sha('results/pilot/refit_preprocessor.npz')},'calibration':A['CQR_calibration'],'calibration_record_sha256':sha('results/pilot/comparator_calibration.json'),'nonshrinking':True,'support_projection':'[max(0,rawL-q),max(0,rawU+q)] after raw endpoint ordering; median unshifted','reselection_allowed':False},'secondary_Bayesian_posthoc':{**read('experiments/v0.4/analysis/principal_posthoc_calibration.json'),'path':'experiments/v0.4/analysis/principal_posthoc_calibration.json','sha256':sha('experiments/v0.4/analysis/principal_posthoc_calibration.json')},'high_rho_v05_role':'Diagnostic only; never a principal posterior replacement','fresh_sampling_retraining_fallback_allowed':False}
write('docs/protocol_lock/FROZEN_MODEL_AND_CONFIGURATION_MANIFEST.json',model)
code={'version':VERSION,'status':'FROZEN','approved_scientific_snapshot':BASE,'approved_amendment_review_snapshot':REVIEW,'scientific_sources':A['scientific_sources'],'scientific_source_map_sha256':A['scientific_source_map_sha256'],'source_map_encoding':'SHA256 UTF-8 sorted-key compact JSON path->SHA256','scientific_configurations':[x for x in A['configurations_before_resume'] if x['path']!='configs/protocol_lock_record.json'],'legacy_governance_record':{'original':'configs/protocol_lock_record.json','archive':preserve['configs/protocol_lock_record.json']['archive'],'sha256':preserve['configs/protocol_lock_record.json']['sha256']},'current_administrative_lock_record':'configs/protocol_lock_record.json; bound in final receipt, not a scientific hyperparameter input','live_environment':A['live_environment'],'environment_fingerprint':A['environment_fingerprint'],'runtime_policy_observation_limit':A['runtime_policy_note'],'dependency_lock':{'path':'configs/requirements-pilot.lock','sha256':sha('configs/requirements-pilot.lock')},'saved_environment_record':{'path':'logs/pilot_environment.json','sha256':sha('logs/pilot_environment.json')},'canonical_quantile_source':A['authoritative_quantile_route'],'legacy_runners':'Development-only historical runners have their original calibration counts/tails and raw prediction helper; they are not official-evaluation drivers. Future separately authorized execution must explicitly pass the locked cohort-specific probabilities/tails/guards to frozen primitives.','official_evaluation_driver_readiness':'No official endpoint run or full protected execution certification; procedural implementation/ledger and integrity checks remain Stage B work after separate authorization.','complete_replay_limit':'33 local-only historical payloads required; no one-command clean or bit-identical cross-platform replay certified','Colab_used_for_G3':False,'new_spending':False,'G3_new_scientific_runs':0}
write('docs/protocol_lock/FROZEN_CODE_AND_ENVIRONMENT_MANIFEST.json',code)
split=read('configs/proposed_split_manifest.json')
data={'version':VERSION,'status':'FROZEN','dataset':'NASA original C-MAPSS FD001','training_sha256':A['input_identities']['data/raw/train_FD001.txt'],'training_rows':20631,'training_engines':100,'training_fields':26,'data_provenance_record':{'path':'data/raw/provenance.json','sha256':sha('data/raw/provenance.json')},'opaque_archive_identities':[x for x in read('data/raw/provenance.json')['files'] if x['path'].endswith('.zip')],'opaque_archive_inspection':'Whole-file hash only; no protected member listing/extraction/read','split_manifest':{'path':'configs/proposed_split_manifest.json','sha256':A['input_identities']['configs/proposed_split_manifest.json'],'entries':split},'split_rule':{'seed':'RP001-20261008-v0.2','roles':'IDs sorted by SHA256(seed|split|ID); 55 fit,15 tune,30 calibration','cutoff':'30 + int(SHA256(seed|cutoff|ID),16)%221','eligibility':'C<T, no redraw/replacement','eligible_counts':{'fit':43,'tune':13,'calibration':25},'refit_engines':56},'calibration_engine_ids':A['CQR_calibration']['calibration_engine_ids'],'preprocessing_policy':'Fit43 for tuning/refit56 for final; equal engine weight1/n,row1/(n*C); SD<=1e-8 drop; PC1 sign largest loading positive; scale sqrt(top eigenvalue); saved refit maps shared','official_cutoff_policy':'One endpoint at last observed C, no hash pseudo-cutoff, label eligibility/min-history/30..250 restriction, engine dropping or pooled test preprocessing','official_population_expected_n':100,'official_count_verified':False,'protected_authorization':auth,'stage_B_integrity_policy':'All expected endpoints, 26 fields, finite values, positive contiguous cycles, unique engine-cycle namespaces; overlap audit and >=30common cycles near-duplicate meanNRMSE<=.02/maxchannel<=.10 heuristic; flag stops for owner, no engine deletion','label_policy':'Stage D only after Stage C acceptance; exact complete N alignment, source/hash, finite positive uncapped RUL','raw_redistribution_rights':'Unresolved; raw archive/training/protected members remain ignored and excluded from public Git','local_only_historical_payloads':[x for x in A['baseline_file_checks'] if not x['available_in_original_git_snapshot']]}
write('docs/protocol_lock/FROZEN_DATA_AND_SPLIT_MANIFEST.json',data)
md('docs/protocol_lock/LOCKED_RESEARCH_PROTOCOL.md',f'''# RP-001 | Locked Research Protocol {VERSION}

**PROTOCOL_LOCKED — formal Stage A only.** Lock record UTC: {now}; owner client date {local_date} Asia/Jakarta. Original scientific baseline {BASE}; approved amendment review commit {REVIEW}.

## Authoritative methods and scope

The [Locked Analysis Contract](LOCKED_ANALYSIS_CONTRACT.md) is the authoritative complete scientific procedure: original v0.5 scientific body with exactly approved G3-AM-001 quantile-clause substitution. The [exact diff](AMENDMENT_DIFF.patch) and [change record](AMENDMENT_CHANGE_RECORD.json) bind that change. Its administrative cover records locked status without changing methods. The documentary amended-source copy retains the old proposal caption solely to make a one-clause diff auditable.

Research question remains: Is a compact hierarchical Bayesian predictor competitive in 90% interval score with calibrated CQR at the official FD001 unseen-engine endpoint, with engine-level uncertainty and audited dependence?

Competitive means descriptive comparative characterization. Primary estimand is complete finite-cohort mean IS90(Bayesian)-IS90(CQR), raw uncapped cycles, one stored final-observed endpoint for every expected official engine (metadata expects 100). Both mean scores, signed contrast, defined ratio, per-engine differences and width/miss-penalty decomposition describe these realized procedures. No population hypothesis, fixed practical margin, superiority/equivalence/noninferiority or operational claim.

## Frozen procedure

Reuse the Gaussian latent level/slope, AR1 sensors, Gaussian log-RUL joint model, analytically integrated latent effects and anchored_v04 priors. Reuse v04_main_r1/r2/r3 exactly: 12 pooled chains/96000 retained draws, separately sensor-reweighted per new engine. Use only the pinned precision-helper route for stored primary quantiles and independent-fit diagnostics. High-rho v05 fit is diagnostic, not production.

CQR retains the original 12 candidates, 13-engine tuning/tie rules, selected gradient boost, 56-engine refit maps/model, fixed 25-engine calibration, rank24/q=19.987558518873357 and nonnegative support projection. No reselection. Fixed Bayesian posthoc calibration is secondary exploratory only.

Training split/cutoff/preprocessing remain exactly the approved contract; official endpoint cutoff uses its last observed cycle. Complete input/prediction/quantile/MCMC/replication failure ledger is mandatory. Failure before labels stops; no drop, repair, additional draws or automatic fallback. Post-label score/kink numerical qualification retains the complete stored score and prohibits unauthorized repair. Primary contrast requires float64 finite scores and compensated aggregation; missing/nonfinite pair gives UNAVAILABLE.

The three frozen manifests record exact source/configuration/environment/posterior/training/split/model identities. Future endpoint guards and protected driver/ledger readiness must be verified during separately authorized execution; locking primitives and procedures is not certification that every future engine passes.

## Boundaries and stopping gate

[Claim boundaries](SCIENTIFIC_CLAIM_BOUNDARIES.md) and [protected access policy](PROTECTED_EVALUATION_ACCESS_POLICY.md) are mandatory. All historical adverse evidence is retained. No new scientific experiment, fitting, resampling, threshold relaxation, official prediction/scoring or publication is authorized by this lock.

Stop after final receipt and completion report. Stage B sensor access, Stage C freeze acceptance and Stage D labels/scoring need separate owner decisions. Nothing here grants any of them.

[Decision record](LOCK_DECISION_RECORD.md) · [Verification report](LOCK_VERIFICATION_REPORT.md) · [Final receipt](LOCK_RECEIPT.json).
''')
md('docs/protocol_lock/SCIENTIFIC_CLAIM_BOUNDARIES.md','''# RP-001 | Locked Scientific Claim Boundaries

The primary comparison is descriptive enumeration of the exact complete finite FD001 benchmark and its frozen stored predictions. Negative Bayesian-minus-CQR mean score means lower stored Bayesian mean score on that benchmark. Competitive is comparative characterization, with no binary practical superiority/equivalence decision or five-cycle margin.

Report both mean90% interval scores, signed paired contrast, score ratio when CQR mean>0, interval width/miss penalties, complete per-engine records, exact empirical coverage fraction and descriptive median errors. No population p-value, engine-sampling SE/CI, Wilson/binomial CI, population bootstrap, general superiority/noninferiority/equivalence, guaranteed official conformal coverage, maintenance utility/safety certification, causal benefit of Bayesian philosophy or physical identification.

Model-conditional predictive uncertainty, conditional numerical MCSE and observed pipeline sensitivity are distinct. Numerical guards/Satterthwaite bounds are approximate under stationarity/mixing/ratio-CLT/density assumptions; they are not guaranteed absolute-error or finite-sample coverage bounds. Score influence retains shared posterior dependence. CQR has no posterior Monte Carlo error conditional on its frozen fit/correction; full repeated-training/calibration uncertainty remains unestimated.

Disclose original high-rho failure and bounded diagnostic PASS without replacement, v0.3 precision failure, weak nuisance separation, small 25-calibration/13-tuning cohorts, exposed calibration/prior adaptation, eight dependent pipeline perturbations and winner changes, adverse bootstrap findings/999 unavailable replicates, unequal features/search/compute, unknown cutoff exchangeability/transport, synthetic-to-real gap and all prediction failures. No removal of difficult engines. Limited or negative results are scientifically admissible.

Novelty review, data-rights clearance, lawful custodian availability for 33 ignored historical payloads and reproducibility limits remain outstanding before scientific publication. Public GitHub access does not certify rights or scientific validity. PROTOCOL_LOCKED is not RESEARCH_VALIDATED.
''')
md('docs/protocol_lock/PROTECTED_EVALUATION_ACCESS_POLICY.md',f'''# RP-001 | Protected Evaluation Access Policy

Current owner authority: {json.dumps(auth)}.

| Phase | Current permission | Separate owner evidence required |
|---|---|---|
| A: formal protocol lock | Authorized and completed after verification/receipt | Original G3 directive plus approved G3-AM-001 |
| B: official test sensors | NOT AUTHORIZED | New explicit instruction before sensor extraction/read/statistics/predictions |
| C: prediction-freeze acceptance | NOT AUTHORIZED | Owner review of complete ledger, numerical gates, hashes and source/config identity |
| D: official labels and scoring | NOT AUTHORIZED | Separate label-release decision after accepted Stage C |

No protected archive members may be read/listed/extracted for previews, preprocessing, integrity statistics or model experiments during G3. Whole opaque archive hashes bind custody without opening members. Public NASA availability or public GitHub visibility is not authorization.

After separately authorized B: preserve exact sensor source/hash, extract sensors only; check all expected 100 endpoints/26 fields, finite positive contiguous cycles, namespaces and unique engine-cycle keys. Complete overlap/near-duplicate audit; the prespecified heuristic requires >=30 common cycles, mean normalized RMSE<=.02 and max channel<=.10. Heuristic limitations remain disclosed. Input/overlap/count flags stop for owner review; never exclude/redefine cohort. Fixed-model prediction and all quantile/MCMC/replication guards must pass; preserve all failures and immutable source/model/sensor/prediction/diagnostic hashes.

Only after C accepts the complete freeze may a separate D authorize labels. Validate complete N alignment/hash/finite positive uncapped RUL; use already frozen endpoints, no label-driven repair. Complete finite score uses float64 and compensated contrast; any missing/nonfinite primary pair makes UNAVAILABLE. Score MCSE/kink qualification does not authorize resampling or replacing predictions; retain stored score and report flags.

Protection is procedural; no independent encrypted vault or software-enforced separate identity system is claimed. Stop/report/retain on failure. No silent seeds, draws, priors, model fallback, bracket-method or threshold changes. Each future permission and any amendment requires a dated owner decision and auditable exact identities.
''')
md('docs/protocol_lock/LOCK_DECISION_RECORD.md',f'''# RP-001 | Formal Lock Decision Record {VERSION}

**Decision: PROTOCOL_LOCKED, Stage A only.** Observed UTC {now}; owner client date {local_date} Asia/Jakarta.

Authority is the human Raihan in the current conversation, stated Research Owners Raihan x Rei. [Original G3 directive](OWNER_AUTHORIZATION_G3.md) grants formal lock only. [G3-AM-001 decision](OWNER_AMENDMENT_DECISION_G3_AM_001.md) explicitly approves the recommended quantile clarification after reviewing {REVIEW}. That second file is a UTF-8 transcription of the user message; its content hash certifies stored bytes, not legal identity or a cryptographic signature. No invented owner signature.

The original v0.5 contract and approved scientific source remain byte-preserved at {BASE}. Failed G3 evidence/receipt remain byte-preserved under history/G3_lock_attempt_1 and at {REVIEW}. Their FAIL/PENDING states are not overwritten or retroactively accepted. Current lock succeeds after the approved single-clause correction and resumed checks; there is no new method, posterior, comparator, estimand or threshold.

Direct SOL verification covers model, prior, separate-engine prediction, corrected mixture-CDF route, CQR rank/calibration/support, primary score, numerical guards, aligned score-uncertainty propagation, exact finite estimand and protected phases. Canonical precision source SHA-256: {A['authoritative_quantile_route']['module_sha256']}.

Three manifests bind frozen inputs/states/source/config/environment. Historical source aliases/runners and older proposed protocols are provenance, not permission or alternative official methods. Only the current locked contract and explicit four-phase policy govern future execution. The legacy native owner_stage_b_approved field denotes final-protocol completion; official sensor Stage B remains explicitly false.

The payload commit and final contract/package hashes are supplied by LOCK_RECEIPT.json, stored in a subsequent administrative receipt commit to avoid circular self-commit identity. The payload receipt stub is clearly pending until that final receipt. No branch/head movement is treated as a new scientific snapshot without reviewed amendment.

Stop at the next gate. B sensors, C acceptance and D labels/scoring are unauthorized. Scientific publication, raw redistribution, new fitting/sampling/experiments and fallback are unauthorized.
''')
# Native metadata advances only administrative references/status; scientific policies stay untouched.
p=read('research/protocol.json')
p.update(status='PROTOCOL_LOCKED',protocol_locked_at=now,updated_at=now,artifact_version=VERSION,pilot_disposition='PROTOCOL_LOCKED_AWAITING_SEPARATE_STAGE_B_AUTHORIZATION',owner_stage_b_approved=True,formal_lock_integrity='PASS_AFTER_APPROVED_G3_AM_001',locked_analysis_contract='docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md',locked_analysis_contract_sha256=sha('docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md'),locked_research_protocol='docs/protocol_lock/LOCKED_RESEARCH_PROTOCOL.md',approved_amendment='G3-AM-001',owner_amendment_decision='docs/protocol_lock/OWNER_AMENDMENT_DECISION_G3_AM_001.md',protected_evaluation_authorization=auth,legacy_owner_stage_b_field_note='Legacy field means final-protocol approval/completion only; official sensor Stage B is explicitly false in protected_evaluation_authorization.',authoritative_scientific_contract_note='Complete methods and claim boundaries are the locked amended v0.5 contract; older generic native wording is historical metadata and does not authorize population inference or protected access.')
p['preregistration'].update(location='docs/protocol_lock/LOCK_RECEIPT.json',registered_at=now)
write('research/protocol.json',p)
s=read('research/state_manifest.json')
s.update(record_type='current-formal-G3-locked-state-pointer',updated_at=now,protocol_status='PROTOCOL_LOCKED',recommendation='PROTOCOL_LOCKED_AWAITING_SEPARATE_STAGE_B_AUTHORIZATION',protocol_lock_authorized=True,protocol_lock_succeeded=True,protocol_locked_at=now,locked_protocol_version=VERSION,protected_evaluation_authorization=auth,blockers=[],resolved_amendments=['G3-AM-001'],latest_status_report='docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md',latest_attempt_receipt='docs/protocol_lock/LOCK_RECEIPT.json',lock_receipt='docs/protocol_lock/LOCK_RECEIPT.json',owner_amendment_decision='docs/protocol_lock/OWNER_AMENDMENT_DECISION_G3_AM_001.md',historical_attempt_receipt='docs/protocol_lock/history/G3_lock_attempt_1/LOCK_RECEIPT.json',baseline_state_archive=preserve['research/state_manifest.json']['archive'],note='Formal G3 lock completed after approved quantile specification amendment; no scientific implementation change or protected permission.')
write('research/state_manifest.json',s)
lock={'schema_version':'G3-1','artifact_version':VERSION,'status':'PROTOCOL_LOCKED','locked_at':now,'owner':'Raihan x Rei','owner_authorization':['docs/protocol_lock/OWNER_AUTHORIZATION_G3.md','docs/protocol_lock/OWNER_AMENDMENT_DECISION_G3_AM_001.md'],'approved_scientific_commit':BASE,'approved_amendment_review_commit':REVIEW,'locked_contract_path':'docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md','locked_contract_sha256':sha('docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md'),'scientific_source_map_sha256':A['scientific_source_map_sha256'],'environment_fingerprint':A['environment_fingerprint'],'dataset_sha256':A['input_identities']['data/raw/train_FD001.txt'],'split_sha256':A['input_identities']['configs/proposed_split_manifest.json'],'protected_evaluation_authorization':auth,'scientific_publication_authorized':False,'confirmatory_evaluation_authorized':False,'official_test_access_authorized':False,'receipt':'docs/protocol_lock/LOCK_RECEIPT.json'}
write('configs/protocol_lock_record.json',lock)
g=read('research/gate_results.json');g.update(version=VERSION,scope='Formal G3 lock only; future evaluation remains unauthorized',recommendation='PROTOCOL_LOCKED_AWAITING_SEPARATE_STAGE_B_AUTHORIZATION',updated_at=now)
for row in g['gates']:
 if row['gate']=='OWNER_PROTOCOL_LOCK':row.update(state='PASS',artifact_version=VERSION,evidence_ids=['G3-LOCK-VERIFY','G3-AM-DECISION'],rationale='Human formal lock and quantile amendment approved; exact corrected specification/source consistency and integrity PASS.')
g['gates'].append({'gate':'G3_AMENDMENT_SOURCE_CONSISTENCY','state':'PASS','owner':'Rei / SOL direct verifier','artifact_version':VERSION,'evidence_ids':['G3-AM-DECISION','G3-LOCK-VERIFY'],'rationale':'Only approved quantile clause substituted; original scientific source unchanged.'})
write('research/gate_results.json',g)
# Historical risk remains historical; current risk record resolves only the approved blocker.
write('research/protocol_lock/final_G3/risk_register.json',{'version':VERSION,'G3_AM_001':{'status':'RESOLVED_BY_EXPLICIT_OWNER_AMENDMENT','decision_source':'docs/protocol_lock/OWNER_AMENDMENT_DECISION_G3_AM_001.md','original_failed_case':'docs/protocol_lock/history/G3_lock_attempt_1/LOCK_VERIFICATION_REPORT.md'},'unresolved_scientific_risks':'research/v0.5/blocker_disposition.json','execution_stage_readiness':'DEFERRED_UNTIL_SEPARATE_STAGE_B_AUTHORIZATION','novelty_data_rights_clean_replay':'UNRESOLVED_PUBLICATION_REQUIREMENTS'})
write('docs/protocol_lock/LOCK_RECEIPT.json',{'version':VERSION,'status':'PENDING_POSTCOMMIT_RECEIPT','protocol_status':'PROTOCOL_LOCKED','lock_payload_commit':None,'note':'Payload receipt stub only. Final receipt follows committed verified payload, preventing circular self-commit identity.','protected_evaluation_authorization':auth})
write('logs/protocol_lock/final_G3/build_context.json',{'version':VERSION,'recorded_lock_at_utc':now,'client_date':local_date,'amendment_change_record':change,'preservation_map':preserve,'source_map_sha256':A['scientific_source_map_sha256']})
print(json.dumps({'version':VERSION,'scientific_substitutions':1,'original_scientific_source_unchanged':True,'historical_aliases_preserved':len(preserve),'locked_contract_sha256':sha('docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md'),'phase_permissions':auth},indent=2))
