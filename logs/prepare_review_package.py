"""Prepare RP-001 review ledgers. No model fitting, no test data access."""
from pathlib import Path
import json, csv, hashlib, datetime
ROOT=Path(__file__).resolve().parents[1]
def read(rel): return json.loads((ROOT/rel).read_text(encoding="utf8"))
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
def write(rel,obj,replace=False):
    target=ROOT/rel
    if target.exists() and not replace: raise FileExistsError(target)
    target.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
def csvwrite(rel,fields,rows):
    target=ROOT/rel
    if target.exists():
        existing=list(csv.DictReader(target.open(encoding="utf8",newline="")))
        if existing: raise FileExistsError(f"nonempty existing ledger {target}")
    with target.open("w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
profile=read("data/raw/training_audit.json")
precision=read("logs/sample_precision.json")
g0=read("docs/g0_handoff.json")
records=read("literature/evidence_records.json")["records"]
provenance={
 "dataset_id":"NASA-C-MAPSS-FD001","family":"original C-MAPSS, not N-CMAPSS/PHM08 challenge",
 "retrieved_at":now,"retrieval_date_local":"2026-10-08 Asia/Jakarta",
 "source_page":"https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/",
 "download_url":"https://phm-datasets.s3.amazonaws.com/NASA/6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip",
 "catalog":"https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data",
 "lineage":"official repository link -> original outer ZIP -> CMAPSSData.zip -> allowed training/readme extraction -> training-only profile",
 "files":[{"path":p,"sha256":sha(p),"size_bytes":(ROOT/p).stat().st_size}
          for p in ["data/raw/NASA_CMAPSS_original.zip","data/raw/CMAPSSData.zip","data/raw/train_FD001.txt","data/raw/readme.txt"]],
 "extracted_entries":["train_FD001.txt","readme.txt"],
 "never_opened_entries":["test_FD001.txt","RUL_FD001.txt","FD002/FD003/FD004 payloads","Damage Propagation Modeling.pdf"],
 "test_label_bytes_exist_in_zip":True,"test_labels_extracted_or_read":False,
 "license":"NASA catalog: License not specified; no blanket redistribution permission inferred",
 "terms_source":"NASA repository acknowledgment/use-at-own-risk notice",
 "release_rights_status":"DEFERRED before public redistribution/publication release",
 "source_version":"content hashes, no unique archive release version supplied",
 "raw_mutation_policy":"immutable; preserve downloaded bytes",
 "audit_scope":"training structure/aggregate lifetime only; no calibration scores or models",
 "calibration_exposure_note":"Full training file profiled before partition; aggregate lifetimes/eligibility observed. Does not establish strict calibration-label blindness; no calibration residual or supervised tuning used.",
 "limitations":["full train-test duplication/schema audit deferred","physical sensor unit metadata not independently verified","official cutoff mechanism unavailable"]}
write("data/raw/provenance.json",provenance)
schema={"schema_version":"0.2","dataset":"FD001_train","mode":"time-series","field_count":26,
 "fields":[{"name":"engine_id","type":"integer","unit":"identifier","nullable":False,"namespace":"FD001_train"},
           {"name":"cycle","type":"integer","unit":"operating cycle","nullable":False,"range":"positive consecutive integer"}]+
          [{"name":f"setting_{j}","type":"float","unit":"not independently verified","nullable":False} for j in range(1,4)]+
          [{"name":f"sensor_{j}","type":"float","unit":"not independently verified","nullable":False} for j in range(1,22)],
 "key":["engine_id","cycle"],"outcome":"uncapped terminal_cycle-cutoff; prediction only while cutoff<terminal_cycle",
 "checks":{"finite_numeric":True,"unique_keys":True,"ordered_complete_cycles":True},
 "no_cleaning_or_remediation":True}
write("data/raw/schema_contract.json",schema)
protocol=read("research/protocol.json")
assert protocol["status"]=="DISCOVERY" and not protocol["research_question"]
protocol.update({
 "schema_version":"0.2","status":"PROTOCOL_DRAFTED","artifact_version":"0.2","owner":"Raihan",
 "research_question":"Is a compact hierarchical Bayesian predictor competitive in 90% interval score with calibrated CQR at the official FD001 unseen-engine endpoint, with engine-level uncertainty and audited dependence?",
 "background_gap":"Narrative evidence map; Bayesian and conformal RUL already exist. Novelty unresolved; rigorous conditional-pipeline comparative evaluation proposed.",
 "unit_of_analysis":"independent engine for primary outcome; sensor cycles nested within engine",
 "target_context":"simulated FD001 official-cutoff benchmark; broader generator/cutoff transport assumption qualified",
 "confirmatory_or_exploratory":"One proposed directional confirmatory comparison after final lock; all remaining analyses exploratory",
 "hypotheses":["H0: D>=0; H1: D<0, Bayesian minus CQR mean90% interval score conditional frozen pipeline"],
 "primary_claims":["Bayesian lower interval score is unresolved; no empirical model result exists"],
 "primary_outcomes":["Mean90% interval score in cycles, uncapped RUL, one endpoint per engine"],
 "secondary_outcomes":["PICP/Wilson95 interval","width","MAE/RMSE/bias for median forecasts","lower/upper miss penalties","prior/dependence/stage diagnostics"],
 "baselines":["Gaussian log-RUL reference","primary CQR","optional matched Gaussian plugin"],
 "data_plan":"Official NASA original archive; only train_FD001/readme extracted; complete integrity before evaluation; data/raw/provenance.json",
 "split_policy":"55/15/30 reserved; seedRP001-20261008-v0.2; one outcome-blind hash cutoff30..250; eligible43/13/25; refit56,calibrate25; configs/proposed_split_manifest.json",
 "test_access_policy":"No test labels before owner StageB lock/readiness and all prediction hashes. No model/preprocessing selection using test covariates. Only predefined per-engine sensor inference at prediction.",
 "model_selection_policy":"Fixed Bayesian candidate; CQR12 fixed configurations selected by uncalibrated mean interval score on13 tuning engines; refit56; calibration25 reserved.",
 "hyperparameter_policy":"Fixed priors; exploratory sensitivities not winner search. CQR8 boosting +4 linear endpoint configurations; final selected tau.50 fit only.",
 "analysis_plan":"docs/04_statistical_analysis_plan.md; paired mean score difference, bootstrap-t20,000 engine resamples, one-sided upper95% bound; descriptive finite benchmark and qualified population inference",
 "uncertainty_plan":"Conditional pipeline paired engine uncertainty; no training/selection/calibration variability included; diagnostics/design simulation before lock",
 "multiple_comparisons_plan":"One primary comparison; secondary findings exploratory; no post-hoc winner substitution",
 "ablation_plan":"rho0, Bayesian calibration, restricted representation sensitivity; exploratory",
 "robustness_plan":"Prior half/double, contamination-normal residual alternative, stage diagnostics; FD003 deferred",
 "stopping_rule":"Fixed planned runs; at most2 computational repairs; any method change before lock recorded; no post-test redesign retains confirmatory status.",
 "compute_budget":"Proposed32 aggregate CPU-hours/10GiB artifacts; local isolated CPU first, user-reported ColabPro option; estimates unmeasured",
 "ethics_and_risk":"Synthetic research only, no real-engine safety/maintenance deployment; raw redistribution terms review before release; risks docs/08",
 "preregistration":{"required":True,"location":"configs/protocol_lock_record.json after final owner approval","registered_at":None},
 "protocol_locked_at":"","owner_stage_a_approved":False,"owner_stage_b_approved":False,
 "new_engine_conditioning":"Full joint sensor-only theta update candidate; precise implementation/MC acceptance pending pilot; modular approximation only if explicitly revised before lock",
 "deviations":[{"date":"2026-10-08","phase":"pre-lock review","disclosed":True,
                "change":"Scope narrowed to comparative evidence; joint sensor landmark candidate specified; median/short-history/hash wording corrected after independent audit",
                "held_out_labels_visible":False}]
})
write("research/protocol.json",protocol,replace=True)
write("configs/proposed_protocol_v0.2.json",protocol)
write("configs/protocol_lock_record.json",{
 "artifact_version":"0.2","status":"PROPOSED_NOT_LOCKED","owner":"Raihan",
 "stage_a_approved":False,"stage_b_approved":False,"locked_at":None,
 "proposed_protocol_sha256":sha("configs/proposed_protocol_v0.2.json"),
 "proposed_split_sha256":sha("configs/proposed_split_manifest.json"),
 "primary_model_and_prediction":"docs/03_candidate_mathematical_model.md",
 "primary_analysis":"docs/04_statistical_analysis_plan.md",
 "approval_source":"None; user proposal requires approval before confirmatory experiment",
 "next":"Review package -> ownerStageA -> development validation -> final ownerStageB"})
environment=read("research/environment_manifest.json")
assert not environment["runtime"]
environment.update({"runtime":"Preflight only: bundled CPython3.12.14; global3.11.9 inventoried separately",
 "git_commit":"not yet committed at manifest preparation","git_dirty":True,
 "dependency_lock":"not created; research environment unvalidated",
 "container_image_or_digest":"not used",
 "hardware":g0["evidence"]["environment"],
 "preflight_python":read("logs/python_capabilities.json"),
 "colab_pro":{"available":True,"source":"user message during this review","account_inspected":False,"runtime_started":False},
 "notes":"No model fit/package installation. pyproject is provisional unpinned manifest. Authorizes no computation beyond current preflight.",
 "research_environment_approved":False})
write("research/environment_manifest.json",environment,replace=True)
data_manifest={"schema_version":"0.2","datasets":[{"id":"FD001_train","provenance":"data/raw/provenance.json",
 "sha256":profile["raw_sha256"],"engines":100,"rows":20631,"structure_status":"training audited",
 "full_integrity_status":"DEFERRED","official_test_labels_read":False,"split":"configs/proposed_split_manifest.json"}]}
write("research/data_manifest.json",data_manifest,replace=True)
gates=[
 {"gate":"G0_WORKSPACE","state":"PASS","owner":"Rei research lead","artifact_version":"0.2","evidence_ids":["E-G0"],"rationale":"Required structure and byte-identical source verified"},
 {"gate":"G1_NARRATIVE_EVIDENCE_MAP","state":"PASS","owner":"literature-evidence-engine","artifact_version":"0.2","evidence_ids":["S03","S05","S06","S07","S09"],"rationale":"Scoped design review, no systematic completeness or novelty certification"},
 {"gate":"EVIDENCE_VALIDATED","state":"DEFERRED","owner":"literature-evidence-engine","artifact_version":"0.2","evidence_ids":["S12","S13"],"rationale":"Current full-method/status/novelty review not complete; narrow methods claims supported"},
 {"gate":"DATA_VALIDATED","state":"DEFERRED","owner":"data-quality-engine","artifact_version":"0.2","evidence_ids":["E-TRAIN"],"rationale":"Training audit only; whole benchmark/rights release not validated"},
 {"gate":"G2_ESTIMAND_DRAFT","state":"PASS","owner":"rei-quant-research","artifact_version":"0.2","evidence_ids":["E-PRECISION","E-METHOD-AUDIT"],"rationale":"Independent units, population assumptions and endpoint explicit"},
 {"gate":"PROTOCOL_LOCK","state":"BLOCKED","owner":"Raihan","artifact_version":"0.2","evidence_ids":["E-PROPOSAL"],"rationale":"No owner approval; implementation/pilot numerical acceptance unresolved"},
 {"gate":"EXPERIMENT_VALIDATED","state":"DEFERRED","owner":"scientific-research-engine","artifact_version":"0.2","evidence_ids":[],"rationale":"No experiment run; specialists activated when scope enters experiment"},
 {"gate":"SCIENTIFIC_VALIDATED","state":"DEFERRED","owner":"scientific-research-engine","artifact_version":"0.2","evidence_ids":[],"rationale":"No empirical model comparison evidence"}]
write("research/gate_results.json",{"status":"PROTOCOL_DRAFTED","gates":gates})
write("research/workflow_route.json",{"workflow":"scientific-research","risk_tier":"research-grade",
 "governor":"rei-research-engineering-suite","parent":"scientific-research-engine",
 "specialists":[{"name":"literature-evidence-engine","reason":"prior evidence and novelty review"},
               {"name":"data-quality-engine","reason":"training-only audit of real dataset"},
               {"name":"rei-quant-research","reason":"hierarchy, predictive estimand, precision and paired inference"}],
 "conditional_skills_deferred":[{"name":"ml-experiment-engine","reason":"no fitting/experiment in current scope"},
                               {"name":"ai-evaluation-engine","reason":"full evaluation implementation not yet authorized"},
                               {"name":"latex-academic-publishing","reason":"no empirical paper/submission artifact yet"}],
 "delegation":[{"task":"g0_workspace","model":"GPT-6 LUNA","reasoning":"Max","authorization":"user proposal section19"},
               {"task":"methodology_audit","model":"inherited lead model","authorization":"suite topological delegation and independent quantitative review"}]})
lit_rows=[{"evidence_id":x["id"],"title":x["title"],"year":x.get("year",""),"venue":x["source_type"],
           "doi":x.get("doi",""),"url":x["url"],"source_type":x["source_type"],
           "verified":"yes" if x["support"]!="metadata-only" else "metadata-only",
           "stance":x["stance"],"relevance":x["finding"],"notes":x["support"]+"; "+x["limitations"]} for x in records]
csvwrite("research/literature_ledger.csv",["evidence_id","title","year","venue","doi","url","source_type","verified","stance","relevance","notes"],lit_rows)
claims=[
 {"claim_id":"C01","claim":"FD001 official training contains100 engines and20631 complete rows","claim_type":"descriptive","scope":"downloaded training hash only","evidence_ids":"E-TRAIN","status":"supported","caveats":"No test schema audit"},
 {"claim_id":"C02","claim":"Bayesian has lower90% interval score than CQR","claim_type":"comparative","scope":"future locked FD001 endpoint comparison","evidence_ids":"","status":"unresolved","caveats":"No models/evaluation"},
 {"claim_id":"C03","claim":"Exact conformal90% guarantee holds at official cutoff mechanism","claim_type":"theoretical","scope":"official FD001 test","evidence_ids":"S05;S07;S08","status":"not-supported","caveats":"Exchangeability/selection mechanism not established"},
 {"claim_id":"C04","claim":"RP001 research combination is publication-novel","claim_type":"evidence-gap","scope":"current literature","evidence_ids":"S03;S04;S10;S11;S12;S13","status":"unresolved","caveats":"Narrative search, missing full methods and recent identity discrepancies"},
 {"claim_id":"C05","claim":"100 engines establish tight±2pp90% calibration","claim_type":"comparative","scope":"future coverage estimation","evidence_ids":"E-PRECISION","status":"not-supported","caveats":"Observed90/100 hypothetical Wilson95 interval82.56..94.48%"},
 {"claim_id":"C06","claim":"Synthetic FD001 evidence generalizes to real-engine operational safety","claim_type":"generalization","scope":"real fleet","evidence_ids":"S01;S02","status":"not-supported","caveats":"Synthetic-to-real gap"},
 {"claim_id":"C07","claim":"Proposed landmark model is algebraically coherent for sampled alive cohort","claim_type":"methodological","scope":"specified equations only","evidence_ids":"E-METHOD-AUDIT","status":"qualified","caveats":"No identification/recovery/computation validation; not a generative survival model"}]
csvwrite("research/claim_ledger.csv",["claim_id","claim","claim_type","scope","evidence_ids","status","caveats"],claims)
write("literature/claim_evidence_map.json",{"claim_links":[
 {"claim":"Bayesian/conformal RUL already have prior art","evidence":["S03","S04","S10","S11"],"relation":"supports","support_basis":"as source ledger"},
 {"claim":"Novelty of engine-disjoint reliability audit unresolved","evidence":["S12","S13"],"relation":"boundary-condition","support_basis":"publisher abstract with identity discrepancy; metadata-only candidate"},
 {"claim":"Conformal guarantees require assumptions","evidence":["S05","S07","S08"],"relation":"boundary-condition","support_basis":"author full text"},
 {"claim":"Interval score is appropriate interval endpoint","evidence":["S06"],"relation":"supports","support_basis":"section6.2"},
 {"claim":"Diagnostics necessary but insufficient for scientific truth","evidence":["S09"],"relation":"supports","support_basis":"author full text"}],
 "quality_appraisal":"Domains assessed in evidence records/docs01; unavailable methods explicitly not assessed, no numeric score",
 "evidence_independence":"All C-MAPSS papers reuse same benchmark; preprint/journal S03 linked as one study"})
audit_expected={
 "02_dataset_feasibility_sample_precision.md":"5009DD6C04512D15F117904BB18E3795232715D974751A0E4DA22350BA130A86",
 "03_candidate_mathematical_model.md":"CA2F407AB13709ADE2F3C8625E42754C8F8EF12B748BF545C391629CAC5491ED",
 "04_statistical_analysis_plan.md":"C1AE4E4920B153D2781CA0E76F91E53DFA6D2F0CAC160069D919CBE05A078DB8",
 "05_fair_comparator_design.md":"CD52AB07FC44088368EDAD6D4054BA3790787413C022BFF9C1AFE2E09563B143",
 "06_proposed_protocol_lock.md":"83B79DE560054C59FE7AEEFA378E2AFDF143C2E7B2CE6B24331EA8E984BFCD14"}
audit_items=[]
for name,expected in audit_expected.items():
    path="logs/methodology_audit_inputs/"+name
    actual=sha(path)
    assert actual.upper()==expected
    audit_items.append({"path":path,"sha256":actual})
write("logs/methodology_audit_inputs.json",{"version":"0.2-before-lead-fixes","documents":audit_items})
decision_path=ROOT/"research/decision_log.md"
assert "Workspace initialized" in decision_path.read_text(encoding="utf8")
decision_path.write_text("# Decision Log\n\n- 2026-10-08: G0 delegated per source proposal; source copy and root verified.\n"
 "- 2026-10-08: NASA original archive acquired; only FD001 training/readme opened; full training aggregate structure audited before proposed split; no test labels.\n"
 "- 2026-10-08: Outcome-blind cutoff/split proposed once; surviving roles43/13/25; no favorable split search.\n"
 "- 2026-10-08: Narrative prior art reviewed; novelty remains unresolved; inferential claims narrowed.\n"
 "- 2026-10-08: Candidate joint sensor/landmark model and conditional-pipeline SAP drafted. No model fitting.\n"
 "- 2026-10-08: User reports ColabPro; added as optional untested compute resource.\n"
 "- 2026-10-08: Independent methods audit completed; median, short-history, hash wording repaired; numerical pilot gates remain deferred.\n"
 "- 2026-10-08: Package offered for owner StageA review; approval absent. Source proposal section18 governs final confirmatory authorization.\n",encoding="utf8")
required=["docs","literature","data/raw","data/interim","data/processed","src","notebooks","configs","experiments","results","figures","tests","manuscript","logs"]
assert all((ROOT/p).is_dir() for p in required)
assert sha("docs/proposal_v0.1.md").upper()==g0["evidence"]["source"]["sha256"]
evidence=[{"evidence_id":eid,"kind":kind,"location":loc,"collected_at":"2026-10-08","method":method,"supports":supports,
           "provenance_chain":chain} for eid,kind,loc,method,supports,chain in [
 ("E-PROPOSAL","user-instruction","docs/proposal_v0.1.md","byte-identical source copy","scope and approval policy","attachment->source copy"),
 ("E-G0","filesystem","docs/g0_handoff.json","lead directory/source check","initialization","delegation->lead verification"),
 ("E-TRAIN","computed-data-audit","data/raw/training_audit.json","stdlib training-only executable audit","training structure","NASA->archive->training->profile"),
 ("E-PRECISION","computed-planning","logs/sample_precision.json","analytic calculations retained in executable","sample precision","stated assumptions->code->numbers"),
 ("E-METHOD-AUDIT","independent-review","docs/09_methodology_audit.md","independent algebra/specification audit","draft repairs","input snapshots->audit->lead dispositions")]]
risks=[{"risk_id":rid,"statement":statement,"severity":severity,"likelihood":"not quantified from available evidence",
        "affected_claims_or_gates":gate,"owner":owner,"disposition":disposition,"trigger":trigger}
       for rid,statement,severity,gate,owner,disposition,trigger in [
 ("R01","Official cutoff transport/exchangeability not established","critical","C03; protocol scope","lead","qualified empirical benchmark only","formal guarantee proposed"),
 ("R02","Candidate identifiability and posterior reliability untested","critical","model acceptance","lead","pilot gate pending","poor recovery or diagnostics"),
 ("R09","Novelty and recent full-method status unresolved","high","C04; publication","literature lead","further review before novelty claim","publication"),
 ("R12","Environment/Colab runtime unvalidated","medium","experiment readiness","lead","StageA pilot pending","implementation"),
 ("R13","Synthetic evidence not real-engine safety evidence","high","C06","owner+lead","permanent scope limitation","deployment claim")]]
handoff={"schema_version":"1.0.0","handoff_id":"RP001-LEAD-REVIEW-20261008","parent_work_id":"RP-001",
 "producer":"Rei research lead","consumer":"Raihan research owner","artifact_type":"preimplementation-review-package",
 "artifact_version":"0.2","artifact_identity":{"path_or_uri":"docs/00_research_lead_review.md","sha256_or_version":sha("docs/00_research_lead_review.md"),
     "created_at":now,"source_revision":"source proposal v0.1 hash"+sha("docs/proposal_v0.1.md")},
 "scope":"G0 and eight preimplementation deliverables; no confirmatory experiment",
 "applicability":"APPLICABLE_MANDATORY","claims_or_requirements":"Proposal sections18/19 fulfilled at review-draft stage",
 "evidence":evidence,"gate_results":gates,
 "assumptions":["Owner approval absent","No test labels read","Hash cutoff outcome-blind, not proved stochastic independence"],
 "risks":risks,"unresolved":["StageA approval","candidate recovery/diagnostics","exact predictive update algorithm","complete data integrity","novelty before publication"],
 "requested_decision":"Review and approve development-only StageA with scope/compute/practical-scale choices; final StageB separately after readiness",
 "return_to_parent":"COMPLETE"}
write("docs/research_lead_handoff.json",handoff)
# Read and inspect the scaffold before replacing it.
readme=ROOT/"README.md"
current=readme.read_text(encoding="utf8")
assert "G0 workspace scaffold" in current and "no runnable model or experiment" in current
readme.write_text("""# RP-001 — Bayesian RUL Reliability

Status: PROTOCOL_DRAFTED / REVISE BEFORE LOCK, 8 October2026. No model fitted and no confirmatory experiment run.

Start with [Research Lead Review](docs/00_research_lead_review.md).

## Review package

1. [Literature gap and novelty](docs/01_literature_gap_novelty_review.md)
2. [Dataset feasibility and precision](docs/02_dataset_feasibility_sample_precision.md)
3. [Candidate mathematical model](docs/03_candidate_mathematical_model.md)
4. [Statistical analysis plan](docs/04_statistical_analysis_plan.md)
5. [Fair comparators](docs/05_fair_comparator_design.md)
6. [Proposed protocol lock](docs/06_proposed_protocol_lock.md)
7. [Local/Colab compute feasibility](docs/07_compute_feasibility_estimate.md)
8. [Risks, assumptions and decisions](docs/08_risks_assumptions_decisions.md)

Source proposal is preserved byte-identically at docs/proposal_v0.1.md. Independent methodology audit and repairs are documented in docs/09_methodology_audit.md.

## Dataset and outcome protection

Official NASA C-MAPSS archive is stored under data/raw and ignored by Git. Only train_FD001.txt and readme.txt were extracted/opened. Test sensor and RUL label entries remain unextracted; label bytes are present in the archive, so this is an access policy, not cryptographic custody. Data provenance, SHA256, schema and training audit are versioned JSON metadata. No cap is applied to RUL.

Training audit:100 engines,20631 rows. Proposed engine split55/15/30 with outcome-blind cutoff30..250 gives43/13/25 eligible engines; final fit+tune cohort56. Fixed hashing does not prove independence or official-cutoff exchangeability.

## Environment and execution

Python>=3.11 per provisional pyproject.toml. The bundled preflight used CPython3.12.14; research dependencies are unpinned and not installed/validated. Use an isolated project environment after development approval. Raihan has ColabPro as optional compute; no Colab account accessed or runtime started.

The retained preflight calculation is python src/rp001_preflight.py. It expects training bytes in data/raw and refuses to overwrite audit outputs. For reproduction, use a fresh versioned output checkout or adapt output version explicitly; never overwrite raw bytes. Numerical checks are in tests/verify_protocol_mathematics.py. There is no training/evaluation command until implementation and final protocol are approved.

## Governance and reproducibility

research/ contains protocol, evidence/claim/artifact ledgers, data/environment manifests, empty experiment registry, decisions and gate results. configs/ contains a proposed split and unapproved lock record. Logs preserve quantitative planning, capabilities, audit inputs and delivery verification.

Approval sequence: owner StageA development-only -> synthetic/training-only validation and pinned code/environment -> owner StageB final lock -> forecast all official endpoints and hash predictions -> access labels for locked scoring. Current permissions do not bypass proposal section18.

Use repository-relative paths in code. Git is local; no remote/publication configured. Data, secrets, caches and large posterior stores are ignored; provenance/config/source/review files remain tracked. All work artifacts stay in this project directory.
""",encoding="utf8")
print(json.dumps({"status":"PROTOCOL_DRAFTED","review_deliverables":8,"g0_verified":True,"source_hash_verified":True,
 "records":len(records),"claims":len(claims),"gate_states":{x["gate"]:x["state"] for x in gates},"test_labels_read":False},indent=2))
