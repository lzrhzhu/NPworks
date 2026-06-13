import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

N = 200
M = 50000
l = 1.0
dt = 1.0
D = l ** 2 / (2.0 * dt)

steps = np.random.choice([-l, l], size=(M, N))
x_final = np.sum(steps, axis=1)

fig, ax = plt.subplots(figsize=(9, 6))

counts, bins, _ = ax.hist(x_final, bins=80, density=True, alpha=0.7, edgecolor='black', label='Random Walk Simulation')

sigma_rw = l * np.sqrt(N)
x_range = np.linspace(x_final.min(), x_final.max(), 300)
gaussian_rw = (1.0 / (sigma_rw * np.sqrt(2 * np.pi))) * np.exp(-x_range ** 2 / (2 * sigma_rw ** 2))
ax.plot(x_range, gaussian_rw, 'r-', linewidth=2, label='Gaussian from CLT')

t = N * dt
P_analytical = (1.0 / np.sqrt(4.0 * np.pi * D * t)) * np.exp(-x_range ** 2 / (4.0 * D * t))
ax.plot(x_range, P_analytical, 'g--', linewidth=2, label='Diffusion eq: P(x,t) = 1/sqrt(4*pi*D*t) * exp(-x^2/(4Dt))')

ax.set_xlabel('Position x')
ax.set_ylabel('Probability Density')
ax.set_title('Random Walk vs Analytical Diffusion (N={}, M={})'.format(N, M))
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('diffusion_comparison')
plt.show()
print('ch06_diffusion_comparison.png saved')
print('D = l^2/(2*dt) = {:.4f}'.format(D))
print('sigma_RW = {:.4f}, sigma_diffusion = {:.4f}'.format(sigma_rw, np.sqrt(2 * D * t)))
