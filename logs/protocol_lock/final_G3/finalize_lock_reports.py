from pathlib import Path
import json,hashlib,copy,datetime,csv,io
R=Path.cwd();D=R/'docs/protocol_lock';L=R/'logs/protocol_lock/final_G3'
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def write(p,x):
 q=R/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
def md(p,x):(R/p).write_text(x.strip()+'\n',encoding='utf8')
A=read('logs/protocol_lock/final_G3/resume_baseline_verification.json');C=read('logs/protocol_lock/final_G3/build_context.json');P=C['preservation_map'];V=C['version'];now=C['recorded_lock_at_utc'];BASE=A['original_scientific_commit'];REVIEW=A['reviewed_amendment_commit'];change=C['amendment_change_record'];state=read('research/state_manifest.json')
old=read('logs/protocol_lock/direct_SOL_component_review.json');review=copy.deepcopy(old);review.update(version=V,overall='PASS_FOR_FORMAL_G3_LOCK_ONLY',locked=True,amendment='G3-AM-001',original_scientific_source_unchanged=True,official_test_access=False,new_scientific_runs=0)
for row in review['components']:
 row.update(verified_at=now,disposition='PASS_FOR_LOCK_CONSISTENCY',scope='Direct SOL static specification/source/derivation verification, newly checked artifact identities and retained prior numerical evidence; no fresh scientific experiment.')
 if row['component']=='NUMERICAL_GATES':
  row['rationale']='Approved precision helper route matches source SHA396a5f55...; probability-dependent radius, 100 deterministic attempts, exact expansion/failure, xtol1e-12, rtol4eps. Existing convergence/MCSE/ESS/root residual/replication/failure policies unchanged. Future endpoint guards remain unexecuted.'
 elif row['component']=='POSTERIOR_PREDICTION':
  row['rationale']='Separate engine sensor-only theta update and conditional Gaussian mixture agree. Three saved 4x8000 principal states/finiteness/hash verified; approved precision-helper quantiles supply stored endpoints and aligned diagnostics; legacy helper historical only.'
 elif row['component']=='PROTECTED_ACCESS':
  row['rationale']='Formal A lock authorized and completed; B sensors, C freeze acceptance, D labels/scoring explicitly separate and false. No member read/prediction/scoring.'
 for p,digest in row['source_hashes'].items():assert sha(p)==digest,(row['component'],p)
review['amended_contract_sha256']=sha('docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md')
review['canonical_quantile_route']=A['authoritative_quantile_route']
write('logs/protocol_lock/final_G3/direct_SOL_component_review.json',review)
postrows='\n'.join('| '+x['run_id']+' | '+x['sha256']+' | 4 x 8000 | PASS |' for x in A['principal_posteriors'])
rows='\n'.join('| '+x['component']+' | PASS | '+x['rationale']+' |' for x in review['components'])
md('docs/protocol_lock/LOCK_VERIFICATION_REPORT.md',f'''# RP-001 | Final G3 Lock Verification Report {V}

**PASS FOR FORMAL PROTOCOL LOCK ONLY. PROTOCOL_LOCKED.** Direct SOL verification record UTC {now}; client date 2026-10-09 Asia/Jakarta.

## Authority and exact change

Original owner-approved scientific snapshot: {BASE}. Owner-approved amendment review snapshot: {REVIEW}. Human Raihan's [G3-AM-001 decision](OWNER_AMENDMENT_DECISION_G3_AM_001.md) permits the one numerical specification clarification and necessary administrative references. The recorded transcript SHA is {sha('docs/protocol_lock/OWNER_AMENDMENT_DECISION_G3_AM_001.md')}; no cryptographic signature/independent legal identity is claimed.

Original v0.5 contract SHA {change['original_contract_sha256']} remains unchanged. The approved replacement is exactly the recommended clause; inverse substitution recovers the original bytes. [Exact one-clause diff](AMENDMENT_DIFF.patch) SHA {change['exact_diff_sha256']}. [Amended documentary source](provenance/amended_v0.5_source_contract.md) SHA {change['amended_source_contract_sha256']}. Locked administrative cover plus scientific body SHA {change['locked_contract_sha256']}; scientific-body-only SHA {change['locked_scientific_body_sha256']}. No other scientific body bytes changed. Original typography is preserved rather than normalized.

The previous failed G3 documents/receipt remain byte-exact in history/G3_lock_attempt_1 and at {REVIEW}. Current formal-lock PASS applies to the amended package, not retroactive acceptance of that failed attempt. Administrative aliases have exact archives in the [preservation map](../../research/protocol_lock/final_G3/preservation_map.json).

## Actual baseline/artifact identity checks

Resumed verification rehashed all 593 v0.5 baseline files via current files or exact historical aliases: 560 entries bound to the original Git snapshot and 33 retained local-only payloads. The earlier 38 sealed failed-attempt evidence files and its receipt match the reviewed snapshot. All scientific source bytes still match exact {BASE} Git blobs. Scientific source-map SHA is {A['scientific_source_map_sha256']}.

Actual installed interpreter/platform/64 packages match environment {A['environment_fingerprint']}; float64/nutpie/one-thread remain frozen policy labels, not freshly run sampler/BLAS observations. Dependency-lock SHA {sha('configs/requirements-pilot.lock')}. Training SHA {A['input_identities']['data/raw/train_FD001.txt']}; split/cutoff SHA {A['input_identities']['configs/proposed_split_manifest.json']}; v05 plan SHA {A['input_identities']['configs/v0.5/resolution_plan.json']}. Opaque ZIP files were whole-byte hashed; no archive member listing/read/extraction occurred.

| Principal posterior | SHA-256 | Retained chains x draws | Saved diagnostics rechecked against fixed guards |
|---|---|---|---|
{postrows}

Physical/auxiliary values are finite and saved dimensions unchanged. Saved diagnostic values satisfy Rhat<1.01, both ESS>=400, zero divergences, BFMI>.3, depth saturation<=.01. No diagnostic estimator or sampler was rerun. The three saved preprocessing maps and comparator embedded map match the frozen refit preprocessor. Actual stored CQR model parameters/refit56/calibration25/rank24/q=19.987558518873357 agree. Frozen quantile/score policy does not alter selection or recompute predictions.

[Resumed baseline verification](../../logs/protocol_lock/final_G3/resume_baseline_verification.json) contains full file/source/config/NC identities and metadata. Three frozen manifests bind the principal model/configuration, code/environment and data/split. A future official count of 100 is expected metadata, not an observation made during G3.

## Direct SOL material scientific component sign-off

| Component | Final consistency disposition | Direct verification |
|---|---|---|
{rows}

[Full source-bound sign-off](../../logs/protocol_lock/final_G3/direct_SOL_component_review.json). Model consistency follows Czz=B S B'+sigma_z^2K, V=(S^-1+B'R^-1B)^-1 and conditional logR mean a beta+gamma'm, variance sigma_r^2+gamma'V gamma; source implements equivalent AR whitening/Woodbury. Prior coefficient/scale/correlation policies match anchored_v04 and saved configuration.

The approved quantile source SHA {A['authoritative_quantile_route']['module_sha256']} has radius (abs(Phi^-1(p))+12)*max(SD)+(max(mu)-min(mu)), lower=min(mu)-radius, upper=max(mu)+radius, exactly range(100) bracketing attempts, doubling/failure semantics and Brent xtol1e-12/rtol4eps. Pinned SciPy version {A['authoritative_quantile_route']['scipy_version']} binds remaining defaults (maxiter100); source and signature were inspected, not invoked to generate predictions. Root residual<=1e-10 and all prior acceptance/failure guards remain explicit contract/caller obligations. Legacy prediction helper is excluded from official primary quantiles.

Conformal rank ceil(26*.9)=24 and nonshrinking q/support projection agree; this alone grants no official coverage theorem without exchangeability. IS90 endpoint derivatives are -1+20I[y<L], 1-20I[y>U]. Quantile cycle influence -Q*w*(F-p)/(mean(w)*f) and aligned joint chain-batch covariance projection preserve endpoint/engine dependence in the finite contrast. Satterthwaite upper MCSE is approximate, not a finite guarantee. Max derivative magnitude19 supplies the conditional Lipschitz sensitivity, not an MCSE error certificate. Score kinks/undefined or excessive upper MCSE qualify ideal-posterior ranking, while the complete stored score/flags remain. No population interval, practical margin or superiority claim.

No additional material mathematical/methodological contradiction was identified. Existing development numerical evidence supports its previously qualified scope; locking does not certify future endpoint success, full protected driver readiness, whole-pipeline uncertainty, operational prediction or publication novelty.

## Preservation, readiness and failure policies

Original high-rho3 FAIL, bounded diagnostic inquiry PASS, v03 quantile precision FAIL (.728972>.5), pipeline perturbation/winner sensitivity and adverse/999-unavailable bootstrap evidence remain. Existing 59-test XML is hash-bound, not rerun; experiment ledger stays 73 records and claim ledger is unchanged. New scientific runs/sampling/predictions/scoring: zero.

Administrative stale artifact-map aliases are rebound only to existing byte-exact historical archives when hashes match; no underlying historical artifact content or digest is changed. The exact old CSV is preserved; reconciliation log records each reference correction.

Pre-label input/model/numerical failure stops with complete evidence and no engine removal/seed/draw/posterior/threshold/fallback change. Post-label numerical qualification retains frozen stored score; no unauthorized repair. Descriptive finite claims and publication/data-rights/replay limits are unchanged.

## Protected gate and package integrity

A lock is authorized; B sensors, C freeze acceptance and D labels/scoring remain false. No protected data access or extra spending/Colab/new experiment occurred. Stop after receipt. First action only under a separate future B decision: bind that instruction/source identity, extract sensors only, audit complete expected cohort/schema/cycles/overlap, then execute frozen-method predictions/guards and freeze all records for C review. Labels require separate D permission.

[Package QC](../../logs/protocol_lock/final_G3/package_qc.json), native structural validation, history/staged public scans and final receipt provide re-verification evidence. Native validators verify structure/status, not mathematical truth. Repository remains PUBLIC; raw archives/training/protected members remain excluded. Novelty, legal redistribution and complete clean replay remain outstanding publication requirements.

[Completion report](G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md) · [Decision record](LOCK_DECISION_RECORD.md) · [Final receipt](LOCK_RECEIPT.json).
''')
md('docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md',f'''# RP-001 | G3 FORMAL PROTOCOL LOCK COMPLETION REPORT

**SUCCESS: PROTOCOL_LOCKED. Version {V}. Formal Stage A only.**

Owners Raihan x Rei approved G3 and approved G3-AM-001 after reviewing {REVIEW}. Direct SOL final source/specification checks pass. The only scientific documentation change is the approved quantile-clause clarification. No scientific implementation, prior, posterior, CQR, estimand, guard or acceptance policy changed. No new experiment or protected evaluation occurred.

| Required final handoff | Result |
|---|---|
| Lock success / version | PROTOCOL_LOCKED / {V} |
| Exact lock payload commit | Full SHA in [LOCK_RECEIPT.json](LOCK_RECEIPT.json), recorded after payload commit; the receipt's own storage commit is separate. |
| Locked analysis contract | SHA-256 {sha('docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md')} |
| Scientific source map | SHA-256 {A['scientific_source_map_sha256']}; all individual source hashes in frozen code manifest. |
| Environment | {A['environment_fingerprint']} |
| FD001 training | {A['input_identities']['data/raw/train_FD001.txt']} |
| Split/cutoff | {A['input_identities']['configs/proposed_split_manifest.json']} |
| Principal posterior states | v04_main_r1/r2/r3, each4x8000, total96000; exact NC fingerprints in frozen model manifest/verification report. |
| Verification | Baseline593 / original snapshot entries560 / local-only33 PASS; prior38 sealed evidence files PASS; amended body/route and all nine material component sign-offs PASS. |
| Historical adverse findings | Original high-rhoFAIL/v03 precisionFAIL/pipeline sensitivity/bootstrap adverse and unavailable findings retained; failed G3 attempt byte-preserved. |
| Permission status | A completed; B sensors, C acceptance, D labels/scoring all NOT AUTHORIZED. |
| Execution risks | Future schema/overlap/numerical failures; unknown cutoff exchangeability; exposed calibration/prior adaptation; weak physical nuisance identification; small cohorts; unequal budgets; approximate MCSE/kinks; no whole-pipeline inference. |
| Reproducibility/publication limits | 33 retained local-only payloads required; no one-command cross-platform clean replay certified; novelty and data-rights remain unresolved. |
| First action under separately authorized B | Record explicit permission/source identity; extract sensor member only and audit complete expected100/schema/cycles/overlap before fixed predictions. |

The [Locked Analysis Contract](LOCKED_ANALYSIS_CONTRACT.md), [Locked Research Protocol](LOCKED_RESEARCH_PROTOCOL.md), three frozen manifests, [decision record](LOCK_DECISION_RECORD.md), [claim boundaries](SCIENTIFIC_CLAIM_BOUNDARIES.md), [protected policy](PROTECTED_EVALUATION_ACCESS_POLICY.md), [verification report](LOCK_VERIFICATION_REPORT.md) and [receipt](LOCK_RECEIPT.json) form the required ten-file lock core. Amendment diff/owner decisions, component sign-offs, lineage archives and verification logs supplement it.

Human authority is recorded from this conversation; transcript/attachment hashes identify stored text, not an invented cryptographic signature. Observed lock time UTC {now}; client date 2026-10-09 Asia/Jakarta.

**Stop at the next gate. This lock does not authorize official sensors/labels, scoring, sampling, model selection/fallback or scientific publication and does not establish RESEARCH_VALIDATED.**
''')
md('docs/protocol_lock/README.md',f'''# RP-001 | Formal Protocol Lock {V}

**PROTOCOL_LOCKED — Stage A complete; B/C/D remain separately unauthorized.**

- [Final completion report](G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md)
- [Locked research protocol](LOCKED_RESEARCH_PROTOCOL.md) and [analysis contract](LOCKED_ANALYSIS_CONTRACT.md)
- [Model/configuration manifest](FROZEN_MODEL_AND_CONFIGURATION_MANIFEST.json)
- [Code/environment manifest](FROZEN_CODE_AND_ENVIRONMENT_MANIFEST.json)
- [Data/split manifest](FROZEN_DATA_AND_SPLIT_MANIFEST.json)
- [Decision record](LOCK_DECISION_RECORD.md), [claim boundaries](SCIENTIFIC_CLAIM_BOUNDARIES.md), [protected access policy](PROTECTED_EVALUATION_ACCESS_POLICY.md)
- [Verification report](LOCK_VERIFICATION_REPORT.md) and [final receipt](LOCK_RECEIPT.json)
- [Approved amendment decision](OWNER_AMENDMENT_DECISION_G3_AM_001.md), [exact diff](AMENDMENT_DIFF.patch), [change record](AMENDMENT_CHANGE_RECORD.json)

[Original proposed v0.5 contract](../v0.5/02_proposed_locked_analysis_contract.md) is unchanged. [Failed G3 attempt](history/G3_lock_attempt_1/HISTORY_CONTEXT.md) is byte-preserved. Original amendment request retains its historical pending caption; explicit approval and current lock records now govern.
''')
md('README.md',f'''# RP-001 — Bayesian RUL Reliability

**PROTOCOL_LOCKED — {V}. Formal Stage A completed after approved G3-AM-001.**

Start with the [final G3 completion report](docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md), [locked contract](docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md), and [lock index](docs/protocol_lock/README.md). The approved amendment corrects only the numerical quantile specification; scientific source, priors, posterior states, CQR, estimand, thresholds and failure policies are unchanged.

Primary interpretation is descriptive complete finite-FD001 benchmark comparison of stored 90% intervals. No population superiority, practical margin, formal official coverage guarantee or operational utility claim. Existing adverse development findings remain.

Official B sensors, C prediction-freeze acceptance and D labels/scoring remain separately unauthorized. No protected access, new experiments, fitting/resampling, reselection, fallback or threshold relaxation occurred during G3.

[Original v0.5](docs/v0.5/README.md), [failed G3 attempt archive](docs/protocol_lock/history/G3_lock_attempt_1/HISTORY_CONTEXT.md) and earlier evidence remain. Repository PUBLIC under explicit owner direction; raw training/NASA archives/protected members remain excluded. 33 local-only historical payloads are hash-bound. Novelty, lawful redistribution and complete clean replay remain unresolved.

[Final receipt](docs/protocol_lock/LOCK_RECEIPT.json) · [verification report](docs/protocol_lock/LOCK_VERIFICATION_REPORT.md) · [protected access policy](docs/protocol_lock/PROTECTED_EVALUATION_ACCESS_POLICY.md).
''')
md('GITHUB_REVIEW.md',f'''# RP-001 — Web Review

Repository PUBLIC. Status terbaru: **PROTOCOL_LOCKED — {V}, Stage A saja**.

Baca [completion report](docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md), [locked contract](docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md), [verification](docs/protocol_lock/LOCK_VERIFICATION_REPORT.md), dan [receipt](docs/protocol_lock/LOCK_RECEIPT.json).

G3-AM-001 sudah disetujui owner. Perubahan hanya klarifikasi prosedur quantile yang cocok dengan kode tersimpan; tidak ada perubahan implementasi/model/prior/posterior/CQR/estimand/threshold. Kontrak v0.5 asli serta [laporan G3 gagal](docs/protocol_lock/history/G3_lock_attempt_1/HISTORY_CONTEXT.md) dipertahankan utuh.

B official sensors, C freeze acceptance, D labels/scoring masih memerlukan izin terpisah. Tidak ada test access atau eksperimen baru. Public GitHub tidak menggantikan izin dataset redistribution/publication; raw data/protected members tetap tidak dipublikasikan.
''')
# Append governance record; prior exact full decision log has its archive.
old_bytes=(R/'research/decision_log.md').read_bytes()
(R/'research/decision_log.md').write_bytes(old_bytes+f'\n\n## {now} | Formal G3 lock completed after approved G3-AM-001\n\nHuman Raihan explicitly approved the existing precision-helper clarification at reviewed1fc660b. Single clause corrected; all original scientific bytes unchanged. Direct SOL source/model/prior/CQR/score/numerical/finite/protected consistency PASS. Original contract/failed G3 archive retained; exact diff and identities recorded. PROTOCOL_LOCKED; no scientific experiments or official access; B/C/D false. Receipt binds post-verification payload commit. Historical adverse findings and publication/replay limits retained.\n'.encode())
# Resolve only administrative artifact references, matching their existing immutable hash to a byte archive.
raw=(R/'research/artifact_map.csv').read_bytes();lines=raw.splitlines(keepends=True);corrections=[]
for i,line in enumerate(lines[1:],1):
 row=next(csv.reader([line.decode('utf8')]));p=row[2];digest=row[-1]
 if not (R/p).is_file() or sha(p)!=digest:
  candidates=[]
  if p in P:candidates.append(P[p]['archive'])
  for prefix in ('research/v0.5/baseline_current_aliases/','research/v0.4/baseline_current_aliases/','research/protocol_lock/baseline_current_aliases/','research/protocol_lock/final_G3/baseline_current_aliases/'):candidates.append(prefix+p)
  matching=next((q for q in candidates if (R/q).is_file() and sha(q)==digest),None)
  if matching is None:raise ValueError(('Unresolvable historical artifact reference',row[0],p,digest))
  row[2]=matching;buf=io.StringIO(newline='');csv.writer(buf).writerow(row);lines[i]=buf.getvalue().encode()
  corrections.append({'artifact_id':row[0],'original_reference':p,'archived_reference':matching,'unchanged_artifact_sha256':digest})
write('logs/protocol_lock/final_G3/administrative_reference_reconciliation.json',{'scope':'Administrative path references only; historical content/digests unchanged; original CSV byte archived','corrections':corrections,'original_CSV_archive':P['research/artifact_map.csv']})
entries=[('G3-LOCK-REPORT','docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md'),('G3-LOCK-VERIFY','docs/protocol_lock/LOCK_VERIFICATION_REPORT.md'),('G3-AM-DECISION','docs/protocol_lock/OWNER_AMENDMENT_DECISION_G3_AM_001.md'),('G3-LOCK-CONTRACT','docs/protocol_lock/LOCKED_ANALYSIS_CONTRACT.md'),('G3-LOCK-PROTOCOL','docs/protocol_lock/LOCKED_RESEARCH_PROTOCOL.md'),('G3-LOCK-CHANGE','docs/protocol_lock/AMENDMENT_CHANGE_RECORD.json'),('G3-LOCK-SOURCE','docs/protocol_lock/FROZEN_CODE_AND_ENVIRONMENT_MANIFEST.json'),('G3-LOCK-DATA','docs/protocol_lock/FROZEN_DATA_AND_SPLIT_MANIFEST.json'),('G3-LOCK-MODEL','docs/protocol_lock/FROZEN_MODEL_AND_CONFIGURATION_MANIFEST.json')]
buf=io.StringIO(newline='');writer=csv.writer(buf)
for eid,p in entries:writer.writerow([eid,'formal-lock-governance',p,'','RP001-G3-AM001-owner-approved-lock-only',sha(p)])
(R/'research/artifact_map.csv').write_bytes(b''.join(lines)+buf.getvalue().encode())
risk={'risk_id':'EXECUTION-PUBLICATION-LIMITS','statement':'Future endpoints/driver/integrity/numerical success untested; restricted finite claims and replay/data-rights limits remain.','severity':'high','likelihood':'Known limitations/future performance unknown','affected_claims_or_gates':['OFFICIAL_EVALUATION','PUBLICATION'],'owner':'Research Owners Raihan x Rei; SOL enforces scientific policy','disposition':'Retain restricted claims; future stages require separate authorization and guards; novelty/rights/replay before publication','trigger':'Any proposed Stage B/C/D or publication'}
evidence=[{'evidence_id':eid,'kind':'formal-lock-verification','location':p,'sha256':sha(p),'collected_at':now,'method':'Direct SOL source consistency, exact approved diff, actual identity checks','supports':'Authorized formal lock, no scientific result validation','provenance_chain':'Human G3 directive -> c583 -> failed G3 1fc -> human G3-AM001 approval -> unchanged pinned source -> exact corrected contract -> verified lock'} for eid,p in entries]
handoff={'schema_version':'1.0.0','handoff_id':'RP001-G3-FINAL-LOCK-AM1','parent_work_id':'RP-001','producer':'scientific-research-engine','consumer':'scientific-research-engine','producer_role':'Rei / SOL direct final mathematical verifier','consumer_role':'Research Owners','human_recipient':'Raihan x Rei','artifact_type':'formal-protocol-lock-completion','artifact_version':V,'artifact_identity':{'path_or_uri':'docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md','sha256_or_version':sha('docs/protocol_lock/G3_FORMAL_PROTOCOL_LOCK_COMPLETION_REPORT.md'),'created_at':now,'source_revision':BASE+'; approved amendment review '+REVIEW},'scope':'G3 formal lock only; no new science or protected access','applicability':'APPLICABLE_MANDATORY','claims_or_requirements':'Complete immutable approved lock and halt at separately authorized B gate','evidence':evidence,'gate_results':[{'gate':'G3_SOURCE_AND_APPROVED_CONTRACT','state':'PASS','owner':'Rei / SOL direct verifier','artifact_version':V,'evidence_ids':['G3-LOCK-VERIFY','G3-AM-DECISION','G3-LOCK-CHANGE'],'rationale':'Approved one-clause correction, all scientific source unchanged, direct component consistency PASS.'},{'gate':'OWNER_FORMAL_PROTOCOL_LOCK','state':'PASS','owner':'Raihan x Rei Research Owners','artifact_version':V,'evidence_ids':['G3-AM-DECISION','G3-LOCK-REPORT'],'rationale':'G3 directive and explicit approved amendment permit formal lock only.'},{'gate':'PROTECTED_EVALUATION','state':'BLOCKED','owner':'Research Owners','artifact_version':V,'evidence_ids':['G3-LOCK-REPORT'],'rationale':'B/C/D each require separate future authorization.'}],'assumptions':['Original qualified scientific evidence remains unchanged.','Future endpoint success/official count and driver readiness are not certified by protocol lock.'],'risks':[risk],'unresolved':['Future separately authorized endpoint integrity/numerical completion','Novelty, lawful dataset redistribution and complete clean replay'],'requested_decision':'Review completed receipt/package; any Stage B decision is separate. No additional authorization requested to complete G3.','return_to_parent':{'state':'COMPLETE','decision_owner':'Research Owners Raihan x Rei','reason':'Formal G3 completion only; halt before B/C/D.'}}
write('docs/protocol_lock/research_lead_handoff.json',handoff)
print(json.dumps({'current_state':'PROTOCOL_LOCKED','direct_material_components_verified':len(review['components']),'administrative_reference_corrections':len(corrections),'successful_lock_documents':True,'new_scientific_runs':0},indent=2))
