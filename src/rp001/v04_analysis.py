"""Lead analysis of prespecified v0.4 fits. No scientific choice from scores."""
from dataclasses import replace
import json,time
from itertools import combinations
import numpy as np
import arviz as az
from scipy.stats import norm
from .data import ROOT,load_training,manifest,make_dataset,LandmarkData
from .model import covariance
from .prediction import mixture_quantile
from .pilot import predictive_checks
from .model import flatten_parameters
from .v04_model import draw_prior
from .v04_predict import arrays,sensor_terms
from .v04_precision import estimate_mixture_quantile_mcse
from .v04_common import PLAN,provenance,write,sha
from .v04_inference import _wilson_summary
from .metrics import interval_score,calibrate
DIR=ROOT/'experiments/v0.4/fits'
OUT=ROOT/'experiments/v0.4/analysis'

def load_data(path,sensor=False):
    d=np.load(path);return LandmarkData(d['a'],d['z'],None if sensor else d['y'],d['ids'],d['B'],str(path))

def raw_quantiles(idata,data,error='normal',reweight=True):
    p=arrays(idata);lz,mu,var=sensor_terms(p,data);sr=p['sigma_r']
    result=[]
    for i,engine in enumerate(data.ids):
        lw=lz[:,i] if reweight else np.zeros(len(lz));w=np.exp(lw-lw.max());w=w/w.sum()
        result.append(dict(engine=int(engine),quantiles=[mixture_quantile(mu[:,i],var[:,i],w,q,error,sr) for q in (.05,.5,.95)],weight_ess=float(1/(w@w))))
    return result

def precision(idata,data,reweight=True,batches=(250,500),error='normal'):
    p=arrays(idata);lz,mu,var=sensor_terms(p,data);chains=int(idata.posterior.sizes['chain']);draws=int(idata.posterior.sizes['draw']);out=[]
    for i,engine in enumerate(data.ids):
        lw=lz[:,i].reshape(chains,draws) if reweight else np.zeros((chains,draws))
        for q in PLAN['precision']['quantiles']:
            r=estimate_mixture_quantile_mcse(mu[:,i].reshape(chains,draws),var[:,i].reshape(chains,draws),lw,q,tail_probability=PLAN['precision']['upper_mcse_tail_probability'],batch_sizes=batches,error=error,sigma_r=p['sigma_r'].reshape(chains,draws))
            r['engine']=int(engine)
            r['gate_pass']=bool(r['weight_ess']>=1000 and all(x['approximate_upper_quantile_rul_mcse'] is not None and x['approximate_upper_quantile_rul_mcse']<=.5 and x['influence_ess'] is not None and x['influence_ess']>=400 for x in r['batch_size_results']))
            out.append(r)
    return out

def prior_analysis():
    policies={};draws0=None
    for index,name in enumerate(PLAN['prior_predictive']['policies']):
        prior=dict(PLAN['prior']);scale=1.5 if name=='broader1p5' else 1.
        if name=='historical_v03':
            prior.update(beta_sd=[1.,.75],gamma_sd=.5,Gamma_sd=[1.,.5],tau_sd=.5,sigma_z_sd=.5,sigma_r_sd=.5)
        draws=draw_prior(12000,49001+index,prior,scale)
        if name=='anchored_v04': draws0=draws
        rng=np.random.default_rng(49101+index);a=np.array([[1.,np.log(c/100)] for c in (30,100,250)]);ys=[];sensor=[]
        for p in draws:
            g=rng.multivariate_normal(np.zeros(2),covariance(p),3)+a@p['Gamma'].T
            ys.append(a@p['beta']+g@p['gamma']+rng.normal(0,p['sigma_r'],3))
            sensor.append(g[:,0]+rng.normal(0,p['sigma_z'],3))
        ys=np.asarray(ys);x=a[:,1]
        gs=prior['gamma_sd']*scale;G=np.asarray(prior['Gamma_sd'])*scale;ts=prior['tau_sd']*scale;ss=prior['sigma_r_sd']*scale;bs=np.asarray(prior['beta_sd'])*scale
        analytic=bs[0]**2+bs[1]**2*x**2+2*gs**2*(G[0]**2+G[1]**2*x**2+ts**2)+ss**2
        policies[name]=dict(ages=[30,100,250],draws=12000,seed=49001+index,log_rul_mean=ys.mean(0).tolist(),log_rul_variance=ys.var(0,ddof=1).tolist(),log_rul_mean_mcse=(ys.std(0,ddof=1)/np.sqrt(len(ys))).tolist(),log_rul_variance_mcse=np.sqrt(np.maximum(0,np.mean((ys-ys.mean(0))**4,axis=0)-(len(ys)-3)/(len(ys)-1)*ys.var(0,ddof=1)**2)/len(ys)).tolist(),analytic_log_rul_variance=analytic.tolist(),rul_quantiles=np.exp(np.quantile(ys,[.01,.05,.5,.95,.99],axis=0)).tolist(),prob_lt1=np.mean(ys<0,axis=0).tolist(),prob_gt1000=np.mean(ys>np.log(1000),axis=0).tolist(),prob_gt5000=np.mean(ys>np.log(5000),axis=0).tolist(),sensor_endpoint_variance=np.var(sensor,axis=0,ddof=1).tolist(),analytic_sensor_endpoint_variance=(G[0]**2+G[1]**2*x**2+ts**2+(prior['sigma_z_sd']*scale)**2).tolist())
    write(OUT/'prior_predictive.json',dict(provenance=provenance(),policies=policies))
    return draws0

def main():
    OUT.mkdir(parents=True,exist_ok=True);start=time.perf_counter();cpu=time.process_time();prov=provenance()
    if any(OUT.iterdir()): raise FileExistsError('Preserve all partial/completed analysis; new repair identity required')
    analysis_record=ROOT/'experiments/v0.4/registry/v04_lead_analysis.json'
    if analysis_record.exists(): raise FileExistsError('Preserve analysis registry')
    write(analysis_record,dict(prov,run_id='v04_lead_analysis',status='running'))
    records={r['run_id']:json.loads((ROOT/'experiments/v0.4/registry'/f"{r['run_id']}.json").read_text()) for r in PLAN['runs']}
    preparation_failures=[]
    for key,record in list(records.items()):
        repair=ROOT/'experiments/v0.4/registry'/f'{key}_infra1.json'
        if record['status']=='failed' and repair.exists():
            resumed=json.loads(repair.read_text())
            assert resumed['infrastructure_repair_of']==key and resumed['configuration']==record['configuration'] and record['artifacts_sha256']=={}
            preparation_failures.append(record);records[key]=resumed
    missing=[k for k,r in records.items() if r['status']!='completed']
    prior_draws=prior_analysis()
    prior_sd={k:np.std(np.asarray([p[k] for p in prior_draws]).reshape(12000,-1),axis=0,ddof=1) for k in prior_draws[0]}
    recovered=[]
    for cfg in PLAN['runs']:
        record=records[cfg['run_id']];name=record['run_id']
        if record['status']!='completed': continue
        idata=az.from_netcdf(DIR/f'{name}.nc');pa=arrays(idata);names=[];parts=[];info=[]
        for key in ('beta','gamma','Gamma','tau','r_g','sigma_z','sigma_r','rho'):
            arr=pa[key].reshape(len(pa['rho']),-1);parts.append(arr)
            for j in range(arr.shape[1]):
                label=f'{key}[{j}]';names.append(label);scale=cfg.get('prior_scale',1.) if key in ('beta','gamma','Gamma','tau','sigma_z','sigma_r') else 1.;psd=float(prior_sd[key][j]*scale);fixed=(key=='rho' and cfg.get('rho_zero',False));info.append(dict(parameter=label,posterior_sd=float(arr[:,j].std(ddof=1)),prior_sd=0. if fixed else psd,sd_ratio=None if fixed else float(arr[:,j].std(ddof=1)/psd),policy='fixed/not-data-contraction' if fixed else 'matching-prior-reference'))
        corr=np.corrcoef(np.column_stack(parts),rowvar=False)
        couplings=sorted([dict(a=names[i],b=names[j],correlation=float(corr[i,j])) for i in range(len(names)) for j in range(i+1,len(names)) if np.isfinite(corr[i,j])],key=lambda x:abs(x['correlation']),reverse=True)[:10]
        detail=dict(run_id=name,posterior_evidence_accepted=record['diagnostics']['acceptance']=='PASS',unaccepted_scope='Raw diagnostic summaries retained; no calibrated posterior/coverage conclusion from a failed convergence fit',diagnostics=record.get('diagnostics'),recovery=record.get('recovery'),prior_posterior_sd=info,strongest_correlations=couplings)
        if cfg['kind']=='synthetic':
            assessment=load_data(DIR/f'{name}_assessment.npz');pred=raw_quantiles(idata,replace(assessment,y=None));Q=np.asarray([p['quantiles'] for p in pred]);y=np.exp(assessment.y);covered=(y>=Q[:,0])&(y<=Q[:,2]);scores=interval_score(y,Q[:,0],Q[:,2]);detail['predictive_assessment']=dict(n=len(y),coverage=_wilson_summary(int(covered.sum()),len(y)),median_rmse=float(np.sqrt(np.mean((y-Q[:,1])**2))),mean_interval_score=float(scores.mean()),engine_predictions=pred,truth_rul=y.tolist(),scope='Independent synthetic engines; fixed-truth/selected age law; predictive adequacy diagnostic only')
            recovered.append(detail)
        write(OUT/f'{name}_checks.json',detail)
    principal_names=[f'v04_main_r{i}' for i in (1,2,3)]
    precision_summary=None
    if all(records[n]['status']=='completed' for n in principal_names):
        reps=[az.from_netcdf(DIR/f'{n}.nc') for n in principal_names]
        pre=dict(np.load(DIR/'v04_main_r1_pre.npz'));cal=make_dataset(load_training(),pre,('calibration',),allow_calibration=True);sensor=replace(cal,y=None)
        assert len(sensor.ids)==25 and len(set(sensor.ids))==25 and {11,61,86}.issubset(set(sensor.ids))
        expected_ids=sorted(r['engine'] for r in manifest() if r['role']=='calibration' and r['eligible_alive'])
        assert sorted(sensor.ids.tolist())==expected_ids
        np.savez(OUT/'principal_calibration_inputs.npz',a=cal.a,z=cal.z,y=cal.y,ids=cal.ids,B=cal.B,**pre)
        for index,name in enumerate(principal_names):
            other=dict(np.load(DIR/f'{name}_pre.npz'))
            for key in pre: np.testing.assert_array_equal(pre[key],other[key])
        pooled=az.concat(*reps,dim='chain');pooled.posterior=pooled.posterior.assign_coords(chain=np.arange(12))
        rs=precision(pooled,sensor);assert len(rs)==75 and len({(r['engine'],r['probability']) for r in rs})==75 and {r['engine'] for r in rs}==set(expected_ids);write(OUT/'principal_precision_all25.json',dict(provenance=prov,results=rs))
        rep_results=[precision(rep,sensor) for rep in reps];write(OUT/'principal_replication_precision.json',dict(provenance=prov,results=rep_results))
        comparisons=[];zcut=norm.ppf(1-.05/(2*225))
        for a,b in combinations(range(3),2):
            for ra,rb in zip(rep_results[a],rep_results[b]):
                ca=max(x['quantile_rul_mcse'] for x in ra['batch_size_results']);cb=max(x['quantile_rul_mcse'] for x in rb['batch_size_results']);diff=abs(ra['quantile_rul']-rb['quantile_rul']);se=np.hypot(ca,cb)
                comparisons.append(dict(replications=[a+1,b+1],engine=ra['engine'],probability=ra['probability'],difference=diff,combined_mcse=float(se),z=float(diff/se) if np.isfinite(se) and se>0 else None,compatible=bool(np.isfinite(se) and se>0 and diff<=zcut*se)))
        oracles=[];ozcut=norm.ppf(1-.05/(2*9))
        for engine in (11,61,86):
            name=f'v04_oracle_e{engine}'
            if records[name]['status']!='completed': continue
            oi=az.from_netcdf(DIR/f'{name}.nc');one=load_data(DIR/f'{name}_extra.npz',True);assert one.ids.tolist()==[engine] and records[name]['configuration']['engine']==engine;rr=precision(oi,one,reweight=False)
            for a,b in zip([r for r in rs if r['engine']==engine],rr):
                ca=max(x['quantile_rul_mcse'] for x in a['batch_size_results']);cb=max(x['quantile_rul_mcse'] for x in b['batch_size_results']);diff=abs(a['quantile_rul']-b['quantile_rul']);se=np.hypot(ca,cb)
                oracles.append(dict(engine=engine,probability=a['probability'],importance_quantile=a['quantile_rul'],oracle_quantile=b['quantile_rul'],combined_mcse=float(se),difference=diff,z=float(diff/se) if np.isfinite(se) and se>0 else None,compatible=bool(np.isfinite(se) and se>0 and diff<=ozcut*se),oracle_precision=b,oracle_mcmc=records[name]['diagnostics']['acceptance']))
        maxmc=max(float('inf') if b['approximate_upper_quantile_rul_mcse'] is None else b['approximate_upper_quantile_rul_mcse'] for r in rs for b in r['batch_size_results'])
        passes=all(r['gate_pass'] for r in rs) and all(r['compatible'] for r in comparisons) and len(oracles)==9 and all(r['compatible'] and r['oracle_mcmc']=='PASS' for r in oracles) and all(records[n]['diagnostics']['acceptance']=='PASS' for n in principal_names)
        validation_path=ROOT/'experiments/v0.4/precision/v04_precision_mcse_validation.json';validation=json.loads(validation_path.read_text());vr=json.loads((ROOT/'experiments/v0.4/registry/v04_precision_validation.json').read_text());assert vr['frozen_plan_sha256']==prov['plan_sha256'] and vr['shared_v04_common_provenance']['plan_sha256']==prov['plan_sha256'];validation_pass=all(g['plan_criterion_checks']['both'] for g in validation['summary']['groups']);recovery=json.loads((ROOT/'experiments/v0.4/registry/v04_precision_validation_storage_recovery.json').read_text());assert recovery['status']=='completed' and recovery['result_artifact']['sha256']==sha(validation_path);assert len(validation['raw_records'])==600 and len(validation['summary']['groups'])==18;assert validation['raw_records']==vr['partial_raw_records'];component_pass=passes;passes=passes and validation_pass
        precision_summary=dict(mcse_estimator_validation_pass=validation_pass,component_mcmc_prediction_gate='PASS' if component_pass else 'FAIL',n_engines=25,n_quantiles=75,n_draws=96000,max_upper_mcse_cycles=maxmc,min_weight_ess=min(r['weight_ess'] for r in rs),min_influence_ess=min(b['influence_ess'] for r in rs for b in r['batch_size_results']),numerical_gate='PASS' if passes else 'FAIL',replication_z_threshold=float(zcut),oracle_z_threshold=float(ozcut),replication_comparisons=comparisons,oracle_comparisons=oracles)
        write(OUT/'precision_summary.json',precision_summary)
        Q=np.array([[r['quantile_rul'] for r in rs if r['engine']==e] for e in cal.ids]);posthoc=calibrate(np.exp(cal.y),Q[:,0],Q[:,2]);write(OUT/'principal_posthoc_calibration.json',dict(correction=float(posthoc),rank=24,n=25,secondary_only=True,development_calibration_exposed=True))
        # Prior sensitivity is prediction sensitivity only, not calibration-score search.
        sensitivity={}
        for name in ('v04_broader','v04_rho_zero','v04_contamination'):
            if records[name]['status']=='completed': sensitivity[name]=raw_quantiles(az.from_netcdf(DIR/f'{name}.nc'),sensor,error=records[name]['configuration'].get('error','normal'))
        write(OUT/'sensitivity_prediction_maps.json',dict(principal=[dict(engine=e,quantiles=[r['quantile_rul'] for r in rs if r['engine']==e]) for e in cal.ids.tolist()],alternatives=sensitivity,score_selection_performed=False))
        train=load_data(DIR/'v04_main_r1_data.npz');ppc=predictive_checks(train,flatten_parameters(reps[0]),51001)
        write(OUT/'posterior_predictive.json',ppc)
        # Historical failure remains; this alternate estimator is retrospective diagnostic only.
        old=az.from_netcdf(ROOT/'results/pilot/refit.nc');retro=precision(old,sensor)
        write(OUT/'v03_retrospective_precision.json',dict(old_reported_max_mcse=.728972,old_failure_retained=True,results=retro))
    pipeline=[]
    for cfg in [r for r in PLAN['runs'] if r['kind']=='pipeline']:
        record=records[cfg['run_id']];name=record['run_id'];row=dict(run_id=name,status=record['status'],configuration=cfg,stage_metadata=record.get('pipeline_metadata'),cqr=record.get('cqr'))
        if record['status']=='completed':
            anchor=load_data(DIR/f'{name}_anchors.npz',True);row['bayesian_anchors']=raw_quantiles(az.from_netcdf(DIR/f'{name}.nc'),anchor)
            calibration=load_data(DIR/f'{name}_calibration.npz');cal_predictions=raw_quantiles(az.from_netcdf(DIR/f'{name}.nc'),replace(calibration,y=None));CQ=np.asarray([p['quantiles'] for p in cal_predictions]);row['bayesian_posthoc_correction']=float(calibrate(np.exp(calibration.y),CQ[:,0],CQ[:,2]));row['calibration_distinct_n']=len(set(calibration.ids));row['calibration_score_rows']=len(calibration.ids)
            cp=DIR/f'{name}_cqr_anchors.npz'
            if cp.exists(): row['cqr_anchors']={k:v.tolist() for k,v in dict(np.load(cp)).items()}
        pipeline.append(row)
    write(OUT/'pipeline_variation.json',dict(provenance=prov,runs=pipeline,purpose=PLAN['pipeline']['purpose']))
    regimes={}
    for regime in PLAN['synthetic']['regimes']:
        rows=[r for r in recovered if records[r['run_id']]['configuration']['regime']==regime]
        params={}
        if rows:
            for j in range(len(rows[0]['recovery']['parameters'])):
                v=[r['recovery']['parameters'][j] for r in rows];params[v[0]['parameter']]=dict(covered95=_wilson_summary(sum(p['truth_in95'] for p in v),len(v)),mean_bias=float(np.mean([p['mean']-p['truth'] for p in v])),max_abs_z=max(abs(p['standardized_mean_error']) for p in v))
        regimes[regime]=dict(n_completed=len(rows),n_mcmc_pass=sum(r['diagnostics']['acceptance']=='PASS' for r in rows),parameter_summary=params,n_predictive=sum(r['predictive_assessment']['n'] for r in rows),predictive_covered=sum(r['predictive_assessment']['coverage']['successes'] for r in rows))
    summary=dict(provenance=prov,failed_run_ids=missing,precision=precision_summary,synthetic=regimes,n_mcmc_fits=len(records),preparation_failures=[r['run_id'] for r in preparation_failures],preparation_cpu_seconds=sum(r['cpu_seconds'] for r in preparation_failures),n_mcmc_completed=sum(r['status']=='completed' for r in records.values()),mcmc_failed_diagnostics=[n for n,r in records.items() if r.get('diagnostics',{}).get('acceptance')=='FAIL'],cpu_fit_seconds=sum(r['cpu_seconds'] for r in records.values()),wall_fit_seconds=sum(r['wall_seconds'] for r in records.values()),analysis_wall_seconds=time.perf_counter()-start,analysis_cpu_seconds=time.process_time()-cpu)
    write(OUT/'summary.json',summary);write(ROOT/'experiments/v0.4/registry/v04_lead_analysis.json',dict(prov,run_id='v04_lead_analysis',status='completed',cpu_seconds=summary['analysis_cpu_seconds'],wall_seconds=summary['analysis_wall_seconds'],calibration_inputs_sha256=sha(OUT/'principal_calibration_inputs.npz'),result_sha256=sha(OUT/'summary.json')))
    print(json.dumps({k:v for k,v in summary.items() if k not in ('provenance','precision','synthetic')},indent=2),flush=True)
if __name__=='__main__':main()