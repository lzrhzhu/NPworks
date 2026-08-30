"""
1D Poisson equation via FEM: -T'' = f(x), T(0)=0, T(1)=0.
Compares numerical (FEM) solution with analytical solution.
"""
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


L = 1.0
N = 10
q = 1.0
h = L / N
x_nodes = np.linspace(0, L, N + 1)

K = np.zeros((N + 1, N + 1))
F = np.zeros(N + 1)
for e in range(N):
    he = x_nodes[e + 1] - x_nodes[e]
    Ke = (1.0 / he) * np.array([[1, -1], [-1, 1]])
    Fe = (q * he / 2.0) * np.array([1.0, 1.0])
    for i_local in range(2):
        i_global = e + i_local
        F[i_global] += Fe[i_local]
        for j_local in range(2):
            K[i_global, e + j_local] += Ke[i_local, j_local]

inner = np.arange(1, N)
T_inner = np.linalg.solve(K[np.ix_(inner, inner)], F[inner])
T = np.zeros(N + 1)
T[1:N] = T_inner

x_anal = np.linspace(0, L, 200)
T_anal = 0.5 * q * x_anal * (L - x_anal)
T_anal_nodes = 0.5 * q * x_nodes * (L - x_nodes)
error = np.abs(T - T_anal_nodes)

# --- 图1：FEM 解 vs 解析解 ---
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.plot(x_nodes, T, 'ro-', markersize=6, label='FEM (N={})'.format(N))
ax.plot(x_anal, T_anal, 'b-', label='Analytical')
ax.set_xlabel('x (L)'); ax.set_ylabel('T (qL²/κ)')
ax.set_title('1D Poisson: FEM vs analytical')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('fem_1d')

# --- 图2：节点误差 ---
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.semilogy(x_nodes[1:-1], error[1:-1], 'rs-', markersize=6)
ax.set_xlabel('x (L)'); ax.set_ylabel('|T_FEM − T_exact|')
ax.set_title('Nodal error')
plt.tight_layout()
plt.suptitle('fem_1d_error')

print(f"Max nodal error: {np.max(error[1:-1]):.2e}")
print("01_fem_1d_poisson.py done")

plt.show()
