# Reproducibility, environment and compute report v0.4

Local CPU completed the bounded pilot. Registered scientific and infrastructure process CPU totals **2493.968750seconds (0.692769hours)**, below the6hour envelope. The current v0.4 scientific payload is 127.707MiB, below2GiB. There are33 completed MCMC fits (504,000 retained draws/132 chains);32 pass all physical/auxiliary diagnostics, while v04_syn_high_rho_3 fails Rhat. Zero divergences were observed. No fit reached the10minute limit. At most two scientific CPU processes ran concurrently. Colab/GPU were unused; no additional spending occurred.

## Measured components and limits

| Component | Process CPU seconds |
|---|---:|
|33 MCMC fits including their preprocessing/CQR work | 2395.421875 |
|Four failed canonical preparations, before any sampling | 2.812500 |
|Lead analysis including prior/PPC/synthetic/pipeline prediction checks | 69.062500 |
|600-replication correlated-chain validation |14.640625|
|4,000-dataset bootstrap OC |11.140625|
|Storage-only precision recovery |0.890625|

Fit wall times sum to1974.173215seconds; overlapping process times must not be mistaken for calendar duration. CPU timers start after interpreter/package imports and exclude packaging, Git, QA and source-review tool work. This is the registered scientific/repair total, not an OS-wide energy/cost measurement. Peak per-fit process RSS and each wall/CPU interval are retained in individual records. Scientific payload size is also finalized in the delivery manifest; caches and the Python environment are excluded from payload accounting. The hardware remains i7-10750H(6physical/12logical cores),15.776GiB RAM. Performance is specific to this environment.

## Immutable failures and two infrastructure repairs

Four canonical pipeline preparations rejected an inapplicable alternate cutoff-salt argument. No HPO, dataset artifact or sampler started in those attempts; all original failed records remain unchanged. One preparation-repair campaign corrected only the helper call and then ran the four originally planned fits with unchanged configs/seeds/draws, using _infra1 identities. Actual MCMC fit count remains33, not37. This is no scientific retry or outcome-selected seed.

The single precision-validation invocation completed all600 samples but failed writing its result into an absent directory. Its failed registry retained every raw record. Infrastructure-repair campaign2 archived that registry byte-for-byte and deterministically rebuilt18 summaries/serialized the same600 records. The original scientific run and runtime remain ba44bc1; storage recovery has its own f81da0f source snapshot and runtime. No RNG, resampling or validation-runner reinvocation occurred. Original/archive SHA ed6777b5ebff7f4204088da0ee5bfb6e98e841eff44f03a09f06fc86082357e9; canonical raw-record SHA5caee94be4986610d9f34195d38ac2b4c3cef4a317788719e30ae05e4e53172e. Both repairs remain within the prospectively allowed two infrastructure repairs. Earlier launch parsing was fixed before any experiment registration. A CQR endpoint-support fix was committed before any affected pipeline run.

Analysis-only review corrections were completed before analysis execution: matching prior SD denominators, fixed-rho information labeled not applicable, conjugate validation included in the overall numerical gate, degenerate MCSE comparisons fail closed, exact25/75 identities checked, manifest/oracle inputs bound, and partial analysis protected. These changed neither frozen seeds, MCMC configuration, model likelihood/prior, scientific targets nor thresholds. Structural-proof wording was corrected to acknowledge lag2 second differences share an endpoint.

## Exact fingerprints

- Environment: **f57b00a67e9d67b2920791bfddc8dc812dbdeb9306588a26557dfd6be15f826c**.
- Authorized train_FD001 bytes: **963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8**.
- Frozen split/cutoff manifest: **6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b**.
- Frozen v0.4 plan: **0c6a7e1e924636cec6196295eac19b29a6bd7faa85e18b081549f8287ab0b99b**.
- Prospective plan Git checkpoint: **1f01ef5c576094e3564172f03a22b1f172e37f27**.
- Scientific fits preserve exact start commits and every executed Python-source hash. Lead analysis snapshot: **87a0083** (full hash is in its registry). The final delivery receipt supplies the complete final Git hash and manifest fingerprint separately, avoiding a circular self-hash.

CPython3.12.14,PyMC5.28.5,nutpie0.16.11,ArviZ0.23.4,NumPy2.4.6,SciPy1.18.1,scikit-learn1.9.1. Full64-package versions and installation provenance are in [environment](../../logs/pilot_environment.json), [exact lock](../../configs/requirements-pilot.lock) and the preserved v0.3 install report. float64 is used throughout; BLAS/OMP/MKL/NumExpr threads are1, sampler cores2. Python source/Git byte checks and the baseline manifest bind inputs. SHA fingerprints bind bytes; they do not prove statistical assumptions or guarantee bit-identical sampling across different OS/compiler/library builds.

## Reproduction and custody

Inspect the complete saved posterior NC/NPZ and raw JSON records first; the code refuses overwriting completed/failed scientific outputs. For a fresh authorized replay, use an isolated checkout of the pre-evidence source snapshot87a0083, the pinned Python/package lock and only the fingerprint-matched training file. Create experiments/v0.4/precision before the validation call. Set PYTHONPATH to src and the thread settings above; use the documented forward-slash PyTensor base_compiledir. Run `python -m rp001.v04_run <prespecified-run-id>` for exactly the configured fits. Run `rp001.v04_precision_validation.run_precision_mcse_validation(frozen_commit=<that checkout HEAD>)` once, then `python -m rp001.v04_inference_run` and `python -m rp001.v04_analysis`, respecting two-process/budget limits. The analysis expects the archived historical payload and, for this specific evidence package, the original/recovery validation ledger; a clean new invocation must use its own validation-ledger binding rather than manufacture the historical storage failure. Thus this package provides executable component/source reproduction and exact retained-data verification; the historical delivery workflow is not a one-command clean replay.

Use [lead final QC](../../logs/v0.4/lead_final_qc.py) to recompute the18 raw-record RMS/coverage groups, known-target quantiles, recount4,000 OC outcomes, assert75 unique prediction cases, verify source Git blobs/manifest custody and check immutable historical files. The final55-test suite passes [XML](../../logs/v0.4/final_tests.xml). Full posterior and synthetic arrays,PRNG stream identities, all12 candidate records per pipeline and per-run diagnostics are retained. The descriptive seeded streams are pseudorandom; no claim of cryptographic random generation is made.

Only train/readme were extracted historically. Official test sensor/label archive members remain unopened and were not evaluated. Hashing the retained outer archive is a custody check, not access to its compressed members. Protection remains procedural, not an independently encrypted data vault. Final owners must authorize any future test/label phases. Historical documents/results/source are preserved; new reports are under docs/v0.4. Native current-state metadata is advanced only to this draft/evidence-return disposition; no final research authorization is inferred.
