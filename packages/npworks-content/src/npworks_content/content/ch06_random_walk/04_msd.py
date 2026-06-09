import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

N = 500
M = 5000
l = 1.0

steps = np.random.choice([-l, l], size=(M, N))

x = np.zeros((M, N + 1))
x[:, 1:] = np.cumsum(steps, axis=1)

msd = np.mean(x ** 2, axis=0)

steps_arr = np.arange(N + 1)

fig, ax = plt.subplots(figsize=(8, 6))

ax.plot(steps_arr, msd, 'b-', label='Simulation MSD', alpha=0.8, linewidth=1)
ax.plot(steps_arr, l ** 2 * steps_arr, 'r--', linewidth=2, label=r'Theory: $\langle x^2 \rangle = l^2 N$')
ax.set_xlabel('Step N')
ax.set_ylabel(r'MSD $\langle x^2 \rangle$')
ax.set_title('Mean Square Displacement of 1D Random Walk (M={})'.format(M))
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('msd')
plt.show()
print('ch06_msd.png saved')
