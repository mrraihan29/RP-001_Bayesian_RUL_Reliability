# RP-001 v0.4 worker pipeline contract

Status: training-only data-builder and CQR helper contract. This document does not lock the research protocol or authorize any Bayesian sampling, prediction, test-data access, or confirmatory evaluation.

## Scope and entry points

The new module src/rp001/v04_pipeline.py adds two explicit operations:

- build_bootstrap_pipeline_data(engines, bootstrap_seed, cutoff_mode=..., cutoff_salt=..., split_manifest=..., input_source_sha256=...) builds one resampled pipeline's data and preprocessing state.
- reselect_refit_calibrate_cqr(bootstrap) applies the existing CQR grid and selection rule to that one prepared replicate.

The caller supplies a mapping of the 100 FD001 training engine arrays. The module does not load raw files or archives, alter data.py, fit the Bayesian model, predict RUL, write artifacts, or run a loop of replicates. With the default manifest it reads only the frozen training split manifest through data.manifest().

## Resampling and cutoffs

Each role is sampled with replacement from its own frozen roster and retains the assigned draw size: fit 55, tune 15, calibration 30. The same nonnegative bootstrap seed produces the same role draw IDs in canonical and alternate cutoff modes. A sampled engine receives one cutoff per replicate, so every repeated draw of that engine shares its cutoff, prefix, and log-R target.

Canonical mode reproduces the v0.3 manifest rule, 30 + SHA256(SEED|cutoff|engine) mod 221. Alternate mode uses 30 + SHA256(SEED|<cutoff_salt>|engine) mod 221; the salt should identify a named deterministic scenario such as cutoff-sensitivity-001. Hash inputs and digests are recorded by engine and stage.

Eligibility remains C < T. Ineligible draws stay in the IDs, multiplicities, cutoff, and eligibility metadata, then are omitted from stage datasets. No role or engine is redrawn. The minimums are checked on distinct eligible IDs: fit 20, tune 5, calibration 9. A failed replicate returns status="failed" and its full stage metadata without fitting downstream preprocessors.

## PCA and stage datasets

The selection PCA is fitted on eligible fit prefixes. The refit PCA is fitted again on eligible fit plus tune prefixes. Both use only sensor columns observed through each sampled cutoff. For unique engine i with bootstrap multiplicity m_i and prefix length C_i, each prefix row receives weight proportional to m_i / C_i; weights are normalized over the eligible cohort. Weighted scaling drops channels whose SD is at most 1e-8. PC1 orientation and fitting-variance scaling match v0.3.

A successful BootstrapPipelineData exposes:

- fit and tune: expanded eligible draws transformed by the fit-only selection PCA;
- refit_fit_tune: expanded eligible fit plus tune draws transformed by the refit PCA;
- calibration: expanded eligible calibration draws transformed by the refit PCA, with uncapped log(T-C) targets;
- selection_preprocessor and refit_preprocessor;
- anchor: the fixed 25 canonical eligible calibration sensor prefixes, transformed with the refit PCA and carrying y=None;
- anchor_features["summary"] and anchor_features["full_sequence"]: the existing CQR feature forms for those fixed anchor sensors.

Landmark rows retain the original engine ID. Repeated rows encode that engine's bootstrap multiplicity; they are not new independent engines. Metadata records the complete role draw sequence, unique IDs, multiplicities, cutoff and eligibility maps, hash inputs/digests, stage hashes, preprocessing hashes, and dataset hashes. The optional input source digest is recorded as supplied but is not verified by this module.

The fixed anchor is only for descriptive prediction-map sensitivity. Its labels are omitted, and the helper does not use anchor outcomes for prior or algorithm selection.

## CQR behavior

The CQR helper uses candidate_specs(), fit_candidate, predict_endpoints, mean90_interval_score, select_candidate, fit_median_candidate, and calibrate from the existing v0.3 implementation. It fits all 12 fixed configurations on the expanded fit rows, scores them on expanded tune rows, uses the existing 0.5-cycle tie band and deterministic simplicity rule, then refits the selected interval and median models on expanded fit+tune rows after PCA refitting. The linear candidates share one fit-only scaler during selection; the selected linear model receives a scaler fitted on the refit cohort.

Calibration outcomes enter after selection and refitting, only to compute the existing nonshrinking rank correction on the expanded bootstrap score sequence. The result stores both the distinct eligible calibration-engine count and the expanded score-row count, the rank, correction, and hashes. Repeated bootstrap scores do not receive a formal conformal exchangeability guarantee. Official cutoff transport and coverage remain unverified. Candidate failures are retained in the result; there are no replacement trials.

## Interpretation and limits

The planned eight empirical perturbations are four bootstrap multiplicity seeds paired across canonical and alternate cutoff variants. This helper does not orchestrate those eight calls. These conditional empirical perturbations vary cohort membership, cutoffs, PCA, CQR tuning/refitting, and calibration correction, but they do not estimate true total pipeline sampling uncertainty or independent loss/performance. They do not resolve the v0.3 Bayesian predictive-precision failure, prior plausibility, identifiability, calibration transport, or final owner authorization.

Unit tests use synthetic in-memory training-shaped arrays and mocked CQR estimators where needed. No test sensors, test labels, archive members, or calibration-based prior choices are part of this worker contract.