# RP-001 — Bayesian RUL Reliability

Status: PROTOCOL_DRAFTED / REVISE BEFORE LOCK, 8 October 2026. No model fitted and no confirmatory experiment run.

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

Training audit: 100 engines, 20,631 rows. Proposed engine split 55/15/30 with outcome-blind cutoff 30–250 gives 43/13/25 eligible engines; final fit+tune cohort 56. Fixed hashing does not prove independence or official-cutoff exchangeability.

## Environment and execution

Python >=3.11 per provisional pyproject.toml. The bundled preflight used CPython 3.12.14; research dependencies are unpinned and not installed/validated. Use an isolated project environment after development approval. Raihan has Colab Pro as optional compute; no Colab account accessed or runtime started.

The retained preflight calculation is python src/rp001_preflight.py. It expects training bytes in data/raw and refuses to overwrite audit outputs. For reproduction, use a fresh versioned output checkout or adapt output version explicitly; never overwrite raw bytes. Numerical checks are in tests/verify_protocol_mathematics.py. There is no training/evaluation command until implementation and final protocol are approved.

## Governance and reproducibility

research/ contains protocol, evidence/claim/artifact ledgers, data/environment manifests, empty experiment registry, decisions and gate results. configs/ contains a proposed split and unapproved lock record. Logs preserve quantitative planning, capabilities, audit inputs and delivery verification.

Approval sequence: owner Stage A development-only -> synthetic/training-only validation and pinned code/environment -> owner Stage B final lock -> forecast all official endpoints and hash predictions -> access labels for locked scoring. Current permissions do not bypass proposal section 18.

Use repository-relative paths in code. Git is local; no remote/publication configured. Data, secrets, caches and large posterior stores are ignored; provenance/config/source/review files remain tracked. All work artifacts stay in this project directory.
