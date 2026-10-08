"""Fixed saved-draw demonstration of joint score numerical uncertainty."""
import json, time
from dataclasses import replace
import numpy as np
import arviz as az
from scipy.stats import norm, chi2
from .data import ROOT
from .v04_analysis import load_data
from .v04_predict import arrays, sensor_terms
from .v04_common import sha, write
from .v05_highrho import provenance, plan
from .v05_score_numerics import endpoint_cycle_quantile_influence, estimate_joint_interval_score_mcse, interval_score_90

def main():
    out=ROOT/'experiments/v0.5/analysis/score_propagation.json'
    registry=ROOT/'experiments/v0.5/registry/v05_score_propagation.json'
    if out.exists() or registry.exists(): raise FileExistsError('Retain original demonstration evidence')
    meta=provenance();start=time.perf_counter();cpu=time.process_time()
    meta.update(run_id='v05_score_propagation',status='running',sampler_invocations=0,scope='Known training calibration labels and saved posterior only; no CQR comparison/model selection/official data')
    write(registry,meta)
    inputs=['experiments/v0.4/analysis/principal_calibration_inputs.npz','experiments/v0.4/analysis/principal_precision_all25.json','experiments/v0.4/analysis/principal_replication_precision.json']+[f'experiments/v0.4/fits/v04_main_r{i}.nc' for i in (1,2,3)]
    meta['input_sha256']={p:sha(ROOT/p) for p in inputs}
    data=load_data(ROOT/inputs[0]); sensor=replace(data,y=None)
    reps=[az.from_netcdf(ROOT/p) for p in inputs[3:]]
    pooled=az.concat(*reps,dim='chain')
    assert pooled.posterior.sizes['chain']==12 and pooled.posterior.sizes['draw']==8000
    lz,mu,var=sensor_terms(arrays(pooled),sensor)
    lw=lz.reshape(12,8000,25);w=np.exp(lz-lz.max(axis=0)); y=np.exp(data.y)
    rs=json.loads((ROOT/inputs[1]).read_text(encoding='utf8'))['results']
    detail={}
    for probability in (.05,.95):
        r=[next(r for r in rs if r['engine']==int(e) and r['probability']==probability) for e in data.ids]
        q=np.array([r['quantile_log_rul'] for r in r]);Q=np.exp(q)
        u=(q[None,:]-mu)/np.sqrt(var);cdf=norm.cdf(u)
        density=np.sum(w*norm.pdf(u)/np.sqrt(var),axis=0)/np.sum(w,axis=0)
        f_saved=np.array([r['weighted_mixture_density_log_rul'] for r in r])
        np.testing.assert_allclose(density,f_saved,rtol=1e-12,atol=1e-12)
        np.testing.assert_allclose(np.sum(w*cdf,axis=0)/w.sum(0),probability,rtol=0,atol=1e-10)
        upper=np.array([[next(b['approximate_upper_quantile_rul_mcse'] for b in rr['batch_size_results'] if b['batch_size']==batch) for rr in r] for batch in (250,500)])
        inf=endpoint_cycle_quantile_influence(lw,cdf.reshape(12,8000,25),probability,Q,density)['influence_cycles']
        detail[probability]=dict(influence=inf,Q=Q,upper=upper)
    lo,hi=detail[.05],detail[.95]
    result=estimate_joint_interval_score_mcse(lo['influence'],hi['influence'],y,lo['Q'],hi['Q'],lo['upper'],hi['upper'],tail_probability=.05/2)
    # Independent scalar oracle: project first, then use np.var on chain-batch means.
    H=np.einsum('cde,e->cd',lo['influence'],(-1+20*(y<lo['Q']))/25)+np.einsum('cde,e->cd',hi['influence'],(1-20*(y>hi['Q']))/25)
    np.testing.assert_allclose(H,result['score_influence'],rtol=1e-12,atol=1e-12)
    oracles=[]
    for group in result['batch_size_results']:
        b=group['batch_size'];v=b*np.var(H.reshape(12,8000//b,b).mean(2),axis=1,ddof=1)*8000/96000**2
        total=float(v.sum());df=total**2/np.sum(v*v/(8000//b-1))
        upper=float(np.sqrt(total*df/chi2.ppf(.025,df)))
        np.testing.assert_allclose(total,group['score_variance_cycles_squared'],rtol=1e-11,atol=1e-12)
        np.testing.assert_allclose(upper,group['approximate_upper_quantile_score_mcse_cycles'],rtol=1e-11,atol=1e-12)
        oracles.append(dict(batch_size=b,variance=total,upper_mcse_cycles=upper,max_projection_residual=group['joint_score_variance_projection_abs_residual'],status='PASS'))
    rep_rs=json.loads((ROOT/inputs[2]).read_text(encoding='utf8'))['results']
    replicate_scores=[]
    for rows in rep_rs:
        L=np.array([next(r['quantile_rul'] for r in rows if r['engine']==int(e) and r['probability']==.05) for e in data.ids])
        U=np.array([next(r['quantile_rul'] for r in rows if r['engine']==int(e) and r['probability']==.95) for e in data.ids])
        replicate_scores.append(float(np.mean(interval_score_90(y,L,U))))
    max_upper=max(g['approximate_upper_quantile_score_mcse_cycles'] for g in result['batch_size_results'])
    result.pop('joint_endpoint_influence_cycles');result.pop('score_influence')
    result.update(engine_ids=data.ids.tolist(),outcomes_cycles=y.tolist(),lower_cycles=lo['Q'].tolist(),upper_cycles=hi['Q'].tolist(),independent_scalar_oracles=oracles,replicate_mean_scores_cycles=replicate_scores,replicate_range_cycles=max(replicate_scores)-min(replicate_scores),numerical_policy_result='NUMERICALLY_QUALIFIED' if result['label_kink']['any'] or max_upper>.5 else 'PASS',scope=meta['scope'],primary_CQR_contrast_computed=False,ideal_posterior_mcse_approximate=True,provenance=meta)
    write(out,result)
    meta.update(status='completed',cpu_seconds=time.process_time()-cpu,wall_seconds=time.perf_counter()-start,result_sha256=sha(out),independent_verification='PASS',numerical_policy_result=result['numerical_policy_result'])
    write(registry,meta)
    print(json.dumps(dict(status=meta['status'],mean_score=result['finite_mean_interval_score_cycles'],max_upper_score_mcse=max_upper,label_kink=result['label_kink']['any'],replicate_range=result['replicate_range_cycles'],numerical_policy=result['numerical_policy_result'],cpu=meta['cpu_seconds'])),flush=True)
if __name__=='__main__':main()
