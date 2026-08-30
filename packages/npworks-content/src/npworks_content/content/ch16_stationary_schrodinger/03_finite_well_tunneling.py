"""Finite barrier tunneling: transmission coefficient T(E) vs energy E."""
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


V0 = 1.0
a = 4.0


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
fig, ax = plt.subplots()
ax.plot(E_arr / V0, T_arr, 'b-', linewidth=1.5)
ax.axvline(1.0, color='r', linestyle='--', alpha=0.6, label='E = V0')
ax.set_xlabel("E / V0")
ax.set_ylabel("Transmission coefficient T")
ax.set_title("Analytical Transmission of a Rectangular Barrier")
ax.legend(frameon=False)
ax.minorticks_on()
ax.set_ylim(-0.05, 1.1)
plt.tight_layout()
plt.suptitle('tunneling')

# --- 图2：势垒示意 ---
fig, ax = plt.subplots()
x_outer = a / 2 + 1.5
x_diagram = np.array([-x_outer, -a / 2, -a / 2, a / 2, a / 2, x_outer])
V_diagram = np.array([0, 0, V0, V0, 0, 0])
ax.fill_between(x_diagram, V_diagram, alpha=0.3, color='orange')
ax.plot(x_diagram, V_diagram, 'k-', linewidth=2)
ax.set_xlabel("x (natural units)")
ax.set_ylabel("V(x) (natural units)")
ax.set_title("Rectangular Barrier: height V0, width a")
ax.set_ylim(-0.2, 1.5 * V0)
ax.set_xlim(-x_outer, x_outer)
ax.minorticks_on()
ax.annotate("V0", xy=(0, V0), xytext=(0.3, V0 + 0.15), fontsize=12,
            arrowprops=dict(arrowstyle='->', color='black'))
plt.tight_layout()
plt.suptitle('tunneling_barrier')

print("03_finite_well_tunneling.py done")

plt.show()
