"""
2D FDTD: Point source radiation (TM mode, Ez).
Saves Ez field snapshots at several time steps.
"""
import numpy as np
import matplotlib.pyplot as plt

c0 = 3e8
mu0 = 4e-7 * np.pi
eps0 = 1.0 / (mu0 * c0 ** 2)

Nx, Ny = 200, 200
dx = dy = 1e-3
S = 0.5
dt = S * dx / (c0 * np.sqrt(2))
Nt = 400

Ez = np.zeros((Nx + 1, Ny + 1))
Hx = np.zeros((Nx + 1, Ny))
Hy = np.zeros((Nx, Ny + 1))

CHx = dt / (mu0 * dy)
CHy = dt / (mu0 * dx)
CEz_x = dt / (eps0 * dx)
CEz_y = dt / (eps0 * dy)

src_i, src_j = Nx // 2, Ny // 2
tau = 40 * dt
t0 = 3 * tau

snap_times = [50, 150, 300]
snapshots = []

for n in range(Nt):
    Hx -= CHx * (Ez[:, 1:] - Ez[:, :-1])
    Hy += CHy * (Ez[1:, :] - Ez[:-1, :])
    Ez[1:-1, 1:-1] += CEz_x * (Hy[1:, 1:-1] - Hy[:-1, 1:-1]) \
                     - CEz_y * (Hx[1:-1, 1:] - Hx[1:-1, :-1])
    t = n * dt
    Ez[src_i, src_j] += np.exp(-((t - t0) / tau) ** 2)
    Ez[0, :] = 0
    Ez[Nx, :] = 0
    Ez[:, 0] = 0
    Ez[:, Ny] = 0
    if n in snap_times:
        snapshots.append((n, Ez.copy()))

fig, axes = plt.subplots(1, len(snapshots), figsize=(5 * len(snapshots), 5))
if len(snapshots) == 1:
    axes = [axes]
for ax, (n, field) in zip(axes, snapshots):
    vmax = max(0.05, np.max(np.abs(field)) * 0.8)
    im = ax.imshow(field.T, cmap='RdBu', vmin=-vmax, vmax=vmax,
                   extent=[0, (Nx + 1) * dx * 1e3, 0, (Ny + 1) * dy * 1e3],
                   origin='lower')
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title(f"Ez at step {n}")
    plt.colorbar(im, ax=ax, shrink=0.8)
fig.suptitle('fdtd_2d_point')
fig.tight_layout()

plt.show()
print("02_fdtd_2d_point_source.py done")
