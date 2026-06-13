import numpy as np
import matplotlib.pyplot as plt

mu_ts_list = [2.0, 3.1, 3.45, 3.8]
n_iter = 80

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes_flat = axes.flatten()

for idx, mu in enumerate(mu_ts_list):
    x = 0.5
    xs = np.zeros(n_iter)
    for i in range(n_iter):
        xs[i] = x
        x = mu * x * (1.0 - x)
    axes_flat[idx].plot(range(n_iter), xs, 'b.-', markersize=3, linewidth=0.5)
    axes_flat[idx].set_xlabel('n')
    axes_flat[idx].set_ylabel(r'$x_n$')
    axes_flat[idx].set_title(r'Logistic Map $\mu={}$'.format(mu))
    axes_flat[idx].grid(True, alpha=0.3)

plt.tight_layout()

fig2, ax2 = plt.subplots(figsize=(10, 7))

mu_values = np.linspace(2.5, 4.0, 1000)
n_relay = 200
n_sample = 100

all_mu = []
all_x = []

for mu in mu_values:
    x = 0.5
    for i in range(n_relay):
        x = mu * x * (1.0 - x)
    for i in range(n_sample):
        x = mu * x * (1.0 - x)
        all_mu.append(mu)
        all_x.append(x)

ax2.plot(all_mu, all_x, 'k.', markersize=0.1)
ax2.set_xlabel(r'$\mu$')
ax2.set_ylabel(r'$x$')
ax2.set_title('Feigenbaum Bifurcation Diagram (Logistic Map)')

plt.tight_layout()
plt.suptitle('logistic_map')
plt.show()
print("12_logistic_map.py done")
