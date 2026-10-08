from pathlib import Path
import hashlib, importlib.metadata, inspect, json, platform, subprocess, sys
import numpy as np, scipy, pymc as pm, arviz as az, nutpie, psutil
ROOT=Path(__file__).resolve().parents[2]
def main():
    packages={d.metadata["Name"]:d.version for d in importlib.metadata.distributions()}
    stable={"python":platform.python_version(),"implementation":platform.python_implementation(),
            "platform":platform.platform(),"packages":dict(sorted(packages.items(),key=lambda x:x[0].lower())),
            "float_dtype":"float64","sampler":"nutpie NUTS","blas_threads":1}
    fingerprint=hashlib.sha256(json.dumps(stable,sort_keys=True).encode()).hexdigest()
    result=dict(stable,fingerprint=fingerprint,executable=sys.executable,
                total_ram_gib=psutil.virtual_memory().total/2**30,
                cpu_logical=psutil.cpu_count(),cpu_physical=psutil.cpu_count(logical=False),
                package_import_smoke="PASS",sample_signature=str(inspect.signature(pm.sample)),
                nutpie_signature=str(inspect.signature(nutpie.sample)),colab_used=False,
                official_test_access=False,dependency_install_report="logs/pilot_install_report.json")
    path=ROOT/"logs/pilot_environment.json"
    if path.exists(): raise FileExistsError("Environment fingerprint already captured")
    path.write_text(json.dumps(result,indent=2)+"\n")
    lock=subprocess.check_output([sys.executable,"-m","pip","freeze","--all"],text=True)
    (ROOT/"configs/requirements-pilot.lock").write_text(lock)
    print(json.dumps({"environment_fingerprint":fingerprint,"python":stable["python"],
                      "pymc":pm.__version__,"arviz":az.__version__,"nutpie":nutpie.__version__,
                      "import_smoke":"PASS","packages":len(packages)}))
if __name__=="__main__": main()
