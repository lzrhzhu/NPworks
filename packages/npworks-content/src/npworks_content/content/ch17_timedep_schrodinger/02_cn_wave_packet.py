"""
Crank-Nicolson method for Gaussian wave packet hitting a potential barrier.
Shows |psi|^2 at different times.
Uses hbar=1, m=1.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.sparse.linalg import spsolve

hbar = 1.0
m = 1.0

x_min, x_max = -15.0, 15.0
N = 600
x = np.linspace(x_min, x_max, N)
dx = x[1] - x[0]

dt = 0.005
Nt = 2000

V_height = 1.5
V_width = 0.5
V_center = 0.0
V = np.zeros(N)
V[np.abs(x - V_center) < V_width / 2] = V_height

x0 = -5.0
sigma = 1.0
k0 = 3.0

psi = (2 * np.pi * sigma ** 2) ** (-0.25) \
      * np.exp(-(x - x0) ** 2 / (4 * sigma ** 2)) \
      * np.exp(1j * k0 * x)
norm = np.sqrt(np.trapz(np.abs(psi) ** 2, x))
psi = psi / norm

alpha = 1j * dt / (4 * m * dx ** 2) * hbar

diag_main = 1 + 2 * alpha + 1j * dt / (2 * hbar) * V
diag_off = -alpha * np.ones(N - 1)

A = sparse.diags([diag_off, diag_main, diag_off], [-1, 0, 1], format='csc')
B_diag_main = 1 - 2 * alpha - 1j * dt / (2 * hbar) * V
B_diag_off = alpha * np.ones(N - 1)
B_mat = sparse.diags([B_diag_off, B_diag_main, B_diag_off], [-1, 0, 1], format='csc')

snap_times = [0, 400, 800, 1400, 2000]
snapshots = [(0, np.abs(psi) ** 2)]

for n in range(1, Nt + 1):
    rhs = B_mat @ psi
    psi = spsolve(A, rhs)
    psi[0] = 0
    psi[-1] = 0
    if n in snap_times:
        snapshots.append((n, np.abs(psi) ** 2))

fig, axes = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [3, 1]})

colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
for (n, prob), color in zip(snapshots, colors):
    t_val = n * dt
    axes[0].plot(x, prob, color=color, label=f"t = {t_val:.2f}")

V_scaled = V / np.max(V) * np.max(snapshots[0][1]) * 0.5 if np.max(V) > 0 else V
axes[0].fill_between(x, 0, V_scaled, alpha=0.2, color='red', label='Barrier')
axes[0].set_xlabel("x")
axes[0].set_ylabel("|psi|^2")
axes[0].set_title("Crank-Nicolson: Wave Packet vs Barrier (V0=1.5, E=k0^2/2=4.5)")
axes[0].legend(fontsize=8)
axes[0].grid(True)
axes[0].set_xlim(-12, 12)

axes[1].fill_between(x, 0, V, alpha=0.4, color='orange')
axes[1].plot(x, V, 'k-', linewidth=1)
axes[1].set_xlabel("x")
axes[1].set_ylabel("V(x)")
axes[1].set_title("Potential barrier")
axes[1].grid(True)

fig.tight_layout()

fig.suptitle('cn_barrier')
plt.show()
