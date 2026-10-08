"""One fixed equivalent-posterior inquiry. No official-data entry point."""
import argparse, json, os, threading, time, traceback, subprocess
import numpy as np
import pymc as pm
import pytensor.tensor as pt
import arviz as az
import nutpie, psutil
from scipy.linalg import cho_factor, cho_solve
from scipy.stats import norm, halfnorm, beta as beta_dist
from .data import ROOT, LandmarkData
from .model import symbolic_terms
from .v04_model import build_model as original_model
from .v04_common import provenance as original_provenance, sha, write
from .pilot import convert_trace, diagnostics, recovery

PLAN_PATH = ROOT/'configs/v0.5/resolution_plan.json'
OUT = ROOT/'experiments/v0.5'
def plan(): return json.loads(PLAN_PATH.read_text(encoding='utf8'))
def provenance():
    meta = original_provenance()
    dirty = subprocess.check_output([r'C:\Program Files\Git\cmd\git.exe','-C',str(ROOT),'status','--porcelain','--','configs/v0.5','src/rp001','tests/test_v05_score_numerics.py'],text=True).strip()
    if dirty: raise RuntimeError('Commit frozen v05 source/plan before execution: '+dirty)
    meta.update(plan_sha256=sha(PLAN_PATH), owner_reviewed_scientific_commit=plan()['owner_reviewed_scientific_commit'])
    return meta
def input_data():
    cfg = plan()['investigation']; path=ROOT/cfg['input_path']
    assert sha(path)==cfg['input_sha256']
    d=np.load(path)
    return LandmarkData(d['a'],d['z'],d['y'],d['ids'],d['B'],str(path))
def innovation_model(data, prior):
    with pm.Model() as model:
        b=pm.Normal('beta',prior['beta_mu'],prior['beta_sd'],shape=2)
        g=pm.Normal('gamma',0,prior['gamma_sd'],shape=2)
        G=pm.Normal('Gamma',0,np.tile(prior['Gamma_sd'],(2,1)),shape=(2,2))
        t=pm.HalfNormal('tau',prior['tau_sd'],shape=2)
        rg=pm.Deterministic('r_g',2*pm.Beta('gcor_u',prior['lkj_eta'],prior['lkj_eta'])-1)
        eta=pm.Normal('eta_rho',0,prior['eta_rho_sd'])
        rho=pm.Deterministic('rho',pt.tanh(eta))
        nu=pm.HalfNormal('nu',prior['sigma_z_sd'])
        sz=pm.Deterministic('sigma_z',nu*pt.cosh(eta))
        ref=pm.HalfNormal.dist(prior['sigma_z_sd'])
        pm.Potential('original_scale_prior',pm.logp(ref,sz)-pm.logp(ref,nu)+pt.log(pt.cosh(eta)))
        sr=pm.HalfNormal('sigma_r',prior['sigma_r_sd'])
        p=dict(beta=b,gamma=g,Gamma=G,tau=t,r_g=rg,sigma_z=sz,sigma_r=sr,rho=rho)
        lz,ly,*_=symbolic_terms(data,p)
        pm.Potential('engine_likelihood',pt.sum(lz+ly))
    return model
def dense_joint_loglike(data,p):
    # Independent 31-dimensional marginal MVN; no AR whitening/Woodbury or conditional-y helper.
    t=np.asarray(p['tau']); S=np.outer(t,t)*np.array([[1,p['r_g']],[p['r_g'],1]])
    n=data.z.shape[1]; K=p['rho']**np.abs(np.arange(n)[:,None]-np.arange(n)[None,:])
    Czz=data.B@S@data.B.T+p['sigma_z']**2*K
    cy=data.B@S@np.asarray(p['gamma'])
    C=np.block([[Czz,cy[:,None]],[cy[None,:],np.array([[p['sigma_r']**2+np.asarray(p['gamma'])@S@np.asarray(p['gamma'])]])]])
    cf=cho_factor(C,lower=True); ld=2*np.log(np.diag(cf[0])).sum()
    mg=data.a@np.asarray(p['Gamma']).T
    means=np.column_stack((mg@data.B.T,data.a@np.asarray(p['beta'])+mg@np.asarray(p['gamma'])))
    r=np.column_stack((data.z,data.y))-means
    return -.5*((n+1)*np.log(2*np.pi)+ld+np.sum(r*cho_solve(cf,r.T).T,axis=1))
def independent_transformed_joint(data,p,prior):
    eta=np.arctanh(p['rho']); u=(p['r_g']+1)/2
    lp=np.sum(norm.logpdf(p['beta'],prior['beta_mu'],prior['beta_sd']))
    lp+=np.sum(norm.logpdf(p['gamma'],0,prior['gamma_sd']))
    lp+=np.sum(norm.logpdf(p['Gamma'],0,np.tile(prior['Gamma_sd'],(2,1))))
    lp+=np.sum(halfnorm.logpdf(p['tau'],scale=prior['tau_sd']))+np.log(p['tau']).sum()
    for name in ('sigma_z','sigma_r'):
        lp+=halfnorm.logpdf(p[name],scale=prior[name+'_sd'])+np.log(p[name])
    lp+=beta_dist.logpdf(u,prior['lkj_eta'],prior['lkj_eta'])+np.log(u*(1-u))
    lp+=norm.logpdf(eta,0,prior['eta_rho_sd'])
    return float(dense_joint_loglike(data,p).sum()+lp)
def point(model,p,innovation=False):
    q=model.initial_point()
    for key in ('beta','gamma','Gamma'): q[key]=np.asarray(p[key],dtype=float)
    q['tau_log__']=np.log(p['tau']); q['gcor_u_logodds__']=np.log((1+p['r_g'])/(1-p['r_g']))
    q['sigma_r_log__']=np.log(p['sigma_r']); eta=np.arctanh(p['rho']); q['eta_rho']=eta
    q['nu_log__' if innovation else 'sigma_z_log__']=np.log(p['sigma_z'])-(np.log(np.cosh(eta)) if innovation else 0)
    return q
def preflight():
    result_path=OUT/'analysis/math_preflight.json'
    if result_path.exists(): raise FileExistsError('No preflight evidence overwrite')
    cfg=plan()['investigation']; prior=plan()['prior']; data=input_data(); meta=provenance()
    old=original_model(data,prior); new=innovation_model(data,prior)
    lo=old.compile_logp(); ln=new.compile_logp()
    go=old.compile_dlogp(vars=[old['sigma_z'],old['eta_rho']])
    gn=new.compile_dlogp(vars=[new['nu'],new['eta_rho']])
    dt=cfg['density_tolerance']; gt=cfg['gradient_tolerance']; h=gt['finite_difference_step']; records=[]
    try:
        for rho in cfg['preflight_rho']:
            for sz in cfg['preflight_sigma_z']:
                p={k:np.asarray(v,dtype=float) if isinstance(v,list) else v for k,v in cfg['truth'].items()}
                p.update(rho=rho,sigma_z=sz)
                po=point(old,p); pn=point(new,p,True)
                independent=independent_transformed_joint(data,p,prior); a=float(lo(po)); b=float(ln(pn))
                grads=[]
                for innovation,fun,pp in ((False,go,po),(True,gn,pn)):
                    actual=np.asarray(fun(pp)); expected=[]
                    eta=np.arctanh(rho); logscale=np.log(sz)-(np.log(np.cosh(eta)) if innovation else 0)
                    for coordinate in range(2):
                        vals=[]
                        for sign in (-1,1):
                            x=logscale+(sign*h if coordinate==0 else 0)
                            e=eta+(sign*h if coordinate==1 else 0)
                            z=np.exp(x)*(np.cosh(e) if innovation else 1)
                            trial=dict(p,rho=float(np.tanh(e)),sigma_z=float(z))
                            vals.append(independent_transformed_joint(data,trial,prior))
                        expected.append((vals[1]-vals[0])/(2*h))
                    expected=np.asarray(expected)
                    grads.append(dict(parameterization='innovation' if innovation else 'original',autodiff=actual.tolist(),dense_finite_difference=expected.tolist(),max_abs_difference=float(np.max(np.abs(actual-expected))),pass_check=bool(np.allclose(actual,expected,atol=gt['atol'],rtol=gt['rtol']))))
                records.append(dict(rho=rho,sigma_z=sz,original_logp=a,innovation_logp=b,independent_dense_logp=independent,original_vs_new_abs=abs(a-b),original_vs_dense_abs=abs(a-independent),density_pass=bool(np.isclose(a,b,**dt) and np.isclose(a,independent,**dt)),gradients=grads))
        passed=all(r['density_pass'] and all(g['pass_check'] for g in r['gradients']) for r in records)
        meta.update(status='PASS' if passed else 'FAIL',grid=records,n_density_points=len(records),n_gradient_coordinates=4*len(records),innovation_jacobian='d sigma_z/d nu=cosh(eta); unconstrained (lognu,eta)->(logsigmaz,eta) determinant1',sampler_invocations=0,data_sha256=cfg['input_sha256'])
    except Exception as exc:
        meta.update(status='FAIL',exception=repr(exc),traceback=traceback.format_exc(),grid=records,sampler_invocations=0)
    write(result_path,meta)
    print(json.dumps({k:meta[k] for k in ('status','sampler_invocations')}),flush=True)
    return meta
def geometry(idata):
    post=idata.posterior
    eta=post['eta_rho'].values; sz=post['sigma_z'].values
    nu=sz/np.cosh(eta)
    values=[np.log(sz).ravel(),eta.ravel(),np.log(nu).ravel(),post['tau'].values[:,:,0].ravel(),post['tau'].values[:,:,1].ravel()]
    return dict(coordinates=['log_sigma_z','eta_rho','log_nu','tau0','tau1'],correlations=np.corrcoef(values),chain_mean_log_sigma_z=np.log(sz).mean(1),chain_mean_eta_rho=eta.mean(1),chain_mean_log_nu=np.log(nu).mean(1),rho_mean=float(np.tanh(eta).mean()),rho_sd=float(np.tanh(eta).std(ddof=1)),sigma_z_mean=float(sz.mean()),sigma_z_sd=float(sz.std(ddof=1)),nu_mean=float(nu.mean()),nu_sd=float(nu.std(ddof=1)))
def run():
    cfg=plan()['investigation']; run_id=cfg['run_id']; path=OUT/'registry'/f'{run_id}.json'; directory=OUT/'fits'
    if path.exists() or (directory/f'{run_id}.nc').exists(): raise FileExistsError('One invocation only; preserve all failed/partial evidence')
    pre=json.loads((OUT/'analysis/math_preflight.json').read_text(encoding='utf8'))
    assert pre['status']=='PASS' and pre['plan_sha256']==sha(PLAN_PATH)
    meta=provenance(); assert meta['git_commit']==pre['git_commit']
    directory.mkdir(parents=True,exist_ok=True)
    meta.update(run_id=run_id,configuration=cfg,status='running',scientific_sampler_started=False,scientific_sampler_invocation_count=0,preflight_sha256=sha(OUT/'analysis/math_preflight.json'),data_sha256=cfg['input_sha256'])
    write(path,meta); start=time.perf_counter(); cpu=time.process_time(); peak=[psutil.Process().memory_info().rss]; done=threading.Event()
    def custody():
        return {str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in directory.glob(f'{run_id}*') if p.is_file()}
    def monitor():
        while not done.wait(.5):
            peak[0]=max(peak[0],psutil.Process().memory_info().rss)
            payload=sum(p.stat().st_size for p in directory.glob(f'{run_id}*') if p.is_file())
            if time.perf_counter()-start>600 or time.process_time()-cpu>3600 or payload>128*1024**2:
                meta.update(status='failed',exception='Prespecified wall/CPU/payload cap exceeded',wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,peak_rss_bytes=peak[0],artifacts_sha256=custody())
                write(path,meta);os._exit(124)
    threading.Thread(target=monitor,daemon=True).start()
    try:
        data=input_data(); model=innovation_model(data,plan()['prior']); compiled=nutpie.compile_pymc_model(model,backend='numba')
        meta.update(scientific_sampler_started=True,scientific_sampler_invocation_count=1);write(path,meta)
        raw=nutpie.sample(compiled,draws=cfg['draws'],tune=cfg['warmup'],chains=cfg['chains'],cores=cfg['cores'],seed=cfg['seed'],target_accept=cfg['target_accept'],maxdepth=cfg['maxdepth'],progress_bar=False,save_warmup=False)
        idata=convert_trace(raw); idata.to_netcdf(directory/f'{run_id}.nc')
        diag,summary=diagnostics(idata)
        aux=az.summary(idata,var_names=cfg['auxiliary'],round_to='none')
        diag.update(auxiliary_rhat_max=float(aux.r_hat.max()),auxiliary_bulk_min=float(aux.ess_bulk.min()),auxiliary_tail_min=float(aux.ess_tail.min()))
        if not np.isfinite(aux[['r_hat','ess_bulk','ess_tail']].values).all() or diag['auxiliary_rhat_max']>=1.01 or diag['auxiliary_bulk_min']<400 or diag['auxiliary_tail_min']<400:
            diag['failures'].append('Auxiliary convergence threshold')
        if not all(np.isfinite(v.values).all() for v in idata.posterior.data_vars.values()) or not np.isfinite(summary[['r_hat','ess_bulk','ess_tail']].values).all():
            diag['failures'].append('Nonfinite posterior/physical diagnostics')
        diag['acceptance']='FAIL' if diag['failures'] else 'PASS'
        summary.to_csv(directory/f'{run_id}_summary.csv');aux.to_csv(directory/f'{run_id}_auxiliary.csv')
        old=az.from_netcdf(ROOT/'experiments/v0.4/fits/v04_syn_high_rho_3.nc')
        write(OUT/'analysis/highrho_geometry.json',dict(provenance=meta,old_failed_diagnostic_only=geometry(old),bounded_innovation=geometry(idata),causal_limit='Parameterization and retained/tuning budgets change together; one case cannot uniquely identify failure cause or establish universal robustness.'))
        meta.update(status='completed',diagnostics=diag,recovery=recovery(idata,cfg['truth']),truth=cfg['truth'],n_engines=len(data.ids),posterior_sha256=sha(directory/f'{run_id}.nc'))
    except Exception as exc:
        meta.update(status='failed',exception=repr(exc),traceback=traceback.format_exc())
    finally:
        done.set();meta.update(wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,peak_rss_bytes=peak[0],artifacts_sha256=custody())
        if meta['wall_seconds']>600 or meta['cpu_seconds']>3600: meta.update(status='failed',compute_failure='Prespecified cap exceeded')
        write(path,meta)
    print(json.dumps(dict(status=meta['status'],diagnostics=meta.get('diagnostics'),wall_seconds=meta['wall_seconds'],cpu_seconds=meta['cpu_seconds'],exception=meta.get('exception'))),flush=True)
    return meta
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['preflight','run']);a=p.parse_args()
    r=preflight() if a.action=='preflight' else run()
    raise SystemExit(0 if r['status'] in ('PASS','completed') else 1)
