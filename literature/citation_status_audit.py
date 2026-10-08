from pathlib import Path
import json, urllib.request, concurrent.futures, datetime
ROOT=Path(__file__).resolve().parents[1]
dois=["10.36001/ijphm.2023.v14i2.3417","10.1016/j.jmsy.2020.11.005","10.1198/016214506000001437","10.1214/20-BA1221","10.65420/sjphrt.v2i3.169","10.1016/j.ress.2026.112763","10.1016/j.engappai.2024.109980","10.1016/j.asej.2026.103992"]
def fetch(doi):
    url="https://api.crossref.org/works/"+doi
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"RP001ResearchReview/0.2"})
        with urllib.request.urlopen(req,timeout=12) as response:
            obj=json.load(response)["message"]
        return {"doi":doi,"source":url,"retrieved_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "title":obj.get("title"),"author":obj.get("author"),"container-title":obj.get("container-title"),
          "published":obj.get("published"),"published-online":obj.get("published-online"),
          "relation":obj.get("relation"),"update-to":obj.get("update-to"),"updated-by":obj.get("updated-by"),
          "abstract":obj.get("abstract"),"license":obj.get("license"),
          "status":"metadata-verified; no assertion of exhaustive retraction-check coverage"}
    except Exception as exc:
        return {"doi":doi,"source":url,"status":"unavailable","error":str(exc)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    output=list(executor.map(fetch,dois))
target=ROOT/"literature/crossref_status_audit.json"
if target.exists(): raise FileExistsError(target)
target.write_text(json.dumps(output,indent=2,ensure_ascii=False),encoding="utf8")
print(json.dumps([{"doi":x["doi"],"title":x.get("title"),"status":x["status"],"update-to":x.get("update-to"),"relation":x.get("relation")} for x in output],indent=2,ensure_ascii=False))
