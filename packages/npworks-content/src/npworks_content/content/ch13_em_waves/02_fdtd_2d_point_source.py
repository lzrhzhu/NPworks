"""
2D FDTD: Point source radiation (TM mode, Ez).
Saves Ez field snapshots at several time steps as independent images.
"""
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


IMG_DIR = _img_dir("ch13")

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
    Ez[0, :] = 0; Ez[Nx, :] = 0; Ez[:, 0] = 0; Ez[:, Ny] = 0
    if n in snap_times:
        snapshots.append((n, Ez.copy()))

first = True
for n, field in snapshots:
    vmax = max(0.05, np.max(np.abs(field)) * 0.8)
    fig, ax = plt.subplots(figsize=(6, 5.5))
    im = ax.imshow(field.T, cmap='RdBu', vmin=-vmax, vmax=vmax,
                   extent=[0, (Nx + 1) * dx * 1e3, 0, (Ny + 1) * dy * 1e3],
                   origin='lower')
    ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
    ax.set_title(f"Ez at step {n}")
    plt.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    fname = "ch13_fdtd_2d_point.png" if first else f"ch13_fdtd_2d_point_step{n}.png"
    plt.savefig(os.path.join(IMG_DIR, fname), dpi=130)
    plt.close(fig)
    first = False

print("02_fdtd_2d_point_source.py done")
