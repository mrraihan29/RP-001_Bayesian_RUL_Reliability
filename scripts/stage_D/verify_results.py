"""Independent SOL arithmetic verification from frozen inputs; internal, not external replication."""
import csv,math
from decimal import Decimal
import numpy as np
from scipy.special import erfc
from common import *
from oracles import verify_evaluation,verify_mcse
def verify_results(pred,y,evaluation,numerical):
    check(not (O/"DIRECT_SOL_RESULT_VERIFICATION.json").exists(),"No verification retry")
    event("DIRECT_SOL_VERIFICATION_BEGIN")
    plan=source_check()
    payload=(O/"labels/RUL_FD001.txt").read_bytes()
    independent=np.array([float(Decimal(s.decode("ascii").strip())) for s in payload.splitlines()],dtype=np.float64)
    check(len(payload.splitlines())==100 and np.all(independent>0) and np.all(np.isfinite(independent)),"Independent label schema")
    np.testing.assert_array_equal(independent,y)
    alignment=read(O/"LABEL_ALIGNMENT.json")["rows"]
    ledger=read(B/"engine_ledger_final.json")
    for i,(a,l) in enumerate(zip(alignment,ledger,strict=True),1):
        check(a["label_row"]==a["engine"]==l["engine"]==i and a["cutoff"]==l["cutoff"] and a["RUL_cycles"]==independent[i-1],"Independent row/ID/cutoff alignment")
    score_check=verify_evaluation(y,pred["Bayesian"],pred["CQR"],evaluation)
    # Full saved cross-engine/cross-endpoint array is checked, not just MCSE summaries.
    with np.load(O/"CORRELATION_PRESERVING_NUMERICAL_ARRAYS.npz",allow_pickle=False) as arrays:
        L=arrays["lower_influence"];U=arrays["upper_influence"];H=arrays["H"]
        np.testing.assert_array_equal(arrays["joint_influence"],np.concatenate((L,U),axis=2))
        endpoint_checks=[]
        for i in range(1,101):
            with np.load(B/f"conditional_terms/engine_{i:03d}.npz",allow_pickle=False) as terms:
                mu=terms["means"];variance=terms["variances"];logw=terms["log_weights"]
                weight=np.exp(logw-np.max(logw));normalizer=float(np.mean(weight))
                for pp,probability,X in ((5,.05,L),(95,.95,U)):
                    record=read(B/f"precision/engine_{i:03d}_pooled_p{pp:02d}.json")
                    # Independent Gaussian CDF identity via erfc, separate from norm.cdf route.
                    cdf=.5*erfc((mu-record["quantile_log_rul"])/np.sqrt(2*variance))
                    reference=-record["quantile_rul"]*(weight/normalizer)*(cdf-probability)/record["weighted_mixture_density_log_rul"]
                    np.testing.assert_allclose(X[:,:,i-1],reference,rtol=2e-10,atol=1e-9)
                    endpoint_checks.append(dict(engine=i,p=probability,max_abs_residual=float(np.max(np.abs(X[:,:,i-1]-reference)))))
        gl=np.array([19. if float(v)<float(l) else -1. for v,l in zip(y,pred["Bayesian"]["lower"])])
        gu=np.array([-19. if float(v)>float(u) else 1. for v,u in zip(y,pred["Bayesian"]["upper"])])
        np.testing.assert_array_equal(gl,numerical["gradient_lower_by_engine"])
        np.testing.assert_array_equal(gu,numerical["gradient_upper_by_engine"])
        # Independent compensated vector accumulation for all 96,000 shared draw positions.
        Href=np.zeros((12,8000));comp=np.zeros_like(Href)
        for i in range(100):
            add=gl[i]*L[:,:,i]+gu[i]*U[:,:,i]
            corrected=add-comp;new=Href+corrected;comp=(new-Href)-corrected;Href=new
        Href/=100
        np.testing.assert_allclose(H,Href,rtol=1e-10,atol=1e-10)
        scalar=verify_mcse(Href,numerical)
        covariance_checks=[]
        contrast=np.r_[gl,gu]/100
        for group in numerical["batch_size_results"]:
            b=group["batch_size"];sum_cov=np.zeros((200,200))
            for c in range(12):
                joint=np.column_stack((L[c],U[c]))
                batchmeans=joint.reshape(8000//b,b,200).mean(axis=1)
                lrv=b*np.cov(batchmeans,rowvar=False,ddof=1)
                np.testing.assert_allclose(lrv,arrays[f"chain_{c}_LRV_covariance_b{b}"],rtol=1e-10,atol=1e-9)
                sum_cov+=8000*lrv/(96000**2)
            saved=arrays[f"joint_MC_covariance_b{b}"]
            np.testing.assert_allclose(sum_cov,saved,rtol=1e-10,atol=1e-10)
            projection=float(contrast@saved@contrast)
            np.testing.assert_allclose(projection,group["score_variance_cycles_squared"],rtol=1e-10,atol=1e-11)
            covariance_checks.append(dict(batch_size=b,full_200_coordinate_covariance_PASS=True,
                scalar_projection_residual=abs(projection-group["score_variance_cycles_squared"])))
    any_kink=False;kink_checks=[]
    for batch_index,b in enumerate((250,500)):
        flags=[]
        for pp,key in ((5,"lower"),(95,"upper")):
            radii=np.array([read(B/f"precision/engine_{i:03d}_pooled_p{pp:02d}.json")["batch_size_results"][batch_index]["approximate_upper_quantile_rul_mcse"] for i in range(1,101)])
            f=np.abs(y-pred["Bayesian"][key])<=3*radii
            np.testing.assert_array_equal(f,numerical["label_kink"]["by_batch_size"][batch_index][key+"_endpoint_by_engine"])
            flags.append(f)
        combined=flags[0]|flags[1]
        np.testing.assert_array_equal(combined,numerical["label_kink"]["by_batch_size"][batch_index]["any_by_engine"])
        any_kink=any_kink or bool(combined.any());kink_checks.append(dict(batch_size=b,engines_flagged=(np.flatnonzero(combined)+1).tolist()))
    ups=[g["approximate_upper_quantile_score_mcse_cycles"] for g in numerical["batch_size_results"]]
    qualified=any_kink or any(v is None or not math.isfinite(v) or v>.5 for v in ups)
    check(numerical["qualification"]["status"]==("NUMERICALLY_QUALIFIED" if qualified else "PASS"),"Independent numerical classification")
    replicas=[]
    sensitivity=read(O/"INDEPENDENT_FIT_SCORE_SENSITIVITY.json")
    for j,fit in enumerate(("v04_main_r1","v04_main_r2","v04_main_r3")):
        p={k:np.array([read(B/f"precision/engine_{i:03d}_{fit}_p{pp:02d}.json")["quantile_rul"] for i in range(1,101)])
            for k,pp in (("lower",5),("median",50),("upper",95))}
        r=read(O/f"independent_fits/{fit}_complete_score.json")
        verify_evaluation(y,p,pred["CQR"],r)
        check(sensitivity["results"][j]["paired_difference_cycles"]==r["paired_difference_cycles"],"Exact individual contrast")
        replicas.append(r["paired_difference_cycles"])
    check(sensitivity["range_cycles"]==max(replicas)-min(replicas),"Exact three-fit spread")
    # Complete Stage B inventories and all approved old public bytes remain unchanged.
    candidate=read(R/"docs/stage_B/CANDIDATE_PACKAGE_RECEIPT.json")
    rehashed=0
    for key in ("base_payload_manifest","verification_manifest","review_tables_manifest"):
        record=candidate[key];check(sha(R/record["path"])==record["sha256"],"Accepted manifest unchanged")
        directory=(R/record["path"]).parent
        for row in read(R/record["path"])["files"]:
            path=directory/row["name"] if key=="review_tables_manifest" else R/row["path"]
            check(sha(path)==row["sha256"] and path.stat().st_size==row["bytes"],"Accepted payload byte unchanged")
            rehashed+=1
    check(rehashed==3022,"Complete frozen manifest count")
    report=dict(at_utc=now(),status="PASS",verifier="Rei / SOL direct source review and independent arithmetic routes",
        external_replication=False,label_alignment="Complete rows 1..100; declared official row ordering; no embedded ID certificate",
        score_verification=score_check,endpoint_influence_checks=endpoint_checks,
        full_96000_draw_H_projection_PASS=True,scalar_batch_MCSE_checks=scalar,
        covariance_checks=covariance_checks,kink_checks=kink_checks,numerical_flag_verified=qualified,
        independent_fit_contrasts_verified=True,frozen_members_rehashed=3022,predictions_changed=False,
        source_sha256=plan["prelabel_source_sha256"],claims="Finite stored-score comparison only; conditional approximate MCSE")
    save(O/"DIRECT_SOL_RESULT_VERIFICATION.json",report)
    event("DIRECT_SOL_VERIFICATION_PASS",report_sha256=sha(O/"DIRECT_SOL_RESULT_VERIFICATION.json"))
