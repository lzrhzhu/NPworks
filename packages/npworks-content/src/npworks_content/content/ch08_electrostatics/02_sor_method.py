import numpy as np
import matplotlib.pyplot as plt


def solve_laplace_jacobi(N, max_iter=5000, tol=1e-10):
    V = np.zeros((N + 1, N + 1))
    V[0, :] = 100.0
    V[-1, :] = 50.0
    V[:, 0] = 0.0
    V[:, -1] = 0.0
    V[0, 0] = 100.0
    V[0, -1] = 100.0
    V[-1, 0] = 50.0
    V[-1, -1] = 50.0
    residuals = []
    for it in range(max_iter):
        V_new = V.copy()
        V_new[1:-1, 1:-1] = 0.25 * (V[:-2, 1:-1] + V[2:, 1:-1] +
                                      V[1:-1, :-2] + V[1:-1, 2:])
        diff = np.max(np.abs(V_new - V))
        residuals.append(diff)
        V = V_new
        if diff < tol:
            break
    return residuals


def solve_laplace_gs(N, max_iter=5000, tol=1e-10):
    V = np.zeros((N + 1, N + 1))
    V[0, :] = 100.0
    V[-1, :] = 50.0
    V[:, 0] = 0.0
    V[:, -1] = 0.0
    V[0, 0] = 100.0
    V[0, -1] = 100.0
    V[-1, 0] = 50.0
    V[-1, -1] = 50.0
    residuals = []
    for it in range(max_iter):
        V_old = V.copy()
        for i in range(1, N):
            for j in range(1, N):
                V[i, j] = 0.25 * (V[i-1, j] + V[i+1, j] +
                                   V[i, j-1] + V[i, j+1])
        diff = np.max(np.abs(V - V_old))
        residuals.append(diff)
        if diff < tol:
            break
    return residuals


def solve_laplace_sor(N, omega, max_iter=5000, tol=1e-10):
    V = np.zeros((N + 1, N + 1))
    V[0, :] = 100.0
    V[-1, :] = 50.0
    V[:, 0] = 0.0
    V[:, -1] = 0.0
    V[0, 0] = 100.0
    V[0, -1] = 100.0
    V[-1, 0] = 50.0
    V[-1, -1] = 50.0
    residuals = []
    for it in range(max_iter):
        V_old = V.copy()
        for i in range(1, N):
            for j in range(1, N):
                V_new = 0.25 * (V[i-1, j] + V[i+1, j] +
                                V[i, j-1] + V[i, j+1])
                V[i, j] = (1 - omega) * V[i, j] + omega * V_new
        diff = np.max(np.abs(V - V_old))
        residuals.append(diff)
        if diff < tol:
            break
    return residuals


N = 30

res_jacobi = solve_laplace_jacobi(N)
res_gs = solve_laplace_gs(N)
omega_opt = 2.0 / (1.0 + np.sin(np.pi / N))
res_sor = solve_laplace_sor(N, omega_opt)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

iters_j = np.arange(1, len(res_jacobi) + 1)
iters_gs = np.arange(1, len(res_gs) + 1)
iters_sor = np.arange(1, len(res_sor) + 1)

ax1.semilogy(iters_j, res_jacobi, label='Jacobi')
ax1.semilogy(iters_gs, res_gs, label='Gauss-Seidel')
ax1.semilogy(iters_sor, res_sor, label=f'SOR ($\\omega = {omega_opt:.3f}$)')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Max residual')
ax1.set_title(f'Convergence Comparison (N = {N})')
ax1.legend()
ax1.grid(True, alpha=0.3)

omega_range = np.linspace(1.0, 1.95, 20)
iter_counts = []
for omega in omega_range:
    res = solve_laplace_sor(N, omega, max_iter=5000, tol=1e-8)
    iter_counts.append(len(res))

ax2.plot(omega_range, iter_counts, 'o-', markersize=5)
ax2.axvline(omega_opt, color='red', linestyle='--',
            label=f'$\\omega_{{opt}} = {omega_opt:.3f}$')
ax2.set_xlabel('Relaxation factor $\\omega$')
ax2.set_ylabel('Iterations to converge')
ax2.set_title('SOR: Iterations vs $\\omega$')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('sor_convergence')
plt.show()
print(f"02_sor_method.py done (omega_opt={omega_opt:.4f})")
