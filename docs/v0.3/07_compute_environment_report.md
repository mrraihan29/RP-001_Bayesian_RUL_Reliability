# RP-001 — Compute and Environment Report v0.3

**Local CPU pilot completed. Colab Pro was not used; no paid compute or additional expenditure was authorized or incurred by this task.**

## Runtime and reproduction

Isolated runtime: CPython 3.12.14, Windows-11-10.0.26220-SP0, float64, PyMC 5.28.5, PyTensor 2.38.3, nutpie 0.16.11, ArviZ 0.23.4, NumPy 2.4.6, SciPy 1.18.1, scikit-learn 1.9.1. System packages were not replaced. Full exact versions: `configs/requirements-pilot.lock`; resolver wheel URLs/hashes: `logs/pilot_install_report.json`. Import smoke and dependency consistency checks passed. NUTS used the validated Numba/Rust nutpie backend; no unrecorded fallback.

Software environment SHA-256, computed from canonical JSON of Python implementation/version, platform, all package versions, float dtype, sampler and BLAS threads:

`f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c`

Full metadata: `logs/pilot_environment.json`. The fingerprint identifies configuration; it does not guarantee bit-identical results across hardware/threading. The Windows lock is platform-specific. Colab would need a separately fingerprinted/validated environment.

Hardware: Intel i7-10750H, 6 physical/12 logical CPU cores, 15.776 GiB RAM. GTX1650Ti 4GiB present but unused. Four chains with two active cores, 1,000 warmup+2,000 retained draws per chain, one BLAS/OMP/MKL thread, maximum tree depth12, target_accept=.95. Per-run seeds/settings are preserved.

## Measured demand

| Run | Wall seconds | Process CPU seconds | Peak process RSS GiB |
| --- | --- | --- | --- |
| syn_r0 | 109.41 | 111.05 | 0.695 |
| syn_r0_repair1 | 19.21 | 24.92 | 0.372 |
| syn_r0_repair2 | 20.94 | 26.59 | 0.385 |
| syn_r05 | 40.15 | 48.48 | 0.467 |
| syn_r09 | 48.52 | 65.33 | 0.466 |
| syn_weak | 38.19 | 46.11 | 0.466 |
| base | 38.90 | 44.89 | 0.494 |
| prior_half | 39.43 | 45.61 | 0.497 |
| prior_double | 37.75 | 43.73 | 0.483 |
| rho_zero | 34.73 | 38.06 | 0.503 |
| contamination | 35.61 | 40.81 | 0.507 |
| refit | 32.20 | 37.70 | 0.470 |
| sensor_oracle | 42.79 | 49.72 | 0.558 |

Sum of logged sampler **process CPU time**, including two failed storage attempts: 623.015625 seconds (0.1731 CPU-hours). Sum of individual wall times: 537.853 seconds; this is not elapsed calendar time when runs overlap. Peak logged main-process RSS: 0.695 GiB, not total simultaneous system memory. Predictive integration used15.349 wall/15.078 CPU seconds; comparator selection/refit/calibration4.515 wall/4.422 CPU seconds. Statistical design simulation6.387 wall seconds; CPU unmeasured. Dependency installation, tests, worker audits and drafting are excluded from sampler totals and must not be represented as zero-cost work.

Demand is far below the proposed32 aggregate CPU-hour envelope. Each successful fit took less than49 wall seconds in its logged call. Local CPU remains appropriate for numerical refinement. Colab Pro is available by owner report but not needed by these measurements. Broader repeated-pipeline studies require a new measured estimate; no extra spending is authorized.

## Run and storage provenance

The run registry preserves all fits, CQR candidates and development analyses. Sampling records include data payload hash, config hash, seed, software hash, start code commit and dirty-worktree flag. Most runs honestly retain `code_dirty=true`; a commit alone does not prove an executed dirty source state. Final delivery hashes retained sources/evidence/data/posteriors. This is an auditable reproduction specification, not a claim every historical run started clean or the entire project was independently rerun.

Two metadata-serialization repairs support both DataTree and InferenceData; failed runs remain, with unchanged scientific target/seeds/sampler. Windows configuration parsing also created a local compilation-cache directory with backslashes removed from its name. It contains generated cache only and is excluded from Git/scientific manifests. Use a forward-slash absolute cache path in PYTENSOR_FLAGS for future runs. This path issue does not alter likelihood or authorize protected data.

Create a fresh isolated Python3.12.14 environment, install/check the exact lock, verify the training hash, set project `src` as PYTHONPATH, float64 and one BLAS thread. Execute retained mathematical/conditioning/comparator tests before named synthetic/training runs. Freeze CQR selection before calibration responses, then refit56, sensor oracle and predictive integration. Preserve prior failures; use new IDs and a prospective revised precision plan for additional work. Exact Windows commands: `experiments/REPRODUCE_DEVELOPMENT.md`.

## Data and Git identities

Training SHA-256: `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8`.

NASA original outer archive SHA-256: `c9c5dec12a945a82e8bb4446589d7fb3cc057b5e5d81fa1a12e25ee9912ad3b2`.

Source proposal SHA-256: `4ff06a6cf6f7a699dcbb9c66a76bfe6e21d60b64bc738c345e3b08c1f5118346`.

Split manifest SHA-256: `6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b`.

The archive contains unopened test members; only training/readme were extracted. The barrier is procedural, not cryptographic. Final code/evidence checkpoint, delivery-commit convention and manifest identities: `docs/v0.3/delivery_provenance.json` and `logs/v0.3_delivery_manifest.json`. Raw data, .nc/.npz/.joblib scientific payloads remain local ignored artifacts, hash-bound without publishing. Redistribution rights remain unresolved before release.
