"""
1D FDTD stability demo: the CFL condition requires the Courant number
S = c*dt/dx <= 1. With S = 0.99 the run is stable (|Ez| stays bounded),
while S = 1.1 violates CFL and |Ez| grows exponentially -- numerical
instability. PEC boundaries, Gaussian soft source.
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
Nt = 300


def run(S):
    dt = S * dx / c0
    Ez = np.zeros(Nx + 1)
    Hy = np.zeros(Nx)
    coeff_H = dt / (mu0 * dx)
    coeff_E = dt / (eps0 * dx)
    tau = 30 * dt
    t0 = 3 * tau
    src = Nx // 2
    max_field = []
    for n in range(Nt):
        Hy += coeff_H * (Ez[1:] - Ez[:-1])
        Ez[1:-1] += coeff_E * (Hy[1:] - Hy[:-1])
        Ez[src] += np.exp(-((n * dt - t0) / tau) ** 2)
        Ez[0] = 0          # PEC boundaries
        Ez[Nx] = 0
        max_field.append(np.max(np.abs(Ez)))
    return np.array(max_field)


m_stable = run(0.99)
m_unstable = run(1.1)

fig, ax = plt.subplots(figsize=(9, 6))
ax.semilogy(m_stable, label="S = 0.99 (stable)")
ax.semilogy(m_unstable, label="S = 1.1 (unstable, CFL violated)")
ax.set_xlabel("Time step")
ax.set_ylabel("max |Ez| (V/m)")
ax.set_title("1D FDTD stability: CFL condition S = cΔt/Δx ≤ 1")
ax.legend()

plt.suptitle('fdtd_instability')
plt.show()
print("03_fdtd_instability.py done")
