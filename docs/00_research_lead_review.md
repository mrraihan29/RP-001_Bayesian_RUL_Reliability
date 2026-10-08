# RP-001 — Research Lead Technical Review v0.2

Tanggal: 8 Oktober 2026 (Asia/Jakarta). Penanggung jawab ilmiah: Rei sebagai research lead; pemilik keputusan: Raihan. Input: proposal v0.1, disimpan utuh di docs/proposal_v0.1.md.

**Keputusan lead: REVISE BEFORE LOCK. Paket persiapan berstatus PROTOCOL_DRAFTED.** Pertanyaan riset layak diteliti, tetapi novelty publikasi, transportability cutoff, identifiability model, dan kemampuan lingkungan belum cukup untuk menyatakan EXPERIMENT_READY. Tidak ada model fitting, MCMC, calibration residual, atau confirmatory evaluation yang dijalankan.

## Apa yang sudah dilakukan

Struktur G0 dibuat melalui delegasi GPT-6 LUNA Max dan diverifikasi lead. Git lokal tersedia. Arsip diperoleh melalui tautan repository NASA; hanya training FD001 dan readme diekstrak. Official test trajectories dan RUL labels tetap tidak diekstrak/dibaca. File arsip memang memuat bytes label test; “tertutup” berarti tidak diinspeksi, bukan kontrol akses kriptografis.

Audit yang dieksekusi menemukan 20.631 rows, 100 engine, 26 fields, tanpa missing/nonfinite, key engine-cycle duplikat, atau gap cycle. Lifetimes training 128–362 cycles, median 199. Ini adalah audit training, bukan validasi seluruh benchmark.

Delapan deliverable wajib terdapat di docs/01 sampai docs/08. Ledger, proposal protokol, provenance, perhitungan precision, dan manifest split juga disimpan. Tidak ada hasil perbandingan model. Pemeriksaan numerik persamaan conditioning Gaussian lulus pada 12 kasus fixed-parameter (history 1/2/30, termasuk correlation negatif/tinggi), bersama interval score, rank conformal, Wilson precision, dan arah bootstrap-t. Ini bukan synthetic parameter recovery atau validasi sampler; log tersimpan di logs/mathematical_preflight.json.

## Temuan yang mengubah proposal

1. Bayesian RUL, conformal RUL, dan Bayesian uncertainty calibration memiliki prior art. Kontribusi harus berupa evaluasi yang transparan dan terbatas: satu forecast per unseen engine, audit inferensi, paired interval-score uncertainty, dan eksplorasi pengaruh correlation sensor. Klaim “metode pertama” tidak didukung.
2. Satu failure time menghasilkan R_i(t)=T_i-t. Repeated RUL windows bukan pengamatan failure independen. Model principal yang diusulkan memakai satu target per engine dengan likelihood sensor temporal; tidak menempelkan random intercept pada ribuan label deterministik.
3. Exchangeability calibration/test tidak mengikuti otomatis dari engine-disjoint split. Mekanisme cutoff official test tidak cukup terdokumentasi untuk menjamin bahwa pseudo-cutoffs memiliki distribusi sama.
4. Pada n=100, coverage 90/100 mempunyai Wilson 95% CI 82,56–94,48%. FD001 cukup untuk comparative benchmark, tetapi tidak untuk sertifikasi kalibrasi ±2 percentage points.
5. Aturan cutoff tanpa penggunaan outcome yang diusulkan menghasilkan 43 fitting, 13 tuning, dan 25 calibration engine eligible. Ini membatasi kompleksitas, tuning, dan subgroup inference.
6. Stack bundled saat ini belum menyediakan PyMC/ArviZ/SciPy/sklearn. Colab Pro milik Raihan adalah pilihan cadangan yang relevan, tetapi belum diuji.

## Rekomendasi konkret untuk disetujui

Pertahankan endpoint 90% interval score dan satu primary comparison: Bayesian principal tanpa post-hoc calibration versus CQR. Gunakan proposal split 55/15/30; prediksi satu cutoff per engine; setelah pemilihan terbatas, refit fitting+tuning (56 eligible engines), calibration tetap 25 engine. Jadikan hasil comparative evidence pada FD001; H0:D≥0 vs H1:D<0 hanya satu pengujian arah yang direncanakan, tanpa janji bahwa studi mampu mendeteksi efek kecil.

Principal candidate: hierarchical latent level/slope untuk satu ringkasan sensor, AR(1) measurement errors, serta lognormal landmark RUL response. Jumlah parameter global kecil dan latent effects engine baru dikondisikan hanya pada sensor yang telah terlihat. Acceptance masih membutuhkan synthetic recovery dan diagnostic pilot sebelum protokol final dibekukan. Fallback sederhana harus dipilih sebelum final test; tidak boleh mengganti model setelah melihat outcome.

Usulkan 5 cycles interval-score improvement sebagai skala practical significance internal yang harus disetujui owner. Ini bukan threshold keselamatan atau biaya maintenance tervalidasi. Jika tidak ada justifikasi yang disetujui, laporkan effect size tanpa klaim practical superiority/equivalence.

## Gate dan batas persetujuan

| Gate | Status | Makna |
|---|---|---|
| G0 workspace | PASS | Folder dan source copy diverifikasi |
| G1 evidence map | PASS untuk narrative design review | Bukan systematic review atau novelty certification |
| G2 question/estimand draft | PASS | Target benchmark dan scope dinyatakan |
| G3 final protocol lock | BLOCKED | Persetujuan owner dan preflight implementasi belum tersedia |
| G4 complete data integrity | DEFERRED | Training audit selesai; test integrity/rights-release review belum selesai |
| G5 experiments | DEFERRED | Tidak dijalankan |
| Scientific validation/publication | DEFERRED | Tidak ada empirical model results |

Persetujuan tahap berikutnya harus dibatasi pada development implementation dan pilot training-only/synthetic. Setelah feasibility dan diagnostic gates lulus, lead mengembalikan protokol final dengan code/environment hashes untuk persetujuan lock. Persetujuan draft ini tidak membuka official test labels.

## Evidence dan provenance

- Data facts dari eksekusi: data/raw/training_audit.json dan src/rp001_preflight.py.
- Precision calculations: logs/sample_precision.json.
- Source identity: data/raw/provenance.json.
- Literatur dan akses terbatas: literature/evidence_records.json, search_log.json, crossref_status_audit.json.
- Owner steering: ketersediaan Google Colab Pro ditambahkan dalam sesi ini; tidak ada aktivitas pada akun Colab.
- Formal handoff dan daftar risiko: research/gate_results.json, docs/08_risks_assumptions_decisions.md.

NASA mengonfirmasi desain simulated run-to-failure dan endpoint test sebelum failure [S01, S02]. Prior art utama conformal C-MAPSS diverifikasi pada full text [S03]. Interpretasi model yang baru adalah proposal lead, bukan temuan NASA atau hasil empiris.

Lihat [NASA dataset](https://data.nasa.gov/dataset/cmapss-jet-engine-simulated-data) dan [Javanmardi & Hüllermeier, 2023](https://papers.phmsociety.org/index.php/ijphm/article/view/3417).
