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

epsilon = 1.0
sigma = 1.0
r = np.linspace(0.9, 3.0, 500)
r_min_val = 2.0 ** (1.0 / 6.0) * sigma
V = 4.0 * epsilon * ((sigma / r) ** 12 - (sigma / r) ** 6)
F = 24.0 * epsilon * (2.0 * (sigma / r) ** 12 - (sigma / r) ** 6) / r

# --- 图1：Lennard-Jones 势能 V(r) ---
fig, ax = plt.subplots()
ax.plot(r, V, color='#0072B2', linestyle='-')
ax.axhline(y=0, color='black', linestyle='--', linewidth=1.2)
ax.axvline(x=r_min_val, color='#D55E00', linestyle=':', linewidth=1.2,
           label=r'$r_{\min}=2^{1/6}\sigma$')
ax.axvline(x=sigma, color='#009E73', linestyle='-.', linewidth=1.2,
           label=r'$r=\sigma$')
ax.set_xlabel(r'$r/\sigma$')
ax.set_ylabel(r'$V(r)\,/\,\epsilon$')
ax.legend(frameon=False)
ax.set_ylim(-1.5, 3.0)
ax.minorticks_on()
plt.tight_layout()
plt.suptitle('lj_potential')

# --- 图2：Lennard-Jones 力 F(r) ---
fig, ax = plt.subplots()
ax.plot(r, F, color='#D55E00', linestyle='-')
ax.axhline(y=0, color='black', linestyle='--', linewidth=1.2)
ax.axvline(x=r_min_val, color='#0072B2', linestyle=':', linewidth=1.2,
           label=r'$r_{\min}=2^{1/6}\sigma$')
ax.set_xlabel(r'$r/\sigma$')
ax.set_ylabel(r'$F(r)\,\sigma\,/\,\epsilon$')
ax.legend(frameon=False)
ax.set_ylim(-3.0, 5.0)
ax.minorticks_on()
plt.tight_layout()
plt.suptitle('lj_force')

print("01_lj_potential.py done")

plt.show()
