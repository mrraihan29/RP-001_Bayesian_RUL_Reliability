from pathlib import Path
import json,hashlib,csv,io
R=Path('.');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
map_path=R/'research/v0.5/baseline_alias_archive_map.json';maps=json.loads(map_path.read_text(encoding='utf8'))
for path in ['research/claim_ledger.csv','research/artifact_map.csv','README.md','GITHUB_REVIEW.md']:
    dst=R/'research/v0.5/baseline_current_aliases'/path;dst.parent.mkdir(parents=True,exist_ok=True)
    assert not dst.exists();dst.write_bytes((R/path).read_bytes());maps[path]=dict(archive=str(dst).replace('\\','/'),sha256=sha(dst))
map_path.write_text(json.dumps(maps,indent=2)+'\n',encoding='utf8')
(R/'README.md').write_text("""# RP-001 — Bayesian RUL Reliability

**READY FOR OWNER LOCK REVIEW — bounded pre-lock resolution v0.5. Protocol remains PROTOCOL_DRAFTED.**

Start with the [Pre-Lock Resolution Memo](docs/v0.5/01_prelock_resolution_memo.md), [Proposed Locked Analysis Contract](docs/v0.5/02_proposed_locked_analysis_contract.md), and [evidence index](docs/v0.5/README.md). One equivalent-posterior high-rho investigation PASS; original FAIL retained. Direct mathematical preflight and 59 tests PASS. Proposed primary interpretation is descriptive comparison of complete stored predictions on the exact finite FD001 benchmark; no population superiority or fixed practical margin.

Research Owners Raihan × Rei retain final lock and data-access authorization. Official test sensors/labels, confirmatory evaluation, and fallback remain unauthorized and unperformed. Local CPU; no Colab/GPU or additional spending.

[Mathematical assessment](docs/v0.5/03_mathematical_validity.md), [compute/custody and unresolved requirements](docs/v0.5/04_compute_reproducibility.md), [risk matrix](research/v0.5/blocker_disposition.json), [handoff](docs/v0.5/research_lead_handoff.json), [delivery receipt](logs/v0.5/delivery_receipt.json).

Historical [v0.4 package](docs/v0.4/README.md) is preserved at the owner-reviewed scientific commit61b4c2c63cbad6c1b9bd99168e33d1367aa180bc. [v0.3](docs/v0.3/README.md), earlier scientific source/results, and failures remain unchanged. Current alias updates have exact byte archives under research/v0.5/baseline_current_aliases. The first71 of73 experiment-ledger records remain unchanged.

Private GitHub is for owner review. Raw training/NASA archives/official test members are excluded. Thirty-three historical ignored payloads remain local and manifest-bound; complete historical replay is not certified from GitHub alone. No novelty, public redistribution clearance, or real-engine reliability claim.
""",encoding='utf8')
(R/'GITHUB_REVIEW.md').write_text("""# RP-001 — Web Review

Repository private untuk owner review. Versi terbaru: **v0.5 — READY FOR OWNER LOCK REVIEW**, dengan status **PROTOCOL_DRAFTED**.

Mulai dari [Pre-Lock Resolution Memo](docs/v0.5/01_prelock_resolution_memo.md), [Proposed Locked Analysis Contract](docs/v0.5/02_proposed_locked_analysis_contract.md), dan [indeks evidence](docs/v0.5/README.md). Satu investigasi bounded selesai; kegagalan lama tetap tersimpan. Scientific review tidak memberi izin final lock, official sensors/labels, confirmatory evaluation, atau fallback.

[Receipt v0.5](logs/v0.5/delivery_receipt.json) mengidentifikasi snapshot ilmiah dan fingerprint. Receipt administratif tersimpan pada commit sesudah snapshot itu, sehingga tidak mengklaim memuat hash commit dirinya sendiri.

Baseline yang sudah ditinjau owner adalah61b4c2c63cbad6c1b9bd99168e33d1367aa180bc: [paket v0.4](docs/v0.4/README.md) dan [receipt v0.4 tetap](logs/v0.4/delivery_receipt.json). Source/hasil historis tidak ditimpa. Raw training, arsip NASA, official sensors/labels, dan33payload historis yang dikecualikan dari Git tetap lokal serta manifest-bound. Payload baru v0.4/v0.5 dan laporan ada di repository.
""",encoding='utf8')
# Readability edits only in new reports; no equation/threshold/scientific input altered.
replacements={
'61b4':'61b4', 'seed54103':'seed 54103','4chains':'4 chains','4,000retained':'4,000 retained','2,000warmup':'2,000 warmup','target0.95':'target 0.95','depth12':'depth 12','600second':'600 second','12points':'12 points','25already':'25 already','12x8,000draws':'12 x 8,000 draws','scoreMCSE':'score MCSE','upperMCSE':'upper MCSE','endpoint-upper':'endpoint upper','label-kink':'label kink','before labels':'before labels','no5cycle':'no 5 cycles','0.5cycle':'0.5 cycles','smallcalibration':'small calibration','OnePC':'One PC','physicalcoupling':'physical coupling',
'CPUhour':'CPU hour','process-CPU':'process CPU','minimumBFMI':'minimum BFMI','maximumRhat':'maximum Rhat','tailESS':'tail ESS','bulkESS':'bulk ESS','Rhat':'Rhat','999/4,000unavailable':'999/4,000 unavailable','sigma1.5coverage0.914/one-sided rejection0.112':'sigma 1.5 coverage 0.914 / one-sided rejection 0.112','25cal/13tune':'25 calibration / 13 tuning engines','59tests':'59 tests','no further':'no further',
'100engines':'100 engines','20,631rows':'20,631 rows','26fields':'26 fields','first55fit':'first 55 fit','next15tune':'next 15 tune','last30calibration':'last 30 calibration','Eligible43/13/25':'Eligible 43/13/25','refit56fit+tune':'refit 56 fit+tune','historical100salt':'historical 100 salt','fits43eligible':'fits 43 eligible','fits56eligible':'fits 56 eligible','SD<=1e-8channels':'SD <= 1e-8 channels','C<Tfilter':'C<T filter','min-history':'minimum history','30..250restriction':'30..250 restriction','w1level':'w=1 level','slope/residualSD0':'slope/residual SD=0','SDvector':'SD vector',
'v0.3calibration':'v0.3 calibration','v0.4science':'v0.4 science','each4chainsx8,000retained':'each 4 chains x 8,000 retained','pool12chains/96,000equal':'pool 12 chains/96,000 equal','newdraws':'new draws','12independent':'12 independent','8Gradient':'8 Gradient','200trees':'200 trees','rate{':'rate {','leaf{':'leaf {','depth{':'depth {','4linear':'4 linear','L1alpha':'L1 alpha','endpointPC':'endpoint PC','OLSlevel':'OLS level','OLSslope':'OLS slope','residualSD':'residual SD','30interpolatedPCs':'30 interpolated PCs','meanIS90':'mean IS90','13tune':'13 tune engines','within.5cycle':'within 0.5 cycles','strongerpenalty':'stronger penalty','shallowerdepth/largerleaf/smallerrate':'shallower depth / larger leaf / smaller rate','on56':'on 56','Calibration25':'Calibration 25','rank24expansion':'rank 24 expansion','19.987559cycles':'19.987559 cycles','broader1.5scale':'broader 1.5 scale','GaussianlogR':'Gaussian log R','official90%':'official 90%',
'expected100engine':'expected 100 engine','>=30common':'≥30 common','maxchannel':'max channel','completeNrow':'complete N row','perengine':'per engine','exactN alignment':'exact N alignment','20xmiss':'20 x miss','input,prediction':'input, prediction','all3independent':'all 3 independent','All3independent':'All 3 independent','xNengine x3quantiles':'x N engines x 3 quantiles','three exact':'three exact','3endpoint':'3 endpoint','.5cycle':'0.5 cycles','both250/500batches':'both 250/500 batches','AllNengine x3quantiles':'All N engines x 3 quantiles','score/ranking':'score / ranking',
'8dependent':'8 dependent','CQRwinner':'CQR winner','bootstrap999unavailable':'bootstrap 999 unavailable','v0.3precisionFAIL':'v0.3 precision FAIL','highrho3FAIL':'high-rho3 FAIL','inquiryPASS':'inquiry PASS','noColab':'no Colab','33historical':'33 historical','64package':'64 package','oneCPUhour':'one CPU hour','128MiB':'128 MiB','600wall':'600 wall','CPU seconds':'CPU seconds',
'sigma_z .1/.3/.6':'sigma_z .1/.3/.6','12density':'12 density','48gradient':'48 gradient','step1e-5':'step 1e-5','absolute1e-4':'absolute 1e-4','the original55':'the original 55','fixed4':'fixed 4','full31-dimensional':'full 31-dimensional','posterior2':'posterior 2','lengthn':'length n','magnitude is19':'magnitude is 19','correct rank':'correct rank','both250':'both 250','modelPASS':'model PASS',
}
for f in (R/'docs/v0.5').glob('*.md'):
    if f.name in ('prospective_resolution_plan.md',):continue
    text=f.read_text(encoding='utf8')
    for a,b in replacements.items():text=text.replace(a,b)
    f.write_text(text,encoding='utf8')
# Match frozen precision helper rather than the older descriptive helper.
contract=R/'docs/v0.5/02_proposed_locked_analysis_contract.md'
t=contract.read_text(encoding='utf8').replace('xtol1e-10','xtol=1e-12 (frozen v0.4 precision implementation)')
contract.write_text(t,encoding='utf8')
def append_csv(path,rows):
    fields=next(csv.reader((R/path).read_text(encoding='utf8').splitlines()))
    b=io.StringIO(newline='');w=csv.DictWriter(b,fieldnames=fields);w.writerows(rows)
    with (R/path).open('ab') as f:f.write(b.getvalue().encode('utf8'))
append_csv('research/claim_ledger.csv',[
dict(claim_id='V05-C01',claim='One equivalent-posterior high-rho inquiry passes predefined convergence guards',claim_type='bounded-computational',scope='Same failed-case synthetic data; no universal robustness or principal replacement',evidence_ids='V05-MATH;V05-FIT',status='qualified',caveats='Parameterization and retained/warmup budget changed together; original FAIL retained; physical nuisance ridge persists'),
dict(claim_id='V05-C02',claim='Dependence-preserving posterior numerical score propagation passes saved-draw training demonstration',claim_type='numerical-development',scope='25 exposed calibration endpoints; fixed12x8000posterior',evidence_ids='V05-SCORE;V05-TESTS',status='qualified',caveats='No CQR primary contrast, official endpoints or total-pipeline uncertainty; approximate MCSE'),
dict(claim_id='V05-C03',claim='Restricted complete finite-benchmark contract is ready for owner lock review',claim_type='scientific-disposition',scope='Proposed descriptive stored-prediction comparison with fixed guards',evidence_ids='V05-MEMO;V05-CONTRACT',status='qualified',caveats='Protocol draft; no final owner lock/data/confirmatory authorization'),
dict(claim_id='V05-C04',claim='Bayesian is generally superior or practically equivalent to CQR',claim_type='population-generalization',scope='Population/real-fleet/practical claim',evidence_ids='V05-CONTRACT',status='not-supported',caveats='No official score, defensible practical margin, population inference or unconditional pipeline variance')])
# Map current v05 artifacts; self/receipt added via delivery manifest.
fields=next(csv.reader((R/'research/artifact_map.csv').read_text(encoding='utf8').splitlines()))
rows=[]
for i,f in enumerate(sorted([q for root in ['docs/v0.5','configs/v0.5','experiments/v0.5','logs/v0.5','research/v0.5'] for q in (R/root).rglob('*') if q.is_file() and 'baseline_current_aliases' not in str(q) and '__pycache__' not in str(q)]),1):
    vals=[f'V05-A{i:04d}','bounded-prelock-return',str(f).replace('\\','/'),'','RP001-v0.5-bounded-prelock',sha(f)]
    rows.append(dict(zip(fields,vals)))
append_csv('research/artifact_map.csv',rows)
# Update handoff evidence hashes after readability-only edits.
hpath=R/'docs/v0.5/research_lead_handoff.json';h=json.loads(hpath.read_text(encoding='utf8'))
h['artifact_identity']['sha256_or_version']=sha(R/h['artifact_identity']['path_or_uri'])
for e in h['evidence']:e['sha256']=sha(R/e['location'])
hpath.write_text(json.dumps(h,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(advanced_aliases=len(maps),mapped_new_artifacts=len(rows))))
