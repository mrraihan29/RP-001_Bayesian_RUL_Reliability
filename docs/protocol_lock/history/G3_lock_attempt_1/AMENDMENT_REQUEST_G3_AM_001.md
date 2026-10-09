# RP-001 | Amendment Request G3-AM-001

**PENDING OWNER DECISION. No amendment applied. PROTOCOL_DRAFTED.**

Owner-reviewed baseline: c583ce62eac9a6b3dcd29c1929cc07c17569beb7. Section 3 of the [G3 authorization](OWNER_AUTHORIZATION_G3.md) requires returning a material output-related ambiguity for amendment rather than silently repairing it.

## Exact discrepancy

| Location at approved baseline | Numerical rule |
|---|---|
| docs/v0.5/02_proposed_locked_analysis_contract.md:70 | Brent bracket min(mu - 12 SD) to max(mu + 12 SD), xtol=1e-12; called the frozen v0.4 precision implementation. |
| src/rp001/v04_precision.py:78-108 | r=(abs(Phi^-1(p))+12)*s_max+(m_max-m_min); bracket [m_min-r,m_max+r]. Up to 100 predetermined bracket-check attempts, doubling r if not bracketed; invalid/nonfinite radius fails. Brent xtol=1e-12, rtol=4*float64 epsilon. |
| src/rp001/prediction.py:7-17 | Legacy componentwise +/-12 SD bracket, but Brent xtol=1e-10. |

The v0.5 prose combined the legacy bracket with the precision-helper tolerance. Rei's contract drafting failed to distinguish those implementations. Neither helper exactly matches that combined description. Source bytes and historical results remain unchanged.

The precision function supplied the archived quantiles used by precision diagnostics and saved-draw score propagation; the legacy helper also supplied separate development prediction summaries. The official procedure needs one explicit route for stored endpoints and aligned diagnostics/influences.

## Materiality and mathematical assessment

A finite normal mixture with positive variances and normalized nonnegative weights has a continuous strictly increasing CDF and unique target quantile. At the legacy lower bound each component CDF is at most Phi(-12); at the upper bound each is at least Phi(12). Both brackets therefore enclose the same exact root for p=.05/.50/.95. This discrepancy does not demonstrate a different posterior distribution, invalid MCMC evidence, or a material historical score difference.

Initial bounds, bracket-expansion behavior, solver tolerance, floating-point path and potential failures nevertheless differ. No future endpoint computation has quantified their effect. Because G3 requires the exact numerical and failure procedure to be frozen without interpretation, this is a specification consistency blocker requiring owner disposition. It is not an additional robustness stress test.

## Recommended minimal amendment: existing precision implementation

Replace only the bracket/tolerance clause in contract line 70 with this proposed text:

> For principal official endpoints and independent-fit diagnostics, use the quantile returned by rp001.v04_precision.estimate_mixture_quantile_mcse and its _weighted_quantile implementation at the approved source hash. For probability p, finite component means and positive component SDs, set m_min=min(mu), m_max=max(mu), s_max=max(SD), r=(abs(Phi^-1(p))+12)*s_max+(m_max-m_min), and initial bracket [m_min-r,m_max+r]. Preserve the existing deterministic limit of 100 bracket-check attempts, doubling r only if the CDF does not bracket p; invalid/nonfinite bracketing is retained as failure. Brent uses xtol=1e-12, rtol=4*float64 epsilon, and remaining defaults bound to the pinned SciPy environment. The same returned log quantile and exponentiated endpoint supply prediction storage, CDF/density checks, quantile diagnostics and score influence. The legacy rp001.prediction.mixture_quantile helper remains historical and does not supply official primary endpoints. Retain root residual <=1e-10 and every existing numerical/prediction-failure guard. This predetermined algorithm grants no additional draws, model change, result-selected repair or post-label retry.

Approval would align the prose with existing owner-reviewed source. No scientific source modification is requested. Priors, posterior states, preprocessing, CQR selection/correction, score/estimand, MCSE thresholds and claim boundaries remain unchanged. No new science experiment is requested.

Owners may instead require literal +/-12 SD bounds with xtol=1e-12; that would require explicit source amendment and separately scoped deterministic verification. It has not been implemented.

Full source/input/posterior identities are in [VERIFIED_BASELINE_MANIFEST.json](VERIFIED_BASELINE_MANIFEST.json). After an accepted exact amendment, resume G3 packaging/verification only. Complete lock before any separately authorized Stage B work.

**Requested owner decision: approve recommended G3-AM-001 clarification, or specify another reviewed numerical procedure. B/C/D remain unauthorized.**
