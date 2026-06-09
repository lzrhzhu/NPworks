"""
Finite barrier tunneling: transmission coefficient T(E) vs energy E.
Uses transfer matrix method for a rectangular barrier.
"""
import numpy as np
import matplotlib.pyplot as plt

hbar = 1.0
m = 1.0

V0 = 1.0
a = 1.0

def transmission(E, V0, a, m=1.0, hbar=1.0):
    if E <= 0:
        return 0.0
    k1 = np.sqrt(2 * m * E) / hbar
    if E > V0:
        k2 = np.sqrt(2 * m * (E - V0)) / hbar
        delta = k2 * a
        denom = 1 + (k1 ** 2 - k2 ** 2) ** 2 / (4 * k1 ** 2 * k2 ** 2) * np.sin(delta) ** 2
        return 1.0 / denom
    else:
        kappa = np.sqrt(2 * m * (V0 - E)) / hbar
        T_val = 1.0 / (1 + (k1 ** 2 + kappa ** 2) ** 2 / (4 * k1 ** 2 * kappa ** 2)
                        * np.sinh(kappa * a) ** 2)
        return T_val

E_arr = np.linspace(0.01, 3.0 * V0, 1000)
T_arr = np.array([transmission(E, V0, a) for E in E_arr])

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].plot(E_arr / V0, T_arr, 'b-', linewidth=1.5)
axes[0].axvline(1.0, color='r', linestyle='--', alpha=0.6, label='E = V0')
axes[0].set_xlabel("E / V0")
axes[0].set_ylabel("Transmission T")
axes[0].set_title("Tunneling: T(E) for Rectangular Barrier")
axes[0].legend()
axes[0].grid(True)
axes[0].set_ylim(-0.05, 1.1)

x_diagram = np.array([-2, -0.5, -0.5, 0.5, 0.5, 2])
V_diagram = np.array([0, 0, V0, V0, 0, 0])
axes[1].fill_between(x_diagram, V_diagram, alpha=0.3, color='orange')
axes[1].plot(x_diagram, V_diagram, 'k-', linewidth=2)
axes[1].set_xlabel("x")
axes[1].set_ylabel("V(x)")
axes[1].set_title("Rectangular Barrier: V0={:.1f}, a={:.1f}".format(V0, a))
axes[1].set_ylim(-0.2, 1.5 * V0)
axes[1].grid(True)
axes[1].annotate("V0", xy=(0, V0), xytext=(0.3, V0 + 0.15),
                 fontsize=12, arrowprops=dict(arrowstyle='->', color='black'))

fig.tight_layout()

fig.suptitle('tunneling')
plt.show()
