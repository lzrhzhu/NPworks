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
N = 10000
uniform_samples = rng.uniform(0, 1, N)
normal_samples = rng.normal(0, 1, N)

# --- 图1：均匀分布 ---
fig, ax = plt.subplots()
ax.hist(uniform_samples, bins=20, edgecolor='black', alpha=0.7)
ax.set_xlabel('Random number $u$')
ax.set_ylabel('Count')
fig.suptitle('random_numbers')
fig.tight_layout()

# --- 图2：正态分布 ---
fig, ax = plt.subplots()
ax.hist(normal_samples, bins=30, edgecolor='black', alpha=0.7)
x_range = np.linspace(-4, 4, 300)
gaussian = N * (1.0 / np.sqrt(2 * np.pi)) * np.exp(-x_range ** 2 / 2.0) * (8.0 / 30)
ax.plot(x_range, gaussian, '--', linewidth=1.8, label='Normal theory')
ax.set_xlabel('Random variable $z$')
ax.set_ylabel('Count')
ax.legend(frameon=False)
fig.suptitle('random_numbers_normal')
fig.tight_layout()

print("01_random_numbers.py done")

plt.show()
