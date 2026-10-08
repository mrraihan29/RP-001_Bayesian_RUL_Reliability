# Independent Methodology Audit — Return to Lead v0.2

Audit completed 8 October 2026; read-only, no models or held-out files accessed. Scientific approval DEFERRED. Inputs snapshot: logs/methodology_audit_inputs.json. Producer: independent methodology audit subagent under suite delegation; consumer Rei research lead.

## Findings and lead dispositions

P1: CQR two endpoints did not identify median required by point metrics. Resolved in draft: separately fit τ=0.50 with selected configuration on fit+tune, no point-metric tuning/conformal shift.

P2: OLS residual degrees of freedom and short-history interpolation unspecified. Resolved in draft: w1/w2 conventions and exact interpolation grid, no extrapolation; interpretation as missing information retained.

P2: Hash outcome blindness described as independence. Resolved in draft prose: outcome-blind deterministic proxy; stochastic target independence remains assumption and cannot be inferred from fixed hash.

Pre-lock: MC precision, importance degeneracy, and bootstrap stability tolerances not validated. Proposed numerical rules added; empirical acceptance remains DEFERRED. No draft wording upgraded to scientific validation.

## Independently checked mathematics

Joint Gaussian means/covariance blocks; latent-effect conditioning; full sensor-only θ update proportional to p(z*|a*,θ)p(θ|Dfit); one RUL response per engine; score width+20×miss distance; bootstrap-t interval direction and lower-tail p-value; conformal rank/nonshrinking/support; Wilson90/100 and sample planning counts. No algebraic inconsistency found.

## Original input identities

- docs/02: 5009DD6C04512D15F117904BB18E3795232715D974751A0E4DA22350BA130A86
- docs/03: CA2F407AB13709ADE2F3C8625E42754C8F8EF12B748BF545C391629CAC5491ED
- docs/04: C1AE4E4920B153D2781CA0E76F91E53DFA6D2F0CAC160069D919CBE05A078DB8
- docs/05: CD52AB07FC44088368EDAD6D4054BA3790787413C022BFF9C1AFE2E09563B143
- docs/06: 83B79DE560054C59FE7AEEFA378E2AFDF143C2E7B2CE6B24331EA8E984BFCD14

Original inputs are preserved as separate Markdown files in logs/methodology_audit_inputs/; logs/methodology_audit_inputs.json records their identities and SHA-256 hashes. Final revised documents have different hashes recorded by the delivery manifest. Audit findings do not certify posterior sampling, exchangeability, identifiability, runtime, or empirical superiority. Lead acceptance is acceptance of completed review and specified repairs, not acceptance of the eventual model.
