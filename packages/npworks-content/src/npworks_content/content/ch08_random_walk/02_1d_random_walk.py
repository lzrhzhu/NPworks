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

N = 1000
l = 1.0

steps = rng.choice([-l, l], size=N)
x = np.concatenate(([0], np.cumsum(steps)))

fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(range(N + 1), x / l, linewidth=1.2)
ax.axhline(y=0, color='0.3', linestyle='--', linewidth=1.2)
ax.set_xlabel('Step number $N$')
ax.set_ylabel('Position $x/l$')
fig.suptitle('1d_random_walk')
fig.tight_layout()
plt.show()
print('02_1d_random_walk.py done')
