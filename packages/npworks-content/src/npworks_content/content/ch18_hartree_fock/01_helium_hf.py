# -*- coding: utf-8 -*-
"""Helium atom minimal basis HF calculation (single s-type Gaussian)."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

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
eps = h_core(alpha_opt) + two_electron(alpha_opt)
print(f"alpha* = {alpha_opt:.4f}")
print(f"E_HF   = {E_opt:.4f} Hartree")
print(f"eps    = {eps:.4f} Hartree,  IP (Koopmans) = {-eps * 27.2114:.2f} eV")

alphas = np.linspace(0.1, 3.0, 200)
energies = np.array([total_energy(a) for a in alphas])
H_cores = np.array([h_core(a) for a in alphas])
J_vals = np.array([two_electron(a) for a in alphas])

# --- 图1：能量 vs alpha ---
fig, ax = plt.subplots(figsize=(7.0, 4.8))
ax.plot(alphas, energies, 'b-', linewidth=2, label='Total energy $E(\\alpha)$')
ax.plot(alphas, 2 * H_cores, 'r--', label='$2\\,h_{11}$ (kinetic + nuclear)')
ax.plot(alphas, J_vals, 'g-.', label='$(11|11)$ (electron-electron)')
ax.axvline(alpha_opt, color='gray', linestyle=':', alpha=0.8, label=f'$\\alpha^*$ = {alpha_opt:.3f}')
ax.axhline(E_exact, color='purple', linestyle=(0, (3, 1, 1, 1)), alpha=0.8,
           label=f'Exact = {E_exact:.3f}')
ax.plot(alpha_opt, E_opt, 'o', color='red', markersize=7, zorder=5)
ax.annotate(f'$\\alpha^*$={alpha_opt:.3f}\n$E$={E_opt:.3f}', xy=(alpha_opt, E_opt),
            xytext=(alpha_opt + 0.45, E_opt + 0.28),
            arrowprops=dict(arrowstyle='->', color='red'), fontsize=10, color='red')
ax.set_xlabel('$\\alpha$ (Gaussian exponent)')
ax.set_ylabel('Energy (Hartree)')
ax.set_title('He atom: energy vs Gaussian exponent')
ax.legend(fontsize=9, frameon=False)
plt.suptitle('helium_hf')

# --- 图2：能量对比柱状图 ---
labels = ['1 Gaussian\n(this work)', 'STO-3G\n(3 Gaussians)', 'HF limit', 'Exact\n(nonrel.)']
energies_bar = [E_opt, -2.8078, -2.8617, E_exact]
fig, ax = plt.subplots(figsize=(7.0, 4.5))
bars = ax.barh(range(len(labels)), [abs(e) for e in energies_bar],
               color=['#e74c3c', '#3498db', '#2ecc71', '#9b59b6'],
               alpha=0.75, edgecolor='black')
ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel('|Energy| (Hartree)')
ax.set_title('He atom: energy by basis set')
for bar, e in zip(bars, energies_bar):
    ax.text(bar.get_width() + 0.008, bar.get_y() + bar.get_height() / 2, f'{e:.4f}',
            va='center', fontsize=10)
plt.suptitle('helium_hf_comparison')

print("01_helium_hf.py done")

plt.show()
