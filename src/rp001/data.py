from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib, json
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
TRAIN_SHA="963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"
@dataclass
class LandmarkData:
    a: np.ndarray
    z: np.ndarray
    y: np.ndarray | None
    ids: np.ndarray
    B: np.ndarray
    source: str
def load_training():
    path=ROOT/"data/raw/train_FD001.txt"
    assert hashlib.sha256(path.read_bytes()).hexdigest()==TRAIN_SHA
    raw=np.loadtxt(path)
    assert raw.shape==(20631,26) and np.isfinite(raw).all()
    return {i:raw[raw[:,0]==i] for i in range(1,101)}
def manifest():
    return json.loads((ROOT/"configs/proposed_split_manifest.json").read_text())
def fit_preprocessor(engines, ids):
    rows=[]
    weights=[]
    byid={r["engine"]:r for r in manifest()}
    for i in ids:
        c=byid[int(i)]["proposed_cutoff"]
        prefix=engines[int(i)][engines[int(i)][:,1]<=c,5:]
        assert len(prefix)==c
        rows.append(prefix)
        weights.append(np.full(c,1.0/(len(ids)*c)))
    x=np.vstack(rows)
    weight=np.concatenate(weights)
    mean=np.sum(x*weight[:,None],axis=0)
    sd=np.sqrt(np.sum((x-mean)**2*weight[:,None],axis=0))
    retained=sd>1e-8
    standardized=(x[:,retained]-mean[retained])/sd[retained]
    cov=standardized.T@(standardized*weight[:,None])
    eig,vec=np.linalg.eigh(cov)
    pc=vec[:,-1]
    if pc[np.argmax(np.abs(pc))]<0: pc=-pc
    scale=np.sqrt(eig[-1])
    return {"mean":mean,"sd":sd,"retained":retained,"pc":pc,"pc_scale":scale,
            "fit_ids":np.asarray(ids),"pc1_explained_ratio":float(eig[-1]/eig.sum())}
def transform_prefix(rows, c, pre):
    allowed=rows[rows[:,1]<=c]
    assert len(allowed)==c and np.max(allowed[:,1])<=c
    x=allowed[-min(30,c):,5:]
    z=((x[:,pre["retained"]]-pre["mean"][pre["retained"]])/pre["sd"][pre["retained"]])@pre["pc"]/pre["pc_scale"]
    return z
def make_dataset(engines, pre, roles=("fit",), allow_calibration=False):
    entries=[r for r in manifest() if r["eligible_alive"] and r["role"] in roles]
    if "calibration" in roles and not allow_calibration:
        raise PermissionError("Calibration outcomes require a frozen selection record.")
    aa,zz,yy,ids=[],[],[],[]
    for r in entries:
        i,c=r["engine"],r["proposed_cutoff"]
        rows=engines[i]
        assert c<int(rows[-1,1])
        aa.append([1.,np.log(c/100.)])
        zz.append(transform_prefix(rows,c,pre))
        yy.append(np.log(rows[-1,1]-c))
        ids.append(i)
    assert all(len(z)==30 for z in zz)
    B=np.column_stack((np.ones(30),np.arange(-29,1)/30.))
    return LandmarkData(np.array(aa),np.array(zz),np.array(yy),np.array(ids),B,
                        "FD001 training landmarks; roles="+",".join(roles))
def truth_parameters(rho=0.5, weak=False):
    return {"beta":np.array([np.log(100),-0.40]),"gamma":np.array([-0.35,0.15]) if not weak else np.array([-0.03,0.02]),
            "Gamma":np.array([[0.10,0.50],[-0.10,-0.25]]),
            "tau":np.array([0.45,0.30]),"r_g":0.20,"sigma_z":0.30,"sigma_r":0.25,"rho":rho}
def generate_synthetic(n, seed, rho=0.5, weak=False, w=30):
    rng=np.random.default_rng(seed)
    theta=truth_parameters(rho,weak)
    c=rng.integers(30,251,size=n)
    a=np.column_stack((np.ones(n),np.log(c/100)))
    B=np.column_stack((np.ones(w),np.arange(-(w-1),1)/30.))
    S=np.diag(theta["tau"])@np.array([[1.,theta["r_g"]],[theta["r_g"],1.]])@np.diag(theta["tau"])
    g=rng.multivariate_normal(np.zeros(2),S,size=n)+a@theta["Gamma"].T
    K=rho**np.abs(np.arange(w)[:,None]-np.arange(w)[None,:])
    e=rng.multivariate_normal(np.zeros(w),theta["sigma_z"]**2*K,size=n)
    z=g@B.T+e
    y=a@theta["beta"]+g@theta["gamma"]+rng.normal(0,theta["sigma_r"],size=n)
    return LandmarkData(a,z,y,np.arange(n),B,f"synthetic seed={seed}; n={n}; rho={rho}; weak={weak}"),theta
def features(data, full=False):
    w=data.z.shape[1]
    if w>=2:
        coef=np.linalg.lstsq(data.B,data.z.T,rcond=None)[0].T
        residual=data.z-coef@data.B.T
        rs=np.sqrt(np.sum(residual**2,axis=1)/(w-2)) if w>=3 else np.zeros(len(data.ids))
    else:
        coef=np.column_stack((data.z[:,0],np.zeros(len(data.ids))))
        rs=np.zeros(len(data.ids))
    if full:
        grid=np.linspace(0,w-1,30)
        seq=np.array([np.interp(grid,np.arange(w),z) for z in data.z])
        return np.column_stack((data.a[:,1],seq))
    return np.column_stack((data.a[:,1],coef,rs))
