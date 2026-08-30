# -*- coding: utf-8 -*-
"""H2 molecule STO-3G HF/SCF: bond-length scan, convergence, orbitals."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf

plt.rcParams.update({
    'savefig.dpi': 300,
    'figure.figsize': (6.4, 4.0),
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'axes.grid': False,
    'axes.unicode_minus': False,
})

BOHR_TO_ANGSTROM = 0.529177
HARTREE_TO_EV = 27.2114

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
    return alpha * beta / p * (3.0 - 2.0 * alpha * beta / p * np.sum((RA - RB) ** 2)) * S


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


def run_scf(S, H_core, eri, K=2, Nel=2, max_iter=100, conv=1e-10, P0=None):
    """SCF loop. Default initial guess: diagonalize the core Hamiltonian."""
    s_eval, s_evec = np.linalg.eigh(S)
    X = s_evec @ np.diag(1.0 / np.sqrt(s_eval))          # 正交化 X = S^(-1/2)
    if P0 is None:
        # 初猜：对角化芯哈密顿矩阵（core guess）
        eps, Cp = np.linalg.eigh(X.T @ H_core @ X)
        C = X @ Cp
        P = 2.0 * np.outer(C[:, 0], C[:, 0])              # 闭壳层密度矩阵
    else:
        P = P0.copy()
    energies = []
    for iteration in range(max_iter):
        G = np.einsum('kl,ijkl->ij', P, eri) \
            - 0.5 * np.einsum('kl,ikjl->ij', P, eri)      # Coulomb + 交换
        F = H_core + G
        E_elec = 0.5 * np.sum(P * (H_core + F))           # 式 (18.37)
        energies.append(E_elec)
        eps, Cp = np.linalg.eigh(X.T @ F @ X)             # 广义本征值问题
        C = X @ Cp
        P_new = 2.0 * np.outer(C[:, 0], C[:, 0])
        if iteration > 0 and abs(energies[-1] - energies[-2]) < conv \
                and np.max(np.abs(P_new - P)) < 1e-8:
            break
        P = P_new
    return E_elec, eps, C, P, F, energies


def compute_total_energy(R, Z1=1.0, Z2=1.0):
    S, T, V, H_core, eri, E_nuc = build_integrals(R, Z1, Z2)
    E_elec, eps, C, P, F, energies = run_scf(S, H_core, eri)
    return E_elec + E_nuc, eps, C, P, energies


# 孤立氢原子的 STO-3G 能量（同一基组的离解极限参考值）
RA = np.array([0.0, 0.0, 0.0])
E_H_sto3g = contract_kinetic(STO3G_COEFFICIENTS, STO3G_EXPONENTS, STO3G_NORMALIZATION,
                             STO3G_COEFFICIENTS, STO3G_EXPONENTS, STO3G_NORMALIZATION, RA, RA) \
    + contract_nuclear(STO3G_COEFFICIENTS, STO3G_EXPONENTS, STO3G_NORMALIZATION,
                       STO3G_COEFFICIENTS, STO3G_EXPONENTS, STO3G_NORMALIZATION, RA, RA, [(RA, 1.0)])
print(f"E(H, STO-3G) = {E_H_sto3g:.4f} Hartree  ->  2H limit = {2 * E_H_sto3g:.4f} Hartree")

# 键长扫描
Rs = np.linspace(0.3, 8.0, 200)
E_hf = np.array([compute_total_energy(R)[0] for R in Rs])
i_min = np.argmin(E_hf)
R_min = Rs[i_min]; E_min = E_hf[i_min]
D_e = abs(E_min - 2 * E_H_sto3g)          # 同基组结合能
exact_Re = 1.4011; exact_De = 0.17447     # 实验平衡键长与势阱深度 D_e（不含零点能）
print(f"R_e = {R_min:.3f} bohr ({R_min * BOHR_TO_ANGSTROM:.3f} A),"
      f"  E_min = {E_min:.4f} Hartree")
print(f"D_e (vs 2H, same basis) = {D_e:.4f} Hartree = {D_e * HARTREE_TO_EV:.2f} eV"
      f"  (experiment: {exact_Re:.3f} bohr, {exact_De * HARTREE_TO_EV:.2f} eV)")

# SCF 收敛演示：R = 2.5 bohr，两种初猜
R_demo = 2.5
S, T, V, H_core, eri, E_nuc = build_integrals(R_demo)
E_core, eps_c, C_c, P_c, F_c, trace_core = run_scf(S, H_core, eri)
E_ion, eps_i, C_i, P_i, F_i, trace_ion = run_scf(S, H_core, eri, P0=np.diag([2.0, 0.0]))
print(f"SCF at R = {R_demo} bohr: core guess -> {len(trace_core)} iterations, "
      f"ionic guess -> {len(trace_ion)} iterations")

# 平衡键长处的轨道
R_eq = 1.4
E_tot, eps, C, P, energies_conv = compute_total_energy(R_eq)
print(f"orbital energies at R = {R_eq} bohr (Hartree): {np.round(eps, 4)}")

# --- 图1：势能曲线 ---
fig, ax = plt.subplots(figsize=(7.0, 4.8))
ax.plot(Rs, E_hf, 'b-', linewidth=2, label='STO-3G HF')
ax.axhline(2 * E_H_sto3g, color='green', linestyle='--', alpha=0.8,
           label=f'2H (STO-3G limit) = {2 * E_H_sto3g:.4f}')
ax.axhline(-1.0, color='purple', linestyle=(0, (3, 1, 1, 1)), alpha=0.8,
           label='2H (exact) = $-$1.0')
ax.plot(R_min, E_min, 'o', color='red', markersize=7, zorder=5)
ax.annotate(f'$R_e$={R_min:.2f}\n$E$={E_min:.4f}', xy=(R_min, E_min),
            xytext=(R_min + 0.7, E_min - 0.09), fontsize=10, color='red',
            arrowprops=dict(arrowstyle='->', color='red'))
ax.set_xlabel('R (bohr)')
ax.set_ylabel('E (Hartree)')
ax.set_title('H$_2$ potential energy curve (STO-3G HF)')
ax.legend(fontsize=9, frameon=False)
plt.suptitle('h2_scf')

# --- 图2：SCF 收敛 ---
fig, ax = plt.subplots(figsize=(7.0, 4.5))
ax.plot(range(1, len(trace_core) + 1), trace_core, 'bo-', markersize=5,
        label='core-Hamiltonian guess')
ax.plot(range(1, len(trace_ion) + 1), trace_ion, 'rs--', markersize=5,
        label='ionic guess (2e on atom A)')
ax.set_xlabel('SCF iteration')
ax.set_ylabel('Electronic energy (Hartree)')
ax.set_title(f'SCF convergence at R = {R_demo} bohr')
ax.legend(fontsize=10, frameon=False)
plt.suptitle('h2_scf_convergence')

# --- 图3：分子轨道 ---
x = np.linspace(-3, 3, 300)
chi_A = np.exp(-1.0 * (x + R_eq / 2) ** 2); chi_B = np.exp(-1.0 * (x - R_eq / 2) ** 2)
psi_g = C[0, 0] * chi_A + C[1, 0] * chi_B; psi_u = C[0, 1] * chi_A + C[1, 1] * chi_B
psi_g /= np.max(np.abs(psi_g)); psi_u /= np.max(np.abs(psi_u))
fig, ax = plt.subplots(figsize=(7.0, 4.5))
ax.plot(x, psi_g, 'b-', linewidth=2, label=r'$\sigma_g$ (bonding)')
ax.plot(x, psi_u, 'r--', linewidth=2, label=r'$\sigma_u$ (antibonding)')
ax.axvline(-R_eq / 2, color='gray', linestyle=':', alpha=0.8)
ax.axvline(R_eq / 2, color='gray', linestyle=':', alpha=0.8)
ax.annotate('H$_A$', xy=(-R_eq / 2, -1.15), fontsize=10, ha='center')
ax.annotate('H$_B$', xy=(R_eq / 2, -1.15), fontsize=10, ha='center')
ax.set_xlabel('x (bohr)')
ax.set_ylabel(r'$\psi$ (normalized)')
ax.set_title(r'Molecular orbitals of H$_2$ at $R$ = 1.4 bohr')
ax.legend(fontsize=10, frameon=False)
ax.set_ylim(-1.3, 1.3)
plt.suptitle('h2_scf_mos')

# --- 图4：STO-3G vs 实验（分离不同物理量的单位） ---
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.8))
bar_width = 0.35
axes[0].bar([-bar_width / 2, bar_width / 2], [R_min, exact_Re], bar_width,
            color=['#3498db', '#2ecc71'], alpha=0.75, edgecolor='black')
axes[0].set_xticks([-bar_width / 2, bar_width / 2])
axes[0].set_xticklabels(['STO-3G HF', 'Experiment'], rotation=15, fontsize=9)
axes[0].set_ylabel('$R_e$ (bohr)')
axes[0].set_title('(a) Equilibrium bond length')
axes[0].text(0, R_min, f'{R_min:.3f}', ha='center', va='bottom', fontsize=9)
axes[0].text(bar_width, exact_Re, f'{exact_Re:.3f}', ha='center', va='bottom', fontsize=9)

axes[1].bar([-bar_width / 2, bar_width / 2], [D_e * HARTREE_TO_EV, exact_De * HARTREE_TO_EV], bar_width,
            color=['#3498db', '#2ecc71'], alpha=0.75, edgecolor='black')
axes[1].set_xticks([-bar_width / 2, bar_width / 2])
axes[1].set_xticklabels(['STO-3G HF', 'Experiment'], rotation=15, fontsize=9)
axes[1].set_ylabel('$D_e$ (eV)')
axes[1].set_title('(b) Well depth')
axes[1].text(-bar_width / 2, D_e * HARTREE_TO_EV, f'{D_e * HARTREE_TO_EV:.2f}', ha='center', va='bottom', fontsize=9)
axes[1].text(bar_width / 2, exact_De * HARTREE_TO_EV, f'{exact_De * HARTREE_TO_EV:.2f}', ha='center', va='bottom', fontsize=9)
fig.suptitle('h2_scf_comparison')

print("02_h2_scf.py done")

plt.show()
