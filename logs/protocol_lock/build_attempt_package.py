from pathlib import Path
import json,hashlib,datetime,csv,io
R=Path.cwd();D=R/'docs/protocol_lock';D.mkdir(parents=True,exist_ok=True)
A=json.loads((R/'logs/protocol_lock/baseline_verification.json').read_text(encoding='utf8'))
S=json.loads((R/'logs/protocol_lock/saved_state_verification.json').read_text(encoding='utf8'))
assert A['baseline_integrity']==S['overall_saved_state_integrity']=='PASS'
now=datetime.datetime.now(datetime.timezone.utc).isoformat();version='G3-lock-attempt-1';base=A['owner_baseline_commit']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,obj):
    path=R/p;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def md(p,body):(R/p).write_text(body.strip()+'\n',encoding='utf8')
AUTH=Path(r'C:\Users\Raihan\.codex\attachments\0b4e45e1-4671-4a5b-80f0-da81ebcfd851\Pasted text.txt')
(D/'OWNER_AUTHORIZATION_G3.md').write_bytes(AUTH.read_bytes())
aliases=['README.md','GITHUB_REVIEW.md','research/protocol.json','research/state_manifest.json','research/gate_results.json','research/decision_log.md','research/artifact_map.csv']
archives={}
for p in aliases:
    arc='research/protocol_lock/baseline_current_aliases/'+p;path=R/arc;path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError(arc)
    payload=(R/p).read_bytes();path.write_bytes(payload)
    archives[p]={'archive':arc,'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}
write('research/protocol_lock/baseline_alias_archive_map.json',archives)
contract='docs/v0.5/02_proposed_locked_analysis_contract.md'
manifest={'artifact_version':version,'status':'VERIFIED_BASELINE_NOT_LOCKED','owner_reviewed_scientific_commit':base,'administrative_baseline_head':A['administrative_head_before_G3'],'contract_path':contract,'contract_sha256':sha(contract),'source_map_sha256':A['scientific_source_map_sha256'],'source_map_encoding':A['source_map_encoding'],'scientific_source_files':A['scientific_source_files'],'environment_fingerprint':A['environment_fingerprint'],'dataset_split_plan':A['identities'],'principal_posteriors':A['principal_posteriors'],'saved_models_and_preprocessing':S,'owner_authority':A['owner_directive'],'owner_authority_document_sha256':sha('docs/protocol_lock/OWNER_AUTHORIZATION_G3.md'),'v05_delivery_manifest_sha256':sha('logs/v0.5/delivery_manifest.json'),'v05_delivery_receipt_sha256':sha('logs/v0.5/delivery_receipt.json'),'baseline_file_checks':A['file_checks'],'current_alias_archives':archives,'successful_lock':False}
write('docs/protocol_lock/VERIFIED_BASELINE_MANIFEST.json',manifest)
md('docs/protocol_lock/AMENDMENT_REQUEST_G3_AM_001.md','''# RP-001 | Amendment Request G3-AM-001

**PENDING OWNER DECISION. No amendment applied. PROTOCOL_DRAFTED.**

Owner-reviewed baseline: c583ce62eac9a6b3dcd29c1929cc07c17569beb7. Section 3 of the [G3 authorization](OWNER_AUTHORIZATION_G3.md) requires returning a material output-related ambiguity for amendment rather than silently repairing it.

## Exact discrepancy

| Location at approved baseline | Numerical rule |
|---|---|
| docs/v0.5/02_proposed_locked_analysis_contract.md:70 | Brent bracket min(mu - 12 SD) to max(mu + 12 SD), xtol=1e-12; called the frozen v0.4 precision implementation. |
| src/rp001/v04_precision.py:78-108 | r=(abs(Phi^-1(p))+12)*s_max+(m_max-m_min); bracket [m_min-r,m_max+r]. Up to 100 predetermined bracket-check attempts, doubling r if not bracketed; invalid/nonfinite radius fails. Brent xtol=1e-12, rtol=4*float64 epsilon. |
| src/rp001/prediction.py:7-17 | Legacy componentwise +/-12 SD bracket, but Brent xtol=1e-10. |

The v0.5 prose combined the legacy bracket with the precision-helper tolerance. Rei's contract drafting failed to distinguish those implementations. Neither helper exactly matches that combined description. Source bytes and historical results remain unchanged.

The precision function supplied the archived quantiles used by precision diagnostics and saved-draw score propagation; the legacy helper also supplied separate development prediction summaries. The official procedure needs one explicit route for stored endpoints and aligned diagnostics/influences.

## Materiality and mathematical assessment

A finite normal mixture with positive variances and normalized nonnegative weights has a continuous strictly increasing CDF and unique target quantile. At the legacy lower bound each component CDF is at most Phi(-12); at the upper bound each is at least Phi(12). Both brackets therefore enclose the same exact root for p=.05/.50/.95. This discrepancy does not demonstrate a different posterior distribution, invalid MCMC evidence, or a material historical score difference.

Initial bounds, bracket-expansion behavior, solver tolerance, floating-point path and potential failures nevertheless differ. No future endpoint computation has quantified their effect. Because G3 requires the exact numerical and failure procedure to be frozen without interpretation, this is a specification consistency blocker requiring owner disposition. It is not an additional robustness stress test.

## Recommended minimal amendment: existing precision implementation

Replace only the bracket/tolerance clause in contract line 70 with this proposed text:

> For principal official endpoints and independent-fit diagnostics, use the quantile returned by rp001.v04_precision.estimate_mixture_quantile_mcse and its _weighted_quantile implementation at the approved source hash. For probability p, finite component means and positive component SDs, set m_min=min(mu), m_max=max(mu), s_max=max(SD), r=(abs(Phi^-1(p))+12)*s_max+(m_max-m_min), and initial bracket [m_min-r,m_max+r]. Preserve the existing deterministic limit of 100 bracket-check attempts, doubling r only if the CDF does not bracket p; invalid/nonfinite bracketing is retained as failure. Brent uses xtol=1e-12, rtol=4*float64 epsilon, and remaining defaults bound to the pinned SciPy environment. The same returned log quantile and exponentiated endpoint supply prediction storage, CDF/density checks, quantile diagnostics and score influence. The legacy rp001.prediction.mixture_quantile helper remains historical and does not supply official primary endpoints. Retain root residual <=1e-10 and every existing numerical/prediction-failure guard. This predetermined algorithm grants no additional draws, model change, result-selected repair or post-label retry.

Approval would align the prose with existing owner-reviewed source. No scientific source modification is requested. Priors, posterior states, preprocessing, CQR selection/correction, score/estimand, MCSE thresholds and claim boundaries remain unchanged. No new science experiment is requested.

Owners may instead require literal +/-12 SD bounds with xtol=1e-12; that would require explicit source amendment and separately scoped deterministic verification. It has not been implemented.

Full source/input/posterior identities are in [VERIFIED_BASELINE_MANIFEST.json](VERIFIED_BASELINE_MANIFEST.json). After an accepted exact amendment, resume G3 packaging/verification only. Complete lock before any separately authorized Stage B work.

**Requested owner decision: approve recommended G3-AM-001 clarification, or specify another reviewed numerical procedure. B/C/D remain unauthorized.**
''')
components=[
('MODEL_SPECIFICATION','CONSISTENT','Direct SOL review: joint Gaussian g/z/logR marginal, covariance and AR1/Woodbury source match; prior dense-oracle evidence retained.',['src/rp001/model.py','src/rp001/v04_model.py']),
('PRIOR','CONSISTENT','anchored_v04 priors and saved fit policy match; exposed development adaptation remains disclosed.',['src/rp001/v04_model.py','configs/v0.4/remediation_plan.json']),
('POSTERIOR_PREDICTION','CONSISTENT_WITH_ROUTE_BLOCKER','Separate sensor-only importance update/conditional Gaussian mixture match; 3 x 4 x 8000 principal states verified. Quantile route pending.',['src/rp001/v04_predict.py','src/rp001/v04_analysis.py']),
('CQR','CONSISTENT','12 fixed candidates/ties/refit agree; ceil(26*.9)=24, q=19.987558518873357; support projection retained. No official exchangeability guarantee.',['src/rp001/comparators.py','src/rp001/metrics.py','results/pilot/comparator_calibration.json']),
('PRIMARY_SCORE','CONSISTENT','IS90=U-L+20max(L-y,0)+20max(y-U,0); Bayesian-minus-CQR on complete uncapped finite cohort. Future contrast requires compensated aggregation.',['src/rp001/metrics.py','src/rp001/v05_score_numerics.py']),
('NUMERICAL_GATES','FAIL','Other guard thresholds/influence formulas agree; bracket/tolerance/helper identity conflicts (G3-AM-001). No threshold relaxed.',['src/rp001/v04_precision.py','src/rp001/prediction.py',contract]),
('SCORE_UNCERTAINTY','CONSISTENT','X=-Q*w*(F-p)/(mean(w)*f), indicator score gradients, aligned joint covariance/projection, Satterthwaite approximation, kink qualification and 19/N conditional sensitivity agree. Prior saved-draw check retained.',['src/rp001/v05_score_numerics.py','docs/v0.5/03_mathematical_validity.md']),
('FINITE_ESTIMAND','CONSISTENT','Exact complete stored prediction comparison only; no population inference, binary competitive decision, practical margin, superiority/equivalence/noninferiority or operational certification.',[contract]),
('PROTECTED_ACCESS','CONSISTENT_AND_HONORED','A lock authorized but unsuccessful; B sensors, C freeze acceptance and D labels/scoring separate and unauthorized. No protected member reads/predictions.',['docs/protocol_lock/OWNER_AUTHORIZATION_G3.md',contract])]
signoffs=[{'component':c,'disposition':s,'direct_verifier':'Rei / SOL lead','verified_at':now,'rationale':r,'source_hashes':{p:sha(p) for p in paths},'scope':'Direct static scientific consistency review, saved-state identity/metadata and already archived scoped numerical evidence; no fresh numerical experiment'} for c,s,r,paths in components]
write('logs/protocol_lock/direct_SOL_component_review.json',{'version':version,'overall':'FAIL_FOR_FORMAL_LOCK','locked':False,'cryptographic_signature':None,'identity_limit':'AI role attribution only; not a human signature or independently authenticated identity','components':signoffs})
rows='\n'.join('| '+c+' | '+s+' | '+r+' |' for c,s,r,paths in components)
posts='\n'.join('| '+p['run_id']+' | '+p['sha256']+' | 4 x 8000 | '+p['diagnostics']['acceptance']+' |' for p in A['principal_posteriors'])
md('docs/protocol_lock/LOCK_VERIFICATION_REPORT.md',f'''# RP-001 | G3 Lock Verification Report

**Overall: FAIL FOR FORMAL LOCK. Baseline integrity: PASS. State: PROTOCOL_DRAFTED.**

Verification UTC: {now}; local calendar date 2026-10-09 Asia/Jakarta.
Owner-reviewed scientific commit: {base}.
Administrative baseline HEAD: {A['administrative_head_before_G3']}.

## Actual identity verification

All 593 v0.5 manifest entries match actual byte lengths/SHA-256: 560 also match exact Git blobs at the approved snapshot; 33 are retained verified local-only payloads. No missing/mismatching baseline artifact. Actual final local delivery receipt matches its manifest hash and scientific commit. [Complete audit](../../logs/protocol_lock/baseline_verification.json).

Fresh interpreter, platform and installed-package metadata matches saved environment. Float64/nutpie/one-thread labels identify preserved execution policy; no sampler or BLAS workload was run to recapture them. The 64-package lock is hash-bound. Actual authorized input files were hashed. Whole opaque archive bytes were hashed only; no archive listing/member reads.

| Identity | Actual SHA-256 |
|---|---|
| Approved v0.5 contract | {sha(contract)} |
| Scientific source map (sorted compact JSON) | {A['scientific_source_map_sha256']} |
| Environment stable fingerprint | {A['environment_fingerprint']} |
| FD001 training | {A['identities']['data/raw/train_FD001.txt']['sha256']} |
| Split/cutoff | {A['identities']['configs/proposed_split_manifest.json']['sha256']} |
| v0.5 resolution plan | {A['identities']['configs/v0.5/resolution_plan.json']['sha256']} |
| Dependency lock bytes | {sha('configs/requirements-pilot.lock')} |
| Local final v0.5 receipt | {sha('logs/v0.5/delivery_receipt.json')} |
| Selected CQR fitted object | {S['selected_comparator']['sha256']} |
| Refit preprocessing | {S['refit_preprocessor']['sha256']} |

| Principal state | SHA-256 | Chains x retained draws | Saved diagnostics |
|---|---|---|---|
{posts}

Saved posterior dimensions/finite physical and auxiliary values were inspected without sampling/recomputing diagnostics. Selected CQR endpoint/median objects are completed 56-engine refits: 200 trees, depth 1, leaf 10, learning rate .1, seed 20261008. Saved refit maps match all three principal preprocessor maps exactly. Eligibility remains 43/13/25; calibration rank 24 and q=19.987558518873357. [Saved-state audit](../../logs/protocol_lock/saved_state_verification.json).

## Direct SOL scientific sign-off by component

| Component | Disposition | Finding |
|---|---|---|
{rows}

CONSISTENT is a scoped static consistency sign-off using already archived numerical evidence; it does not grant PROTOCOL_LOCKED or RESEARCH_VALIDATED or guarantee future endpoint success. [Full sign-off/source hashes](../../logs/protocol_lock/direct_SOL_component_review.json).

## Material inconsistency and halt

Contract line 70 combines the legacy +/-12 SD bracket with precision-helper 1e-12 tolerance. Precision source actually uses a larger probability-dependent radius and deterministic bracket expansion; legacy source uses 1e-10 tolerance. Neither exactly matches the combined description. [G3-AM-001](AMENDMENT_REQUEST_G3_AM_001.md) supplies exact locations, a direct uniqueness/bracketing argument, materiality assessment and minimal unexecuted replacement.

The mismatch concerns exact numerical procedure/failure behavior. It does not demonstrate changed posterior target, invalid historical sampling or a material historical score difference. No future endpoint computation quantified its effect. G3 section 3 prohibits silently choosing between the rules.

No final ten-file lock package is certified, no locked research/analysis contract is manufactured, no lock timestamp is assigned, and successful lock commit is null. Receipt is an unsuccessful-attempt receipt. Original scientific source/configuration/results remain unchanged. Seven advanced administrative aliases have byte-preserved archives.

## Historical failures and evidence preserved

- Original v04_syn_high_rho_3 remains FAIL; bounded v05 diagnostic inquiry PASS is not a production posterior replacement.
- v0.3 quantile precision FAIL (.728972 versus .5 cycles) remains; v0.4 calibration precision PASS is not official endpoint certification.
- Eight dependent pipeline perturbations/four paired contrasts and CQR winner changes remain; no unconditional pipeline variance estimate.
- Adverse bootstrap operating characteristics and 999 unavailable replicates remain; no primary population bootstrap.
- Existing 59-test XML was hash-verified, not rerun. Registry remains 73 records; original 71-record prefix unchanged. G3 appended no scientific run.

## Authorization and next gate

Stage A formal lock is authorized, but consistency failed. B official sensors, C prediction-freeze acceptance and D labels/scoring remain separately unauthorized. No official members were extracted/read/previewed/predicted/scored. No MCMC, new experiment, reselection, fallback, threshold relaxation or spending.

After accepted amendment and successful resumed G3, the first action **only if separately authorized for B** is to record the exact instruction/source identities, extract sensors alone, and audit all expected endpoints for schema/IDs/finite contiguous cycles/overlap before fixed-model predictions. Stage C acceptance and Stage D labels remain separate decisions.

Outstanding execution risks: unknown cutoff transport/exchangeability, future numerical/input failures, weak physical nuisance identification, exposed calibration/prior adaptation, unequal features/search/compute, small tuning/calibration cohorts, approximate MCSE/kink qualification, incomplete cross-platform clean replay, 33 local-only historical payloads, unresolved novelty and lawful redistribution. Retained limitations are not additional automatic lock blockers; G3-AM-001 is the sole current freeze blocker.

Repository remains PUBLIC under explicit owner direction. [History audit](../../logs/protocol_lock/public_history_audit.json) found no forbidden raw/protected input paths or concrete credential signatures in its bounded scope; staged-file audit follows before push. This is not proof of absence of every possible secret. Public review access does not authorize scientific publication or raw-data redistribution.
''')
md('docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md',f'''# RP-001 | G3 FORMAL PROTOCOL LOCK COMPLETION REPORT

**Lock not completed. PROTOCOL_DRAFTED. Recommendation: OWNER AMENDMENT REVIEW REQUIRED (G3-AM-001).**

Formal Stage A authorization is received. Actual baseline identities PASS. The quantile bracket/tolerance wording does not match either stored helper; G3 requires returning this inconsistency rather than silently repairing it. No new experiment or protected-data access.

| Required item | Result |
|---|---|
| Lock success | No; numerical-procedure consistency FAIL. |
| Exact locked version | None. Candidate v0.5 unchanged at {base}; audit package {version}. |
| Successful lock commit | None/null. LOCK_RECEIPT.json records the administrative evidence commit, not a successful lock. |
| Contract/scientific source hashes | Full hashes in VERIFIED_BASELINE_MANIFEST.json and LOCK_VERIFICATION_REPORT.md. |
| Input/environment/posterior fingerprints | Actual file/environment checks PASS; all principal 3 x 4 x 8000 states verified. |
| Verification results | 593 files / 560 Git blobs / 33 local-only PASS; stored CQR/maps PASS; numerical-route consistency FAIL. |
| Historical failures | Original high-rho FAIL, v0.3 precision FAIL, pipeline sensitivity and adverse/unavailable bootstrap retained. |
| Authorization | A authorized but unsuccessful; B sensors, C freeze acceptance, D labels/scoring unauthorized. |
| Execution risks | Restricted-claim limitations fully listed in verification report. |
| First separately authorized B action | After amended successful G3: record separate permission/provenance, extract sensors only, audit complete schema/identity/overlap. |

[Amendment request](AMENDMENT_REQUEST_G3_AM_001.md) provides a concrete minimal clarification to use the existing reviewed precision helper for stored official endpoints and aligned diagnostics. It changes no source bytes, posterior/prior, comparator, estimand, thresholds or claim boundaries. It is **not applied**.

[Verification report](LOCK_VERIFICATION_REPORT.md) · [Baseline manifest](VERIFIED_BASELINE_MANIFEST.json) · [Attempt receipt](LOCK_RECEIPT.json) · [Direct SOL review](../../logs/protocol_lock/direct_SOL_component_review.json).

[Owner authorization](OWNER_AUTHORIZATION_G3.md) is byte-exact. Human sender Raihan is verified only from this conversation; stated Research Owners Raihan x Rei. Observed date is recorded, with no invented cryptographic signature or independent legal identity claim.

**Halted at Stage A consistency gate. Owner G3-AM-001 disposition is required before resumed lock. No Stage B work begins.**
''')
md('docs/protocol_lock/README.md','''# RP-001 | G3 formal-lock attempt

**PROTOCOL_DRAFTED — G3-AM-001 pending owner disposition.**

- [Completion/status report](G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md)
- [Concrete amendment request](AMENDMENT_REQUEST_G3_AM_001.md)
- [Verification report](LOCK_VERIFICATION_REPORT.md)
- [Verified baseline identities](VERIFIED_BASELINE_MANIFEST.json)
- [Owner authorization](OWNER_AUTHORIZATION_G3.md)
- [Attempt receipt](LOCK_RECEIPT.json)

This records a halted attempt, not a certified locked protocol. Original v0.5 evidence is unchanged; A is authorized, B/C/D remain unauthorized.
''')
authorization={'stage_A_formal_lock':True,'stage_B_official_test_sensors':False,'stage_C_prediction_freeze_acceptance':False,'stage_D_official_test_labels_and_scoring':False}
state=json.loads((R/'research/state_manifest.json').read_text())
state.update(record_type='current-G3-lock-attempt-state-pointer',updated_at=now,protocol_status='PROTOCOL_DRAFTED',recommendation='OWNER AMENDMENT REVIEW REQUIRED',protocol_lock_authorized=True,protocol_lock_succeeded=False,protocol_locked_at=None,owner_directive='docs/protocol_lock/OWNER_AUTHORIZATION_G3.md',owner_directive_sha256=sha('docs/protocol_lock/OWNER_AUTHORIZATION_G3.md'),protected_evaluation_authorization=authorization,blockers=['G3-AM-001'],latest_status_report='docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md',latest_attempt_receipt='docs/protocol_lock/LOCK_RECEIPT.json',baseline_state_archive=archives['research/state_manifest.json']['archive'],note='Human G3 lock authorized; consistency fails pending amendment. No protected access or new science.')
write('research/state_manifest.json',state)
protocol=json.loads((R/'research/protocol.json').read_text())
protocol.update(updated_at=now,status='PROTOCOL_DRAFTED',protocol_locked_at=None,pilot_disposition='OWNER AMENDMENT REVIEW REQUIRED',owner_protocol_lock_directive_received=True,owner_protocol_lock_directive='docs/protocol_lock/OWNER_AUTHORIZATION_G3.md',formal_lock_integrity='FAIL_G3_AM_001',protected_evaluation_authorization=authorization,legacy_owner_stage_b_field_note='Legacy final-protocol completion remains false: no consistent final lock completed. This is not the new official-sensor Stage B, whose separate authorization is explicitly false.')
write('research/protocol.json',protocol)
gates=json.loads((R/'research/gate_results.json').read_text())
gates.update(scope='G3 formal lock verification only',recommendation='OWNER AMENDMENT REVIEW REQUIRED',updated_at=now)
for g in gates['gates']:
    if g['gate']=='OWNER_PROTOCOL_LOCK':g.update(state='FAIL',rationale='Stage A authorization received; G3-AM-001 consistency mismatch prevents lock.',evidence_ids=['G3-AM-001','G3-VERIFY'])
gates['gates'].append({'gate':'G3_BASELINE_BYTE_IDENTITY','state':'PASS','owner':'Rei / SOL','artifact_version':version,'evidence_ids':['G3-BASELINE'],'rationale':'593 files, 560 Git blobs, 33 local-only plus live environment match.'})
write('research/gate_results.json',gates)
old=(R/'research/decision_log.md').read_bytes()
(R/'research/decision_log.md').write_bytes(old+f'\n\n## {now} | G3 formal lock: AMENDMENT REQUIRED\n\nHuman Stage A lock authorization recorded byte-exact. Actual baseline PASS; G3-AM-001 bracket/tolerance/helper mismatch fails consistency. Direct SOL review retained. No source/method/results changed, scientific runs appended or protected data accessed. PROTOCOL_DRAFTED. Concrete existing-precision-helper amendment awaits owner acceptance. B/C/D unauthorized. Historical private captions retained; repository PUBLIC under later explicit human direction and G3 instruction.\n'.encode())
md('README.md','''# RP-001 — Bayesian RUL Reliability

**G3 lock halted: G3-AM-001 pending owner disposition. PROTOCOL_DRAFTED.**

Read the [G3 status report](docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md), [minimal amendment](docs/protocol_lock/AMENDMENT_REQUEST_G3_AM_001.md), and [verification report](docs/protocol_lock/LOCK_VERIFICATION_REPORT.md). All 593 baseline files match; the prospective quantile bracket/tolerance/helper description requires clarification before consistent lock.

Owner A lock authorization is received. B sensors, C freeze acceptance and D labels/scoring remain unauthorized. No new experiments, protected access, fallback, reselection or relaxed threshold.

[Approved v0.5 contract](docs/v0.5/02_proposed_locked_analysis_contract.md), [memo](docs/v0.5/01_prelock_resolution_memo.md), [evidence](docs/v0.5/README.md) and [v0.4](docs/v0.4/README.md) remain unchanged. Primary interpretation is descriptive exact finite-benchmark comparison; no population superiority or practical margin.

Repository PUBLIC under explicit owner visibility direction. Historical private-review captions are retained as history. Raw training/NASA archives/protected members excluded; 33 historical local-only payloads remain fingerprint-bound. Public access does not certify dataset redistribution, novelty, operational utility or complete clean replay.

[Attempt receipt](docs/protocol_lock/LOCK_RECEIPT.json) · [baseline manifest](docs/protocol_lock/VERIFIED_BASELINE_MANIFEST.json) · [alias archive map](research/protocol_lock/baseline_alias_archive_map.json).
''')
md('GITHUB_REVIEW.md','''# RP-001 — Web Review

Repository PUBLIC sesuai instruksi Raihan. **PROTOCOL_DRAFTED — G3-AM-001 pending owner disposition.**

Baca [G3 status report](docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md), [amendment terbatas](docs/protocol_lock/AMENDMENT_REQUEST_G3_AM_001.md), dan [verification report](docs/protocol_lock/LOCK_VERIFICATION_REPORT.md). Seluruh 593 baseline files cocok. Lock berhenti karena aturan bracket/toleransi quantile tidak cocok dengan helper kode; tidak diperbaiki diam-diam.

[Attempt receipt](docs/protocol_lock/LOCK_RECEIPT.json) mencatat evidence commit administratif; successful lock commit null. A diizinkan tetapi belum berhasil; B sensors, C freeze acceptance, D labels/scoring masih terpisah dan belum diizinkan.

[Paket v0.5](docs/v0.5/README.md) dan c583ce62eac9a6b3dcd29c1929cc07c17569beb7 dipertahankan. Raw data/protected members tidak dipublikasikan. Current aliases memiliki byte archives. Caption private pada evidence lama merupakan catatan historis.
''')
entries=[('G3-REPORT','docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md'),('G3-AM-001','docs/protocol_lock/AMENDMENT_REQUEST_G3_AM_001.md'),('G3-VERIFY','docs/protocol_lock/LOCK_VERIFICATION_REPORT.md'),('G3-BASELINE','logs/protocol_lock/baseline_verification.json'),('G3-AUTH','docs/protocol_lock/OWNER_AUTHORIZATION_G3.md'),('G3-SAVED','logs/protocol_lock/saved_state_verification.json')]
raw=(R/'research/artifact_map.csv').read_bytes();buf=io.StringIO(newline='');writer=csv.writer(buf)
for eid,p in entries:writer.writerow([eid,'governance-verification',p,'','RP001-G3-formal-lock-only',sha(p)])
(R/'research/artifact_map.csv').write_bytes(raw+buf.getvalue().encode())
evidence=[{'evidence_id':eid,'kind':'static-governance-verification','location':p,'sha256':sha(p),'collected_at':now,'method':'Actual hashes/Git/environment/static SOL review','supports':'Baseline PASS, consistent formal lock FAIL','provenance_chain':'Human G3 -> approved c583 -> existing byte/source audit -> amendment -> owner return'} for eid,p in entries]
risk={'risk_id':'G3-AM-001','statement':'Exact quantile numerical description combines legacy/precision procedures.','severity':'critical','likelihood':'Observed','affected_claims_or_gates':['G3_PROTOCOL_LOCK_CONSISTENCY'],'owner':'Research Owners Raihan x Rei; SOL supplies clarification','disposition':'Draft retained; concrete existing-source amendment unexecuted','trigger':'Before lock completion and Stage B'}
write('research/protocol_lock/risk_register.json',{'artifact_version':version,'risks':[risk],'retained_scientific_risks':'research/v0.5/blocker_disposition.json','new_robustness_experiment_required':False})
handoff={'schema_version':'1.0.0','handoff_id':'RP001-G3-LOCK-ATTEMPT-1','parent_work_id':'RP-001','producer':'scientific-research-engine','consumer':'scientific-research-engine','producer_role':'Rei / SOL lead','consumer_role':'Research Owners','human_recipient':'Raihan x Rei','artifact_type':'formal-lock-verification-and-amendment-request','artifact_version':version,'artifact_identity':{'path_or_uri':'docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md','sha256_or_version':sha('docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md'),'created_at':now,'source_revision':base},'scope':'Formal lock only; no experiments or protected evaluation','applicability':'APPLICABLE_MANDATORY','claims_or_requirements':'Return failed consistency gate and concrete amendment; do not force lock.','evidence':evidence,'gate_results':[{'gate':'G3_BASELINE_IDENTITY','state':'PASS','owner':'Rei / SOL','artifact_version':version,'evidence_ids':['G3-BASELINE'],'rationale':'All baseline actual identities match.'},{'gate':'G3_PROTOCOL_LOCK_CONSISTENCY','state':'FAIL','owner':'Rei / SOL; owner amendment decision','artifact_version':version,'evidence_ids':['G3-AM-001','G3-VERIFY'],'rationale':'Exact quantile procedure mismatches approved prose.'}],'assumptions':['Target mixture/formulas unchanged; no demonstrated posterior invalidity or material historical score difference.','Historical scientific bytes preserved.'],'risks':[risk],'unresolved':['G3-AM-001 numerical-route disposition'],'requested_decision':'Approve recommended existing-helper clarification or specify alternative reviewed procedure; then resume G3 only.','return_to_parent':{'state':'BLOCKED','decision_owner':'Research Owners Raihan x Rei','reason':'G3 section 3 requires owner amendment; concrete proposal supplied.'}}
write('docs/protocol_lock/research_lead_handoff.json',handoff)
print(json.dumps({'package':version,'state':state['protocol_status'],'aliases_archived':len(archives),'formal_lock_success':False}))
