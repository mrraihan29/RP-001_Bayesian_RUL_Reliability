# Audit Split, Eligibility, dan Cutoff Dataset v0.3

Tanggal: 8 Oktober 2026. Status: audit pengembangan training-only; bukan protocol lock atau evaluasi konfirmatori.

## Cakupan

Audit mereproduksi manifest FD001 training, hash split 55/15/30, kelayakan C<T, pembentukan prefix, ukuran subgroup, distribusi cutoff yang teramati pada metadata training, serta sensitivitas desain terhadap variasi salt cutoff. File input raw tidak diubah. Tidak ada official test trajectory, label, atau archive entry yang dibuka; tidak ada calibration residual atau model yang dihitung.

Pertanyaan riset utama tetap. Threshold praktis 5 cycle belum disetujui dan tidak digunakan.

## Integritas split dan kelayakan

Hash split dan cutoff pada manifest berhasil direproduksi dari seed RP001-20261008-v0.2. Seluruh 100 engine memiliki satu role dan tidak ada redraw. Eligible didefinisikan sebagai C<T.

| Role | Dicadangkan | Eligible | Tidak eligible |
|---|---:|---:|---:|
| fit | 55 | 43 | 12 |
| tune | 15 | 13 | 2 |
| calibration | 30 | 25 | 5 |
| Total | 100 | 81 | 19 |

Hitungan canonical cocok dengan 43 fitting, 13 tuning, dan 25 calibration eligible: True. Ini hanya validasi split dan eligibility training yang diusulkan.

## Cutoff, lifetime, dan survival selection

| Kelompok | n | C min | C median | C mean | C max |
|---|---:|---:|---:|---:|---:|
| Semua engine dicadangkan | 100 | 30 | 126.0 | 129.6 | 249 |
| Eligible saja | 81 | 30 | 110.0 | 112.2 | 230 |

Histogram cutoff canonical untuk seluruh engine yang dicadangkan:

| Rentang C | Semua | Eligible |
|---|---:|---:|
| 30–73 | 23 | 23 |
| 74–117 | 21 | 21 |
| 118–161 | 23 | 21 |
| 162–205 | 19 | 12 |
| 206–250 | 14 | 4 |

Secara deskriptif, hubungan cutoff-lifetime pada seluruh 100 engine: Pearson r=-0.015, Spearman ρ=-0.067. Di antara 81 survivor: Pearson r=0.244, Spearman ρ=0.180. Ini bukan uji independensi atau estimasi transportability.

| Lifetime rank-quartile | Dicadangkan | Eligible | Proporsi eligible | Rentang T |
|---|---:|---:|---:|---:|
| Q1 | 25 | 14 | 0.560 | 128–174 |
| Q2 | 25 | 20 | 0.800 | 178–199 |
| Q3 | 25 | 22 | 0.880 | 199–229 |
| Q4 | 25 | 25 | 1.000 | 230–362 |

Aturan C<T menyingkirkan engine yang sudah mencapai endpoint training pada cutoff, sehingga komposisi survivor bergantung pada cutoff. Hash bersifat outcome-blind secara konstruksi, tetapi satu realisasi deterministik tidak membuktikan independensi stokastik cutoff dan lifetime.

Distribusi cutoff official tidak dapat diidentifikasi dari metadata training yang diizinkan. Audit ini tidak mengklaim exchangeability antara pseudo-cutoff training dan cutoff official.

## Prefix dan risiko kebocoran temporal

Prefix 81 engine eligible dibangun hanya dari cycle 1 sampai C; total 9092 baris prefix diperiksa dan 0 baris setelah C dipakai sebagai feature. Feature memuat setting dan sensor menurut schema; engine ID, cycle, lifetime terminal, dan outcome tidak masuk matriks feature. Lifetime T hanya dipakai untuk aturan kelayakan training.

Exact common-prefix: 0 pasangan. Near-duplicate screen: 0 kandidat dari 3240 pasangan yang dibandingkan. Perbandingan memakai overlap awal yang cycle-aligned, minimum 30 cycle. Ambang mean normalized RMSE ≤ 0.02 dan kanal maksimum ≤ 0.10 SD. Ini heuristic review screen, bukan oracle duplikasi semantik.

## Ukuran subgroup

Role utama berukuran 55/15/30 dicadangkan dan 43/13/25 eligible. Sel role × lifetime quartile berikut kecil atau kosong; hasilnya tidak mendukung klaim reliabilitas subgroup.

| Role | Lifetime quartile | Dicadangkan | Eligible |
|---|---:|---:|---:|
| fit | Q1 | 15 | 8 |
| tune | Q1 | 5 | 3 |
| calibration | Q1 | 5 | 3 |
| fit | Q2 | 11 | 9 |
| tune | Q2 | 3 | 3 |
| calibration | Q2 | 11 | 8 |
| fit | Q3 | 15 | 12 |
| tune | Q3 | 2 | 2 |
| calibration | Q3 | 8 | 8 |
| fit | Q4 | 14 | 14 |
| tune | Q4 | 5 | 5 |
| calibration | Q4 | 6 | 6 |

## Sensitivitas cutoff untuk desain

Dibandingkan 100 salt cutoff deterministik dengan rentang 30..250 yang sama, sambil mempertahankan role split canonical. Audit hanya mengukur variasi jumlah dan keanggotaan eligible; tidak ada fitting, score, atau pemilihan berdasarkan performa.

Eligible canonical: 81; rentang eligible pada skenario alternatif: 69–85, median 78.0. 83 engine berubah status pada sebagian skenario.

| Role | Eligible canonical | Min alternatif | Median alternatif | Maks alternatif |
|---|---:|---:|---:|---:|
| fit | 43 | 34 | 43.0 | 51 |
| tune | 13 | 8 | 11.5 | 15 |
| calibration | 25 | 18 | 23.0 | 29 |

Variasi hash ini adalah design sensitivity, bukan distribusi sampling inferensial, bukan bukti mekanisme cutoff official, dan bukan dasar mengganti manifest canonical atau memilih model.

## Handoff dan batas klaim

Gate yang diserahkan: TRAINING_DATA_VALIDATED untuk audit split/eligibility/cutoff FD001 training saja. Gate ini tidak menyatakan seluruh benchmark tervalidasi dan tidak membuka akses test. Cutoff official dan mekanismenya tidak teramati; exchangeability tidak dibuktikan; duplikasi lintas train-test, schema/test-label integrity belum diaudit. Subgroup kecil dan ambang near-duplicate heuristic membatasi klaim.

Tidak ada perubahan primary question, tidak ada evaluasi konfirmatori, dan practical threshold 5 cycle belum disetujui.

Perintah eksekusi: C:\Users\Raihan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe "C:\Coding\Project\NAOBI RESEARCH\RP-001_Bayesian_RUL_Reliability\src\rp001\development_data_audit.py" --project-root "C:\Coding\Project\NAOBI RESEARCH\RP-001_Bayesian_RUL_Reliability"
SHA-256 script: 5697fc66c254637547499f9a88e2ced5472a6de176bb4a26972975710ea16f92
SHA-256 training trajectory: 963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8
SHA-256 manifest: 6d6e0f10d979d41739c6c07b6bab8f0c32d2844ebd150e82d13caa3bd29e124b
SHA-256 audit JSON: 0d87c1ee401b63d043d693857a41aa0b7f9a6728b88f93b3ce45665c0e58fe16
