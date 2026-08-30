"""Quantum harmonic oscillator: E_n = (n + 0.5)*hbar*omega."""
import math
import numpy as np
import matplotlib.pyplot as plt

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


def chebyshev_harmonic_energies(n_nodes, x_bound, n_levels=3):
    """Chebyshev collocation energies; the interior matrix is not symmetric."""
    j = np.arange(n_nodes + 1)
    xi = np.cos(np.pi * j / n_nodes)
    c = np.ones(n_nodes + 1)
    c[[0, -1]] = 2.0
    D = np.zeros((n_nodes + 1, n_nodes + 1))
    for row in range(n_nodes + 1):
        for col in range(n_nodes + 1):
            if row != col:
                D[row, col] = (c[row] / c[col]) * (-1.0) ** (row + col) / (xi[row] - xi[col])
    D[np.diag_indices_from(D)] = -np.sum(D, axis=1)
    D2_inner = (D @ D)[1:-1, 1:-1] / x_bound ** 2
    x_cheb = x_bound * xi[1:-1]
    H_cheb = -0.5 * D2_inner + np.diag(0.5 * omega ** 2 * x_cheb ** 2)
    # Collocation H_cheb is generally non-symmetric in the Euclidean inner product.
    energies = np.linalg.eigvals(H_cheb)
    energies = np.sort(np.real_if_close(energies).real)
    return energies[:n_levels]


hbar = 1.0; m = 1.0; omega = 1.0
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
E_cheb = chebyshev_harmonic_energies(50, x_max, n_levels=3)
x_inner = x[1:-1]
colors = plt.cm.tab10(np.linspace(0, 1, n_states))
line_styles = ['-', '--', '-.', ':', (0, (5, 2)), (0, (3, 1, 1, 1))]

# --- 图1：波函数 ---
fig, ax = plt.subplots()
x_plot = np.linspace(x_min, x_max, 300)
ax.plot(x_plot, 0.5 * m * omega ** 2 * x_plot ** 2, 'k-', linewidth=2, label="V(x)")
for n in range(n_states):
    psi = eigenvectors[:, n]
    anchor = np.argmax(np.abs(psi))
    sign = np.sign(psi[anchor]) or 1.0
    psi = sign * psi / np.sqrt(np.trapz(psi ** 2, x_inner))
    ax.plot(x_inner, psi * 2 + E_num[n], color=colors[n], linestyle=line_styles[n],
            label=f"n={n}, E={E_num[n]:.3f}")
    ax.axhline(E_num[n], color=colors[n], linestyle='--', alpha=0.3)
ax.set_xlim(-6, 6); ax.set_ylim(-0.5, n_states + 1.5)
ax.set_xlabel("x (natural units)")
ax.set_ylabel("E and scaled psi(x) (natural units)")
ax.set_title("Harmonic-Oscillator Eigenstates")
ax.legend(fontsize=7, loc='upper right', frameon=False, ncol=2)
ax.minorticks_on()
plt.tight_layout()
plt.suptitle('harmonic_oscillator')

# --- 图2：能级 ---
n_plot = min(15, len(E_num))
ns = np.arange(n_plot)
fig, ax = plt.subplots()
ax.plot(ns, E_num[:n_plot], 'ro', markersize=6, label="Numerical")
ax.plot(ns, E_ana[:n_plot], 'b-', label="Analytical (n+0.5)*hbar*w")
ax.set_xlabel("Quantum number n")
ax.set_ylabel("E (natural units)")
ax.set_title("Harmonic-Oscillator Energy Levels")
ax.legend(frameon=False)
ax.minorticks_on()
plt.tight_layout()
plt.suptitle('harmonic_oscillator_levels')

print("Finite-difference energies:", E_num[:3])
print("Chebyshev-collocation energies:", E_cheb)
print("02_harmonic_oscillator.py done")

plt.show()
