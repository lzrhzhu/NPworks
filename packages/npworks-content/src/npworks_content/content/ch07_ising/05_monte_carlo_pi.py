import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)

N = 10000
x = rng.uniform(-1, 1, N)
y = rng.uniform(-1, 1, N)
inside = x**2 + y**2 <= 1

pi_estimate = 4 * np.sum(inside) / N
print(f"pi estimate: {pi_estimate:.4f} (error: {abs(pi_estimate - np.pi):.4f})")

N_conv = np.arange(100, N + 1, 100)
pi_convergence = 4 * np.cumsum(inside) / np.arange(1, N + 1)
pi_convergence = pi_convergence[99::100]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.scatter(x[inside], y[inside], s=1, c='blue', alpha=0.5, label='Inside')
ax1.scatter(x[~inside], y[~inside], s=1, c='red', alpha=0.5, label='Outside')
theta = np.linspace(0, 2 * np.pi, 200)
ax1.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=2)
ax1.set_xlabel('$x$')
ax1.set_ylabel('$y$')
ax1.set_title(f'Monte Carlo $\\pi \\approx {pi_estimate:.4f}$ ($N = {N}$)')
ax1.set_aspect('equal')
ax1.legend(markerscale=10)

ax2.plot(N_conv, pi_convergence, 'b-', linewidth=0.8)
ax2.axhline(np.pi, color='red', linestyle='--', linewidth=1.5, label=f'$\\pi = {np.pi:.4f}$')
ax2.set_xlabel('Number of samples $N$')
ax2.set_ylabel(r'$\pi$ estimate')
ax2.set_title('Convergence of Monte Carlo $\\pi$ Estimation')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('monte_carlo_pi')
plt.show()
