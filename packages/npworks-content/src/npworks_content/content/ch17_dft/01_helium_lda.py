# -*- coding: utf-8 -*-
"""
15.5.1 Helium atom: KS-DFT with LDA exchange-correlation, minimal basis
Single s-type Gaussian: g(r) = (2*alpha/pi)^(3/4) * exp(-alpha*r^2)

KS-DFT energy:  E = 2*H_core + 2*J + E_xc
  where H_core = 3*alpha/2 - 2*Z*sqrt(2*alpha/pi)   (analytic)
        J      = (2/sqrt(pi))*sqrt(alpha)             (analytic)
        E_xc   = integral rho(r)*eps_xc(rho(r)) dr    (numerical, 1D radial)

LDA exchange (Dirac):  eps_x(rho) = -3/4*(3/pi)^(1/3)*rho^(1/3)
                        V_x(rho)  = -(3/pi)^(1/3)*rho^(1/3)
LDA correlation (VWN): Vosko-Wilk-Nusair parameterization
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
from scipy.integrate import quad

Z = 2.0

def h_core(alpha):
    return 1.5 * alpha - 2.0 * Z * np.sqrt(2.0 * alpha / np.pi)

def coulomb_J(alpha):
    return (2.0 / np.sqrt(np.pi)) * np.sqrt(alpha)

def gaussian_density(r, alpha):
    N2 = (2.0 * alpha / np.pi) ** 1.5
    return 2.0 * N2 * np.exp(-2.0 * alpha * r ** 2)

def vwn_ec(rs):
    if rs < 1e-14:
        return 0.0
    A, x0, b, c = 0.0621814, -0.10498, 3.72744, 12.9352
    Q = np.sqrt(4.0 * c - b ** 2)
    x = np.sqrt(rs)
    Xx = x ** 2 + b * x + c
    Xx0 = x0 ** 2 + b * x0 + c
    t1 = np.log(x ** 2 / Xx)
    t2 = 2.0 * b / Q * np.arctan(Q / (2.0 * x + b))
    t3 = np.log((x - x0) ** 2 / Xx)
    t4 = 2.0 * (b + 2.0 * x0) / Q * np.arctan(Q / (2.0 * x + b))
    return A / 2.0 * (t1 + t2 - b * x0 / Xx0 * (t3 + t4))

def vwn_dec_drs(rs):
    h = 1e-6 * max(rs, 1e-10)
    return (vwn_ec(rs + h) - vwn_ec(rs - h)) / (2.0 * h)

def epsilon_x(rho):
    if rho < 1e-30:
        return 0.0
    return -0.75 * (3.0 / np.pi) ** (1.0 / 3.0) * rho ** (1.0 / 3.0)

def v_x_exchange(rho):
    if rho < 1e-30:
        return 0.0
    return -(3.0 / np.pi) ** (1.0 / 3.0) * rho ** (1.0 / 3.0)

def epsilon_c(rho):
    if rho < 1e-30:
        return 0.0
    rs = (3.0 / (4.0 * np.pi * rho)) ** (1.0 / 3.0)
    return vwn_ec(rs)

def v_x_correlation(rho):
    if rho < 1e-30:
        return 0.0
    rs = (3.0 / (4.0 * np.pi * rho)) ** (1.0 / 3.0)
    return vwn_ec(rs) - rs / 3.0 * vwn_dec_drs(rs)

def epsilon_xc(rho):
    return epsilon_x(rho) + epsilon_c(rho)

def v_xc(rho):
    return v_x_exchange(rho) + v_x_correlation(rho)

def compute_exc(alpha):
    def integrand(r):
        rho = gaussian_density(r, alpha)
        if rho < 1e-30:
            return 0.0
        return rho * epsilon_xc(rho) * r ** 2
    val, _ = quad(integrand, 0, 20, limit=200, epsabs=1e-12, epsrel=1e-12)
    return 4.0 * np.pi * val

def compute_vxc_mat(alpha):
    N = (2.0 * alpha / np.pi) ** 0.75
    def integrand(r):
        g = N * np.exp(-alpha * r ** 2)
        rho = 2.0 * g ** 2
        if rho < 1e-30:
            return 0.0
        return g ** 2 * v_xc(rho) * r ** 2
    val, _ = quad(integrand, 0, 20, limit=200, epsabs=1e-12, epsrel=1e-12)
    return 4.0 * np.pi * val

def total_energy_dft(alpha):
    return 2.0 * h_core(alpha) + 2.0 * coulomb_J(alpha) + compute_exc(alpha)

def total_energy_hf(alpha):
    return 2.0 * h_core(alpha) + coulomb_J(alpha)

print("=" * 65)
print("He Atom: KS-DFT with LDA (Minimal Basis, Single s-Gaussian)")
print("=" * 65)
print(f"Z = {Z}, Basis: g(r) = (2*alpha/pi)^(3/4) * exp(-alpha*r^2)")
print(f"E_DFT = 2*H_core + 2*J + E_xc[rho]")
print(f"E_HF   = 2*H_core + J")

res_hf = minimize_scalar(total_energy_hf, bounds=(0.1, 5.0), method='bounded',
                          options={'xatol': 1e-12})
res_dft = minimize_scalar(total_energy_dft, bounds=(0.1, 5.0), method='bounded',
                           options={'xatol': 1e-10})

alpha_hf = res_hf.x
alpha_lda = res_dft.x
E_hf = res_hf.fun
E_lda = res_dft.fun

print(f"\nOptimization results:")
print(f"  HF  : alpha* = {alpha_hf:.6f}, E = {E_hf:.6f} Hartree")
print(f"  LDA : alpha* = {alpha_lda:.6f}, E = {E_lda:.6f} Hartree")

E_xc_val = compute_exc(alpha_lda)
V_xc_val = compute_vxc_mat(alpha_lda)
eps_ks = h_core(alpha_lda) + 2.0 * coulomb_J(alpha_lda) + V_xc_val

print(f"\nEnergy decomposition (LDA, alpha*={alpha_lda:.6f}):")
print(f"  2*H_core  = {2*h_core(alpha_lda):.6f}")
print(f"  2*J       = {2*coulomb_J(alpha_lda):.6f}")
print(f"  E_xc      = {E_xc_val:.6f}  (E_x={compute_exc.__module__})")
E_x_only = 4*np.pi*quad(lambda r: gaussian_density(r, alpha_lda)*epsilon_x(gaussian_density(r, alpha_lda))*r**2 if gaussian_density(r, alpha_lda)>1e-30 else 0, 0, 20, limit=200)[0]
E_c_only = E_xc_val - E_x_only
print(f"    E_x     = {E_x_only:.6f}  (LDA exchange)")
print(f"    E_c     = {E_c_only:.6f}  (VWN correlation)")
print(f"  KS orbital energy eps = {eps_ks:.6f}")

E_exact = -2.9037
E_HF_limit = -2.8617
print(f"\nComparison with reference values:")
print(f"  {'Method':<30} {'E (Hartree)':>14} {'Error (eV)':>12}")
print(f"  {'-'*56}")
print(f"  {'HF (1 Gaussian, this work)':<30} {E_hf:>14.6f} {(E_hf-E_exact)*27.2114:>12.4f}")
print(f"  {'LDA (1 Gaussian, this work)':<30} {E_lda:>14.6f} {(E_lda-E_exact)*27.2114:>12.4f}")
print(f"  {'HF limit (large basis)':<30} {E_HF_limit:>14.4f} {(E_HF_limit-E_exact)*27.2114:>12.4f}")
print(f"  {'Exact non-relativistic':<30} {E_exact:>14.4f} {0.0:>12.4f}")

alphas = np.linspace(0.1, 3.0, 200)
E_hf_arr = np.array([total_energy_hf(a) for a in alphas])
E_lda_arr = np.array([total_energy_dft(a) for a in alphas])

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

ax1 = axes[0]
ax1.plot(alphas, E_hf_arr, 'r-', linewidth=2, label='HF: E = 2$H_{core}$ + J')
ax1.plot(alphas, E_lda_arr, 'b-', linewidth=2, label='LDA: E = 2$H_{core}$ + 2J + $E_{xc}$')
ax1.axhline(E_exact, color='purple', linestyle='-.', alpha=0.7,
            label=f'Exact = {E_exact:.4f}')
ax1.plot(alpha_hf, E_hf, 'ro', markersize=10, zorder=5)
ax1.plot(alpha_lda, E_lda, 'bs', markersize=10, zorder=5)
ax1.annotate(f'HF: $\\alpha^*$={alpha_hf:.3f}\nE={E_hf:.4f}',
             xy=(alpha_hf, E_hf), xytext=(1.5, -2.0),
             arrowprops=dict(arrowstyle='->', color='red'), fontsize=9, color='red')
ax1.annotate(f'LDA: $\\alpha^*$={alpha_lda:.3f}\nE={E_lda:.4f}',
             xy=(alpha_lda, E_lda), xytext=(1.5, -2.5),
             arrowprops=dict(arrowstyle='->', color='blue'), fontsize=9, color='blue')
ax1.set_xlabel('$\\alpha$ (Gaussian exponent)', fontsize=12)
ax1.set_ylabel('Energy (Hartree)', fontsize=12)
ax1.set_title('He Atom: HF vs LDA')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

ax2 = axes[1]
r = np.linspace(0, 3, 300)
rho_hf = np.array([gaussian_density(ri, alpha_hf) for ri in r])
rho_lda = np.array([gaussian_density(ri, alpha_lda) for ri in r])
ax2.plot(r, rho_hf, 'r-', linewidth=2, label=f'HF ($\\alpha$={alpha_hf:.3f})')
ax2.plot(r, rho_lda, 'b-', linewidth=2, label=f'LDA ($\\alpha$={alpha_lda:.3f})')
ax2.set_xlabel('r (bohr)', fontsize=12)
ax2.set_ylabel('$\\rho(r)$ (e/bohr$^3$)', fontsize=12)
ax2.set_title('He Atom: Electron Density')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

ax3 = axes[2]
methods = ['HF\n(1 Gauss)', 'LDA\n(1 Gauss)', 'HF limit', 'PBE\n(ref)', 'B3LYP\n(ref)', 'Exact']
energies = [E_hf, E_lda, -2.8617, -2.860, -2.907, -2.9037]
colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
bars = ax3.bar(range(len(methods)), [abs(e) for e in energies],
               color=colors, alpha=0.7, edgecolor='black')
ax3.set_xticks(range(len(methods)))
ax3.set_xticklabels(methods, fontsize=9)
ax3.set_ylabel('|Energy| (Hartree)', fontsize=12)
ax3.set_title('He Atom: Method Comparison')
for bar, e in zip(bars, energies):
    ax3.text(bar.get_width() / 2 + bar.get_x(), bar.get_height() + 0.01,
             f'{e:.4f}', ha='center', fontsize=8, rotation=45)
ax3.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
fig.suptitle('helium_lda')
plt.show()
