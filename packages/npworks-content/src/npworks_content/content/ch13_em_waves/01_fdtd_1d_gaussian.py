"""
1D FDTD: Gaussian pulse propagation with Mur absorbing boundary conditions.
Saves Ez snapshots at several time steps.
"""
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0),
                     'font.size': 11, 'axes.titlesize': 12,
                     'axes.labelsize': 11, 'xtick.labelsize': 10,
                     'ytick.labelsize': 10, 'legend.fontsize': 10,
                     'xtick.direction': 'in', 'ytick.direction': 'in',
                     'xtick.top': True, 'ytick.right': True,
                     'axes.grid': False, 'axes.unicode_minus': False})

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
snap_times = [50, 100, 150, 200, 250]

for n in range(Nt):
    e0, e1 = Ez[0], Ez[1]
    en1, en2 = Ez[Nx - 1], Ez[Nx]
    Hy += coeff_H * (Ez[1:] - Ez[:-1])
    Ez[1:-1] += coeff_E * (Hy[1:] - Hy[:-1])
    t = n * dt
    Ez[src_pos] += np.exp(-((t - t0) / tau) ** 2)
    # Mur 1st-order ABC: needs the time-n values saved above
    Ez[0] = e1 + mur_coeff * (Ez[1] - e0)
    Ez[Nx] = en1 + mur_coeff * (en2 - Ez[Nx])
    if n in snap_times:
        snapshots.append((n, Ez.copy()))

x = np.linspace(0, 1, Nx + 1)

fig, ax = plt.subplots(figsize=(10, 5))
colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
styles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1))]
for (n, frame), color, ls in zip(snapshots, colors, styles):
    ax.plot(x, frame, label=f"n = {n}", color=color, ls=ls)
ax.set_xlabel("x (m)")
ax.set_ylabel("Ez (V/m)")
ax.set_title("1D FDTD: Gaussian Pulse with Mur ABC")
ax.legend(frameon=False, loc='upper right')
ax.set_xlim(0, 1)

plt.suptitle('fdtd_1d_gaussian')
plt.show()
print("01_fdtd_1d_gaussian.py done")
