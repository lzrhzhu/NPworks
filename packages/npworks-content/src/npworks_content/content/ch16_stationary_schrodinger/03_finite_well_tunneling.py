"""Finite barrier tunneling: transmission coefficient T(E) vs energy E."""
import numpy as np
import matplotlib.pyplot as plt


V0 = 1.0
a = 1.0


def transmission(E, V0, a, m=1.0, hbar=1.0):
    if E <= 0:
        return 0.0
    k1 = np.sqrt(2 * m * E) / hbar
    if E > V0:
        k2 = np.sqrt(2 * m * (E - V0)) / hbar
        denom = 1 + (k1 ** 2 - k2 ** 2) ** 2 / (4 * k1 ** 2 * k2 ** 2) * np.sin(k2 * a) ** 2
        return 1.0 / denom
    else:
        kappa = np.sqrt(2 * m * (V0 - E)) / hbar
        return 1.0 / (1 + (k1 ** 2 + kappa ** 2) ** 2 / (4 * k1 ** 2 * kappa ** 2) * np.sinh(kappa * a) ** 2)


E_arr = np.linspace(0.01, 3.0 * V0, 1000)
T_arr = np.array([transmission(E, V0, a) for E in E_arr])

# --- 图1：透射系数 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(E_arr / V0, T_arr, 'b-', linewidth=1.5)
ax.axvline(1.0, color='r', linestyle='--', alpha=0.6, label='E = V0')
ax.set_xlabel("E / V0"); ax.set_ylabel("Transmission T")
ax.set_title("Tunneling: T(E) for Rectangular Barrier"); ax.legend(); ax.grid(True)
ax.set_ylim(-0.05, 1.1)
plt.tight_layout()
plt.suptitle('tunneling')

# --- 图2：势垒示意 ---
fig, ax = plt.subplots(figsize=(8, 5))
x_diagram = np.array([-2, -0.5, -0.5, 0.5, 0.5, 2])
V_diagram = np.array([0, 0, V0, V0, 0, 0])
ax.fill_between(x_diagram, V_diagram, alpha=0.3, color='orange')
ax.plot(x_diagram, V_diagram, 'k-', linewidth=2)
ax.set_xlabel("x"); ax.set_ylabel("V(x)")
ax.set_title("Rectangular Barrier: V0={:.1f}, a={:.1f}".format(V0, a))
ax.set_ylim(-0.2, 1.5 * V0); ax.grid(True)
ax.annotate("V0", xy=(0, V0), xytext=(0.3, V0 + 0.15), fontsize=12,
            arrowprops=dict(arrowstyle='->', color='black'))
plt.tight_layout()
plt.suptitle('tunneling_barrier')

print("03_finite_well_tunneling.py done")

plt.show()
