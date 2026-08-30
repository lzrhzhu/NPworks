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

N = 500
M = 5000
l = 1.0

steps = rng.choice([-l, l], size=(M, N))

x = np.zeros((M, N + 1))
x[:, 1:] = np.cumsum(steps, axis=1)

msd = np.mean(x ** 2, axis=0)

steps_arr = np.arange(N + 1)

fig, ax = plt.subplots()

ax.plot(steps_arr, msd / l ** 2, '-', marker='o', markevery=50,
        label='Simulation MSD')
ax.plot(steps_arr, steps_arr, '--', linewidth=1.8,
        label=r'Theory: $\langle x^2 \rangle/l^2=N$')
ax.set_xlabel('Step number $N$')
ax.set_ylabel(r'MSD $\langle x^2 \rangle/l^2$')
ax.legend(frameon=False)
fig.suptitle('msd')
fig.tight_layout()
plt.show()
print('04_msd.py done')
