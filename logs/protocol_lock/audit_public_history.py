from pathlib import Path
import subprocess,json,re,hashlib,datetime
R=Path.cwd()
def git(*a):return subprocess.check_output(['git',*a])
objects=git('rev-list','--objects','--all').decode('utf8').splitlines()
entries=[line.split(' ',1) for line in objects]
meta=git('cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)',) if False else subprocess.run(['git','cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)'],input=('\n'.join(x[0] for x in entries)+'\n').encode(),stdout=subprocess.PIPE,check=True).stdout.decode().splitlines()
info={x.split()[0]:(x.split()[1],int(x.split()[2])) for x in meta}
forbidden=re.compile(r'(^|/)(?:NASA_CMAPSS_original\.zip|CMAPSSData\.zip|train_FD00[1-4]\.txt|test_FD00[1-4]\.txt|RUL_FD00[1-4]\.txt|\.env(?:\..*)?|credentials(?:\..*)?|id_rsa|id_ed25519)$',re.I)
patterns={'AWS_ACCESS_KEY':re.compile(rb'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b'),'GITHUB_TOKEN':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b'),'OPENAI_KEY':re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}'),'GOOGLE_API_KEY':re.compile(rb'\bAIza[0-9A-Za-z_-]{35}\b'),'PRIVATE_KEY':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')}
paths=[];secret=[];scanned=0;binary=0;oversize=0
# Batch-fetch all candidate text-sized history blobs; never read local raw archives or archive members.
blobs=[(x[0],x[1] if len(x)>1 else None) for x in entries if info[x[0]][0]=='blob']
for oid,path in blobs:
    if path and forbidden.search(path):paths.append({'path':path,'object':oid})
    if info[oid][1]>5*1024*1024:oversize+=1;continue
    payload=git('cat-file','blob',oid)
    if b'\0' in payload[:8192]:binary+=1;continue
    scanned+=1
    for label,pat in patterns.items():
        if pat.search(payload):secret.append({'path':path,'object':oid,'type':label})
result={'audit_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head_before_G3':git('rev-parse','HEAD').decode().strip(),'scope':'All reachable Git history: filename audit plus concrete credential/private-key signature scan of text-sized blobs; no secret values printed. No public release of raw/protected inputs. This bounded scan is not a proof of absence of every possible secret.','reachable_blob_count':len(blobs),'text_blobs_scanned':scanned,'binary_blobs_skipped_for_secret_patterns':binary,'over_5MiB_blobs_skipped_for_secret_patterns':oversize,'forbidden_path_findings':paths,'credential_pattern_findings':secret,'status':'PASS' if not paths and not secret else 'FAIL','history_identity_sha256':hashlib.sha256(('\n'.join(objects)+'\n').encode()).hexdigest(),'repository_visibility':'PUBLIC; verified through authenticated gh repo view','scientific_publication_authorized':False,'raw_dataset_redistribution_rights':'unresolved; raw dataset/protected members remain ignored and unpublished'}
(R/'logs/protocol_lock/public_history_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2));assert result['status']=='PASS'