import numpy as np
import matplotlib.pyplot as plt


np.random.seed(42)
N = 10000
uniform_samples = np.random.uniform(0, 1, N)
normal_samples = np.random.normal(0, 1, N)

# --- 图1：均匀分布 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(uniform_samples, bins=20, edgecolor='black', alpha=0.7)
ax.set_title('Uniform Distribution [0, 1)')
ax.set_xlabel('Value')
ax.set_ylabel('Count')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('random_numbers')

# --- 图2：正态分布 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(normal_samples, bins=30, edgecolor='black', alpha=0.7, color='orange')
x_range = np.linspace(-4, 4, 300)
gaussian = N * (1.0 / np.sqrt(2 * np.pi)) * np.exp(-x_range ** 2 / 2.0) * (8.0 / 30)
ax.plot(x_range, gaussian, 'r-', linewidth=2, label='Gaussian fit')
ax.set_title('Normal Distribution (mu=0, sigma=1)')
ax.set_xlabel('Value')
ax.set_ylabel('Count')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('random_numbers_normal')

print("01_random_numbers.py done")

plt.show()
