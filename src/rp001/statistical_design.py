"""Lead-executed calibration mathematics and pipeline-uncertainty illustration.
Synthetic only; no primary comparison, no official benchmark evaluation.
"""
import hashlib,json,math,time
from pathlib import Path
import numpy as np
from scipy.stats import beta,norm,t
from .metrics import conformal_rank,calibrate,apply_correction,interval_score
from .data import ROOT
def calibration_design():
    rng=np.random.default_rng(8103301)
    rows=[]
    B=5000
    for n in (9,19,25,30,50,100):
        k=conformal_rank(n)
        scores=np.abs(rng.normal(size=(B,n)))
        threshold=np.partition(scores,k-1,axis=1)[:,k-1]
        conditional=2*norm.cdf(threshold)-1
        theory=beta(k,n+1-k)
        rows.append({"n_calibration":n,"rank":k,"rank_coverage":k/(n+1),
                     "coverage_mean_theory":float(theory.mean()),"coverage_sd_theory":float(theory.std()),
                     "conditional_coverage95_range_theory":theory.ppf([.025,.975]).tolist(),
                     "prob_conditional_coverage_lt90_theory":float(theory.cdf(.9)),
                     "simulated_mean_conditional_coverage":float(conditional.mean()),
                     "mean_mcse":float(conditional.std(ddof=1)/math.sqrt(B)),
                     "simulated_conditional_coverage95_range":np.quantile(conditional,[.025,.975]).tolist(),
                     "simulation_count":B})
    q25=np.partition(np.abs(rng.normal(size=(B,25))),23,axis=1)[:,23]
    shifted=2*norm.cdf(q25/1.5)-1
    return {"finite_rank_formula":"ceil((n+1)*(1-alpha)); alpha=.10",
            "n25_wrong_rank23_ideal_coverage":23/26,
            "n25_correct_rank24_ideal_coverage":24/26,
            "continuous_score_conditional_coverage_law":"Beta(k,n+1-k), conditional fixed fit; ties/nonshrinking may overcover",
            "design_rows":rows,"shift_illustration":{"target_score_sd_multiple":1.5,
                 "mean_coverage":float(shifted.mean()),"mcse":float(shifted.std(ddof=1)/math.sqrt(B)),
                 "scope":"Synthetic score-distribution mismatch, not measured official-test shift"},
            "seed":8103301,"official_test_access":False}
def pipeline_variance():
    rng=np.random.default_rng(8103302)
    betatrue=np.array([np.log(100),-.4,-.35,.15]);noise=.25
    def generate(n):
        age=np.log(rng.integers(30,251,n)/100)
        health=.5*age+rng.normal(0,.45,n);slope=-.25*age+rng.normal(0,.3,n)
        X=np.column_stack((np.ones(n),age,health,slope))
        R=np.exp(X@betatrue+rng.normal(0,noise,n))
        return X,R
    def fit():
        X,R=generate(56);coef=np.linalg.lstsq(X,np.log(R),rcond=None)[0]
        rank=np.linalg.matrix_rank(X);df=len(R)-rank
        sigma=np.sqrt(np.sum((np.log(R)-X@coef)**2)/df)
        inv=np.linalg.pinv(X.T@X)
        return coef,sigma,inv,df
    def endpoints(X,fit):
        coef,sigma,inv,df=fit
        width=t.ppf(.95,df)*sigma*np.sqrt(1+np.sum((X@inv)*X,axis=1))
        return np.exp(X@coef-width),np.exp(X@coef+width)
    pipeline_means=[];within=[];qvalues=[]
    # Includes refitting regression and replacing calibration cohorts; no HPO/PCA/Bayesian refits.
    for _ in range(400):
        fitted=fit()
        Xcal,Rcal=generate(25);lo,up=endpoints(Xcal,fitted)
        q=calibrate(Rcal,lo,up)
        scores=[]
        for _ in range(40):
            X,R=generate(100);lo,up=endpoints(X,fitted)
            lo,up=apply_correction(lo,up,q)
            scores.append(float(interval_score(R,lo,up).mean()))
        pipeline_means.append(np.mean(scores));within.append(np.var(scores,ddof=1));qvalues.append(q)
    within_mean=float(np.mean(within))
    between_raw=float(np.var(pipeline_means,ddof=1))
    between_debiased=max(0.,between_raw-within_mean/40)
    return {"n_pipeline_realizations":400,"assessment_repetitions_per_pipeline":40,
            "engines_per_assessment":100,"n_fitting":56,"n_calibration":25,
            "within_fixed_pipeline_variance_mean":within_mean,
            "between_pipeline_variance_mc_debiased":between_debiased,
            "total_variance_law_estimate":within_mean+between_debiased,
            "fixed_pipeline_sd":math.sqrt(within_mean),
            "all_pipeline_sd":math.sqrt(within_mean+between_debiased),
            "correction_quantiles":np.quantile(qvalues,[.025,.5,.975]).tolist(),
            "pipeline_mean_score_quantiles":np.quantile(pipeline_means,[.025,.5,.975]).tolist(),
            "seed":8103302,
            "scope":"Synthetic Gaussian-regression/conformal illustration only. Includes fit+calibration variation; excludes HPO, PCA, Bayesian sampling and data-selection variation. Not an uncertainty estimate for proposed primary comparison."}
def bootstrap_design():
    rng=np.random.default_rng(8103303)
    # Pilot assess approximation in an ideal Normal and a skewed centered score-difference law.
    simulations=1000;resamples=1000;n=100
    rows=[]
    for distribution in ("normal","centered_lognormal"):
        covered=0;rejected=0;invalid=0
        for _ in range(simulations):
            d=rng.normal(size=n) if distribution=="normal" else rng.lognormal(0,1,size=n)-np.exp(.5)
            m=d.mean();se=d.std(ddof=1)/math.sqrt(n)
            sample=d[rng.integers(0,n,size=(resamples,n))]
            sem=sample.std(axis=1,ddof=1)/math.sqrt(n)
            good=sem>0
            if good.mean()<.99: invalid+=1;continue
            pivot=(sample[good].mean(axis=1)-m)/sem[good]
            low=m-np.quantile(pivot,.975)*se;up=m-np.quantile(pivot,.025)*se
            oneup=m-np.quantile(pivot,.05)*se
            covered+=int(low<=0<=up);rejected+=int(oneup<0)
        valid=simulations-invalid
        coverage=covered/valid;reject=rejected/valid
        rows.append({"distribution":distribution,"valid_simulations":valid,"invalid":invalid,
                     "two_sided95_coverage":coverage,"coverage_mcse":math.sqrt(coverage*(1-coverage)/valid),
                     "one_sided_false_positive":reject,"false_positive_mcse":math.sqrt(reject*(1-reject)/valid)})
    return {"results":rows,"simulations":simulations,"bootstrap_resamples_each":resamples,
            "n_engines":n,"seed":8103303,"scope":"Synthetic bootstrap operating characteristics; no observed primary test. Heavy influence can invalidate approximation; no favorable fallback selected."}
def main():
    start=time.perf_counter()
    path=ROOT/"results/pilot/statistical_design.json"
    if path.exists():raise FileExistsError("Preserve prior design result")
    path.parent.mkdir(parents=True,exist_ok=True)
    result={"calibration":calibration_design(),"pipeline_uncertainty":pipeline_variance(),
            "bootstrap_design":bootstrap_design(),"status":"EXECUTED_EXPLORATORY_DESIGN_ONLY",
            "wall_seconds":time.perf_counter()-start,"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "official_test_access":False,"confirmatory":False}
    path.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"n25":result["calibration"]["design_rows"][2],
                      "pipeline_uncertainty":result["pipeline_uncertainty"],
                      "bootstrap_design":result["bootstrap_design"],"wall_seconds":result["wall_seconds"]}))
if __name__=="__main__":main()
