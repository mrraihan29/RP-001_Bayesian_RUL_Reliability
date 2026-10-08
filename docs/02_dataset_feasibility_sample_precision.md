# Dataset Feasibility & Sample Precision v0.2

Status: training-only audit completed; full benchmark integrity DEFERRED. Semua angka berikut berasal dari audit yang dieksekusi atau perhitungan planning, dibedakan secara eksplisit.

## Acquisition dan target

NASA repository menautkan original C-MAPSS package [S01/S02]. Arsip luar 12.429.152 bytes berisi CMAPSSData.zip; hanya train_FD001.txt dan readme diekstrak. Original bytes tidak diubah. Hash dan URLs tercatat dalam data/raw/provenance.json.

Scope: simulated FD001 engines, satu operating condition, HPC fault mode. Outcome uncapped R=T-t, dalam cycles. Last training cycle digunakan sebagai operational failure convention. Final-cycle t=T mempunyai R=0 dan dikeluarkan dari landmark prediction sebab target mensyaratkan masih beroperasi. Tidak ada RUL cap 125/130.

Input schema: engine ID, cycle, 3 settings, 21 sensors = 26 fields. Readme mempunyai keliru penomoran akhir sensor; schema matematika dan actual field count mengonfirmasi 21 sensors. Physical unit tiap channel belum diverifikasi; jangan mengarang unit. Train/test numeric IDs mempunyai namespace berbeda.

## Temuan audit training

| Properti | Hasil |
|---|---:|
| Engine | 100 |
| Rows | 20.631 |
| Fields / row | 26 |
| Nonfinite/missing fields | 0 |
| Duplicate engine-cycle key | 0 |
| Consecutive cycles sejak 1 | PASS per engine |
| Training lifetime min / median / max | 128 / 199 / 362 cycles |

Sensor ranges/variance tersedia pada training_audit.json. Full-data descriptive profiling tidak menghasilkan fitted preprocessing. Feature selection, scaling, PCA, prior development, dan hyperparameter selection kemudian hanya menggunakan allowed fit information.

Belum diperiksa: exact/near trajectory duplication lintas train-test, physical sensor meanings, official test schema, test cutoff distribution, atau labels integrity. Benchmark exposure dalam published literature juga mencegah klaim benar-benar pristine historical holdout. Labels belum dibaca dalam sesi ini.

## Proposed split dan pseudo-cutoff

Seed string tetap: RP001-20261008-v0.2. Urutan engine ditentukan SHA-256(seed|split|ID); first 55 fit, next 15 tune, last 30 calibration. Cutoff C=30+[SHA-256(seed|cutoff|ID) mod 221], sehingga 30≤C≤250, ditentukan tanpa memakai T. Landmark eligible hanya jika C<T. Tidak ada redraw atau penggantian engine yang gagal lebih awal.

| Role | Reserved engines | Eligible alive |
|---|---:|---:|
| Fit | 55 | 43 |
| Tune | 15 | 13 |
| Calibration | 30 | 25 |

Ini proposed manifest, bukan approved/locked split. Setelah model selection, refit fit+tune menghasilkan 56 eligible engine. Calibration 25 engine tetap tidak masuk fitting. Survival eligibility memakai training failure endpoint hanya untuk aturan inclusion; future readings/outcomes tidak masuk features. Hash modulo adalah practical deterministic uniform approximation; bukan bukti randomization atau stochastic independence. Log preflight lama memakai istilah independent sebagai shorthand outcome-blind; klarifikasi ini mengoreksi interpretasinya, bukan angka audit.

Generator adalah outcome-blind proxy untuk prospective operational-age sampling. Population reference P_engine×G_C dikondisikan C<T memakai asumsi prospective random C independen dari T; fixed hash/seed yang dieksekusi tidak membuktikan asumsi stochastic itu. Official test menggunakan mechanism G_official yang belum diketahui. Maka comparator adalah empirically evaluated calibrated comparator; exact 90% guarantee pada official endpoint tidak boleh diklaim. Cutoff berbeda tidak dapat diperbaiki hanya dengan bootstrap.

## Attainable precision

Jika 90 dari 100 official test engine covered, Wilson 95% CI = [0,825634;0,944771]. Planning SE pada p=0,90 adalah 0,03. Untuk half-width kira-kira ±0,02 dibutuhkan 865 independent engines; ±0,05 sekitar 139, memakai normal approximation dan p=0,90. Ini bukan observed coverage atau certified sample-size requirement.

Untuk paired score d_i dan n=100:

| Assumed SD(d), cycles | Approximate 95% CI half-width | Approximate 80% one-sided detectable reduction |
|---:|---:|---:|
| 10 | 1,98 | 2,49 |
| 20 | 3,97 | 4,97 |
| 40 | 7,94 | 9,95 |
| 80 | 15,87 | 19,89 |

Half-width menggunakan t_99≈1,984; MDE=(z_0.95+z_0.80)σ_d/√100. Normal planning hanya orientasi; skew, heterogeneity, miss penalties, dan fitted-pipeline variation memerlukan design simulation setelah implementation disetujui. SD(d) belum diketahui. Tidak ada post-hoc power.

Dengan 25 calibration engines: k=ceil(26×0,90)=24; finite order-statistic rank fraction 24/26=92,31%, granularity 3,85 percentage points. Ini bukan coverage yang diamati atau conditional-on-calibration guarantee. Minimum finite rank untuk α=0,10 adalah n_cal≥9; threshold studi proposed ≥19 memberi granularity ≤5%. Lebih banyak windows dalam engine tidak memperbesar n_cal.

## Feasibility decision

Feasible untuk compact comparative benchmark. Tidak adequate untuk klaim tight calibration tolerance, small-subgroup reliability, real-engine safety, atau modest effects tanpa sufficient precision. Jangan membuka test untuk memperkirakan variance lalu melakukan power-based design changes.

NASA acknowledgment diminta repository. Portal menampilkan license not specified: paket dan terms disimpan, research use dibatasi ke scope ini; redistribution/publication terms harus di-review sebelum release. Tidak menyatakan public-domain blanket license.

Reproduce setelah Python tersedia: python src/rp001_preflight.py. Script sengaja menolak overwrite audit outputs; gunakan fresh checkout/output-version jika ingin rerun. [NASA dataset](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data), [NASA PCoE repository](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/).
