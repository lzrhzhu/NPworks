# -*- coding: utf-8 -*-
"""Helium atom minimal basis HF calculation (single s-type Gaussian)."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar


Z = 2.0


def h_core(alpha, Z=2.0):
    return 1.5 * alpha - 2.0 * Z * np.sqrt(2.0 * alpha / np.pi)


def two_electron(alpha):
    return (2.0 / np.sqrt(np.pi)) * np.sqrt(alpha)


def total_energy(alpha, Z=2.0):
    return 2.0 * h_core(alpha, Z) + two_electron(alpha)


res = minimize_scalar(total_energy, bounds=(0.01, 10.0), method='bounded', options={'xatol': 1e-12})
alpha_opt = res.x
E_opt = res.fun
E_exact = -2.9037

alphas = np.linspace(0.1, 3.0, 200)
energies = np.array([total_energy(a) for a in alphas])
H_cores = np.array([h_core(a) for a in alphas])
J_vals = np.array([two_electron(a) for a in alphas])

# --- 图1：能量 vs alpha ---
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(alphas, energies, 'b-', linewidth=2, label='Total energy E($\\alpha$)')
ax.plot(alphas, 2 * H_cores, 'r--', label='2*H$_{core}$')
ax.plot(alphas, J_vals, 'g--', label='(11|11)')
ax.axvline(alpha_opt, color='gray', linestyle=':', alpha=0.7, label=f'$\\alpha^*$ = {alpha_opt:.4f}')
ax.axhline(E_exact, color='purple', linestyle='-.', alpha=0.7, label=f'Exact = {E_exact:.4f}')
ax.plot(alpha_opt, E_opt, 'ro', markersize=10, zorder=5)
ax.annotate(f'$\\alpha^*$={alpha_opt:.4f}\nE={E_opt:.4f}', xy=(alpha_opt, E_opt),
            xytext=(alpha_opt + 0.4, E_opt + 0.15),
            arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red')
ax.set_xlabel('$\\alpha$ (Gaussian exponent)'); ax.set_ylabel('Energy (Hartree)')
ax.set_title('He Atom: Energy vs Gaussian Exponent'); ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('helium_hf')

# --- 图2：能量对比柱状图 ---
basis_data = [('1 Gaussian (this)', -2.699, '#e74c3c'), ('STO-3G (3 Gauss)', -2.808, '#3498db'),
              ('HF limit', -2.8617, '#2ecc71'), ('Exact', -2.9037, '#9b59b6')]
labels = [d[0] for d in basis_data]
energies_bar = [d[1] for d in basis_data]
colors = [d[2] for d in basis_data]
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(range(len(labels)), [abs(e) for e in energies_bar], color=colors, alpha=0.7, edgecolor='black')
ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel('|Energy| (Hartree)'); ax.set_title('He Atom: Energy Comparison')
for bar, e in zip(bars, energies_bar):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2, f'{e:.4f}', va='center', fontsize=10)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.suptitle('helium_hf_comparison')

print("01_helium_hf.py done")

plt.show()
