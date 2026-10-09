"""One owner-authorized label release and fixed scoring; no retries or adaptive repair."""
import csv,math,os,time,zipfile
import numpy as np
from scipy.stats import norm
from common import *
from core import parse_labels,evaluate,qualification
from integrity import verify_integrity
from rp001.v05_score_numerics import endpoint_cycle_quantile_influence,estimate_joint_interval_score_mcse

def load_predictions():
    out={}
    for method in ("Bayesian","CQR"):
        with (T/f"{method}_predictions.csv").open(newline="",encoding="utf8") as f:rows=list(csv.DictReader(f))
        check([int(r["engine"]) for r in rows]==list(range(1,101)),"Complete frozen IDs")
        out[method]={k:np.array([float(r[k]) for r in rows],dtype=np.float64) for k in ("lower","median","upper")}
    return out

def derive_influences(pred):
    lower=np.empty((12,8000,100));upper=np.empty_like(lower)
    radii={.05:np.empty((2,100)),.95:np.empty((2,100))}
    density_checks=[]
    for i in range(1,101):
        with np.load(B/f"conditional_terms/engine_{i:03d}.npz",allow_pickle=False) as terms:
            mu=terms["means"];var=terms["variances"];lw=terms["log_weights"]
            check(int(terms["engine"])==i and all(a.shape==(12,8000) for a in (mu,var,lw)),"Conditional engine/axis alignment")
            check(np.all(np.isfinite(mu)) and np.all(np.isfinite(var)) and np.all(var>0),"Frozen conditional moments")
            sd=np.sqrt(var);w=np.exp(lw-lw.max())
            for probability,destination,key in ((.05,lower,"lower"),(.95,upper,"upper")):
                rec=read(B/f"precision/engine_{i:03d}_pooled_p{int(probability*100):02d}.json")
                q=rec["quantile_log_rul"];Q=rec["quantile_rul"]
                check(float(Q).hex()==float(pred["Bayesian"][key][i-1]).hex(),"Stored canonical quantile identity")
                check(float(np.exp(q)).hex()==float(Q).hex(),"Canonical log/cycle route")
                z=(q-mu)/sd;cdf=norm.cdf(z)
                density=float(np.sum(w*norm.pdf(z)/sd)/np.sum(w))
                np.testing.assert_allclose(density,rec["weighted_mixture_density_log_rul"],rtol=1e-12,atol=1e-12)
                weighted_cdf=float(np.sum(w*cdf)/np.sum(w))
                check(abs(weighted_cdf-probability)<=1e-10,"Stored endpoint CDF residual")
                influence=endpoint_cycle_quantile_influence(lw[:,:,None],cdf[:,:,None],probability,Q,
                    rec["weighted_mixture_density_log_rul"])
                np.testing.assert_allclose(influence["scaled_weight_mean_by_engine"][0],
                    rec["importance_weight_mean_scaled"],rtol=1e-12,atol=1e-12)
                destination[:,:,i-1]=influence["influence_cycles"][:,:,0]
                for j,b in enumerate(rec["batch_size_results"]):radii[probability][j,i-1]=b["approximate_upper_quantile_rul_mcse"]
                density_checks.append(dict(engine=i,p=probability,density_abs_residual=abs(density-rec["weighted_mixture_density_log_rul"]),
                    weighted_cdf_abs_residual=abs(weighted_cdf-probability)))
    return lower,upper,radii,density_checks

def write_engine_tables(y,pred,evaluation):
    with (O/"PER_ENGINE_PAIRED_DECOMPOSITION.csv").open("x",newline="",encoding="utf8") as f:
        fields=["engine","label"]+[m+"_"+k for m in ("Bayesian","CQR") for k in
            ("lower","median","upper","width","below_penalty","above_penalty","score","covered","median_error")]+["paired_"+k for k in ("width","below_penalty","above_penalty","score")]
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for i in range(100):
            row=dict(engine=i+1,label=float(y[i]))
            for m in ("Bayesian","CQR"):
                for k in ("lower","median","upper"):row[m+"_"+k]=float(pred[m][k][i])
                for k in ("width","below_penalty","above_penalty","score","covered","median_error"):
                    row[m+"_"+k]=bool(evaluation["components"][m][k][i]) if k=="covered" else float(evaluation["components"][m][k][i])
            for k in ("width","below_penalty","above_penalty","score"):row["paired_"+k]=float(evaluation["paired"][k][i])
            writer.writerow(row)

def main():
    check((O/"PRE_LABEL_RECEIPT.json").is_file(),"No pre-label PASS receipt")
    check(not (O/"EXECUTION_BEGIN.json").exists(),"Stage D execution is single attempt; owner review required for any retry")
    start=time.perf_counter();cpu=time.process_time();labels_accessed=False
    save(O/"EXECUTION_BEGIN.json",dict(at_utc=now(),execution_commit=git("rev-parse","HEAD")))
    event("EXECUTION_BEGIN",labels_accessed=False)
    try:
        plan=source_check()
        public_receipt=D/"PRE_LABEL_INTEGRITY_RECEIPT.json"
        check(sha(public_receipt)==sha(O/"PRE_LABEL_RECEIPT.json"),"Pre-label receipt exact")
        prior=read(public_receipt)
        check(prior["status"]=="PASS" and prior["plan_sha256"]==sha(R/"configs/stage_D_execution_plan.json"),"Pinned plan/receipt")
        integrity=verify_integrity()
        save(O/"IMMEDIATE_PRE_ACCESS_INTEGRITY.json",integrity)
        pred=load_predictions()
        # Derive fixed endpoint influence from frozen terms BEFORE exposure.
        lower,upper,radii,density_checks=derive_influences(pred)
        save(O/"PRE_ACCESS_INFLUENCE_CHECKS.json",dict(status="PASS",checks=density_checks,
            source_sha256=sha(R/"src/rp001/v05_score_numerics.py"),new_roots=0,new_draws=0))
        from threadpoolctl import threadpool_info
        threads=threadpool_info();check(all(t["num_threads"]==1 for t in threads),"Actual BLAS threads must equal one")
        event("IMMEDIATE_PRE_ACCESS_GATES_PASS",receipt_sha256=sha(O/"IMMEDIATE_PRE_ACCESS_INTEGRITY.json"),
            frozen_scoring_source_sha256=plan["prelabel_source_sha256"])
        archive=R/plan["label_source"]["inner_archive_path"]
        with zipfile.ZipFile(archive) as z:
            name=plan["label_source"]["member"]
            check(sum(x.filename==name for x in z.infolist())==1,"Unique exact official label member")
            info=z.getinfo(name)
            event("LABEL_ACCESS_BEGIN",member=name,archive_sha256=sha(archive),
                owner_authorization_sha256=plan["owner_authorization_sha256"],execution_commit=git("rev-parse","HEAD"))
            labels_accessed=True
            payload=z.read(info)
        label_path=O/"labels/RUL_FD001.txt"
        label_path.parent.mkdir()
        with label_path.open("xb") as f:f.write(payload)
        provenance=dict(at_utc=now(),label_file=str(label_path.relative_to(R)).replace("\\","/"),
            extracted_sha256=sha(label_path),bytes=len(payload),member=name,member_CRC32=info.CRC,
            member_uncompressed_bytes=info.file_size,member_compressed_bytes=info.compress_size,
            member_compression_type=info.compress_type,member_archive_timestamp=list(info.date_time),
            official_source_provenance=read(R/"data/raw/provenance.json"),
            outer_archive_sha256=sha(R/plan["label_source"]["outer_archive_path"]),
            inner_archive_sha256=sha(archive),owner_authorization_sha256=plan["owner_authorization_sha256"],
            source_plan_sha256=sha(R/"configs/stage_D_execution_plan.json"),execution_commit=git("rev-parse","HEAD"),
            frozen_scoring_source_sha256=plan["prelabel_source_sha256"],first_authorized_outcome_exposure=True,
            identity_limit="Content-addressed local official archive provenance; no independent archive authenticity certificate")
        save(O/"LABEL_ACCESS_AND_PROVENANCE.json",provenance)
        event("LABEL_EXTRACTION_COMPLETE",extracted_sha256=sha(label_path),bytes=len(payload))
        ids=read(B/"engine_ledger_final.json")
        y=parse_labels(payload,[r["engine"] for r in ids])
        save(O/"LABEL_ALIGNMENT.json",dict(status="PASS",schema="Official one-value-per-row RUL; row i maps to engine i",
            rows=[dict(label_row=i+1,engine=i+1,cutoff=ids[i]["cutoff"],RUL_cycles=float(y[i])) for i in range(100)],
            finite_positive_uncapped=True,unmatched=0,duplicates=0,missing=0,
            source_has_embedded_engine_ids=False,ordering_assumption="Declared official FD001 file order, as locked",
            labels_sha256=sha(label_path)))
        event("LABEL_ALIGNMENT_PASS",engine_count=100,no_subset=True)
        evaluation=evaluate(y,pred["Bayesian"],pred["CQR"])
        save(O/"PRIMARY_EVALUATION.json",evaluation)
        write_engine_tables(y,pred,evaluation)
        save(O/"COVERAGE_AND_ERRORS.json",dict(metrics=evaluation["metrics"],
            interpretation="Exact finite counts/errors; no binomial/population confidence intervals"))
        event("COMPLETE_STORED_SCORE_COMPUTED",payload_sha256=sha(O/"PRIMARY_EVALUATION.json"),engine_count=100)
        numerical=estimate_joint_interval_score_mcse(lower,upper,y,pred["Bayesian"]["lower"],pred["Bayesian"]["upper"],
            radii[.05],radii[.95],tail_probability=.025,batch_sizes=(250,500))
        arrays=dict(lower_influence=lower,upper_influence=upper,H=numerical.pop("score_influence"),
            joint_influence=numerical.pop("joint_endpoint_influence_cycles"))
        for group in numerical["batch_size_results"]:
            b=group["batch_size"]
            arrays[f"joint_MC_covariance_b{b}"]=group.pop("joint_endpoint_mc_error_covariance_cycles_squared")
            for c in group["chain_results"]:
                arrays[f"chain_{c['chain']}_LRV_covariance_b{b}"]=c.pop("joint_endpoint_lrv_covariance_cycles_squared")
        save_npz(O/"CORRELATION_PRESERVING_NUMERICAL_ARRAYS.npz",**arrays)
        numerical["qualification"]=qualification(numerical)
        numerical["contrast_MCSE_equals_Bayesian_mean_score_MCSE"]=True
        numerical["CQR_conditional_posterior_MC_error"]=0
        numerical["endpoint_radii"]=radii
        save(O/"SCORE_NUMERICAL_UNCERTAINTY.json",numerical)
        replicas=[]
        for fit in ("v04_main_r1","v04_main_r2","v04_main_r3"):
            p={k:np.array([read(B/f"precision/engine_{i:03d}_{fit}_p{pp:02d}.json")["quantile_rul"] for i in range(1,101)])
                for k,pp in (("lower",5),("median",50),("upper",95))}
            r=evaluate(y,p,pred["CQR"])
            save(O/f"independent_fits/{fit}_complete_score.json",r)
            replicas.append(dict(fit=fit,mean_Bayesian_score_cycles=r["metrics"]["Bayesian"]["mean_interval_score_cycles"],
                paired_difference_cycles=r["paired_difference_cycles"]))
        contrasts=[r["paired_difference_cycles"] for r in replicas]
        save(O/"INDEPENDENT_FIT_SCORE_SENSITIVITY.json",dict(results=replicas,range_cycles=max(contrasts)-min(contrasts),
            min_contrast_cycles=min(contrasts),max_contrast_cycles=max(contrasts),
            independent_fit_quantile_batch_exceedances=13,interpretation="Fixed fit diagnostic; no model choice or ranking certificate"))
        secondary=read(R/"experiments/v0.4/analysis/principal_posthoc_calibration.json")
        check(secondary["correction"]==0.0,"Predeclared posthoc correction identity")
        save(O/"SECONDARY_POSTHOC_ABLATION.json",dict(status="IDENTICAL_TO_PRIMARY_STORED_BAYESIAN",
            fixed_nonnegative_expansion_cycles=0.0,source_sha256=sha(R/"experiments/v0.4/analysis/principal_posthoc_calibration.json"),
            paired_difference_cycles=evaluation["paired_difference_cycles"],secondary_only=True,
            reason="Locked correction zero and all stored Bayesian endpoints positive; no new predictions"))
        save(O/"NUMERICAL_FLAGS_AND_FAILURE_LEDGER.json",dict(qualification=numerical["qualification"],
            label_kink=numerical["label_kink"],failures=[read(p) for p in sorted((O/"failures").glob("*.json"))],
            no_post_outcome_repair=True,stored_complete_score_retained=True))
        event("NUMERICAL_ASSESSMENT_COMPLETE",restricted_payload_sha256=sha(O/"SCORE_NUMERICAL_UNCERTAINTY.json"))
        save(O/"COMPUTE_AND_ENVIRONMENT.json",dict(at_utc=now(),environment_fingerprint=integrity["environment_fingerprint"],
            threadpool_info=threads,processor=__import__("platform").processor(),logical_cores=os.cpu_count(),
            wall_seconds=time.perf_counter()-start,cpu_seconds=time.process_time()-cpu,
            peak_process_memory_bytes=__import__("psutil").Process().memory_info().peak_wset,
            compute="Local CPU",Colab_used=False,additional_spend=0,new_draws=0,new_roots=0,
            new_predictions=0,retraining=False,model_selection=False))
        from verify_results import verify_results
        verify_results(pred,y,evaluation,numerical)
        status="NUMERICALLY QUALIFIED RESULT" if numerical["qualification"]["status"]=="NUMERICALLY_QUALIFIED" else "COMPLETE AND READY FOR OWNER SCIENTIFIC RESULT REVIEW"
        save(O/"EXECUTION_OUTCOME.json",dict(at_utc=now(),status=status,primary_status="AVAILABLE",
            numerical_status=numerical["qualification"]["status"],labels_accessed=True,engines=100,
            internal_SOL_verification="PASS",public_results_release_authorized=False,research_status="PROTOCOL_LOCKED"))
        event("STAGE_D_EXECUTION_COMPLETE",result_sha256=sha(O/"EXECUTION_OUTCOME.json"),
            predictions_changed=False,new_draws=0,public_scientific_release=False)
        print("Stage D execution and internal verification complete; outcomes retained in protected local storage",flush=True)
    except Exception as exc:
        failure(exc,"label_released" if labels_accessed else "immediate_pre_label")
        save(O/"EXECUTION_BLOCKED.json",dict(at_utc=now(),status="STAGE D BLOCKED / PRIMARY RESULT UNAVAILABLE",
            labels_accessed=labels_accessed,type=type(exc).__name__,message=str(exc),retry_authorized=False))
        print("Stage D stopped; immutable protected failure evidence retained",flush=True)
        raise
if __name__=="__main__":main()
