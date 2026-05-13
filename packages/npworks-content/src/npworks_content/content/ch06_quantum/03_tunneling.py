# -*- coding: utf-8 -*-
# 6.3 量子隧穿
# 势垒隧穿模拟

import numpy as np
import matplotlib.pyplot as plt

hbar = 1.0
m = 1.0

def solve_tunneling(E, V0, barrier_width, x, V):
    N = len(x)
    dx = x[1] - x[0]

    k = np.sqrt(np.maximum(2 * m * (E - V) / hbar ** 2, 0))

    psi = np.zeros(N, dtype=complex)
    psi[0] = 1.0 + 0j
    psi[1] = np.exp(1j * np.sqrt(2 * m * E / hbar ** 2) * dx)

    for i in range(1, N - 1):
        k_i = k[i]
        k_prev = k[i - 1]
        k_next = k[i + 1] if i + 1 < N else k[i]

        if k_i > 1e-10:
            psi[i + 1] = (2 - dx ** 2 * (2 * m / hbar ** 2) * (E - V[i])) * psi[i] - psi[i - 1]
        else:
            psi[i + 1] = (2 + dx ** 2 * (2 * m / hbar ** 2) * (V[i] - E)) * psi[i] - psi[i - 1]

    return psi

def transmission_coefficient(E, V0, a):
    if E <= 0:
        return 0.0
    k = np.sqrt(2 * m * E) / hbar
    if E < V0:
        kappa = np.sqrt(2 * m * (V0 - E)) / hbar
        T = 1.0 / (1 + (V0 ** 2 * np.sinh(kappa * a) ** 2) / (4 * E * (V0 - E)))
    else:
        kp = np.sqrt(2 * m * (E - V0)) / hbar
        T = 1.0 / (1 + (V0 ** 2 * np.sin(kp * a) ** 2) / (4 * E * (E - V0)))
    return T

V0 = 5.0
barrier_width = 1.0
N = 500
x = np.linspace(-5, 8, N)
V = np.zeros(N)
barrier_mask = (x >= 0) & (x <= barrier_width)
V[barrier_mask] = V0

print("=== 量子隧穿模拟 ===")
print(f"势垒高度 V₀ = {V0}")
print(f"势垒宽度 a = {barrier_width}")
print()

energies = np.linspace(0.1, 10, 200)
T_values = [transmission_coefficient(E, V0, barrier_width) for E in energies]

print(f"{'能量 E':>10} {'透射率 T':>10} {'E/V₀':>10}")
print("-" * 32)
for E in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]:
    T = transmission_coefficient(E, V0, barrier_width)
    print(f"{E:>10.1f} {T:>10.6f} {E/V0:>10.2f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.fill_between(x, 0, V / V0, alpha=0.3, color="gray", label="势垒 V₀")
ax1.axhline(y=1.0, color="red", linestyle="--", alpha=0.5, label="E = V₀")

for E_demo in [2.0, 4.0, 5.5, 7.0]:
    psi = solve_tunneling(E_demo, V0, barrier_width, x, V)
    prob = np.abs(psi) ** 2
    prob_norm = prob / np.max(prob) * 0.8
    T_demo = transmission_coefficient(E_demo, V0, barrier_width)
    ax1.plot(x, prob_norm + E_demo / V0, label=f"E={E_demo}, T={T_demo:.3f}")

ax1.set_xlabel("x")
ax1.set_ylabel("|ψ|² (偏移=能量)")
ax1.set_title("波函数穿过势垒")
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

ax2.plot(energies / V0, T_values, "b-", linewidth=2, label="透射率 T")
ax2.axvline(x=1.0, color="red", linestyle="--", alpha=0.5, label="E = V₀")
ax2.fill_between(energies / V0, 0, T_values, alpha=0.2)

for width in [0.5, 1.0, 2.0]:
    T_w = [transmission_coefficient(E, V0, width) for E in energies]
    ax2.plot(energies / V0, T_w, "--", label=f"a={width}", alpha=0.7)

ax2.set_xlabel("E / V₀")
ax2.set_ylabel("透射率 T")
ax2.set_title(f"透射率 vs 能量 (V₀={V0})")
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 1.1)

plt.tight_layout()
plt.show()
