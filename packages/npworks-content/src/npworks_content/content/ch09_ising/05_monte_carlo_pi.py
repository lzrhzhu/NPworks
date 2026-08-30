import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})


rng = np.random.default_rng(42)
N = 10000
x = rng.uniform(-1, 1, N)
y = rng.uniform(-1, 1, N)
inside = x ** 2 + y ** 2 <= 1
pi_estimate = 4 * np.sum(inside) / N
print(f"pi estimate: {pi_estimate:.4f} (error: {abs(pi_estimate - np.pi):.4f})")

# --- 图1：散点图 ---
fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(x[inside], y[inside], s=1, c='blue', alpha=0.5, label='Inside')
ax.scatter(x[~inside], y[~inside], s=1, c='red', alpha=0.5, label='Outside')
theta = np.linspace(0, 2 * np.pi, 200)
ax.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=2)
ax.set_xlabel('$x$')
ax.set_ylabel('$y$')
ax.set_title(f'Monte Carlo $\\pi \\approx {pi_estimate:.4f}$ ($N = {N}$)')
ax.set_aspect('equal')
ax.legend(markerscale=10, frameon=False)
plt.tight_layout()
plt.suptitle('monte_carlo_pi')

# --- 图2：收敛 ---
N_conv = np.arange(100, N + 1, 100)
pi_convergence = 4 * np.cumsum(inside) / np.arange(1, N + 1)
pi_convergence = pi_convergence[99::100]
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(N_conv, pi_convergence, 'b-', linewidth=0.8)
ax.axhline(np.pi, color='red', linestyle='--', linewidth=1.5, label=f'$\\pi = {np.pi:.4f}$')
ax.set_xlabel('Number of samples $N$')
ax.set_ylabel(r'$\pi$ estimate')
ax.set_title('Convergence of Monte Carlo $\\pi$ Estimation')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('monte_carlo_pi_convergence')

print("05_monte_carlo_pi.py done")

plt.show()
