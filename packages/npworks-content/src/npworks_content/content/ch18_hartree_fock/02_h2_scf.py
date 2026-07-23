# -*- coding: utf-8 -*-
"""H2 Molecule - Minimal Basis HF/SCF (STO-3G). Splits the 2x2 figure into 4."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf
import os


def _img_dir(ch):
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "markdown")):
            return os.path.join(d, "markdown", "images", ch)
        d = os.path.dirname(d)
    out = os.path.join(os.path.expanduser("~"), "npworks_figures", ch)
    os.makedirs(out, exist_ok=True)
    return out


IMG_DIR = _img_dir("ch18")

STO3G_EXPONENTS = np.array([3.42525091, 0.62391373, 0.16885540])
STO3G_COEFFICIENTS = np.array([0.15432897, 0.53532814, 0.44463454])
STO3G_NORMALIZATION = (2.0 * STO3G_EXPONENTS / np.pi) ** 0.75


def boys0(T):
    return 1.0 if T < 1e-14 else 0.5 * np.sqrt(np.pi / T) * erf(np.sqrt(T))


def prim_overlap_3d(alpha, beta, RA, RB):
    p = alpha + beta
    return (np.pi / p) ** 1.5 * np.exp(-alpha * beta / p * np.sum((RA - RB) ** 2))


def prim_kinetic_3d(alpha, beta, RA, RB):
    p = alpha + beta
    S = prim_overlap_3d(alpha, beta, RA, RB)
    return alpha * beta / p * (3.0 - 2.0 * alpha * beta * np.sum((RA - RB) ** 2) / p) * S


def prim_nuclear_3d(alpha, beta, RA, RB, RC, Zc):
    p = alpha + beta
    RP = (alpha * RA + beta * RB) / p
    return -2.0 * np.pi / p * Zc * np.exp(-alpha * beta / p * np.sum((RA - RB) ** 2)) * boys0(p * np.sum((RP - RC) ** 2))


def prim_eri_3d(alpha, beta, gamma, delta, RA, RB, RC, RD):
    p = alpha + beta; q = gamma + delta
    RP = (alpha * RA + beta * RB) / p; RQ = (gamma * RC + delta * RD) / q
    return 2.0 * np.pi ** 2.5 / (p * q * np.sqrt(p + q)) * \
        np.exp(-alpha * beta / p * np.sum((RA - RB) ** 2) - gamma * delta / q * np.sum((RC - RD) ** 2)) * \
        boys0(p * q / (p + q) * np.sum((RP - RQ) ** 2))


def contract_overlap(di, ai, Ni, dj, aj, Nj, Ri, Rj):
    return sum(da * db * na * nb * prim_overlap_3d(a, b, Ri, Rj)
               for a, da, na in zip(ai, di, Ni) for b, db, nb in zip(aj, dj, Nj))


def contract_kinetic(di, ai, Ni, dj, aj, Nj, Ri, Rj):
    return sum(da * db * na * nb * prim_kinetic_3d(a, b, Ri, Rj)
               for a, da, na in zip(ai, di, Ni) for b, db, nb in zip(aj, dj, Nj))


def contract_nuclear(di, ai, Ni, dj, aj, Nj, Ri, Rj, nuclei):
    return sum(da * db * na * nb * prim_nuclear_3d(a, b, Ri, Rj, Rk, Zk)
               for a, da, na in zip(ai, di, Ni) for b, db, nb in zip(aj, dj, Nj) for Rk, Zk in nuclei)


def contract_eri(di, ai, Ni, dj, aj, Nj, dk, ak, Nk, dl, al, Nl, Ri, Rj, Rk, Rl):
    return sum(da * db * dg * dd * na * nb * ng * nd * prim_eri_3d(a, b, g, d, Ri, Rj, Rk, Rl)
               for a, da, na in zip(ai, di, Ni) for b, db, nb in zip(aj, dj, Nj)
               for g, dg, ng in zip(ak, dk, Nk) for d, dd, nd in zip(al, dl, Nl))


def build_integrals(R, Z1=1.0, Z2=1.0):
    RA = np.array([-R / 2.0, 0.0, 0.0]); RB = np.array([R / 2.0, 0.0, 0.0])
    nuclei = [(RA, Z1), (RB, Z2)]
    d = STO3G_COEFFICIENTS; a = STO3G_EXPONENTS; N = STO3G_NORMALIZATION
    centers = [RA, RB]; K = 2
    S = np.zeros((K, K)); T = np.zeros((K, K)); V = np.zeros((K, K))
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
                    eri[i, j, k, l] = contract_eri(d, a, N, d, a, N, d, a, N, d, a, N,
                                                   centers[i], centers[j], centers[k], centers[l])
    return S, T, V, H_core, eri, Z1 * Z2 / R


def run_scf(S, H_core, eri, K=2, Nel=2, max_iter=200, conv=1e-12):
    s_eval, s_evec = np.linalg.eigh(S)
    X = s_evec @ np.diag(1.0 / np.sqrt(s_eval))
    P = np.zeros((K, K)); energies = []
    for iteration in range(max_iter):
        G = np.zeros((K, K))
        for i in range(K):
            for j in range(K):
                for k in range(K):
                    for l in range(K):
                        G[i, j] += P[k, l] * (eri[i, j, k, l] - 0.5 * eri[i, k, j, l])
        F = H_core + G
        E_elec = np.sum(P * (H_core + F)) * 0.5
        energies.append(E_elec)
        if iteration > 0 and abs(energies[-1] - energies[-2]) < conv:
            break
        eps, Cp = np.linalg.eigh(X.T @ F @ X)
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


R_eq = 1.4
Rs = np.linspace(0.3, 5.0, 80)
E_hf = np.array([compute_total_energy(R)[0] for R in Rs])
i_min = np.argmin(E_hf)
R_min = Rs[i_min]; E_min = E_hf[i_min]
D_e = abs(E_min - (-1.0))
exact_Re = 1.4011; exact_De = 0.17447
E_tot, eps, C, P, energies_conv = compute_total_energy(R_eq)

# --- 图1：势能曲线 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(Rs, E_hf, 'b-', linewidth=2, label='STO-3G HF')
ax.axhline(-1.0, color='green', linestyle='--', alpha=0.5, label='2H (dissociation) = -1.0')
ax.plot(R_min, E_min, 'ro', markersize=10, zorder=5)
ax.annotate(f'R$_{{eq}}$={R_min:.3f}\nE={E_min:.4f}', xy=(R_min, E_min),
            xytext=(R_min + 0.5, E_min + 0.05), arrowprops=dict(arrowstyle='->', color='red'), fontsize=10)
ax.set_xlabel('R (bohr)'); ax.set_ylabel('E (Hartree)')
ax.set_title('H$_2$ Potential Energy Curve (STO-3G HF)'); ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch18_h2_scf.png"), dpi=130)
plt.close(fig)

# --- 图2：SCF 收敛 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(range(1, len(energies_conv) + 1), energies_conv, 'bo-', markersize=5)
ax.set_xlabel('SCF Iteration'); ax.set_ylabel('Electronic Energy (Hartree)')
ax.set_title(f'SCF Convergence at R = {R_eq} bohr'); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch18_h2_scf_convergence.png"), dpi=130)
plt.close(fig)

# --- 图3：分子轨道 ---
x = np.linspace(-3, 3, 300)
chi_A = np.exp(-1.0 * (x + R_eq / 2) ** 2); chi_B = np.exp(-1.0 * (x - R_eq / 2) ** 2)
psi_g = C[0, 0] * chi_A + C[1, 0] * chi_B; psi_u = C[0, 1] * chi_A + C[1, 1] * chi_B
psi_g /= np.max(np.abs(psi_g)); psi_u /= np.max(np.abs(psi_u))
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, psi_g, 'b-', linewidth=2, label=r'$\sigma_g$ (bonding)')
ax.plot(x, psi_u, 'r-', linewidth=2, label=r'$\sigma_u$ (antibonding)')
ax.axvline(-R_eq / 2, color='gray', linestyle=':', alpha=0.5); ax.axvline(R_eq / 2, color='gray', linestyle=':', alpha=0.5)
ax.annotate('H$_A$', xy=(-R_eq / 2, -1.1), fontsize=10, ha='center')
ax.annotate('H$_B$', xy=(R_eq / 2, -1.1), fontsize=10, ha='center')
ax.set_xlabel('x (bohr)'); ax.set_ylabel(r'$\psi$ (normalized)')
ax.set_title('Molecular Orbitals of H$_2$'); ax.legend(fontsize=10); ax.grid(True, alpha=0.3); ax.set_ylim(-1.3, 1.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch18_h2_scf_mos.png"), dpi=130)
plt.close(fig)

# --- 图4：STO-3G vs 精确 ---
fig, ax = plt.subplots(figsize=(8, 5))
bar_width = 0.35
labels = ['R$_{eq}$ (bohr)', 'D$_e$ (eV)', 'D$_e$ (Hartree)']
sto3g = [R_min, D_e * 27.2114, D_e]; exact = [exact_Re, exact_De * 27.2114, exact_De]
x_pos = np.arange(len(labels))
ax.bar(x_pos - bar_width / 2, sto3g, bar_width, label='STO-3G', color='#3498db', alpha=0.7, edgecolor='black')
ax.bar(x_pos + bar_width / 2, exact, bar_width, label='Exact', color='#2ecc71', alpha=0.7, edgecolor='black')
ax.set_xticks(x_pos); ax.set_xticklabels(labels, fontsize=10)
ax.set_title('H$_2$: STO-3G vs Exact'); ax.legend(fontsize=10); ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch18_h2_scf_comparison.png"), dpi=130)
plt.close(fig)

print("02_h2_scf.py done")
