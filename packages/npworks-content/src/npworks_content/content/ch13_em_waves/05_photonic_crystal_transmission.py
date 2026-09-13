"""
2D FDTD transmission spectrum of a square-lattice photonic crystal
(TM mode, Ez). Dielectric rods (eps_r = 8.9, r/a = 0.2) are arranged in a
square lattice spanning the full domain height; a broadband Gaussian line
source (plane wave) enters from the left. The transmitted power flux
(time-averaged Poynting flux through a probe plane right of the crystal)
is compared between a run with the crystal and a reference run (no
crystal); the flux ratio gives |T|^2 vs the normalized frequency f*a/c,
revealing the photonic band gap.
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

a = 20                      # lattice constant in cells
r = int(0.2 * a)            # rod radius in cells
eps_rod = 8.9
npx = 6                     # periods along x (propagation direction)
margin = 50
Nx = npx * a + 2 * margin
Ny = 10 * a                 # crystal spans the full domain height
dx = dy = 1e-3
a_phys = a * dx
S = 0.5
dt = S * dx / (c0 * np.sqrt(2))
Nt = 9000

x0 = margin
ii = np.arange(Nx + 1)
jj = np.arange(Ny + 1)


def build_eps():
    eps = np.ones((Nx + 1, Ny + 1))
    X, Y = np.meshgrid(ii, jj, indexing="ij")
    # fold position onto nearest lattice point; rods tile the full height
    rx = ((X - x0) % a)
    rx = np.minimum(rx, a - rx)
    ry = ((Y - margin) % a)
    ry = np.minimum(ry, a - ry)
    rod = (rx ** 2 + ry ** 2 < r ** 2) & (X >= x0) & (X < x0 + npx * a)
    eps[rod] = eps_rod
    return eps


eps_crystal = build_eps()
Cb = dt / (eps0 * eps_crystal)          # position-dependent (array)
CHx = dt / (mu0 * dy)
CHy = dt / (mu0 * dx)

src_col = margin // 2
flux_col = margin + npx * a + 15        # probe plane right of the crystal
tau = 45 * dt
t0 = 3 * tau
mur = (c0 * dt - dx) / (c0 * dt + dx)


def run(use_crystal):
    cb = Cb if use_crystal else dt / (eps0 * np.ones((Nx + 1, Ny + 1)))
    Ez = np.zeros((Nx + 1, Ny + 1))
    Hx = np.zeros((Nx + 1, Ny))
    Hy = np.zeros((Nx, Ny + 1))
    recE = np.zeros((Nt, Ny + 1))
    recH = np.zeros((Nt, Ny + 1))
    for n in range(Nt):
        eL, eL1 = Ez[0, :].copy(), Ez[1, :].copy()
        eR, eR1 = Ez[Nx, :].copy(), Ez[Nx - 1, :].copy()
        eB, eB1 = Ez[:, 0].copy(), Ez[:, 1].copy()
        eT, eT1 = Ez[:, Ny].copy(), Ez[:, Ny - 1].copy()
        Hx -= CHx * (Ez[:, 1:] - Ez[:, :-1])
        Hy += CHy * (Ez[1:, :] - Ez[:-1, :])
        Ez[1:-1, 1:-1] += cb[1:-1, 1:-1] * (
            (Hy[1:, 1:-1] - Hy[:-1, 1:-1]) / dx
            - (Hx[1:-1, 1:] - Hx[1:-1, :-1]) / dy)
        t = n * dt
        Ez[src_col, :] += np.exp(-((t - t0) / tau) ** 2)   # line source -> plane wave
        # Mur 1st-order ABC on the four edges (time-n values saved above)
        Ez[0, :] = eL1 + mur * (Ez[1, :] - eL)
        Ez[Nx, :] = eR1 + mur * (Ez[Nx - 1, :] - eR)
        Ez[:, 0] = eB1 + mur * (Ez[:, 1] - eB)
        Ez[:, Ny] = eT1 + mur * (Ez[:, Ny - 1] - eT)
        recE[n] = Ez[flux_col, :]
        recH[n] = Hy[flux_col, :]
    Ef = np.fft.rfft(recE, axis=0)
    Hf = np.fft.rfft(recH, axis=0)
    # time-averaged Poynting flux through the probe plane, per frequency
    return np.real(np.sum(Ef * np.conj(Hf), axis=1))


flux_ref = run(False)
flux_cry = run(True)
freqs = np.fft.rfftfreq(Nt, dt)
T = flux_cry / flux_ref        # both fluxes negative in this sign convention
fa_c = freqs * a_phys / c0

fmax = 0.7
band = (fa_c > 0.02) & (fa_c < fmax)
valid = -flux_ref > 0.01 * (-flux_ref[band]).max()   # source has meaningful power
mask = valid & (fa_c > 0.15) & (fa_c < fmax)

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(fa_c[mask], np.abs(T[mask]) ** 2)
ax.set_xlabel("normalized frequency  f·a / c")
ax.set_ylabel("transmittance  |T|²")
ax.set_title("2D photonic crystal (square lattice, εr = 8.9, r/a = 0.2): transmission")
ax.set_xlim(0.15, 0.65)
ax.set_ylim(0, 1.05)

plt.suptitle('photonic_crystal_transmission')
plt.show()
print("05_photonic_crystal_transmission.py done")
