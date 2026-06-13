"""
1D FDTD: Gaussian pulse propagation with Mur absorbing boundary conditions.
Saves Ez snapshots at several time steps.
"""
import numpy as np
import matplotlib.pyplot as plt

c0 = 3e8
mu0 = 4e-7 * np.pi
eps0 = 1.0 / (mu0 * c0 ** 2)

Nx = 200
dx = 1.0 / Nx
S = 0.99
dt = S * dx / c0
Nt = 500

tau = 30 * dt
t0 = 3 * tau
src_pos = Nx // 2

Ez = np.zeros(Nx + 1)
Hy = np.zeros(Nx)

coeff_H = dt / (mu0 * dx)
coeff_E = dt / (eps0 * dx)
mur_coeff = (c0 * dt - dx) / (c0 * dt + dx)

snapshots = []
snap_times = [0, 100, 200, 300, 400]

for n in range(Nt):
    Hy += coeff_H * (Ez[1:] - Ez[:-1])
    Ez[1:-1] += coeff_E * (Hy[1:] - Hy[:-1])
    t = n * dt
    Ez[src_pos] += np.exp(-((t - t0) / tau) ** 2)
    Ez[0] = Ez[1] + mur_coeff * (Ez[1] - Ez[0])
    Ez[Nx] = Ez[Nx - 1] + mur_coeff * (Ez[Nx - 1] - Ez[Nx])
    if n in snap_times:
        snapshots.append((n, Ez.copy()))

x = np.linspace(0, 1, Nx + 1)

fig, ax = plt.subplots(figsize=(10, 6))
colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
for (n, frame), color in zip(snapshots, colors):
    ax.plot(x, frame, label=f"n = {n}", color=color)
ax.set_xlabel("x (m)")
ax.set_ylabel("Ez")
ax.set_title("1D FDTD: Gaussian Pulse with Mur ABC")
ax.legend()
ax.grid(True)
ax.set_xlim(0, 1)

plt.suptitle('fdtd_1d_gaussian')
plt.show()
print("01_fdtd_1d_gaussian.py done")
