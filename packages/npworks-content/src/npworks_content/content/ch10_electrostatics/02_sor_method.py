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


def solve_laplace_jacobi(N, max_iter=5000, tol=1e-10):
    V = np.zeros((N + 1, N + 1))
    V[0, :] = 100.0; V[-1, :] = 50.0; V[:, 0] = 0.0; V[:, -1] = 0.0
    V[0, 0] = 100.0; V[0, -1] = 100.0; V[-1, 0] = 50.0; V[-1, -1] = 50.0
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
    V[0, :] = 100.0; V[-1, :] = 50.0; V[:, 0] = 0.0; V[:, -1] = 0.0
    V[0, 0] = 100.0; V[0, -1] = 100.0; V[-1, 0] = 50.0; V[-1, -1] = 50.0
    residuals = []
    for it in range(max_iter):
        V_old = V.copy()
        for i in range(1, N):
            for j in range(1, N):
                V[i, j] = 0.25 * (V[i-1, j] + V[i+1, j] + V[i, j-1] + V[i, j+1])
        diff = np.max(np.abs(V - V_old))
        residuals.append(diff)
        if diff < tol:
            break
    return residuals


def solve_laplace_sor(N, omega, max_iter=5000, tol=1e-10):
    V = np.zeros((N + 1, N + 1))
    V[0, :] = 100.0; V[-1, :] = 50.0; V[:, 0] = 0.0; V[:, -1] = 0.0
    V[0, 0] = 100.0; V[0, -1] = 100.0; V[-1, 0] = 50.0; V[-1, -1] = 50.0
    residuals = []
    for it in range(max_iter):
        V_old = V.copy()
        for i in range(1, N):
            for j in range(1, N):
                V_new = 0.25 * (V[i-1, j] + V[i+1, j] + V[i, j-1] + V[i, j+1])
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

# --- 图1：收敛对比 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.semilogy(np.arange(1, len(res_jacobi) + 1), res_jacobi, label='Jacobi')
ax.semilogy(np.arange(1, len(res_gs) + 1), res_gs, label='Gauss-Seidel')
ax.semilogy(np.arange(1, len(res_sor) + 1), res_sor, label=f'SOR ($\\omega = {omega_opt:.3f}$)')
ax.set_xlabel('Iteration')
ax.set_ylabel('Max residual')
ax.set_title(f'Convergence Comparison (N = {N})')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch10_sor_convergence.png"), dpi=130)
plt.close(fig)

# --- 图2：迭代次数 vs omega ---
omega_range = np.linspace(1.0, 1.95, 20)
iter_counts = [len(solve_laplace_sor(N, w, max_iter=5000, tol=1e-8)) for w in omega_range]
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.plot(omega_range, iter_counts, 'o-', markersize=5)
ax.axvline(omega_opt, color='red', linestyle='--', label=f'$\\omega_{{opt}} = {omega_opt:.3f}$')
ax.set_xlabel('Relaxation factor $\\omega$')
ax.set_ylabel('Iterations to converge')
ax.set_title('SOR: Iterations vs $\\omega$')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch10_sor_omega.png"), dpi=130)
plt.close(fig)

print(f"02_sor_method.py done (omega_opt={omega_opt:.4f})")
