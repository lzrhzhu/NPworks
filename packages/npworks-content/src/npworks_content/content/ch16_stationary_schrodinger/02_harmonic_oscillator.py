"""
Quantum harmonic oscillator: E_n = (n + 0.5) * hbar * omega.
Uses finite difference discretization and matrix diagonalization.
"""
import math
import numpy as np
import matplotlib.pyplot as plt

hbar = 1.0
m = 1.0
omega = 1.0

x_min, x_max = -8.0, 8.0
N = 500
x = np.linspace(x_min, x_max, N + 1)
dx = x[1] - x[0]

V = 0.5 * m * omega ** 2 * x[1:-1] ** 2

diag_val = 1.0 / dx ** 2 + V
offdiag_val = -0.5 / dx ** 2 * np.ones(N - 2)

H = np.diag(diag_val) + np.diag(offdiag_val, 1) + np.diag(offdiag_val, -1)

eigenvalues, eigenvectors = np.linalg.eigh(H)

n_states = 6
E_num = eigenvalues[:n_states]
E_ana = np.array([(n + 0.5) * hbar * omega for n in range(n_states)])

print("n   E_numerical   E_analytical   Rel.Error")
for n in range(n_states):
    rel_err = abs(E_num[n] - E_ana[n]) / E_ana[n]
    print(f"{n}   {E_num[n]:.6f}      {E_ana[n]:.6f}      {rel_err:.2e}")

x_inner = x[1:-1]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

x_plot = np.linspace(x_min, x_max, 300)
V_plot = 0.5 * m * omega ** 2 * x_plot ** 2
axes[0].plot(x_plot, V_plot, 'k-', linewidth=2, label="V(x)")

colors = plt.cm.tab10(np.linspace(0, 1, n_states))
for n in range(n_states):
    psi = eigenvectors[:, n]
    sign = np.sign(psi[np.argmin(np.abs(x_inner - 0.0))])
    psi = sign * psi / np.sqrt(np.trapz(psi ** 2, x_inner))
    E_n = E_num[n]
    psi_ana = (m * omega / (np.pi * hbar)) ** 0.25 \
              / np.sqrt(2 ** n * math.factorial(n)) \
              * np.exp(-m * omega * x_inner ** 2 / (2 * hbar)) \
              * np.polynomial.hermite.hermval(
                  np.sqrt(m * omega / hbar) * x_inner,
                  [0] * n + [1])
    axes[0].plot(x_inner, psi * 2 + E_n, color=colors[n],
                 label=f"n={n}, E={E_n:.3f}")
    axes[0].axhline(E_n, color=colors[n], linestyle='--', alpha=0.3)

axes[0].set_xlim(-6, 6)
axes[0].set_ylim(-0.5, n_states + 1.5)
axes[0].set_xlabel("x")
axes[0].set_ylabel("Energy / psi(x)")
axes[0].set_title("Harmonic Oscillator Wavefunctions")
axes[0].legend(fontsize=7, loc='upper right')
axes[0].grid(True)

n_plot = min(15, len(E_num))
ns = np.arange(n_plot)
axes[1].plot(ns, E_num[:n_plot], 'ro', markersize=6, label="Numerical")
axes[1].plot(ns, E_ana[:n_plot], 'b-', label="Analytical (n+0.5)*hbar*w")
axes[1].set_xlabel("Quantum number n")
axes[1].set_ylabel("Energy")
axes[1].set_title("Energy Levels")
axes[1].legend()
axes[1].grid(True)

fig.tight_layout()

fig.suptitle('harmonic_oscillator')
plt.show()
