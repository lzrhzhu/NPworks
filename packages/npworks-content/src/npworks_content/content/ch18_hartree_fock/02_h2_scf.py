# -*- coding: utf-8 -*-
"""
16.4.2 H2 Molecule - Minimal Basis HF/SCF Calculation
STO-3G basis: 3 primitive Gaussians per H atom, K=2 contracted basis functions

Each primitive is individually normalized: g_i(r) = N_i * exp(-alpha_i * |r-R|^2)
  where N_i = (2*alpha_i/pi)^(3/4)

Contraction: phi_mu(r) = sum_i d_i * g_i(r)  (d_i = STO-3G coefficients)

All integrals computed analytically using Gaussian product theorem.
SCF iteration solves Roothaan equation: F*C = S*C*epsilon
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf

STO3G_EXPONENTS = np.array([3.42525091, 0.62391373, 0.16885540])
STO3G_COEFFICIENTS = np.array([0.15432897, 0.53532814, 0.44463454])
STO3G_NORMALIZATION = (2.0 * STO3G_EXPONENTS / np.pi) ** 0.75

def boys0(T):
    if T < 1e-14:
        return 1.0
    return 0.5 * np.sqrt(np.pi / T) * erf(np.sqrt(T))

def prim_overlap_3d(alpha, beta, RA, RB):
    p = alpha + beta
    RAB2 = np.sum((RA - RB) ** 2)
    return (np.pi / p) ** 1.5 * np.exp(-alpha * beta / p * RAB2)

def prim_kinetic_3d(alpha, beta, RA, RB):
    p = alpha + beta
    RAB2 = np.sum((RA - RB) ** 2)
    S = prim_overlap_3d(alpha, beta, RA, RB)
    return alpha * beta / p * (3.0 - 2.0 * alpha * beta * RAB2 / p) * S

def prim_nuclear_3d(alpha, beta, RA, RB, RC, Zc):
    p = alpha + beta
    mu = alpha * beta / p
    RAB2 = np.sum((RA - RB) ** 2)
    RP = (alpha * RA + beta * RB) / p
    RPC2 = np.sum((RP - RC) ** 2)
    return -2.0 * np.pi / p * Zc * np.exp(-mu * RAB2) * boys0(p * RPC2)

def prim_eri_3d(alpha, beta, gamma, delta, RA, RB, RC, RD):
    p = alpha + beta
    q = gamma + delta
    mu_ab = alpha * beta / p
    mu_cd = gamma * delta / q
    RAB2 = np.sum((RA - RB) ** 2)
    RCD2 = np.sum((RC - RD) ** 2)
    RP = (alpha * RA + beta * RB) / p
    RQ = (gamma * RC + delta * RD) / q
    RPQ2 = np.sum((RP - RQ) ** 2)
    return 2.0 * np.pi ** 2.5 / (p * q * np.sqrt(p + q)) * \
        np.exp(-mu_ab * RAB2 - mu_cd * RCD2) * \
        boys0(p * q / (p + q) * RPQ2)

def contract_overlap(di, ai, Ni, dj, aj, Nj, Ri, Rj):
    S = 0.0
    for a, da, na in zip(ai, di, Ni):
        for b, db, nb in zip(aj, dj, Nj):
            S += da * db * na * nb * prim_overlap_3d(a, b, Ri, Rj)
    return S

def contract_kinetic(di, ai, Ni, dj, aj, Nj, Ri, Rj):
    T = 0.0
    for a, da, na in zip(ai, di, Ni):
        for b, db, nb in zip(aj, dj, Nj):
            T += da * db * na * nb * prim_kinetic_3d(a, b, Ri, Rj)
    return T

def contract_nuclear(di, ai, Ni, dj, aj, Nj, Ri, Rj, nuclei):
    V = 0.0
    for a, da, na in zip(ai, di, Ni):
        for b, db, nb in zip(aj, dj, Nj):
            for Rk, Zk in nuclei:
                V += da * db * na * nb * prim_nuclear_3d(a, b, Ri, Rj, Rk, Zk)
    return V

def contract_eri(di, ai, Ni, dj, aj, Nj, dk, ak, Nk, dl, al, Nl,
                 Ri, Rj, Rk, Rl):
    V = 0.0
    for a, da, na in zip(ai, di, Ni):
        for b, db, nb in zip(aj, dj, Nj):
            for g, dg, ng in zip(ak, dk, Nk):
                for d, dd, nd in zip(al, dl, Nl):
                    V += da * db * dg * dd * na * nb * ng * nd * \
                        prim_eri_3d(a, b, g, d, Ri, Rj, Rk, Rl)
    return V

def build_integrals(R, Z1=1.0, Z2=1.0):
    RA = np.array([-R / 2.0, 0.0, 0.0])
    RB = np.array([R / 2.0, 0.0, 0.0])
    nuclei = [(RA, Z1), (RB, Z2)]
    d = STO3G_COEFFICIENTS
    a = STO3G_EXPONENTS
    N = STO3G_NORMALIZATION
    centers = [RA, RB]
    K = 2
    S = np.zeros((K, K))
    T = np.zeros((K, K))
    V = np.zeros((K, K))
    for i in range(K):
        for j in range(K):
            S[i, j] = contract_overlap(d, a, N, d, a, N, centers[i], centers[j])
            T[i, j] = contract_kinetic(d, a, N, d, a, N, centers[i], centers[j])
            V[i, j] = contract_nuclear(d, a, N, d, a, N, centers[i], centers[j], nuclei)
    H_core = T + V
    eri = np.zeros((K, K, K, K))
    for i in range(K):
        for j in range(K):
            for k in range(K):
                for l in range(K):
                    eri[i, j, k, l] = contract_eri(
                        d, a, N, d, a, N, d, a, N, d, a, N,
                        centers[i], centers[j], centers[k], centers[l])
    E_nuc = Z1 * Z2 / R
    return S, T, V, H_core, eri, E_nuc

def run_scf(S, H_core, eri, K=2, Nel=2, max_iter=200, conv=1e-12):
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
                        G[i, j] += P[k, l] * (
                            eri[i, j, k, l] - 0.5 * eri[i, k, j, l])
        F = H_core + G
        E_elec = np.sum(P * (H_core + F)) * 0.5
        energies.append(E_elec)
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
    return E_elec, eps, C, P, F, energies

def compute_total_energy(R, Z1=1.0, Z2=1.0):
    S, T, V, H_core, eri, E_nuc = build_integrals(R, Z1, Z2)
    E_elec, eps, C, P, F, energies = run_scf(S, H_core, eri)
    return E_elec + E_nuc, eps, C, P, energies

print("=" * 65)
print("H2 Molecule - STO-3G Minimal Basis HF/SCF Calculation")
print("=" * 65)

R_eq = 1.4
S, T, V, H_core, eri, E_nuc = build_integrals(R_eq)

print(f"\nBond distance R = {R_eq} bohr")
print(f"\nOverlap matrix S:")
print(f"  S = [{S[0,0]:.6f}, {S[0,1]:.6f}]")
print(f"      [{S[1,0]:.6f}, {S[1,1]:.6f}]")
print(f"\nKinetic energy matrix T:")
print(f"  T = [{T[0,0]:.6f}, {T[0,1]:.6f}]")
print(f"      [{T[1,0]:.6f}, {T[1,1]:.6f}]")
print(f"\nNuclear attraction matrix V:")
print(f"  V = [{V[0,0]:.6f}, {V[0,1]:.6f}]")
print(f"      [{V[1,0]:.6f}, {V[1,1]:.6f}]")
print(f"\nCore Hamiltonian H_core = T + V:")
print(f"  H = [{H_core[0,0]:.6f}, {H_core[0,1]:.6f}]")
print(f"      [{H_core[1,0]:.6f}, {H_core[1,1]:.6f}]")
print(f"\nTwo-electron integrals:")
print(f"  (11|11) = {eri[0,0,0,0]:.6f}")
print(f"  (11|22) = {eri[0,0,1,1]:.6f}")
print(f"  (12|12) = {eri[0,1,0,1]:.6f}")

E_tot, eps, C, P, energies = compute_total_energy(R_eq)

print(f"\nSCF Convergence ({len(energies)} iterations):")
for i, e in enumerate(energies):
    if i < 5 or i >= len(energies) - 2:
        print(f"  Iter {i+1:3d}: E_elec = {e:.10f}")
    elif i == 5:
        print(f"  ...")

print(f"\nFinal results at R = {R_eq} bohr:")
print(f"  Orbital energies: eps = [{eps[0]:.6f}, {eps[1]:.6f}]")
print(f"  E_elec  = {energies[-1]:.6f} Hartree")
print(f"  E_nuc   = {E_nuc:.6f} Hartree")
print(f"  E_total = {E_tot:.6f} Hartree")
print(f"\nMO coefficients:")
print(f"  sigma_g: C = [{C[0,0]:.6f}, {C[1,0]:.6f}]")
print(f"  sigma_u: C = [{C[0,1]:.6f}, {C[1,1]:.6f}]")
print(f"  Bond order = {np.sum(P * S) / 2:.4f}")

print("\n" + "=" * 65)
print("Potential Energy Curve: E(R) for H2")
print("=" * 65)

Rs = np.linspace(0.3, 5.0, 80)
E_hf = np.zeros(len(Rs))
for idx, R in enumerate(Rs):
    E_hf[idx], _, _, _, _ = compute_total_energy(R)

i_min = np.argmin(E_hf)
R_min = Rs[i_min]
E_min = E_hf[i_min]
D_e = abs(E_min - (-1.0))

print(f"Equilibrium distance R_eq = {R_min:.3f} bohr ({R_min*0.5292:.3f} Angstrom)")
print(f"Equilibrium energy E(R_eq) = {E_min:.6f} Hartree")
print(f"Dissociation energy D_e = {D_e:.6f} Hartree ({D_e*27.2114:.4f} eV)")

exact_Re = 1.4011
exact_De = 0.17447
print(f"\nComparison with exact (non-relativistic):")
print(f"  {'':30s} {'STO-3G':>12s} {'Exact':>12s}")
print(f"  {'R_eq (bohr)':30s} {R_min:>12.4f} {exact_Re:>12.4f}")
print(f"  {'D_e (Hartree)':30s} {D_e:>12.6f} {exact_De:>12.6f}")
print(f"  {'D_e (eV)':30s} {D_e*27.2114:>12.4f} {exact_De*27.2114:>12.4f}")

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

ax1 = axes[0, 0]
ax1.plot(Rs, E_hf, 'b-', linewidth=2, label='STO-3G HF')
ax1.axhline(-1.0, color='green', linestyle='--', alpha=0.5,
            label='2H (dissociation) = -1.0')
ax1.plot(R_min, E_min, 'ro', markersize=10, zorder=5)
ax1.annotate(f'R$_{{eq}}$={R_min:.3f}\nE={E_min:.4f}',
             xy=(R_min, E_min), xytext=(R_min + 0.5, E_min + 0.05),
             arrowprops=dict(arrowstyle='->', color='red'), fontsize=10)
ax1.set_xlabel('R (bohr)', fontsize=12)
ax1.set_ylabel('E (Hartree)', fontsize=12)
ax1.set_title('H$_2$ Potential Energy Curve (STO-3G HF)')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

ax2 = axes[0, 1]
_, _, _, _, energies_conv = compute_total_energy(R_eq)
ax2.plot(range(1, len(energies_conv) + 1), energies_conv, 'bo-', markersize=5)
ax2.set_xlabel('SCF Iteration', fontsize=12)
ax2.set_ylabel('Electronic Energy (Hartree)', fontsize=12)
ax2.set_title(f'SCF Convergence at R = {R_eq} bohr')
ax2.grid(True, alpha=0.3)
dE = [abs(energies_conv[i] - energies_conv[i - 1])
      for i in range(1, len(energies_conv))]
if len(dE) > 2:
    ax2_inset = ax2.inset_axes([0.45, 0.45, 0.5, 0.5])
    ax2_inset.semilogy(range(2, len(energies_conv) + 1), dE, 'rs-', markersize=4)
    ax2_inset.set_xlabel('Iteration', fontsize=8)
    ax2_inset.set_ylabel('|dE|', fontsize=8)
    ax2_inset.set_title('Convergence', fontsize=8)
    ax2_inset.grid(True, alpha=0.3)

ax3 = axes[1, 0]
x = np.linspace(-3, 3, 300)
chi_A = np.exp(-1.0 * (x + R_eq / 2) ** 2)
chi_B = np.exp(-1.0 * (x - R_eq / 2) ** 2)
psi_g = C[0, 0] * chi_A + C[1, 0] * chi_B
psi_u = C[0, 1] * chi_A + C[1, 1] * chi_B
psi_g /= np.max(np.abs(psi_g))
psi_u /= np.max(np.abs(psi_u))
ax3.plot(x, psi_g, 'b-', linewidth=2, label=r'$\sigma_g$ (bonding)')
ax3.plot(x, psi_u, 'r-', linewidth=2, label=r'$\sigma_u$ (antibonding)')
ax3.axvline(-R_eq / 2, color='gray', linestyle=':', alpha=0.5)
ax3.axvline(R_eq / 2, color='gray', linestyle=':', alpha=0.5)
ax3.annotate('H$_A$', xy=(-R_eq / 2, -1.1), fontsize=10, ha='center')
ax3.annotate('H$_B$', xy=(R_eq / 2, -1.1), fontsize=10, ha='center')
ax3.set_xlabel('x (bohr)', fontsize=12)
ax3.set_ylabel(r'$\psi$ (normalized)', fontsize=12)
ax3.set_title('Molecular Orbitals of H$_2$')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_ylim(-1.3, 1.3)

ax4 = axes[1, 1]
bar_width = 0.35
labels = ['R$_{eq}$ (bohr)', 'D$_e$ (eV)', 'D$_e$ (Hartree)']
sto3g = [R_min, D_e * 27.2114, D_e]
exact = [exact_Re, exact_De * 27.2114, exact_De]
x_pos = np.arange(len(labels))
ax4.bar(x_pos - bar_width / 2, sto3g, bar_width, label='STO-3G',
        color='#3498db', alpha=0.7, edgecolor='black')
ax4.bar(x_pos + bar_width / 2, exact, bar_width, label='Exact',
        color='#2ecc71', alpha=0.7, edgecolor='black')
ax4.set_xticks(x_pos)
ax4.set_xticklabels(labels, fontsize=10)
ax4.set_title('H$_2$: STO-3G vs Exact')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
fig.suptitle('h2_scf')
plt.show()
