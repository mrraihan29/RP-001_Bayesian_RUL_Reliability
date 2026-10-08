from pathlib import Path
import subprocess,re,json,datetime,hashlib
R=Path.cwd()
def git(*a):return subprocess.check_output(['git',*a])
paths=git('diff','--cached','--name-only').decode().splitlines()
forbidden=re.compile(r'(^|/)(?:NASA_CMAPSS_original\.zip|CMAPSSData\.zip|train_FD00[1-4]\.txt|test_FD00[1-4]\.txt|RUL_FD00[1-4]\.txt|\.env(?:\..*)?|credentials(?:\..*)?|id_rsa|id_ed25519)$',re.I)
patterns={'AWS_ACCESS_KEY':re.compile(rb'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b'),'GITHUB_TOKEN':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b'),'OPENAI_KEY':re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}'),'GOOGLE_API_KEY':re.compile(rb'\bAIza[0-9A-Za-z_-]{35}\b'),'PRIVATE_KEY':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')}
findings=[];files=[]
for p in paths:
    if forbidden.search(p):findings.append({'path':p,'type':'forbidden-path'})
    b=git('show',':'+p)
    for label,pat in patterns.items():
        if pat.search(b):findings.append({'path':p,'type':label})
    assert b==(R/p).read_bytes(),p
    files.append({'path':p,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
result={'scope':'All staged files; filenames and concrete credential/private-key signatures; no secret values printed. Bounded scan, not proof against every possible secret.','audited_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS' if not findings else 'FAIL','files_checked':len(files),'findings':findings,'staged_files':files,'historical_scan':'logs/protocol_lock/public_history_audit.json','raw_dataset_redistribution_authorized':False}
(R/'logs/protocol_lock/staged_public_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':result['status'],'files_checked':len(files),'findings':findings},indent=2));assert not findings
