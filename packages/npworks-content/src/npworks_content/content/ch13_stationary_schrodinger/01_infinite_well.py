"""
Infinite square well: energy levels and wavefunctions via matrix diagonalization.
Compares numerical vs analytical E_n = n^2 * pi^2 / (2 * L^2) (hbar=m=1).
"""
import numpy as np
import matplotlib.pyplot as plt

hbar = 1.0
m = 1.0
L = 1.0
N = 500

dx = L / N
x = np.linspace(0, L, N + 1)

diag_val = 1.0 / dx ** 2
offdiag_val = -0.5 / dx ** 2

H = np.zeros((N - 1, N - 1))
for j in range(N - 1):
    H[j, j] = diag_val
    if j > 0:
        H[j, j - 1] = offdiag_val
    if j < N - 2:
        H[j, j + 1] = offdiag_val

eigenvalues, eigenvectors = np.linalg.eigh(H)

n_states = 5
x_inner = x[1:-1]

E_num = eigenvalues[:n_states]
E_ana = np.array([(n + 1) ** 2 * np.pi ** 2 / (2.0 * L ** 2) for n in range(n_states)])

print("n   E_numerical   E_analytical   Rel.Error")
for n in range(n_states):
    rel_err = abs(E_num[n] - E_ana[n]) / E_ana[n]
    print(f"{n+1}   {E_num[n]:.6f}      {E_ana[n]:.6f}      {rel_err:.2e}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

colors = plt.cm.tab10(np.linspace(0, 1, n_states))
for n in range(n_states):
    psi = eigenvectors[:, n]
    norm = np.sqrt(np.trapz(psi ** 2, x_inner))
    psi = psi / norm
    offset = E_num[n]
    axes[0].plot(x_inner, psi + offset, color=colors[n],
                 label=f"n={n+1}, E={E_num[n]:.3f}")
    psi_ana = np.sqrt(2.0 / L) * np.sin((n + 1) * np.pi * x_inner / L)
    axes[0].plot(x_inner, psi_ana + E_ana[n], '--', color=colors[n], alpha=0.5)

axes[0].set_xlabel("x")
axes[0].set_ylabel("psi(x) + E_n")
axes[0].set_title("Infinite Well: Wavefunctions")
axes[0].legend(fontsize=8)
axes[0].grid(True)

n_plot = min(20, len(E_num))
ns = np.arange(1, n_plot + 1)
axes[1].plot(ns, E_num[:n_plot], 'ro', markersize=6, label="Numerical")
axes[1].plot(ns, E_ana[:n_plot], 'b-', label="Analytical n^2*pi^2/(2L^2)")
axes[1].set_xlabel("Quantum number n")
axes[1].set_ylabel("Energy")
axes[1].set_title("Energy Levels")
axes[1].legend()
axes[1].grid(True)

fig.tight_layout()

fig.suptitle('infinite_well')
plt.show()
