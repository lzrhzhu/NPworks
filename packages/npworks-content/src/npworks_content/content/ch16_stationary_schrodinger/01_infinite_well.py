"""Infinite square well: energy levels and wavefunctions via matrix diagonalization."""
import numpy as np
import matplotlib.pyplot as plt


L = 1.0
N = 500
dx = L / N
x = np.linspace(0, L, N + 1)
H = np.zeros((N - 1, N - 1))
for j in range(N - 1):
    H[j, j] = 1.0 / dx ** 2
    if j > 0:
        H[j, j - 1] = -0.5 / dx ** 2
    if j < N - 2:
        H[j, j + 1] = -0.5 / dx ** 2

eigenvalues, eigenvectors = np.linalg.eigh(H)
n_states = 5
x_inner = x[1:-1]
E_num = eigenvalues[:n_states]
E_ana = np.array([(n + 1) ** 2 * np.pi ** 2 / (2.0 * L ** 2) for n in range(n_states)])
colors = plt.cm.tab10(np.linspace(0, 1, n_states))

# --- 图1：波函数 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
for n in range(n_states):
    psi = eigenvectors[:, n]
    psi = psi / np.sqrt(np.trapz(psi ** 2, x_inner))
    ax.plot(x_inner, psi + E_num[n], color=colors[n], label=f"n={n+1}, E={E_num[n]:.3f}")
    ax.plot(x_inner, np.sqrt(2.0 / L) * np.sin((n + 1) * np.pi * x_inner / L) + E_ana[n],
            '--', color=colors[n], alpha=0.5)
ax.set_xlabel("x"); ax.set_ylabel("psi(x) + E_n")
ax.set_title("Infinite Well: Wavefunctions"); ax.legend(fontsize=8); ax.grid(True)
plt.tight_layout()
plt.suptitle('infinite_well')

# --- 图2：能级 ---
n_plot = min(20, len(E_num))
ns = np.arange(1, n_plot + 1)
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(ns, E_num[:n_plot], 'ro', markersize=6, label="Numerical")
ax.plot(ns, E_ana[:n_plot], 'b-', label="Analytical n^2*pi^2/(2L^2)")
ax.set_xlabel("Quantum number n"); ax.set_ylabel("Energy")
ax.set_title("Energy Levels"); ax.legend(); ax.grid(True)
plt.tight_layout()
plt.suptitle('infinite_well_levels')

print("01_infinite_well.py done")

plt.show()
