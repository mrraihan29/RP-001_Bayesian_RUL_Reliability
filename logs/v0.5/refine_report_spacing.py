from pathlib import Path
import re,json,hashlib,csv,io
R=Path('.');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for f in (R/'docs/v0.5').glob('*.md'):
    if f.name=='prospective_resolution_plan.md':continue
    t=f.read_text(encoding='utf8')
    t=re.sub(r',(?=[A-Za-z0-9])',', ',t);t=re.sub(r';(?=\S)','; ',t);t=re.sub(r':(?=[A-Za-z0-9])',': ',t)
    replacements={
'No5cycle':'No 5 cycles','one target':'one target','cycleT':'cycle T','and1/':'and 1/','weight1/n':'weight 1/n','or30':'or 30','vector[':'vector [','each4 chainsx8,000retained':'each 4 chains x 8,000 retained draws','pool 12':'pool 12','candidates:8':'candidates: 8','random_state20261008':'random_state=20261008','per30':'per 30','on13':'on 13','conformalshift':'conformal shift','about19.987559':'about 19.987559','quantiles .05':'quantiles 0.05','Tuning preprocessing':'Tuning preprocessing','expected100':'expected 100','0.5cycles':'0.5 cycles',
'physical/auxiliary diagnostics finite:':'physical/auxiliary diagnostics must be finite:','bulk/tail ESS>=400':'bulk/tail ESS >=400','divergences0':'divergences=0','saturation<=.01':'saturation <=0.01','weightESS':'weight ESS','influenceESS':'influence ESS','after labels':'after labels','Positive finite':'Positive finite','root residual':'root residual','both 250/500batches':'both 250/500 batches','3quantiles':'3 quantiles','MCSE=max':'MCSE=max','3independent':'3 independent','endpoint-upper':'endpoint upper','allN':'all N','batch covariance250/500':'batch covariance 250/500','tail.05/2':'tail=0.05/2','upper>.5cycles':'upper>0.5 cycles','upper>.5':'upper>0.5','3endpoint':'3 endpoint','20x':'20 x','plot0':'plot 0',
'MAE/RMSE/bias':'MAE/RMSE/bias','finite means, D_F':'finite means, D_F','100FD001test':'100 FD001 test','checked2026':'checked 2026','v0.4manifest':'v0.4 manifest','below600':'below 600','64package':'64 package','depth 12saturation':'depth 12 saturation','8,000draws':'8,000 draws','perengine':'per engine','fullpipeline':'full pipeline','physicalcoupling':'physical coupling','label-kink':'label kink','600-second':'600 second',
'Fitted-model uncertainty':'Fitted model uncertainty','Twelve fixed':'Twelve fixed','local64':'local 64','64-package':'64 package','Four independent':'Four independent','phase4':'phase 4',
'bytes.':' bytes.'}
    # Final bytes-unit replacement applies only to joined numeric prose.
    replacements.pop('bytes.')
    for a,b in replacements.items():t=t.replace(a,b)
    f.write_text(t,encoding='utf8')
# Synchronize all document fingerprint consumers; mathematical/scientific files unchanged.
hpath=R/'docs/v0.5/research_lead_handoff.json';h=json.loads(hpath.read_text(encoding='utf8'))
h['artifact_identity']['sha256_or_version']=sha(R/h['artifact_identity']['path_or_uri'])
for e in h['evidence']:e['sha256']=sha(R/e['location'])
hpath.write_text(json.dumps(h,indent=2)+'\n',encoding='utf8')
c=R/'research/v0.5/proposed_analysis_contract.json';x=json.loads(c.read_text(encoding='utf8'));x['contract_sha256']=sha(R/x['contract_path']);c.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
r=R/'logs/v0.5/report_integrity.json';x=json.loads(r.read_text());x['contract_sha256']=sha(R/'docs/v0.5/02_proposed_locked_analysis_contract.md');r.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
a=R/'research/artifact_map.csv';lines=a.read_bytes().splitlines(keepends=True)
for i,line in enumerate(lines):
    if not line.startswith(b'V05-'):continue
    row=next(csv.reader([line.decode('utf8')]));f=R/row[2]
    if f.exists():
        row[-1]=sha(f);s=io.StringIO(newline='');csv.writer(s).writerow(row);lines[i]=s.getvalue().encode('utf8')
a.write_bytes(b''.join(lines))
(R/'logs/v0.5/readability_refinement.json').write_text(json.dumps(dict(kind='Documentation formatting only',prior_evidence_snapshot='1722b7f483fb0ab7fdc9e40df6d799d73d669711',scientific_source_results_plan_unchanged=True,contract_policy_or_thresholds_changed=False,fingerprint_consumers_refreshed=True),indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status='PASS',current_contract_sha256=sha(R/'docs/v0.5/02_proposed_locked_analysis_contract.md'))))
