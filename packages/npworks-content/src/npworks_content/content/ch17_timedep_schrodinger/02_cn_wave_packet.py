"""
Crank-Nicolson method for Gaussian wave packet hitting a potential barrier.
Shows |psi|^2 at different times. (hbar=1, m=1)
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.sparse.linalg import spsolve


x_min, x_max = -15.0, 15.0
N = 600
x = np.linspace(x_min, x_max, N)
dx = x[1] - x[0]
dt = 0.005
Nt = 2000

V_height = 1.5
V_width = 0.5
V = np.zeros(N)
V[np.abs(x) < V_width / 2] = V_height

x0, sigma, k0 = -5.0, 1.0, 3.0
psi = (2 * np.pi * sigma ** 2) ** (-0.25) * np.exp(-(x - x0) ** 2 / (4 * sigma ** 2)) * np.exp(1j * k0 * x)
psi = psi / np.sqrt(np.trapz(np.abs(psi) ** 2, x))

alpha = 1j * dt / (4 * 1.0 * dx ** 2)
diag_main = 1 + 2 * alpha + 1j * dt / 2 * V
diag_off = -alpha * np.ones(N - 1)
A = sparse.diags([diag_off, diag_main, diag_off], [-1, 0, 1], format='csc')
B_mat = sparse.diags([alpha * np.ones(N - 1), 1 - 2 * alpha - 1j * dt / 2 * V, alpha * np.ones(N - 1)],
                     [-1, 0, 1], format='csc')

snap_times = [0, 400, 800, 1400, 2000]
snapshots = [(0, np.abs(psi) ** 2)]
for n in range(1, Nt + 1):
    psi = spsolve(A, B_mat @ psi)
    psi[0] = 0; psi[-1] = 0
    if n in snap_times:
        snapshots.append((n, np.abs(psi) ** 2))

colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
V_scaled = V / np.max(V) * np.max(snapshots[0][1]) * 0.5 if np.max(V) > 0 else V

# --- 图1：波包演化 ---
fig, ax = plt.subplots(figsize=(9, 5.5))
for (n, prob), color in zip(snapshots, colors):
    ax.plot(x, prob, color=color, label=f"t = {n*dt:.2f}")
ax.fill_between(x, 0, V_scaled, alpha=0.2, color='red', label='Barrier')
ax.set_xlabel("x"); ax.set_ylabel("|psi|^2")
ax.set_title("Crank-Nicolson: Wave Packet vs Barrier (V0=1.5, E=k0^2/2=4.5)")
ax.legend(fontsize=8); ax.grid(True); ax.set_xlim(-12, 12)
plt.tight_layout()
plt.suptitle('cn_barrier')

# --- 图2：势垒 ---
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.fill_between(x, 0, V, alpha=0.4, color='orange')
ax.plot(x, V, 'k-', linewidth=1)
ax.set_xlabel("x"); ax.set_ylabel("V(x)")
ax.set_title("Potential barrier"); ax.grid(True)
plt.tight_layout()
plt.suptitle('cn_barrier_potential')

print("02_cn_wave_packet.py done")

plt.show()
