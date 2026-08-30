"""谐振子中的平衡分布与涨落-耗散定理对照。"""
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

rng = np.random.default_rng(8)

gamma = 1.0
k = 1.0
kT = 1.0
dt = 0.01
n_steps = 1000
n_traj = 50000

x_fdt = np.zeros(n_traj)
x_wrong = np.zeros(n_traj)
sigma_fdt = np.sqrt(2 * kT / gamma)
sigma_wrong = np.sqrt(3 * kT / gamma)

for _ in range(n_steps):
    x_fdt += -(k / gamma) * x_fdt * dt + sigma_fdt * np.sqrt(dt) * rng.standard_normal(n_traj)
    x_wrong += -(k / gamma) * x_wrong * dt + sigma_wrong * np.sqrt(dt) * rng.standard_normal(n_traj)

x_grid = np.linspace(-4, 4, 400)
rho = np.exp(-k * x_grid ** 2 / (2 * kT)) / np.sqrt(2 * np.pi * kT / k)

fig, ax = plt.subplots()
ax.hist(x_fdt, bins=70, density=True, histtype='step', linewidth=1.5,
        label=fr'FDT: $\langle x^2\rangle={np.mean(x_fdt**2):.3f}$')
ax.hist(x_wrong, bins=70, density=True, histtype='step', linewidth=1.5, linestyle='--',
        label=fr'noise too strong: $\langle x^2\rangle={np.mean(x_wrong**2):.3f}$')
ax.plot(x_grid, rho, 'k-.', label=r'Boltzmann theory: $k_BT/k=1$')
ax.set_xlabel('$x$ (reduced length)')
ax.set_ylabel('probability density')
ax.set_title('Harmonic equilibrium: FDT controls the variance')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('harmonic_fdt')

print(f'harmonic FDT: variance={np.mean(x_fdt**2):.4f}, expected=1.0000')
print(f'harmonic wrong noise: variance={np.mean(x_wrong**2):.4f}')
print('06_harmonic_fdt.py done')

plt.show()
