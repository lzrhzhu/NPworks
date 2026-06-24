import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

N = 10000

uniform_samples = np.random.uniform(0, 1, N)
normal_samples = np.random.normal(0, 1, N)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].hist(uniform_samples, bins=20, edgecolor='black', alpha=0.7)
axes[0].set_title('Uniform Distribution [0, 1)')
axes[0].set_xlabel('Value')
axes[0].set_ylabel('Count')
axes[0].grid(True, alpha=0.3)

axes[1].hist(normal_samples, bins=30, edgecolor='black', alpha=0.7, color='orange')
x_range = np.linspace(-4, 4, 300)
gaussian = N * (1.0 / np.sqrt(2 * np.pi)) * np.exp(-x_range ** 2 / 2.0) * (8.0 / 30)
axes[1].plot(x_range, gaussian, 'r-', linewidth=2, label='Gaussian fit')
axes[1].set_title('Normal Distribution (mu=0, sigma=1)')
axes[1].set_xlabel('Value')
axes[1].set_ylabel('Count')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('random_numbers')
plt.show()
print('ch07_random_numbers.png saved')
