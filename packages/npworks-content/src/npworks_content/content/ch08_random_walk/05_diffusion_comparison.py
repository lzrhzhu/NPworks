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

rng = np.random.default_rng(42)

N = 200
M = 50000
l = 1.0
dt = 1.0
D = l ** 2 / (2.0 * dt)

steps = rng.choice([-l, l], size=(M, N))
x_final = np.sum(steps, axis=1)

fig, ax = plt.subplots()

counts, bins, _ = ax.hist(x_final, bins=80, density=True, alpha=0.7, edgecolor='black', label='Random Walk Simulation')

sigma_rw = l * np.sqrt(N)
x_range = np.linspace(x_final.min(), x_final.max(), 300)
gaussian_rw = (1.0 / (sigma_rw * np.sqrt(2 * np.pi))) * np.exp(-x_range ** 2 / (2 * sigma_rw ** 2))
ax.plot(x_range, gaussian_rw, '-', linewidth=1.8, label='Gaussian approximation')

t = N * dt
P_analytical = (1.0 / np.sqrt(4.0 * np.pi * D * t)) * np.exp(-x_range ** 2 / (4.0 * D * t))
ax.plot(x_range, P_analytical, '--', linewidth=1.8, label='Diffusion equation')

ax.set_xlabel('Position $x/l$')
ax.set_ylabel('Probability density $P(x)l$')
ax.legend(frameon=False)
fig.suptitle('diffusion_comparison')
fig.tight_layout()
plt.show()
print('05_diffusion_comparison.py done')
print('D = l^2/(2*dt) = {:.4f}'.format(D))
print('sigma_RW = {:.4f}, sigma_diffusion = {:.4f}'.format(sigma_rw, np.sqrt(2 * D * t)))
