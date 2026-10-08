"""Bounded v0.4 scientific fits; separate immutable per-run records."""
import argparse,json,time,threading,traceback,os,sys
from dataclasses import replace,asdict
import arviz as az
import numpy as np
import nutpie,psutil
from .data import ROOT,load_training,manifest,fit_preprocessor,make_dataset
from .v04_model import build_model,generate
from .v04_common import PLAN,provenance,write,sha
from .pilot import convert_trace,diagnostics,recovery

def run(run_id):
    base_id=run_id.removesuffix('_infra1')
    cfg=next(r for r in PLAN['runs'] if r['run_id']==base_id)
    if base_id!=run_id:
        original=json.loads((ROOT/'experiments/v0.4/registry'/f'{base_id}.json').read_text())
        assert cfg['kind']=='pipeline' and cfg['cutoff_mode']=='canonical'
        assert original['status']=='failed' and original['artifacts_sha256']=={}
        assert 'cutoff_salt is only valid' in original['exception']
        assert original['configuration']==cfg, 'No scientific configuration change for infrastructure repair'
    directory=ROOT/'experiments/v0.4/fits';directory.mkdir(parents=True,exist_ok=True)
    record=ROOT/'experiments/v0.4/registry'/f'{run_id}.json'
    if record.exists() or (directory/f'{run_id}.nc').exists(): raise FileExistsError('No scientific overwrite/retry')
    meta=provenance();meta.update(run_id=run_id,configuration=cfg,status='running',infrastructure_repair_of=base_id if base_id!=run_id else None,infrastructure_repair_campaign=1 if base_id!=run_id else None,scientific_sampler_started=False)
    write(record,meta);start=time.perf_counter();cpu=time.process_time();peak=[psutil.Process().memory_info().rss]
    done=threading.Event()
    def monitor():
        while not done.wait(.5):
            peak[0]=max(peak[0],psutil.Process().memory_info().rss)
            if time.perf_counter()-start>600:
                meta.update(status='failed',exception='Prespecified per-fit wall budget exceeded',wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,peak_rss_bytes=peak[0])
                write(record,meta);os._exit(124)
    threading.Thread(target=monitor,daemon=True).start()
    truth=None;extra=None;pre=None;pipeline=None
    try:
        if cfg['kind']=='synthetic':
            regime=PLAN['synthetic']['regimes'][cfg['regime']]
            data,truth=generate(cfg['n'],cfg['data_seed'],regime)
            assess,_=generate(cfg['assessment_n'],cfg['assessment_seed'],regime)
            np.savez(directory/f'{run_id}_assessment.npz',a=assess.a,z=assess.z,y=assess.y,ids=assess.ids,B=assess.B)
        elif cfg['kind']=='pipeline':
            from .v04_pipeline import build_bootstrap_pipeline_data,reselect_refit_calibrate_cqr
            from .comparators import predict_endpoints
            pipeline=build_bootstrap_pipeline_data(load_training(),bootstrap_seed=cfg['bootstrap_seed'],cutoff_mode=cfg['cutoff_mode'],cutoff_salt=str(cfg['cutoff_salt']) if cfg['cutoff_mode']=='alternate' else None,input_source_sha256=sha(ROOT/'configs/proposed_split_manifest.json'))
            meta['pipeline_metadata']=pipeline.metadata
            if pipeline.status!='ready': raise ValueError(';'.join(pipeline.failure_reasons))
            data=pipeline.refit_fit_tune;pre=pipeline.refit_preprocessor
            np.savez(directory/f'{run_id}_calibration.npz',a=pipeline.calibration.a,z=pipeline.calibration.z,y=pipeline.calibration.y,ids=pipeline.calibration.ids,B=pipeline.calibration.B)
            cqr=reselect_refit_calibrate_cqr(pipeline)
            meta['cqr']=dict(status=cqr.status,candidate_summaries=cqr.candidate_summaries,tuning_scores=cqr.tuning_scores,calibration=cqr.calibration_metadata,failures=cqr.failure_reasons)
            if cqr.status=='completed':
                lo,hi=predict_endpoints(cqr.interval_refit,pipeline.anchor_features['summary'],pipeline.anchor_features['full_sequence'])
                np.savez(directory/f'{run_id}_cqr_anchors.npz',lower=np.maximum(0,np.minimum(lo,hi)-cqr.calibration_correction),upper=np.maximum(0,np.maximum(lo,hi)+cqr.calibration_correction),ids=pipeline.anchor.ids)
            np.savez(directory/f'{run_id}_anchors.npz',a=pipeline.anchor.a,z=pipeline.anchor.z,ids=pipeline.anchor.ids,B=pipeline.anchor.B)
        else:
            engines=load_training();ids=[r['engine'] for r in manifest() if r['eligible_alive'] and r['role'] in ('fit','tune')]
            pre=fit_preprocessor(engines,ids);data=make_dataset(engines,pre,('fit','tune'))
            meta['preprocessing_fit_ids']=ids
            if cfg['kind']=='oracle':
                cal=make_dataset(engines,pre,('calibration',),allow_calibration=True)
                ix=np.flatnonzero(cal.ids==cfg['engine'])
                assert len(ix)==1
                extra=replace(cal,a=cal.a[ix],z=cal.z[ix],ids=cal.ids[ix],y=None)
                np.savez(directory/f'{run_id}_extra.npz',a=extra.a,z=extra.z,ids=extra.ids,B=extra.B)
        if pre is not None: np.savez(directory/f'{run_id}_pre.npz',**pre)
        np.savez(directory/f'{run_id}_data.npz',a=data.a,z=data.z,y=data.y,ids=data.ids,B=data.B)
        meta['data_sha256']=sha(directory/f'{run_id}_data.npz')
        model=build_model(data,PLAN['prior'],cfg.get('prior_scale',1.),cfg.get('error','normal'),cfg.get('rho_zero',False),extra)
        compiled=nutpie.compile_pymc_model(model,backend='numba')
        meta['scientific_sampler_started']=True;write(record,meta)
        raw=nutpie.sample(compiled,draws=cfg['draws'],tune=PLAN['sampling']['warmup'],chains=4,cores=2,seed=cfg['seed'],target_accept=.95,maxdepth=12,progress_bar=False,save_warmup=False)
        idata=convert_trace(raw);idata.to_netcdf(directory/f'{run_id}.nc')
        diag,summary=diagnostics(idata,cfg.get('rho_zero',False))
        # Inspect sampling auxiliaries as well as physical coordinates.
        aux=[n for n in ('gcor_u','eta_rho') if n in idata.posterior]
        if aux:
            auxiliary=az.summary(idata,var_names=aux,round_to='none')
            diag['auxiliary_rhat_max']=float(auxiliary.r_hat.max());diag['auxiliary_bulk_min']=float(auxiliary.ess_bulk.min());diag['auxiliary_tail_min']=float(auxiliary.ess_tail.min())
            if diag['auxiliary_rhat_max']>=1.01 or diag['auxiliary_bulk_min']<400 or diag['auxiliary_tail_min']<400:
                diag['acceptance']='FAIL';diag['failures'].append('Auxiliary convergence threshold')
        summary.to_csv(directory/f'{run_id}_summary.csv')
        rec=recovery(idata,truth)
        if rec: rec['interpretation']='One of four fixed-truth replicates per regime; not SBC. Posterior interval recovery and gross standardized errors are diagnostic, not identifiability proof.'
        meta.update(status='completed',diagnostics=diag,recovery=rec,truth=truth,
            posterior_sha256=sha(directory/f'{run_id}.nc'),n_engines=len(data.ids),n_distinct_engines=len(set(data.ids)))
    except Exception as exc:
        meta.update(status='failed',exception=repr(exc),traceback=traceback.format_exc())
    finally:
        done.set();meta.update(wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,peak_rss_bytes=peak[0])
        if meta['wall_seconds']>600: meta.update(status='failed',compute_failure='Per-fit wall limit exceeded')
        meta['artifacts_sha256']={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in directory.glob(f'{run_id}*') if p.is_file()}
        write(record,meta)
    print(json.dumps(dict(run_id=run_id,status=meta['status'],wall=meta['wall_seconds'],diagnostics=meta.get('diagnostics'),exception=meta.get('exception'))),flush=True)
    return meta
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('run_id');result=run(parser.parse_args().run_id);sys.exit(0 if result['status']=='completed' else 1)