"""
2D Poisson equation via linear triangular FEM with a manufactured solution.
Exact: T_exact = sin(pi x) sin(pi y), source f = 2 pi^2 sin(pi x) sin(pi y).
Outputs: numerical solution contours, and mesh-convergence (log-log) study.
"""
import numpy as np
import matplotlib.pyplot as plt


def exact(x, y):
    return np.sin(np.pi * x) * np.sin(np.pi * y)


def source(x, y):
    return 2.0 * np.pi ** 2 * np.sin(np.pi * x) * np.sin(np.pi * y)


def fem_2d_poisson(N):
    h = 1.0 / N
    g = np.linspace(0.0, 1.0, N + 1)
    xs, ys = np.meshgrid(g, g, indexing="xy")
    xs = xs.ravel(); ys = ys.ravel()
    n_id = np.arange((N + 1) ** 2).reshape(N + 1, N + 1)
    nnp = xs.size
    tris = []
    for j in range(N):
        for i in range(N):
            n1 = n_id[j, i]; n2 = n_id[j, i + 1]
            n3 = n_id[j + 1, i]; n4 = n_id[j + 1, i + 1]
            tris.append((n1, n2, n4)); tris.append((n1, n4, n3))
    tris = np.array(tris, dtype=int)
    K = np.zeros((nnp, nnp)); F = np.zeros(nnp)
    for tri in tris:
        ia, ib, ic = tri
        xi, yi = xs[ia], ys[ia]; xj, yj = xs[ib], ys[ib]; xk, yk = xs[ic], ys[ic]
        detJ = (xj - xi) * (yk - yi) - (xk - xi) * (yj - yi)
        area = 0.5 * abs(detJ)
        if area < 1e-15:
            continue
        b = np.array([yj - yk, yk - yi, yi - yj])
        c = np.array([xk - xj, xi - xk, xj - xi])
        Ke = (np.outer(b, b) + np.outer(c, c)) / (4.0 * area)
        cx = (xi + xj + xk) / 3.0; cy = (yi + yj + yk) / 3.0
        Fe = (area / 3.0) * source(cx, cy) * np.ones(3)
        for a in range(3):
            F[tri[a]] += Fe[a]
            for bcol in range(3):
                K[tri[a], tri[bcol]] += Ke[a, bcol]
    is_bnd = np.zeros(nnp, dtype=bool)
    is_bnd[:N + 1] = True; is_bnd[-(N + 1):] = True
    is_bnd[n_id[:, 0]] = True; is_bnd[n_id[:, -1]] = True
    inner = ~is_bnd
    T = np.zeros(nnp)
    T[inner] = np.linalg.solve(K[np.ix_(inner, inner)], F[inner])
    err = T - exact(xs, ys)
    L2 = np.sqrt(np.sum(err ** 2) * h * h)
    return xs, ys, T, h, L2


Ns = [5, 10, 20, 40]
hs, L2s = [], []
last = None
for N in Ns:
    xs, ys, T, h, L2 = fem_2d_poisson(N)
    hs.append(h); L2s.append(L2)
    print(f"N={N:3d}  h={h:.4f}  L2 error={L2:.3e}")
    last = (xs, ys, T, N)

xs, ys, T, N = last
slope = np.polyfit(np.log(hs), np.log(L2s), 1)[0]
print(f"observed convergence order ~ {slope:.2f}")

nn = N + 1
grid = np.linspace(0.0, 1.0, nn)
Z = T.reshape(nn, nn)
Ze = exact(grid[None, :], grid[:, None])
levels = np.linspace(0.0, 1.0, 21)

# --- 图1：数值解 + 解析解等高线 ---
fig, ax = plt.subplots(figsize=(6.5, 6))
cf = ax.contourf(grid, grid, Z, levels=levels, cmap="hot")
ax.contour(grid, grid, Ze, levels=levels, colors="cyan", linewidths=0.8)
fig.colorbar(cf, ax=ax, label="T(x, y)")
ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y")
ax.set_title(f"2D Poisson FEM solution (N={N}); cyan = exact")
plt.tight_layout()
plt.suptitle('fem_2d_validation')

# --- 图2：网格收敛 ---
fig, ax = plt.subplots(figsize=(7, 5.5))
ax.loglog(hs, L2s, "ro-", markersize=7, label=f"FEM L2 error (slope ~ {slope:.2f})")
ref = np.array(hs) ** 2 * (L2s[0] / hs[0] ** 2)
ax.loglog(hs, ref, "k--", label=r"$O(h^2)$ reference")
ax.set_xlabel("mesh size h"); ax.set_ylabel("L2 error")
ax.set_title("Mesh convergence of 2D linear FEM")
ax.grid(True, which="both", ls=":", alpha=0.5); ax.legend()
plt.tight_layout()
plt.suptitle('fem_2d_convergence')

print("02_fem_2d_validation.py done")

plt.show()
