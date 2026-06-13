import numpy as np
from pyscf.dft import libxc

print("VWN correlation check:")
for rho in [0.01, 0.1, 0.5, 1.0]:
    rs = (3.0/(4*np.pi*rho))**(1.0/3.0)
    exc, vxc, _, _ = libxc.eval_xc("lda,vwn", np.array([rho]), spin=0)
    print(f"  rho={rho:.2f}: rs={rs:.4f}, eps_c={exc[0]:.8f}, V_c={vxc[0][0]:.8f}")

# Check LDA exchange
print("\nLDA exchange check:")
for rho in [0.01, 0.1, 0.5, 1.0]:
    exc, vxc, _, _ = libxc.eval_xc("lda,", np.array([rho]), spin=0)
    ex_ours = -0.75*(3.0/np.pi)**(1.0/3.0)*rho**(1.0/3.0)
    vx_ours = -(3.0/np.pi)**(1.0/3.0)*rho**(1.0/3.0)
    print(f"  rho={rho:.2f}: PySCF eps_x={exc[0]:.8f}, ours={ex_ours:.8f}, diff={abs(exc[0]-ex_ours):.2e}")
    print(f"           PySCF V_x  ={vxc[0][0]:.8f}, ours={vx_ours:.8f}, diff={abs(vxc[0][0]-vx_ours):.2e}")

# Check full LDA (exchange + correlation)
print("\nFull LDA (exchange + VWN correlation) check:")
for rho in [0.01, 0.1, 0.5, 1.0]:
    exc, vxc, _, _ = libxc.eval_xc("lda,vwn", np.array([rho]), spin=0)
    print(f"  rho={rho:.2f}: eps_xc={exc[0]:.8f}, V_xc={vxc[0][0]:.8f}")

# Detailed grid test: compute E_xc for H2 at R=1.4 with PySCF's grid
print("\nH2 LDA/STO-3G E_xc from PySCF grid:")
from pyscf import gto, dft
R = 1.4
mol = gto.M(atom=f'H 0 0 {-R/2}; H 0 0 {R/2}', basis='sto-3g', unit='bohr', verbose=0)
mf = dft.RKS(mol)
mf.xc = 'lda,vwn'
mf.grids.level = 3
mf.kernel()
print(f"  E_total = {mf.e_tot:.6f}")
dm = mf.make_rdm1()
rho = mf.numint.get_rho(mol, dm, mf.grids)
Ne = np.dot(rho, mf.grids.weights)
print(f"  N_elec from grid = {Ne:.6f}")
print(f"  Grid: {len(mf.grids.coords)} points, level={mf.grids.level}")
# Compute E_xc manually
exc, vxc, _, _ = libxc.eval_xc('lda,vwn', rho, spin=0)
E_xc_grid = np.dot(mf.grids.weights, rho * exc[0])
print(f"  E_xc from grid = {E_xc_grid:.6f}")
