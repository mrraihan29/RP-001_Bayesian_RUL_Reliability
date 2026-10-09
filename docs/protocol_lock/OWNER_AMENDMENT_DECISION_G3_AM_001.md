# RP-001 | RESEARCH OWNER AMENDMENT DECISION

**Amendment:** G3-AM-001\
**Decision:** APPROVED\
**Scope:** Numerical Quantile Procedure Specification Clarification\
**Reviewed Commit:** `1fc660b3ce09dd2b23b6a05e0698903bf6060355`

Research Owners menyetujui rekomendasi G3-AM-001 untuk menyelaraskan spesifikasi kontrak dengan implementasi numerical precision yang telah diverifikasi.

**Approved correction:**

Gunakan `rp001.v04_precision.estimate_mixture_quantile_mcse` dan `_weighted_quantile` pada approved source hash sebagai satu-satunya authoritative numerical quantile route untuk official primary Bayesian endpoints dan independent-fit diagnostics.

Ikuti secara persis:

- Probability-dependent initial bracket.
- Deterministic maximum 100 bracket checks.
- Existing radius expansion and failure behavior.
- Brent `xtol=1e-12`.
- Brent `rtol=4 × float64 epsilon`.
- Existing numerical root-residual acceptance criterion.
- Existing MCSE, ESS, convergence, and prediction failure policies.

Legacy `rp001.prediction.mixture_quantile` tetap disimpan untuk historical provenance, tetapi tidak digunakan untuk official primary predictions.

**Authorization conditions:**

1. Ubah hanya bagian spesifikasi yang disetujui beserta referensi administratif yang diperlukan.
2. Tidak boleh mengubah scientific implementation, prior, posterior states, CQR, estimand, numerical threshold, atau acceptance policies.
3. Pertahankan kontrak v0.5 asli serta laporan G3 yang gagal sebagai historical evidence.
4. Catat exact amendment diff, source hashes, owner decision, dan verification results.
5. Lakukan direct SOL verification bahwa amended contract konsisten dengan pinned source.
6. Jika ditemukan kontradiksi material baru, hentikan proses dan kembalikan kepada Research Owners.

**Authorized next action:**

Resume **G3 Formal Protocol Lock**, termasuk documentation correction, integrity checks, scientific consistency verification, final lock packaging, dan Git recording.

Apabila seluruh G3 checks lulus, status boleh diperbarui menjadi `PROTOCOL_LOCKED` dan serahkan final completion report.

**NOT AUTHORIZED:**

- Official test-sensor access.
- Official test-label access.
- Confirmatory evaluation.
- Additional scientific experiments.
- Model retraining or posterior resampling.
- Numerical threshold relaxation.
- Model selection or fallback activation.

Persetujuan amendment ini tidak mengesahkan hasil penelitian dan tidak memberikan izin menjalankan Stage B, C, atau D.

**FINAL DECISION: G3-AM-001 APPROVED. PROCEED WITH G3 LOCK COMPLETION ONLY.**
