"""Vectorized AR(1)/two-dimensional Woodbury prediction, independently checked dense."""
import numpy as np
from .model import numpy_terms

def arrays(idata):
    return {n:idata.posterior[n].values.reshape((-1,)+idata.posterior[n].shape[2:]) for n in ('beta','gamma','Gamma','tau','r_g','sigma_z','sigma_r','rho')}

def sensor_terms(p,data,batch=1000):
    n=len(p['rho']);m=len(data.ids);w=data.z.shape[1]
    lz=np.empty((n,m));mean=np.empty_like(lz);var=np.empty_like(lz)
    for begin in range(0,n,batch):
        sl=slice(begin,min(begin+batch,n));rho=p['rho'][sl];sz=p['sigma_z'][sl];tau=p['tau'][sl];rg=p['r_g'][sl]
        s00=tau[:,0]**2;s11=tau[:,1]**2;s01=tau[:,0]*tau[:,1]*rg;ds=s00*s11-s01**2
        mu0=np.einsum('ma,nka->nmk',data.a,p['Gamma'][sl])
        u=data.z[None,:,:]-np.einsum('nmk,wk->nmw',mu0,data.B)
        wb=np.broadcast_to(data.B,(len(rho),w,2)).copy();wu=u.copy()
        if w>1:
            fac=np.sqrt(1-rho**2)
            wb[:,1:]=(data.B[None,1:]-rho[:,None,None]*data.B[None,:-1])/fac[:,None,None]
            wu[:,:,1:]=(u[:,:,1:]-rho[:,None,None]*u[:,:,:-1])/fac[:,None,None]
        J=np.einsum('nwk,nwl->nkl',wb,wb)/sz[:,None,None]**2
        a00=s11/ds+J[:,0,0];a11=s00/ds+J[:,1,1];a01=-s01/ds+J[:,0,1];da=a00*a11-a01**2
        V=np.empty((len(rho),2,2));V[:,0,0]=a11/da;V[:,1,1]=a00/da;V[:,0,1]=V[:,1,0]=-a01/da
        b=np.einsum('nmw,nwk->nmk',wu,wb)/sz[:,None,None]**2
        delta=np.einsum('nmk,nkl->nml',b,V)
        quadratic=np.sum(wu**2,axis=2)/sz[:,None]**2-np.sum(b*delta,axis=2)
        ld=w*np.log(sz**2)+(w-1)*np.log(1-rho**2)+np.log(ds)+np.log(da)
        lz[sl]=-.5*(w*np.log(2*np.pi)+ld[:,None]+quadratic)
        mean[sl]=np.einsum('ma,na->nm',data.a,p['beta'][sl])+np.einsum('nmk,nk->nm',mu0+delta,p['gamma'][sl])
        vg=np.einsum('nk,nkl,nl->n',p['gamma'][sl],V,p['gamma'][sl])
        var[sl]=(p['sigma_r'][sl]**2+vg)[:,None]
    if not all(np.isfinite(v).all() for v in (lz,mean,var)) or np.any(var<=0): raise ValueError('Invalid predictive mixture')
    return lz,mean,var