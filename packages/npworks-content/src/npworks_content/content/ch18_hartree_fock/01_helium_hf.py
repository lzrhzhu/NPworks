# -*- coding: utf-8 -*-
"""
16.4.1 Helium atom minimal basis HF calculation
Single s-type Gaussian basis: g(r) = (2*alpha/pi)^(3/4) * exp(-alpha*r^2)

Analytical integrals:
  H_core(alpha) = 3*alpha/2 - 2*Z*sqrt(2*alpha/pi)
  (11|11)(alpha) = (2/sqrt(pi))*sqrt(alpha)
  E(alpha) = 2*H_core + (11|11)    (E_nuc = 0 for one nucleus)
  F_11 = H_core + (11|11)
  epsilon = F_11 (orbital energy, since K=1)
  alpha* = 8*(Z-0.5)^2 / (9*pi)
"""

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

def fock_matrix(alpha, Z=2.0):
    P = 2.0
    return h_core(alpha, Z) + 0.5 * P * two_electron(alpha)

print("=" * 60)
print("Helium Atom - Minimal Basis HF (Single s-Gaussian)")
print("=" * 60)
print(f"Nuclear charge Z = {Z}")
print(f"Basis: g(r) = (2*alpha/pi)^(3/4) * exp(-alpha*r^2)")
print()

alpha_analytical = 8.0 * (Z - 0.5) ** 2 / (9.0 * np.pi)
print(f"Analytical optimal alpha = 8*(Z-0.5)^2/(9*pi)")
print(f"  alpha* = {alpha_analytical:.6f}")

res = minimize_scalar(total_energy, bounds=(0.01, 10.0), method='bounded',
                      options={'xatol': 1e-12})
alpha_opt = res.x
E_opt = res.fun

print(f"\nNumerical optimization result:")
print(f"  alpha* = {alpha_opt:.6f}")
print(f"  E_total = {E_opt:.6f} Hartree")

H_core_opt = h_core(alpha_opt)
J_opt = two_electron(alpha_opt)
eps = fock_matrix(alpha_opt)

print(f"\nDetailed energy decomposition at alpha*:")
print(f"  H_core = {H_core_opt:.6f} Hartree")
print(f"  (11|11) = {J_opt:.6f} Hartree")
print(f"  Orbital energy epsilon = {eps:.6f} Hartree")
print(f"  Total energy E = 2*H_core + (11|11) = {2*H_core_opt + J_opt:.6f} Hartree")
print(f"  Koopmans IP = -epsilon = {-eps:.6f} Hartree = {-eps*27.2114:.2f} eV")

E_exact = -2.9037
E_HF_limit = -2.8617
E_corr = E_exact - E_HF_limit
error_vs_exact = abs(E_opt - E_exact)
error_pct = error_vs_exact / abs(E_exact) * 100

print(f"\nComparison:")
print(f"  {'Method':<35} {'E (Hartree)':>14}")
print(f"  {'-'*49}")
print(f"  {'This calculation (1 Gaussian)':<35} {E_opt:>14.6f}")
print(f"  {'STO-3G (3 Gaussians)':<35} {'-2.808':>14}")
print(f"  {'HF limit (large basis)':<35} {E_HF_limit:>14.4f}")
print(f"  {'Exact non-relativistic':<35} {E_exact:>14.4f}")
print(f"  {'Correlation energy':<35} {E_corr:>14.4f}")
print(f"\n  Error vs exact: {error_pct:.1f}%")

alphas = np.linspace(0.1, 3.0, 200)
energies = np.array([total_energy(a) for a in alphas])
H_cores = np.array([h_core(a) for a in alphas])
J_vals = np.array([two_electron(a) for a in alphas])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.plot(alphas, energies, 'b-', linewidth=2, label='Total energy E($\\alpha$)')
ax1.plot(alphas, 2*H_cores, 'r--', label='2*H$_{core}$')
ax1.plot(alphas, J_vals, 'g--', label='(11|11)')
ax1.axvline(alpha_opt, color='gray', linestyle=':', alpha=0.7,
            label=f'$\\alpha^*$ = {alpha_opt:.4f}')
ax1.axhline(E_exact, color='purple', linestyle='-.', alpha=0.7,
            label=f'Exact = {E_exact:.4f}')
ax1.plot(alpha_opt, E_opt, 'ro', markersize=10, zorder=5)
ax1.annotate(f'$\\alpha^*$={alpha_opt:.4f}\nE={E_opt:.4f}',
             xy=(alpha_opt, E_opt), xytext=(alpha_opt+0.4, E_opt+0.15),
             arrowprops=dict(arrowstyle='->', color='red'),
             fontsize=10, color='red')
ax1.set_xlabel('$\\alpha$ (Gaussian exponent)', fontsize=12)
ax1.set_ylabel('Energy (Hartree)', fontsize=12)
ax1.set_title('He Atom: Energy vs Gaussian Exponent')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

basis_data = [
    ('1 Gaussian (this)', -2.699, '#e74c3c'),
    ('STO-3G (3 Gauss)', -2.808, '#3498db'),
    ('HF limit', -2.8617, '#2ecc71'),
    ('Exact', -2.9037, '#9b59b6'),
]
labels = [d[0] for d in basis_data]
energies_bar = [d[1] for d in basis_data]
colors = [d[2] for d in basis_data]
bars = ax2.barh(range(len(labels)), [abs(e) for e in energies_bar],
                color=colors, alpha=0.7, edgecolor='black')
ax2.set_yticks(range(len(labels)))
ax2.set_yticklabels(labels, fontsize=10)
ax2.set_xlabel('|Energy| (Hartree)', fontsize=12)
ax2.set_title('He Atom: Energy Comparison')
for bar, e in zip(bars, energies_bar):
    ax2.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
             f'{e:.4f}', va='center', fontsize=10)
ax2.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
fig.suptitle('helium_hf')
plt.show()
