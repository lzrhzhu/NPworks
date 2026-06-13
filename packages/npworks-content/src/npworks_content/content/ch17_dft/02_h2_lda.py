# -*- coding: utf-8 -*-
"""
15.5.2 H2 Molecule: KS-DFT with LDA, STO-3G basis
Reuses ch14 Gaussian integrals; replaces HF exchange with LDA V_xc

H_KS[mu,nu] = H_core[mu,nu] + J_H[mu,nu] + V_xc[mu,nu]
  J_H[mu,nu] = sum_{lam,sig} P[lam,sig] * (mu,nu|lam,sig)    [analytic ERI]
  V_xc[mu,nu] = sum_grid w_i * g_mu(r_i) * g_nu(r_i) * V_xc(rho(r_i))  [numerical]

E_total = Tr[P . H_core] + E_H + E_xc + E_nuc
  E_H   = 0.5 * sum P[mu,nu] P[lam,sig] (mu,nu|lam,sig)
  E_xc  = sum_grid w_i * rho(r_i) * eps_xc(rho(r_i))
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf
from scipy.integrate import quad

STO3G_EXP = np.array([3.42525091, 0.62391373, 0.16885540])
STO3G_COEF = np.array([0.15432897, 0.53532814, 0.44463454])
STO3G_NORM = (2.0 * STO3G_EXP / np.pi) ** 0.75

def boys0(T):
    if T < 1e-14:
        return 1.0
    return 0.5 * np.sqrt(np.pi / T) * erf(np.sqrt(T))

def prim_overlap(a, b, A, B):
    p = a + b
    return (np.pi / p) ** 1.5 * np.exp(-a * b / p * np.sum((A - B) ** 2))

def prim_kinetic(a, b, A, B):
    p = a + b
    R2 = np.sum((A - B) ** 2)
    S = prim_overlap(a, b, A, B)
    return a * b / p * (3.0 - 2.0 * a * b * R2 / p) * S

def prim_nuclear(a, b, A, B, C, Zc):
    p = a + b
    P = (a * A + b * B) / p
    RPC2 = np.sum((P - C) ** 2)
    return -2.0 * np.pi / p * Zc * np.exp(-a * b / p * np.sum((A - B) ** 2)) * boys0(p * RPC2)

def prim_eri(a, b, g, d, A, B, C, D):
    p = a + b; q = g + d
    mu_ab = a * b / p; mu_cd = g * d / q
    RAB2 = np.sum((A - B) ** 2); RCD2 = np.sum((C - D) ** 2)
    P = (a * A + b * B) / p; Q = (g * C + d * D) / q
    RPQ2 = np.sum((P - Q) ** 2)
    return 2.0 * np.pi ** 2.5 / (p * q * np.sqrt(p + q)) * \
        np.exp(-mu_ab * RAB2 - mu_cd * RCD2) * boys0(p * q / (p + q) * RPQ2)

def ctr_ov(di, ai, Ni, dj, aj, Nj, Ri, Rj):
    return sum(da * db * na * nb * prim_overlap(a, b, Ri, Rj)
               for a, da, na in zip(ai, di, Ni) for b, db, nb in zip(aj, dj, Nj))

def ctr_kin(di, ai, Ni, dj, aj, Nj, Ri, Rj):
    return sum(da * db * na * nb * prim_kinetic(a, b, Ri, Rj)
               for a, da, na in zip(ai, di, Ni) for b, db, nb in zip(aj, dj, Nj))

def ctr_nuc(di, ai, Ni, dj, aj, Nj, Ri, Rj, nuclei):
    return sum(da * db * na * nb * prim_nuclear(a, b, Ri, Rj, Rk, Zk)
               for a, da, na in zip(ai, di, Ni) for b, db, nb in zip(aj, dj, Nj)
               for Rk, Zk in nuclei)

def ctr_eri(di, ai, Ni, dj, aj, Nj, dk, ak, Nk, dl, al, Nl, Ri, Rj, Rk, Rl):
    return sum(da * db * dg * dd * na * nb * ng * nd *
               prim_eri(a, b, g, d, Ri, Rj, Rk, Rl)
               for a, da, na in zip(ai, di, Ni) for b, db, nb in zip(aj, dj, Nj)
               for g, dg, ng in zip(ak, dk, Nk) for d, dd, nd in zip(al, dl, Nl))

def build_matrices(R, Z1=1.0, Z2=1.0):
    RA = np.array([-R / 2, 0.0, 0.0]); RB = np.array([R / 2, 0.0, 0.0])
    nuclei = [(RA, Z1), (RB, Z2)]
    c, a, N = STO3G_COEF, STO3G_EXP, STO3G_NORM
    ctrs = [RA, RB]; K = 2
    S = np.zeros((K, K)); H = np.zeros((K, K))
    eri = np.zeros((K, K, K, K))
    for i in range(K):
        for j in range(K):
            S[i, j] = ctr_ov(c, a, N, c, a, N, ctrs[i], ctrs[j])
            H[i, j] = ctr_kin(c, a, N, c, a, N, ctrs[i], ctrs[j]) + \
                       ctr_nuc(c, a, N, c, a, N, ctrs[i], ctrs[j], nuclei)
            for k in range(K):
                for l in range(K):
                    eri[i, j, k, l] = ctr_eri(c, a, N, c, a, N, c, a, N, c, a, N,
                                               ctrs[i], ctrs[j], ctrs[k], ctrs[l])
    return S, H, eri, Z1 * Z2 / R, ctrs

def vwn_ec(rs):
    if rs < 1e-14: return 0.0
    A, x0, b, c = 0.0621814, -0.10498, 3.72744, 12.9352
    Q = np.sqrt(4 * c - b ** 2); x = np.sqrt(rs)
    Xx = x**2 + b*x + c; Xx0 = x0**2 + b*x0 + c
    return A/2 * (np.log(x**2/Xx) + 2*b/Q*np.arctan(Q/(2*x+b))
                  - b*x0/Xx0*(np.log((x-x0)**2/Xx) + 2*(b+2*x0)/Q*np.arctan(Q/(2*x+b))))

def vwn_v(rs):
    if rs < 1e-14: return 0.0
    h = 1e-6 * max(rs, 1e-10)
    dec = (vwn_ec(rs + h) - vwn_ec(rs - h)) / (2 * h)
    return vwn_ec(rs) - rs / 3.0 * dec

def eps_xc_vec(rho):
    out = np.zeros_like(rho)
    m = rho > 1e-30
    rs = (3.0 / (4.0 * np.pi * rho[m])) ** (1.0 / 3.0)
    out[m] = -0.75 * (3.0 / np.pi) ** (1.0 / 3.0) * rho[m] ** (1.0 / 3.0)
    rs_safe = np.where(rs > 1e-14, rs, 1.0)
    e_vwn = np.array([vwn_ec(r) for r in rs_safe])
    out[m] += e_vwn
    return out

def v_xc_vec(rho):
    out = np.zeros_like(rho)
    m = rho > 1e-30
    out[m] = -(3.0 / np.pi) ** (1.0 / 3.0) * rho[m] ** (1.0 / 3.0)
    rs = (3.0 / (4.0 * np.pi * rho[m])) ** (1.0 / 3.0)
    v_vwn = np.array([vwn_v(r) for r in rs])
    out[m] += v_vwn
    return out

def eval_basis_on_grid(grid, ctrs):
    c, a, N = STO3G_COEF, STO3G_EXP, STO3G_NORM
    K = len(ctrs)
    phi = np.zeros((K, len(grid)))
    for mu in range(K):
        for ai, di, ni in zip(a, c, N):
            phi[mu] += di * ni * np.exp(-ai * np.sum((grid - ctrs[mu]) ** 2, axis=1))
    return phi

def make_mol_grid(ctrs, n_r=35, n_ang=14):
    R_AB = np.sqrt(np.sum((ctrs[0] - ctrs[1]) ** 2))
    R_max = max(6.0, R_AB / 2 + 5.0)
    x_gl, w_gl = np.polynomial.legendre.leggauss(n_ang)
    cos_theta = x_gl; sin_theta = np.sqrt(1 - cos_theta ** 2)
    phis = np.linspace(0, 2 * np.pi, 2 * n_ang, endpoint=False)
    dphi = 2 * np.pi / (2 * n_ang)
    ang_pts = []; ang_wts = []
    for i, ct in enumerate(cos_theta):
        for phi in phis:
            ang_pts.append([ct, sin_theta[i] * np.cos(phi), sin_theta[i] * np.sin(phi)])
            ang_wts.append(w_gl[i] * dphi)
    ang_pts = np.array(ang_pts); ang_wts = np.array(ang_wts)
    r_pts, r_wts = np.polynomial.legendre.leggauss(n_r)
    r_pts = R_max * (r_pts + 1) / 2
    r_wts = r_wts * R_max / 2
    all_pts = []; all_wts = []
    n_ang_pts = len(ang_pts)
    for iA, RA in enumerate(ctrs):
        for ir, r in enumerate(r_pts):
            for ia in range(n_ang_pts):
                pt = RA + r * ang_pts[ia]
                all_pts.append(pt)
                all_wts.append(r_wts[ir] * ang_wts[ia] * r ** 2)
    all_pts = np.array(all_pts); all_wts = np.array(all_wts)
    if len(ctrs) == 2:
        rA = np.sqrt(np.sum((all_pts - ctrs[0]) ** 2, axis=1))
        rB = np.sqrt(np.sum((all_pts - ctrs[1]) ** 2, axis=1))
        R_ab = max(np.sqrt(np.sum((ctrs[0] - ctrs[1]) ** 2)), 1e-10)
        mu = (rA - rB) / R_ab
        mu = np.clip(mu, -1, 1)
        s = 1.5 * mu - 0.5 * mu ** 3
        s = 1.5 * s - 0.5 * s ** 3
        s = 1.5 * s - 0.5 * s ** 3
        wA = (1 - s) / 2; wB = (1 + s) / 2
        n_per_atom = len(all_wts) // 2
        all_wts[:n_per_atom] *= wA[:n_per_atom]
        all_wts[n_per_atom:] *= wB[n_per_atom:]
    return all_pts, all_wts

def compute_xc_quantities(P, phi_grid, grid_wts):
    rho_grid = np.einsum('mn,mn->', np.einsum('m,mn->mn', P.diagonal(), phi_grid), phi_grid)
    rho_grid = np.zeros(phi_grid.shape[1])
    for mu in range(P.shape[0]):
        for nu in range(P.shape[1]):
            rho_grid += P[mu, nu] * phi_grid[mu] * phi_grid[nu]
    rho_grid = np.maximum(rho_grid, 0)
    E_xc = np.sum(grid_wts * rho_grid * eps_xc_vec(rho_grid))
    vxc = v_xc_vec(rho_grid)
    Vxc_mat = np.zeros((P.shape[0], P.shape[0]))
    for mu in range(P.shape[0]):
        for nu in range(mu + 1):
            Vxc_mat[mu, nu] = np.sum(grid_wts * phi_grid[mu] * phi_grid[nu] * vxc)
            Vxc_mat[nu, mu] = Vxc_mat[mu, nu]
    return E_xc, Vxc_mat

def run_dft_scf(S, H_core, eri, ctrs, E_nuc, Nel=2, max_iter=200, conv=1e-10):
    K = S.shape[0]
    s_eval, s_evec = np.linalg.eigh(S)
    X = s_evec @ np.diag(1.0 / np.sqrt(s_eval))
    grid_pts, grid_wts = make_mol_grid(ctrs)
    phi_grid = eval_basis_on_grid(grid_pts, ctrs)
    P = np.zeros((K, K))
    energies = []
    for iteration in range(max_iter):
        J_H = np.zeros((K, K))
        for mu in range(K):
            for nu in range(K):
                for lam in range(K):
                    for sig in range(K):
                        J_H[mu, nu] += P[lam, sig] * eri[mu, nu, lam, sig]
        E_xc, Vxc_mat = compute_xc_quantities(P, phi_grid, grid_wts)
        H_KS = H_core + J_H + Vxc_mat
        E_H = 0.5 * np.sum(P * J_H)
        E_elec = np.sum(P * H_core) + E_H + E_xc
        energies.append(E_elec + E_nuc)
        if iteration > 0 and abs(energies[-1] - energies[-2]) < conv:
            break
        Fp = X.T @ H_KS @ X
        eps, Cp = np.linalg.eigh(Fp)
        C = X @ Cp
        P_new = np.zeros((K, K))
        for m in range(Nel // 2):
            for i in range(K):
                for j in range(K):
                    P_new[i, j] += 2.0 * C[i, m] * C[j, m]
        P = P_new
    return energies[-1], eps, C, P, energies, E_xc

def run_hf_scf(S, H_core, eri, E_nuc, Nel=2, max_iter=200, conv=1e-10):
    K = S.shape[0]
    s_eval, s_evec = np.linalg.eigh(S)
    X = s_evec @ np.diag(1.0 / np.sqrt(s_eval))
    P = np.zeros((K, K))
    energies = []
    for iteration in range(max_iter):
        G = np.zeros((K, K))
        for i in range(K):
            for j in range(K):
                for k in range(K):
                    for l in range(K):
                        G[i, j] += P[k, l] * (eri[i, j, k, l] - 0.5 * eri[i, k, j, l])
        F = H_core + G
        E_elec = 0.5 * np.sum(P * (H_core + F))
        energies.append(E_elec + E_nuc)
        if iteration > 0 and abs(energies[-1] - energies[-2]) < conv:
            break
        Fp = X.T @ F @ X
        eps, Cp = np.linalg.eigh(Fp)
        C = X @ Cp
        P_new = np.zeros((K, K))
        for m in range(Nel // 2):
            for i in range(K):
                for j in range(K):
                    P_new[i, j] += 2.0 * C[i, m] * C[j, m]
        P = P_new
    return energies[-1], eps, C, P, energies

print("=" * 65)
print("H2 Molecule: KS-DFT (LDA) vs HF, STO-3G Basis")
print("=" * 65)

R_eq = 1.4
S, H_core, eri, E_nuc, ctrs = build_matrices(R_eq)
print(f"\nR = {R_eq} bohr")
print(f"Overlap S_12 = {S[0,1]:.6f}")
print(f"H_core = [{H_core[0,0]:.6f}, {H_core[0,1]:.6f}]")

E_hf_r, _, _, _, _ = run_hf_scf(S, H_core, eri, E_nuc)
E_lda_r, _, _, _, _, _ = run_dft_scf(S, H_core, eri, ctrs, E_nuc)
print(f"\nAt R = {R_eq} bohr:")
print(f"  E_HF  = {E_hf_r:.6f} Hartree")
print(f"  E_LDA = {E_lda_r:.6f} Hartree")

print("\n" + "=" * 65)
print("Potential Energy Curve: HF vs LDA")
print("=" * 65)

Rs = np.linspace(0.5, 5.0, 50)
E_hf = np.zeros(len(Rs)); E_lda = np.zeros(len(Rs))
for idx, R in enumerate(Rs):
    S, H, eri, Enuc, ctrs = build_matrices(R)
    E_hf[idx], _, _, _, _ = run_hf_scf(S, H, eri, Enuc)
    E_lda[idx], _, _, _, _, _ = run_dft_scf(S, H, eri, ctrs, Enuc)

i_hf = np.argmin(E_hf); i_lda = np.argmin(E_lda)
E_diss_hf = E_hf[-1]; E_diss_lda = E_lda[-1]
D_e_hf = abs(E_hf[i_hf] - E_diss_hf)
D_e_lda = abs(E_lda[i_lda] - E_diss_lda)
print(f"\nHF  (STO-3G): R_eq = {Rs[i_hf]:.3f} bohr, E_min = {E_hf[i_hf]:.6f}, D_e = {D_e_hf:.6f} Ha ({D_e_hf*27.2114:.3f} eV)")
print(f"LDA (STO-3G): R_eq = {Rs[i_lda]:.3f} bohr, E_min = {E_lda[i_lda]:.6f}, D_e = {D_e_lda:.6f} Ha ({D_e_lda*27.2114:.3f} eV)")
print(f"Dissociation limit: HF={E_diss_hf:.6f}, LDA={E_diss_lda:.6f}, Exact=-1.0")
print(f"Exact       : R_eq = 1.401 bohr, D_e = 0.1745 Ha (4.748 eV)")

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

ax1 = axes[0, 0]
ax1.plot(Rs, E_hf, 'r-', linewidth=2, label='HF (STO-3G)')
ax1.plot(Rs, E_lda, 'b-', linewidth=2, label='LDA (STO-3G)')
ax1.axhline(-1.0, color='gray', linestyle='--', alpha=0.5, label='2H = -1.0')
ax1.plot(Rs[i_hf], E_hf[i_hf], 'ro', markersize=8)
ax1.plot(Rs[i_lda], E_lda[i_lda], 'bs', markersize=8)
ax1.set_xlabel('R (bohr)', fontsize=12)
ax1.set_ylabel('E (Hartree)', fontsize=12)
ax1.set_title('H$_2$ Potential Energy Curve: HF vs LDA')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

ax2 = axes[0, 1]
ax2.plot(Rs, (E_hf - E_lda) * 27.2114, 'g-', linewidth=2)
ax2.set_xlabel('R (bohr)', fontsize=12)
ax2.set_ylabel('E$_{LDA}$ - E$_{HF}$ (eV)', fontsize=12)
ax2.set_title('LDA Correlation Energy')
ax2.axhline(0, color='gray', linestyle=':', alpha=0.5)
ax2.grid(True, alpha=0.3)

ax3 = axes[1, 0]
S_r, H_r, eri_r, Enuc_r, ctrs_r = build_matrices(R_eq)
_, _, C_hf, P_hf, _ = run_hf_scf(S_r, H_r, eri_r, Enuc_r)
_, _, C_lda, P_lda, _, _ = run_dft_scf(S_r, H_r, eri_r, ctrs_r, Enuc_r)
x = np.linspace(-3, 3, 300)
chi_A = np.exp(-(x + R_eq / 2) ** 2)
chi_B = np.exp(-(x - R_eq / 2) ** 2)
psi_hf = C_hf[0, 0] * chi_A + C_hf[1, 0] * chi_B
psi_lda = C_lda[0, 0] * chi_A + C_lda[1, 0] * chi_B
psi_hf /= np.max(np.abs(psi_hf)); psi_lda /= np.max(np.abs(psi_lda))
ax3.plot(x, psi_hf, 'r-', linewidth=2, label='HF $\\sigma_g$')
ax3.plot(x, psi_lda, 'b--', linewidth=2, label='LDA $\\sigma_g$')
ax3.axvline(-R_eq / 2, color='gray', linestyle=':', alpha=0.5)
ax3.axvline(R_eq / 2, color='gray', linestyle=':', alpha=0.5)
ax3.set_xlabel('x (bohr)', fontsize=12)
ax3.set_ylabel('$\\psi$ (normalized)', fontsize=12)
ax3.set_title('Bonding MO: HF vs LDA')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

ax4 = axes[1, 1]
methods = ['HF\n(STO-3G)', 'LDA\n(STO-3G)', 'HF\n(cc-pVTZ)', 'LDA\n(cc-pVTZ)', 'B3LYP\n(cc-pVTZ)', 'Expt']
Re_vals = [Rs[i_hf], Rs[i_lda], 1.389, 1.445, 1.410, 1.401]
De_vals = [D_e_hf*27.2114, D_e_lda*27.2114, 3.64, 5.20, 4.55, 4.75]
x_pos = np.arange(len(methods))
w = 0.35
ax4.bar(x_pos - w/2, [r*0.5292 for r in Re_vals], w, label='$R_e$ (A)',
        color='#3498db', alpha=0.7, edgecolor='black')
ax4.bar(x_pos + w/2, De_vals, w, label='$D_e$ (eV)',
        color='#e74c3c', alpha=0.7, edgecolor='black')
ax4.set_xticks(x_pos); ax4.set_xticklabels(methods, fontsize=8)
ax4.set_title('H$_2$: Method Comparison')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
fig.suptitle('h2_lda')
plt.show()
