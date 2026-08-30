import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'axes.grid': False,
    'axes.unicode_minus': False,
})

L, N, sigma, lam, eps = 1.0, 100, 4 * (2.0 / 100), 1.0, 1.0
h = 2 * L / N
x = np.linspace(-L, L, N + 1)
X, Y = np.meshgrid(x, x, indexing='ij')
rho = lam / (2 * np.pi * sigma**2) * np.exp(-(X**2 + Y**2) / (2 * sigma**2))
V = np.zeros_like(rho)
for _ in range(20000):
    V_new = V.copy()
    V_new[1:-1, 1:-1] = 0.25 * (V[:-2, 1:-1] + V[2:, 1:-1] + V[1:-1, :-2] + V[1:-1, 2:]) + h**2 * rho[1:-1, 1:-1] / (4 * eps)
    diff = np.max(np.abs(V_new - V))
    V = V_new
    if diff < 1e-7:
        break

fig, ax = plt.subplots()
cs = ax.contourf(X, Y, V, levels=20, cmap='viridis')
ax.contour(X, Y, V, levels=20, colors='k', linewidths=0.4)
fig.colorbar(cs, ax=ax, label='Potential $V$')
ax.set_xlabel('x (m)'); ax.set_ylabel('y (m)'); ax.set_aspect('equal')
ax.set_title('2D Poisson equation: Gaussian line charge')
fig.suptitle('poisson_gaussian_potential')

r = x[N // 2 + 1:]
v_line = V[N // 2 + 1:, N // 2]
mask = (r >= 3 * sigma) & (r <= 0.7 * L)
r_fit = r[mask]
v_fit = v_line[mask]
reference = -lam / (2 * np.pi * eps) * np.log(r_fit)
reference += np.mean(v_fit - reference)
fig, ax = plt.subplots()
ax.plot(r_fit, v_fit, 'o', ms=4, label='Numerical')
ax.plot(r_fit, reference, '--', label='$-\\lambda\\ln r/(2\\pi\\varepsilon)+C$')
ax.set_xlabel('r (m)'); ax.set_ylabel('Potential $V$ (normalized)'); ax.legend(frameon=False)
ax.set_title('Potential away from the charge core')
fig.suptitle('poisson_gaussian_radial')

plt.show()
