# Reproducing the development pilot

Scope: synthetic and official FD001 training only. No test sensors/labels, archive extraction or confirmatory evaluation. A repeated run is exploratory and cannot remove the retained predictive-precision failure. For scientific refinement, first fix a prospective revised precision plan; do not call extra attempts retrospective acceptance.

The retained checkout refuses to overwrite model runs and several analysis outputs. For a complete rerun, use a **separate fresh source-only project** with the same src/tests/configs and scripts, no prior results/pilot payloads and no pilot_selection_freeze.json. Preserve the original evidence checkout. Copy only the exact train_FD001.txt training payload (plus its provenance) into data/raw; no other dataset member is needed. Copy the exact environment metadata as a reference, then verify the actual new environment. Do not represent its old executable path as the new executable.

On the same Windows configuration, create a separate virtual environment with CPython3.12.14 and install configs/requirements-pilot.lock. Keep logs/pilot_install_report.json as historical provenance, not a claim about a fresh installation. Verify dependency consistency and all package versions before using the reference environment fingerprint. A changed platform/lock requires a new fingerprint and backend verification. The canonical fingerprint recipe is in logs/validate_pilot_delivery.py; it uses json.dumps(sort_keys=True) on the seven declared fields, including default JSON separators.

In the fresh source-only project, run these commands in PowerShell (paths are resolved relative to that project):

```powershell
$taskRoot=(Get-Location).Path
$pilotPython=Join-Path $taskRoot '.venv/Scripts/python.exe'
$env:PYTHONPATH=Join-Path $taskRoot 'src'
$cachePath=(Join-Path $taskRoot '.cache/pytensor').Replace('\','/')
$env:PYTENSOR_FLAGS="floatX=float64,cxx=,base_compiledir=$cachePath"
$env:OMP_NUM_THREADS='1'
$env:OPENBLAS_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
& $pilotPython -m pip check
& $pilotPython -m pytest tests/test_pilot_mathematics.py tests/test_backend_serialization.py tests/test_comparators_worker.py tests/test_lead_comparator_and_prediction.py tests/test_lead_data_and_conditioning.py -q
& $pilotPython -m rp001.pilot --run prior
foreach ($runName in @('syn_r0','syn_r05','syn_r09','syn_weak','base','prior_half','prior_double','rho_zero','contamination')) {
  & $pilotPython -m rp001.pilot --run $runName
  if ($LASTEXITCODE -ne 0) { throw "Preserve failure and stop: $runName" }
}
& $pilotPython -m rp001.comparator_pilot
& $pilotPython -m rp001.pilot --run refit
& $pilotPython -m rp001.pilot --run sensor_oracle
& $pilotPython -m rp001.predictive_analysis
& $pilotPython -m rp001.statistical_design
```

The final repaired backend should not reproduce the historical serialization failures. Historical failed attempts remain evidence, not a required rerun failure. These commands do not change the run settings or precision threshold. Compare the resulting diagnostics/quantiles with Monte Carlo uncertainty rather than demanding identical binary NetCDF bytes. Source-only preparation must preserve the same plan/manifest/config hashes. Fingerprint newly generated data, posterior files, environment and code; record dirty state, seeds, timing and any deviations. No final benchmark authorization follows from reproducing this pilot.