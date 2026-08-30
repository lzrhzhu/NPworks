"""Insulated circular hole: FEM estimate of the flux concentration factor."""
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})

def solve(nt, nr, grading=1.0, a=1.0, R=5.0, G=1.0):
    s = np.linspace(0.0, 1.0, nr + 1)
    r = a + (R - a) * s**grading
    th = np.linspace(0, 2*np.pi, nt, endpoint=False)
    rr, tt = np.meshgrid(r, th, indexing='ij'); x=(rr*np.cos(tt)).ravel(); y=(rr*np.sin(tt)).ravel()
    def nid(k,m): return k*nt + m % nt
    tris=[]
    for k in range(nr):
        for m in range(nt):
            tris += [(nid(k,m),nid(k+1,m),nid(k+1,m+1)), (nid(k,m),nid(k+1,m+1),nid(k,m+1))]
    n=x.size; K=np.zeros((n,n))
    for ia,ib,ic in tris:
        xe=x[[ia,ib,ic]]; ye=y[[ia,ib,ic]]; det=(xe[1]-xe[0])*(ye[2]-ye[0])-(xe[2]-xe[0])*(ye[1]-ye[0]); A=abs(det)/2
        b=np.array([ye[1]-ye[2],ye[2]-ye[0],ye[0]-ye[1]]); c=np.array([xe[2]-xe[1],xe[0]-xe[2],xe[1]-xe[0]])
        Ke=(np.outer(b,b)+np.outer(c,c))/(4*A); ids=[ia,ib,ic]
        for i in range(3):
            for j in range(3): K[ids[i],ids[j]] += Ke[i,j]
    outer=np.array([nid(nr,m) for m in range(nt)]); bc=-G*x[outer]*(1+a*a/(x[outer]**2+y[outer]**2))
    free=np.ones(n,dtype=bool); free[outer]=False; T=np.zeros(n); T[outer]=bc
    T[free]=np.linalg.solve(K[np.ix_(free,free)], -K[np.ix_(free,outer)]@bc)
    hole=np.array([nid(0,m) for m in range(nt)]); dth=2*np.pi/nt
    qt=-(np.roll(T[hole],-1)-np.roll(T[hole],1))/(2*a*dth)
    return x,y,T,np.max(np.abs(qt))

cases=[(24,8),(36,12),(48,16),(72,24)]; factors=[]; uniform=[]
for nt,nr in cases:
    x,y,T,qmax=solve(nt,nr,1.7); factors.append(qmax)
    uniform.append(solve(nt,nr,1.0)[3])
    print(f'Ntheta={nt:3d}, Nr={nr:2d}, graded={qmax:.4f}, uniform={uniform[-1]:.4f}')
x,y,T,qmax=solve(72,24,1.7)
fig,ax=plt.subplots(figsize=(6.4,4.8)); cf=ax.tricontourf(x,y,T,levels=24,cmap='inferno'); fig.colorbar(cf,ax=ax,label='T (G a)')
ax.set_aspect('equal'); ax.set_xlabel('x (a)'); ax.set_ylabel('y (a)'); ax.set_title('Insulated circular hole: FEM temperature field'); plt.tight_layout(); plt.suptitle('fem_circular_hole')
fig,ax=plt.subplots(figsize=(6.4,4.0)); dof=np.array([nt*(nr+1) for nt,nr in cases]); ax.semilogx(dof,factors,'o-',label='graded radial mesh'); ax.semilogx(dof,uniform,'s--',label='uniform radial mesh'); ax.axhline(2,color='k',ls=':',label='analytical value 2'); ax.set_xlabel('degrees of freedom'); ax.set_ylabel('q_max / q_infinity'); ax.legend(frameon=False); plt.tight_layout(); plt.suptitle('fem_circular_hole_convergence')
print(f'finest concentration={qmax:.4f}, analytical=2.0000'); plt.show()
