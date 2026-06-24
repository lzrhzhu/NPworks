"""
1D Poisson equation via FEM: -T'' = f(x), T(0)=0, T(1)=0.
Compares numerical (FEM) solution with analytical solution.
"""
import numpy as np
import matplotlib.pyplot as plt

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
            j_global = e + j_local
            K[i_global, j_global] += Ke[i_local, j_local]

inner = np.arange(1, N)
K_inner = K[np.ix_(inner, inner)]
F_inner = F[inner]

T_inner = np.linalg.solve(K_inner, F_inner)

T = np.zeros(N + 1)
T[1:N] = T_inner

x_anal = np.linspace(0, L, 200)
T_anal = 0.5 * q * x_anal * (L - x_anal)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(x_nodes, T, 'ro-', markersize=6, label='FEM (N={})'.format(N))
axes[0].plot(x_anal, T_anal, 'b-', label='Analytical')
axes[0].set_xlabel('x')
axes[0].set_ylabel('T(x)')
axes[0].set_title('1D Poisson: FEM vs Analytical')
axes[0].legend()
axes[0].grid(True)

T_anal_nodes = 0.5 * q * x_nodes * (L - x_nodes)
error = np.abs(T - T_anal_nodes)
axes[1].semilogy(x_nodes[1:-1], error[1:-1], 'rs-', markersize=6)
axes[1].set_xlabel('x')
axes[1].set_ylabel('|T_FEM - T_analytical|')
axes[1].set_title('Nodal error')
axes[1].grid(True)

fig.tight_layout()

plt.suptitle('fem_1d')
plt.show()
print(f"Max nodal error: {np.max(error[1:-1]):.2e}")
