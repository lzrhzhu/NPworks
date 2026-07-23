import numpy as np
import matplotlib.pyplot as plt
import os


def _img_dir(ch):
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "markdown")):
            return os.path.join(d, "markdown", "images", ch)
        d = os.path.dirname(d)
    out = os.path.join(os.path.expanduser("~"), "npworks_figures", ch)
    os.makedirs(out, exist_ok=True)
    return out


IMG_DIR = _img_dir("ch10")


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
                if (j == start and start <= i <= end) or (j == end and start <= i <= end):
                    continue
                V_new = 0.25 * (V[i-1, j] + V[i+1, j] + V[i, j-1] + V[i, j+1])
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
start = N // 4
end = N - start

# --- 图1：等势线 ---
fig, ax = plt.subplots(figsize=(7, 6))
levels = np.linspace(-1, 1, 21)
cs = ax.contourf(X, Y, V, levels=levels, cmap='RdBu_r')
ax.contour(X, Y, V, levels=levels, colors='k', linewidths=0.5, alpha=0.5)
plt.colorbar(cs, ax=ax, label='Potential $V$')
ax.plot([start/N, start/N], [start/N, end/N], 'k-', linewidth=3)
ax.plot([end/N, end/N], [start/N, end/N], 'k-', linewidth=3)
ax.set_xlabel('$x / L$'); ax.set_ylabel('$y / L$')
ax.set_title('Parallel Plate Capacitor - Equipotential Contours')
ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch10_capacitor_2d.png"), dpi=130)
plt.close(fig)

# --- 图2：电场 ---
Ey, Ex = np.gradient(-V, 1.0 / N, 1.0 / N)
E_mag = np.sqrt(Ex ** 2 + Ey ** 2)
skip = 4
fig, ax = plt.subplots(figsize=(7, 6))
cf = ax.contourf(X, Y, E_mag, levels=30, cmap='hot')
plt.colorbar(cf, ax=ax, label='$|E|$')
ax.quiver(X[::skip, ::skip], Y[::skip, ::skip], Ex[::skip, ::skip], Ey[::skip, ::skip],
          color='white', alpha=0.7, scale=30)
ax.plot([start/N, start/N], [start/N, end/N], 'k-', linewidth=3)
ax.plot([end/N, end/N], [start/N, end/N], 'k-', linewidth=3)
ax.set_xlabel('$x / L$'); ax.set_ylabel('$y / L$')
ax.set_title('Electric Field')
ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch10_capacitor_field.png"), dpi=130)
plt.close(fig)

print("03_capacitor_2d.py done")
