import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

M = 1000
N = 500
l = 1.0

steps = np.random.choice([-l, l], size=(M, N))
x_final = np.sum(steps, axis=1)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(x_final, bins=50, density=True, edgecolor='black', alpha=0.7, label='Simulation')
mu = 0
sigma = l * np.sqrt(N)
x_range = np.linspace(x_final.min(), x_final.max(), 300)
gaussian = (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-x_range ** 2 / (2 * sigma ** 2))
axes[0].plot(x_range, gaussian, 'r-', linewidth=2, label='Gaussian fit')
axes[0].set_xlabel('Final Position x_N')
axes[0].set_ylabel('Probability Density')
axes[0].set_title('Final Position Distribution (M={}, N={})'.format(M, N))
axes[0].legend()
axes[0].grid(True, alpha=0.3)

rms_sim = np.sqrt(np.mean(x_final ** 2))
rms_theory = l * np.sqrt(N)

n_vals = np.arange(1, N + 1, 10)
rms_vs_n = []
for n in n_vals:
    rms_vs_n.append(l * np.sqrt(n))

axes[1].plot(n_vals, l * np.sqrt(n_vals), 'r-', linewidth=2, label='Theory: sqrt(N)')
axes[1].axhline(y=rms_sim, color='b', linestyle='--', label='Sim RMS = {:.2f}'.format(rms_sim))
axes[1].axhline(y=rms_theory, color='r', linestyle=':', alpha=0.5, label='Theory RMS = {:.2f}'.format(rms_theory))
axes[1].set_xlabel('Step N')
axes[1].set_ylabel('RMS Position')
axes[1].set_title('RMS vs sqrt(N)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('multi_walker')
plt.show()
print('ch06_multi_walker.png saved')
print('Sim RMS = {:.4f}, Theory RMS = {:.4f}'.format(rms_sim, rms_theory))
