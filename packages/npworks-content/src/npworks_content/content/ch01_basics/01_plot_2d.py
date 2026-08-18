import numpy as np
import matplotlib.pyplot as plt


x = np.linspace(0, 2 * np.pi, 100)

fig, ax = plt.subplots(figsize=(8, 6))
ax.plot(x, np.sin(x), 'b-', linewidth=2, label=r'$\sin(x)$')
ax.plot(x, np.cos(x), 'r--', linewidth=1.5, label=r'$\cos(x)$')
ax.set_title(r'$y = \sin(x)$ and $\cos(x)$ on $[0,\,2\pi]$')
ax.set_xlabel('x (radians)')
ax.set_ylabel('y')
ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
ax.set_xticklabels(['0', r'$\pi/2$', r'$\pi$', r'$3\pi/2$', r'$2\pi$'])
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.suptitle('plot_2d')

print("01_plot_2d.py done")

plt.show()
