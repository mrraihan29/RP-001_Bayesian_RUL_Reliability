from pathlib import Path
import json
import subprocess
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"research/environment_manifest.json"
env=json.loads(path.read_text(encoding="utf-8"))
git=env["hardware"]["git_path"]
review_commit=subprocess.check_output([git,"-C",str(ROOT),"rev-parse","HEAD"],text=True).strip()
env["git_commit"]=review_commit
env["git_dirty"]=True
env["snapshot_note"]="References the reviewed source commit before final provenance-only commit; working bytes preserved with .gitattributes. Research environment remains unvalidated."
path.write_text(json.dumps(env,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
attr=ROOT/".gitattributes"
if attr.exists():
    raise FileExistsError("Review existing attributes before modification.")
attr.write_text("# Preserve exact bytes for SHA-256 provenance on every platform.\n* -text\n",encoding="utf-8")
print(json.dumps({"review_source_commit":review_commit,"environment_approved":False,"byte_preserving_git_attributes":True}))
