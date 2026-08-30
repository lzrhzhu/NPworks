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
M = 1000
N = 500
l = 1.0

steps = rng.choice([-l, l], size=(M, N))
positions = np.cumsum(steps, axis=1)
x_final = positions[:, -1]

rms_sim = np.sqrt(np.mean(x_final ** 2))
rms_theory = l * np.sqrt(N)

# --- 图1：末态位置分布 ---
fig, ax = plt.subplots()
ax.hist(x_final, bins=50, density=True, edgecolor='black', alpha=0.7, label='Simulation')
sigma = l * np.sqrt(N)
x_range = np.linspace(x_final.min(), x_final.max(), 300)
gaussian = (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-x_range ** 2 / (2 * sigma ** 2))
ax.plot(x_range, gaussian, '--', linewidth=1.8, label='Gaussian approximation')
ax.set_xlabel('Final position $x_N/l$')
ax.set_ylabel('Probability density $P(x)l$')
ax.legend(frameon=False)
fig.suptitle('multi_walker')
fig.tight_layout()

# --- 图2：RMS vs sqrt(N) ---
n_vals = np.arange(1, N + 1)
rms_by_step = np.sqrt(np.mean(positions ** 2, axis=0))
fig, ax = plt.subplots()
ax.plot(n_vals, rms_by_step / l, '-', marker='o', markevery=50,
        label='Simulation')
ax.plot(n_vals, np.sqrt(n_vals), '--', linewidth=1.8,
        label=r'Theory: $\sqrt{N}$')
ax.set_xlabel('Step number $N$')
ax.set_ylabel(r'RMS position $x_{\mathrm{rms}}/l$')
ax.legend(frameon=False)
fig.suptitle('multi_walker_rms')
fig.tight_layout()

print('Sim RMS = {:.4f}, Theory RMS = {:.4f}'.format(rms_sim, rms_theory))
print("03_multi_walker.py done")

plt.show()
