# Literature Gap & Novelty Review v0.2

Review mode: structured narrative/background review untuk keputusan desain, searched 8 Oktober 2026. Tidak diklaim exhaustive, systematic, atau PRISMA-complete. Unit sintesis: investigation/report dengan duplicate preprint–publication ditautkan, bukan jumlah hasil pencarian.

## Batas search dan verifikasi

Pencarian web scholarly menggunakan istilah Bayesian RUL uncertainty, C-MAPSS calibration, conformal RUL, engine dependence, hierarchical conformal, proper interval scoring, dan MCMC diagnostics. Exact queries yang benar-benar dijalankan tersimpan dalam literature/search_log.json. Sumber prioritas: NASA, publisher/journal, proceedings, arXiv author reports, institutional author manuscripts, dan official software docs. Search snippets hanya untuk discovery.

Identitas, publication status, dan claim support dicatat terpisah. Crossref audit berhasil untuk sebagian record; sebagian 429, satu 404. Tidak ada dasar untuk menyatakan seluruh literatur bebas correction/retraction. Sumber abstract-only tidak dipakai untuk memastikan rincian split, inferensi, atau angka performa. Tidak ada pooling “hasil terbaik” lintas studi dengan preprocessing dan target berbeda.

## Evidence map ringkas

| ID | Report / akses | Apa yang didukung | Batas relevansi |
|---|---|---|---|
| S03 | Javanmardi & Hüllermeier (2023), IJPHM, full text §§3–4 | Conformal RUL, CQR, dan nonexchangeable variants sudah dievaluasi pada C-MAPSS | Target rectification dan sampling/window policies perlu dibedakan dari uncapped study ini |
| S04 | Benker, Furtner, Semm & Zaeh (2021), JMS, publisher abstract | Bayesian neural RUL dengan HMC dan VI pada simulated turbofans sudah ada | Full methods tidak diakses; tidak cukup untuk menilai engine-level reliability |
| S05 | Romano, Patterson & Candès (2019), NeurIPS; author full text Theorem 1 | CQR finite-sample marginal coverage mensyaratkan exchangeability | Bukan theorem khusus C-MAPSS atau conditional stage coverage |
| S06 | Gneiting & Raftery (2007), author manuscript §6.2 | Interval score menggabungkan width dan miss penalties | Tidak mengukur seluruh predictive distribution dari satu interval |
| S07 | Barber et al., author full text v5 (2023) | Ada metodologi untuk coverage degradation ketika exchangeability dilanggar | Arbitrary reweighting tidak otomatis memberi guarantee yang berguna |
| S08 | Lee, Barber & Willett, author full text v4 (2025) | Hierarchical predictive inference memiliki aturan exchangeability tersendiri | Temporal trajectories tidak otomatis memenuhi asumsi repeated-measure methods |
| S09 | Vehtari et al. (2021), author manuscript | Modern R-hat/ESS dan multiple-chain diagnostics tersedia | Convergence diagnostics tidak membuktikan likelihood benar |
| S10 | Chang & Lin (2025), publisher abstract/preview | Bayesian few-shot RUL calibration sudah dikaji | Bearing datasets, bukan FD001; transportability terbatas |
| S11 | Yang et al. (2026), publisher content | Transformer, MC Dropout, dan CP pada FD001/FD003 sudah dibahas | Bukan exact posterior HMC; tidak menyamakan CP dengan isolasi aleatoric uncertainty |
| S12 | Aboudoumat et al. (2026), journal abstract | Report mengklaim engine-disjoint grouped calibration dan official endpoint evaluation | DOI tidak ditemukan dalam Crossref; identitas publisher-level saja, full methods belum diverifikasi |
| S13 | Xu et al. (2026), Crossref metadata | Report bertema Bayesian UQ/calibration teridentifikasi | Issue metadata November 2026; online date/content belum primary-verified; tidak dihitung sebagai hasil yang telah ditelaah |

Biggio et al. arXiv:2104.03613 adalah adjacent N-CMAPSS work, bukan bukti langsung pada C-MAPSS FD001. Preprint 2022 dari S03 ditautkan ke journal report 2023, dihitung satu study.

## Gap yang defensible dan yang belum terbukti

**Bukan novelty:** penggunaan Bayesian untuk RUL; penggunaan conformal pada C-MAPSS; nominal PICP/width reporting; engine-disjoint split sebagai konsep.

**Working gap:** apakah sebuah model Bayesian kecil, dengan posterior computation yang diaudit dan sensor dependence eksplisit, menghasilkan interval score kompetitif terhadap CQR pada endpoint unseen engine, sambil memisahkan finite-benchmark performance, target-distribution assumptions, dan prior sensitivity.

Ini adalah agenda evaluasi yang terukur. Belum ditemukan bukti cukup untuk menyatakan kombinasi tersebut belum pernah diteliti. S12 dekat dengan bagian leakage/engine separation; S13 memerlukan full-text review. Novelty bersifat UNRESOLVED dan tidak menjadi prasyarat untuk validitas sebuah comparative/replication study.

## Synthesis dan counterevidence

Literatur mendukung kebutuhan evaluasi probabilistik, tetapi tidak mendukung asumsi bahwa label “Bayesian” menjamin empirical calibration. S05/S07/S08 membatasi guarantees conformal. S03 membahas stage heterogeneity dan target transformation yang membuat perbandingan angka lintas paper tidak langsung. Bayesian HMC precedent S04 menghilangkan novelty atas inferential engine itu sendiri. Evidence dari bearing/N-CMAPSS merupakan boundary condition, bukan independent confirmation FD001.

Penilaian computational appraisal untuk setiap report mencakup entity split, leakage, landmark selection, target capping, comparator budget, independent units, inference diagnostics, uncertainty, code availability, dan dataset identity. Jika informasi tidak tersedia, catat not assessed; tidak ubah menjadi pass/fail atau quality score numerik.

## Tindakan sebelum publikasi

Dapatkan full methods S04/S10/S11/S12/S13 dan lakukan backward/forward citation search dengan bibliographic database yang sesuai. Verifikasi online-publication date S13; periksa DOI/status S12 melalui registration agency lain/publisher. Search ulang sebelum mengklaim novelty atau memilih venue. Bila overlap tetap luas, posisikan studi sebagai rigorous comparative evaluation/replication dengan contribution pada evidence quality.

Sumber langsung: [S03](https://papers.phmsociety.org/index.php/ijphm/article/view/3417), [S04](https://www.sciencedirect.com/science/article/pii/S0278612520301928), [S05](https://arxiv.org/pdf/1905.03222), [S06](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf), [S07](https://arxiv.org/html/2202.13415v5), [S08](https://arxiv.org/html/2306.06342v4), [S09](https://sites.stat.columbia.edu/gelman/research/published/Vehtari_etal_2020_rhat_ess.pdf), [S10](https://www.sciencedirect.com/science/article/pii/S0952197624021390), [S11](https://www.sciencedirect.com/science/article/pii/S2090447926000195), [S12](https://sjphrt.com.ly/index.php/sjphrt/en/article/view/169), [S13 metadata](https://api.crossref.org/works/10.1016/j.ress.2026.112763).
