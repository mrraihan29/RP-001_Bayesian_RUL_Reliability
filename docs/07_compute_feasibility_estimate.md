# Compute Feasibility Estimate v0.2

Status: capability inventory observed; runtime/RAM estimates provisional; no Bayesian pilot or package installs performed. User addition: Raihan has Google Colab Pro available if needed.

## Observed local capability

G0 inventory: Windows 11, Intel i7-10750H, 12 logical processors, 15.78 GiB RAM, GTX 1650 Ti (4 GiB). Global Python reports 3.11.9; bundled audit interpreter 3.12.14. Mereka environments berbeda, bukan contradictory versions.

Bundled interpreter can locate NumPy/pandas; SciPy, PyMC, ArviZ, statsmodels, sklearn, Matplotlib, pytest not available there. find_spec availability bukan import/ABI compatibility test. pyproject.toml merupakan unpinned requirements wishlist, belum lock. Jangan install ke shared application runtime; proposed project .venv atau isolated Colab session setelah Stage A.

## Mengapa compact model masuk akal

Development fitting 43 engines, final refit 56; each principal history≤30. Marginal Gaussian formulation mempunyai 14 global scalar degrees of freedom (β: 2; γ: 2; Γ: 4; Σ_g: 3; σ_z/σ_r: 2; ρ: 1), dengan jumlah unconstrained sampler coordinates bergantung implementasi. Ini bukan BNN dengan ribuan weights. Latent 2×N bisa analytically integrated.

Dense covariance blocks 30×30 atau joint 31×31; naive per-gradient cost O(Nw³), sekitar 56×30³=1.512 million order-of-magnitude arithmetic units before autodiff/sampler factors. Ini operation-count illustration, bukan FLOP benchmarking atau runtime measured. AR(1)/low-rank structure dapat dioptimasi kemudian dengan numerical equality checks.

Four chains×(1.000 warmup+2.000 draws)=12.000 transitions per accepted fit, dengan multiple leapfrog evaluations tiap transition. ESS bukan count transitions. New-engine exact sensor conditioning dapat lebih mahal dari drawing naive fixed-weight predictions; cost harus diukur pada pilot.

## Planning envelope, bukan benchmark

| Activity | Proposed estimate / limit |
|---|---|
| Data audit & stdlib precision | Executed, seconds-scale compute; network separate |
| CQR 12 configurations+reference | Planning 5–30 minutes CPU |
| Principal 4-chain fit | Planning 0.25–3 hours wall-clock depending geometry/backend |
| Synthetic recovery + design simulation | Planning 2–12 aggregate CPU-hours |
| Principal/refit/limited sensitivities | Planning 8–24 aggregate CPU-hours, overlap with pilots documented |
| Full package budget | Proposed 32 aggregate CPU-hours; 10 GiB artifacts; no new paid purchase |

Ranges are engineering guesses, not guarantees and not additive exact totals. Thermal throttling, BLAS thread oversubscription, slow compilations, and poor posterior geometry can dominate. Prefer 2 chains in parallel locally if 4-chain parallelism crowds RAM; still 4 independent chains total. Record core allocation and elapsed CPU/wall time separately. Max memory proposed <10 GiB total locally to retain system headroom.

If pilot extrapolation exceeds 32 CPU-hours, reduce prespecified exploratory work or return budget/model amendment before test. Do not shorten chains below diagnostics merely to finish.

## Colab Pro plan

Colab Pro is a compute option, not a prerequisite. Google states resources vary and are not guaranteed; paid access depends on availability/compute units, with backend termination possible [S14]. No guaranteed GPU type, RAM amount, continuous uptime, or speedup is assumed.

Begin with CPU runtime. For compact NumPy/PyMC marginal model, CPU+adequate RAM may be sufficient. GPU/JAX/NUTS backend is optional only after compatibility and float64 numerical equivalence review; benchmark ESS/second and relevant predictive MC error, not raw transitions/second. A 4 GiB laptop GPU is not evidence that acceleration helps.

Local project remains canonical workspace. Build a versioned transfer bundle from approved source/config/data manifest, excluding secrets and sealed labels. Colab ephemeral workspace is execution replica; synchronize all planned logs, InferenceData, configs, dependencies, and hardware manifests back under project. Persistent checkpoints after each completed chain/batch; no silently merging partial chains with incompatible adaptation. Do not upload to user's Drive/account or start paid compute until Stage A scope and concrete execution bundle approved. This review did not open Colab or consume units.

## Environment acceptance before execution

Choose one tested CPython 3.11/3.12 stack according to current PyMC compatibility; capture exact resolver lock including NumPy/SciPy/PyTensor/ArviZ/sklearn/BLAS dependencies. Requirements file alone without versions is not approved. Current PyMC docs expose changed posterior-predictive resampling semantics [S15]; verify against the chosen installed release, do not pin an arbitrary version from memory.

Acceptance: clean isolated installation, import smoke test, numerical covariance oracle, synthetic model sampling, diagnostic output read/write, fixed-seed reproducibility caveats, parameter/predictive recovery, full versus modular sensor conditioning check, and locked scoring/calibration tests.

Before production of inference evidence, report pilot wall time, peak RAM, sampler diagnostics, effective sample rate, posterior-prediction cost, and measured compute units if Colab UI provides them. Until then COMPUTE_FEASIBLE is provisional.

[S14 Google Colab FAQ](https://research.google.com/colaboratory/faq.html), [S15 PyMC API](https://www.pymc.io/projects/docs/en/stable/api/generated/pymc.sample_posterior_predictive.html).
