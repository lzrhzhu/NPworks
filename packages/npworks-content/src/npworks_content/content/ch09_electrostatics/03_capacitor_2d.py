import numpy as np
import matplotlib.pyplot as plt


def solve_capacitor(N, max_iter=10000, tol=1e-6, omega=1.5):
    V = np.zeros((N + 1, N + 1))
    start = N // 4
    end = N - start
    for i in range(start, end + 1):
        V[i, start] = -1.0
        V[i, end] = 1.0

    for _ in range(max_iter):
        V_old = V.copy()
        for i in range(1, N):
            for j in range(1, N):
                if (j == start and start <= i <= end) or \
                   (j == end and start <= i <= end):
                    continue
                V_new = 0.25 * (V[i-1, j] + V[i+1, j] +
                                V[i, j-1] + V[i, j+1])
                V[i, j] = (1 - omega) * V[i, j] + omega * V_new
        diff = np.max(np.abs(V - V_old))
        if diff < tol:
            break
    return V


N = 80
V = solve_capacitor(N)

x = np.linspace(0, N, N + 1) / N
y = np.linspace(0, N, N + 1) / N
X, Y = np.meshgrid(x, y)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

levels = np.linspace(-1, 1, 21)
cs = ax1.contourf(X, Y, V, levels=levels, cmap='RdBu_r')
ax1.contour(X, Y, V, levels=levels, colors='k', linewidths=0.5, alpha=0.5)
plt.colorbar(cs, ax=ax1, label='Potential $V$')
start = N // 4
end = N - start
ax1.plot([start/N, start/N], [start/N, end/N], 'k-', linewidth=3)
ax1.plot([end/N, end/N], [start/N, end/N], 'k-', linewidth=3)
ax1.set_xlabel('$x / L$')
ax1.set_ylabel('$y / L$')
ax1.set_title('Parallel Plate Capacitor - Equipotential Contours')
ax1.set_aspect('equal')

Ey, Ex = np.gradient(-V, 1.0 / N, 1.0 / N)
E_mag = np.sqrt(Ex**2 + Ey**2)
skip = 4
ax2.contourf(X, Y, E_mag, levels=30, cmap='hot')
plt.colorbar(ax2.collections[0], ax=ax2, label='$|E|$')
ax2.quiver(X[::skip, ::skip], Y[::skip, ::skip],
           Ex[::skip, ::skip], Ey[::skip, ::skip],
           color='white', alpha=0.7, scale=30)
ax2.plot([start/N, start/N], [start/N, end/N], 'k-', linewidth=3)
ax2.plot([end/N, end/N], [start/N, end/N], 'k-', linewidth=3)
ax2.set_xlabel('$x / L$')
ax2.set_ylabel('$y / L$')
ax2.set_title('Electric Field')
ax2.set_aspect('equal')

plt.tight_layout()
plt.suptitle('capacitor_2d')
plt.show()
print("03_capacitor_2d.py done")
