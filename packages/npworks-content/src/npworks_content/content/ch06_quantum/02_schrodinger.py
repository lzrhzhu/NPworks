# -*- coding: utf-8 -*-
# 6.2 薛定谔方程
# 一维定态薛定谔方程数值解 (无限深势阱和谐振子)

import numpy as np
import matplotlib.pyplot as plt

hbar = 1.0
m = 1.0

def solve_schrodinger(V, x, n_states=5):
    N = len(x)
    dx = x[1] - x[0]
    H = np.zeros((N, N))

    for i in range(N):
        H[i, i] = hbar ** 2 / (m * dx ** 2) + V[i]
        if i > 0:
            H[i, i - 1] = -hbar ** 2 / (2 * m * dx ** 2)
        if i < N - 1:
            H[i, i + 1] = -hbar ** 2 / (2 * m * dx ** 2)

    eigenvalues, eigenvectors = np.linalg.eigh(H)

    for j in range(eigenvectors.shape[1]):
        norm = np.sqrt(np.trapz(eigenvectors[:, j] ** 2, x))
        if norm > 0:
            eigenvectors[:, j] /= norm
        if eigenvectors[N // 2, j] < 0:
            eigenvectors[:, j] *= -1

    return eigenvalues[:n_states], eigenvectors[:, :n_states]

print("=== 无限深势阱 ===")
L_box = 1.0
N_points = 200
x_box = np.linspace(0, L_box, N_points)
V_box = np.zeros(N_points)
V_box[0] = 1e10
V_box[-1] = 1e10

E_box, psi_box = solve_schrodinger(V_box, x_box, n_states=5)

print(f"{'n':>4} {'数值解 E_n':>14} {'精确解 E_n':>14} {'误差':>10}")
print("-" * 46)
for n in range(5):
    E_exact = (n + 1) ** 2 * np.pi ** 2 * hbar ** 2 / (2 * m * L_box ** 2)
    error = abs(E_box[n] - E_exact) / E_exact * 100
    print(f"{n+1:>4} {E_box[n]:>14.6f} {E_exact:>14.6f} {error:>9.2f}%")

print("\n=== 量子谐振子 ===")
N_ho = 300
x_ho = np.linspace(-6, 6, N_ho)
omega = 1.0
V_ho = 0.5 * m * omega ** 2 * x_ho ** 2

E_ho, psi_ho = solve_schrodinger(V_ho, x_ho, n_states=5)

print(f"{'n':>4} {'数值解 E_n':>14} {'精确解 E_n':>14} {'误差':>10}")
print("-" * 46)
for n in range(5):
    E_exact = (n + 0.5) * hbar * omega
    error = abs(E_ho[n] - E_exact) / E_exact * 100
    print(f"{n:>4} {E_ho[n]:>14.6f} {E_exact:>14.6f} {error:>9.4f}%")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

for n in range(4):
    offset = E_box[n]
    psi_plot = psi_box[:, n] * 0.3 + offset
    ax1.plot(x_box, psi_plot, label=f"n={n+1}, E={E_box[n]:.3f}")
    ax1.axhline(y=E_box[n], color="gray", linestyle=":", alpha=0.3)
    E_exact = (n + 1) ** 2 * np.pi ** 2 * hbar ** 2 / (2 * m * L_box ** 2)
    ax1.axhline(y=E_exact, color="red", linestyle="--", alpha=0.2)

ax1.set_xlabel("x")
ax1.set_ylabel("能量 / 波函数")
ax1.set_title("无限深势阱能级和波函数")
ax1.legend()
ax1.grid(True, alpha=0.3)

for n in range(5):
    offset = E_ho[n]
    psi_plot = psi_ho[:, n] * 0.5 + offset
    ax2.fill_between(x_ho, offset, psi_plot, alpha=0.2)
    ax2.plot(x_ho, psi_plot, label=f"n={n}, E={E_ho[n]:.3f}")
    ax2.axhline(y=E_ho[n], color="gray", linestyle=":", alpha=0.3)

ax2.plot(x_ho, V_ho, "k-", linewidth=2, label="V(x) = ½mω²x²")
ax2.set_xlabel("x")
ax2.set_ylabel("能量 / 波函数")
ax2.set_title("量子谐振子能级和波函数")
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(-0.5, 6)

plt.tight_layout()
plt.show()
