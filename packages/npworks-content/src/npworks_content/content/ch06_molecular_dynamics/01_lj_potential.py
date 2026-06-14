import numpy as np
import matplotlib.pyplot as plt

epsilon = 1.0
sigma = 1.0

r = np.linspace(0.9, 3.0, 500)
r_min_val = 2.0 ** (1.0 / 6.0) * sigma

V = 4.0 * epsilon * ((sigma / r) ** 12 - (sigma / r) ** 6)
F = 24.0 * epsilon * (2.0 * (sigma / r) ** 12 - (sigma / r) ** 6) / r

fig, axes = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

axes[0].plot(r, V, 'b-', linewidth=2)
axes[0].axhline(y=0, color='k', linestyle='--', linewidth=0.5)
axes[0].axvline(x=r_min_val, color='r', linestyle=':', linewidth=0.8, label='r_min = 2^(1/6)*sigma')
axes[0].axvline(x=sigma, color='g', linestyle=':', linewidth=0.8, label='r = sigma (V=0)')
axes[0].set_ylabel('V(r) / epsilon')
axes[0].set_title('Lennard-Jones Potential: V(r) = 4*epsilon*[(sigma/r)^12 - (sigma/r)^6]')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(-1.5, 3.0)

axes[1].plot(r, F, 'r-', linewidth=2)
axes[1].axhline(y=0, color='k', linestyle='--', linewidth=0.5)
axes[1].axvline(x=r_min_val, color='r', linestyle=':', linewidth=0.8, label='r_min = 2^(1/6)*sigma')
axes[1].set_xlabel('r / sigma')
axes[1].set_ylabel('F(r) * sigma / epsilon')
axes[1].set_title('Lennard-Jones Force: F(r) = 24*epsilon*[2*(sigma/r)^12 - (sigma/r)^6] / r')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim(-3.0, 5.0)

plt.tight_layout()

plt.suptitle('lj_potential')
plt.show()
print('ch06_lj_potential.png saved')
