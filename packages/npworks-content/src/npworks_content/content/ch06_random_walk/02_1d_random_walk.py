import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

N = 1000
l = 1.0

steps = np.random.choice([-l, l], size=N)
x = np.concatenate(([0], np.cumsum(steps)))

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(range(N + 1), x, linewidth=0.8)
ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
ax.set_xlabel('Step N')
ax.set_ylabel('Position x')
ax.set_title('Single 1D Random Walk Trajectory (N=1000)')
ax.grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('1d_random_walk')
plt.show()
print('ch06_1d_random_walk.png saved')
