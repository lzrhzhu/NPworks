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

seed = 20260827
repeats = 40
sample_sizes = np.array([100, 300, 1000, 3000, 10000, 30000, 100000])
rng = np.random.default_rng(seed)
rmse = []

for sample_size in sample_sizes:
    estimates = []
    for _ in range(repeats):
        x = rng.random(sample_size)
        y = rng.random(sample_size)
        inside = np.count_nonzero(x * x + y * y <= 1.0)
        estimates.append(4.0 * inside / sample_size)
    estimates = np.asarray(estimates)
    rmse.append(np.sqrt(np.mean((estimates - np.pi) ** 2)))

rmse = np.asarray(rmse)
fit_slope, fit_intercept = np.polyfit(np.log(sample_sizes), np.log(rmse), 1)
reference = rmse[0] * np.sqrt(sample_sizes[0] / sample_sizes)

fig, ax = plt.subplots()
ax.loglog(sample_sizes, rmse, 'o-', label='Measured RMSE')
ax.loglog(sample_sizes, reference, '--', label=r'$N^{-1/2}$ reference')
ax.set_xlabel('Sample size, N')
ax.set_ylabel(r'RMSE of $\pi$ estimate')
ax.legend(frameon=False)
ax.minorticks_on()
fig.suptitle('monte_carlo_pi_convergence')

print('Random seed:', seed)
print('Repeats per sample size:', repeats)
print('Fitted log-log slope: %.3f' % fit_slope)

plt.show()
