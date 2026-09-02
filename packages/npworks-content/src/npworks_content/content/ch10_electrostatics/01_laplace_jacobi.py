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


def jacobi_1d_matrix(V_left, V_right, n, max_iter=5000, tol=1e-10):
    A = (np.diag(-2.0 * np.ones(n)) + np.diag(np.ones(n - 1), 1)
         + np.diag(np.ones(n - 1), -1))
    D = np.diag(np.diag(A))
    L_mat = np.tril(A, -1)
    U_mat = np.triu(A, 1)
    B = np.zeros(n)
    B[0] = -V_left
    B[-1] = -V_right
    J_mat = -np.linalg.solve(D, L_mat + U_mat)
    q = np.linalg.solve(D, B)
    x = np.zeros(n)
    for _ in range(max_iter):
        x_new = J_mat @ x + q
        diff = np.max(np.abs(x_new - x))
        x = x_new
        if diff < tol:
            break
    v = np.concatenate(([V_left], x, [V_right]))
    return v


def jacobi_2d(N, max_iter=10000, tol=1e-6):
    V = np.zeros((N + 1, N + 1))
    V[0, :] = 100.0
    V[-1, :] = 50.0
    V[:, 0] = 0.0
    V[:, -1] = 0.0
    V[0, 0] = 100.0; V[0, -1] = 100.0; V[-1, 0] = 50.0; V[-1, -1] = 50.0
    for _ in range(max_iter):
        V_new = V.copy()
        V_new[1:-1, 1:-1] = 0.25 * (V[:-2, 1:-1] + V[2:, 1:-1] +
                                    V[1:-1, :-2] + V[1:-1, 2:])
        diff = np.max(np.abs(V_new - V))
        V = V_new
        if diff < tol:
            break
    return V


V_left, V_right = 0.0, 1.0
n = 9
v1d = jacobi_1d_matrix(V_left, V_right, n)
x1d = np.linspace(0, 1, n + 2)
v1d_analytic = V_left + (V_right - V_left) * x1d

N2d = 50
V2d = jacobi_2d(N2d)
x2d = np.linspace(0, N2d, N2d + 1) / N2d
y2d = np.linspace(0, N2d, N2d + 1) / N2d
X, Y = np.meshgrid(x2d, y2d)

# --- 图1：1D 解 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x1d, v1d, 'bo-', markersize=4, label='Numerical (matrix Jacobi)')
ax.plot(x1d, v1d_analytic, 'r--', linewidth=2, label='Analytical')
ax.set_xlabel('Position $x / L$')
ax.set_ylabel('Potential $V$')
ax.set_title('1D Laplace: V(0)=0, V(L)=1')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('laplace_jacobi_1d')

# --- 图2：2D 等势线 ---
fig, ax = plt.subplots(figsize=(7, 6))
cs = ax.contourf(X, Y, V2d, levels=20, cmap='viridis')
ax.contour(X, Y, V2d, levels=20, colors='k', linewidths=0.5, alpha=0.5)
plt.colorbar(cs, ax=ax, label='Potential $V$')
ax.set_xlabel('$x / L$'); ax.set_ylabel('$y / L$')
ax.set_title('2D Laplace (Jacobi) - Contours')
ax.set_aspect('equal')
plt.tight_layout()
plt.suptitle('laplace_jacobi')

# --- 图3：2D 曲面 ---
fig = plt.figure(figsize=(8, 6))
ax3 = fig.add_subplot(111, projection='3d')
ax3.plot_surface(X, Y, V2d, cmap='viridis', alpha=0.8, edgecolor='none')
ax3.set_xlabel('$x / L$'); ax3.set_ylabel('$y / L$'); ax3.set_zlabel('Potential $V$')
ax3.set_title('2D Laplace (Jacobi) - Surface')
plt.tight_layout()
plt.suptitle('laplace_jacobi_surface')

print("01_laplace_jacobi.py done")

plt.show()
