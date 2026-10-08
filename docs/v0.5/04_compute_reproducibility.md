# Compute, provenance, custody, and outstanding requirements v0.5

Exactly one new synthetic MCMC invocation, on the exact saved failed-case training data; no additional simulation, test data, fallback, or model search. The fixed saved-draw score demonstration performs no sampling. Local CPU default was sufficient; Google Colab Pro/GPU unused, no additional spending.

| Component | Wall seconds | Process CPU seconds |
|---|---:|---:|
| Single high-rho inquiry | 73.500382 | 90.125000 |
| Saved-draw score propagation | 10.158535 | 9.453125 |

Registered timed new scientific work totals **99.578125 CPU seconds**. Timers start after imports; direct preflight, tests, source review, packaging/Git are excluded and no OS-wide total/energy measurement is claimed. Fit remains below600 wall seconds/oneCPU hour; new experiment payload is approximately5.382MiB, below128 MiB. Peak fit RSS:587923456bytes. Hardware i7-10750H,6physical/12logical cores,15.776GiB RAM; float64,BLAS/OMP/MKL/NumExpr threads1,sampler cores2. Warnings about unavailable g++ and loop fusion were recorded; backend was frozen nutpie/Numba.

## Exact identities

- Owner-reviewed scientific snapshot:61b4c2c63cbad6c1b9bd99168e33d1367aa180bc.
- Pre-execution plan/source and high-rho run:304d8e76d03fe7d69dc7f8f9bb6de3c600a219dd.
- Saved-draw demo source:60e9208fdd216abf51677f80514ac77e7e4fe9e6.
- Environment:f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c.
- Authorized train:963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8.
- Original split:6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b.
- v0.5plan:6046cd808d6a4b68ed42fd7d3458f0f142273aa323f64bb077cb8c0bc7dc0745.
- Exact reused synthetic data:3ed0b8984fa4feac1da2633f2db9609f59fe604321eb24e7e1c6067facc9d230.
- Direct preflight:1b1492dadc95d7036da868329070d745f274f51bff660bb28d577f839997cc4f.
- New posterior:fdd3cd80a4eba24b3f3d09b0132ed2fbd9b01b7c63b3726c481c166841e3444b.
- Final snapshot/manifest identities:[delivery receipt](../../logs/v0.5/delivery_receipt.json).

The64 package lock and environment remain unchanged. Per-run records bind every executed source hash, plan, commit, dataset, and no-test-access flag. Original high-rhoFAIL is preserved, not overwritten by the new run. No extra MCMC invocation or retry is permitted by its runner; a record already present prevents reexecution.

## Reproduction boundaries

Saved artifacts allow deterministic recomputation of the documented diagnostics and score-propagation check. For a fresh authorized scientific replay, use an isolated checkout at304d8e7, pinned CPython3.12.14/package lock, and exact historical failed-case data/required retained principal NCs. Set PYTHONPATH=src, float64, one BLAS thread, and forward-slash PyTensor cache directory. The entry points are python -m rp001.v05_highrho preflight then run; they require an empty v0.5 destination and refuse overwrite. The score-demo source is in60e9208; the historical source/provenance assertions intentionally require their own source snapshot. A new replay must record its own commit and identities rather than manufacture the original run receipt.

Complete historical replay still needs33Git-ignored local payload files bound in the v0.4manifest, including trusted comparator object/preprocessing stores; the private GitHub repository does not by itself supply every historical input. No one-command clean/new-platform replay or bit-identical cross-platform sampler claim is certified. Stage an authorized custodian bundle or document lawful fresh acquisition before a public reproducibility claim. Never extract protected official members while reproducing the training pilot.

The [baseline archive map](../../research/v0.5/baseline_alias_archive_map.json) preserves any advanced current metadata byte-for-byte. [QC](../../logs/v0.5/closure_qc.json) checks historical537file manifest custody via those aliases, unchanged old source/evidence, main registry prefix, all59 tests, one invocation, exact fingerprints, and protected draft state. Manifests bind bytes, not scientific assumptions.

## Unresolved rights and publication requirements

[NASA catalog](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data), checked2026-10-08, describes100FD001test trajectories and explicitly reports unspecified license. Only catalog metadata was browsed; no archive sensor/label resource was opened. Acquisition/provenance, permission to use, and permission to redistribute are distinct. Preserve raw-data exclusion and private review visibility; obtain appropriate rights review before public release of data or derived payload. This report does not supply legal clearance.

Novelty remains unverified; CQR/Bayesian RUL are established families. Complete targeted primary-source novelty/evidence review before publication claims. Current disclosure/source custody is sufficient for owner contract review, not certified public research reproducibility. Future official schema/overlap/numerical audits and distinct owner lock/sensor/label permissions remain outstanding execution requirements.
