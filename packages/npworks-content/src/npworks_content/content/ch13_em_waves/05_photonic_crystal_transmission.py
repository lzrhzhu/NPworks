"""
2D FDTD transmission spectrum of a square-lattice photonic crystal
(TM mode, Ez). Dielectric rods (eps_r = 8.9, r/a = 0.2) are arranged in a
square lattice; a broadband Gaussian line source (plane wave) enters from the
left and the transmitted field is recorded on the right. Comparing a run with
the crystal to a reference run (no crystal) and FFT-ing gives |T|^2 vs the
normalized frequency f*a/c, revealing the photonic band gap.
"""
import numpy as np
import matplotlib.pyplot as plt

c0 = 3e8
mu0 = 4e-7 * np.pi
eps0 = 1.0 / (mu0 * c0 ** 2)

a = 20                      # lattice constant in cells
r = int(0.2 * a)            # rod radius in cells
eps_rod = 8.9
npx, npy = 6, 5             # periods along x (propagation) and y
margin = 25
Nx = npx * a + 2 * margin
Ny = npy * a + 2 * margin
dx = dy = 1e-3
a_phys = a * dx
S = 0.5
dt = S * dx / (c0 * np.sqrt(2))
Nt = 4500

# crystal occupies [margin : margin + npx*a] in x
x0 = margin
ii = np.arange(Nx + 1)
jj = np.arange(Ny + 1)


def build_eps():
    eps = np.ones((Nx + 1, Ny + 1))
    X, Y = np.meshgrid(ii, jj, indexing="ij")
    # fold position onto nearest lattice point; rod centered at each lattice site
    rx = ((X - x0) % a)
    rx = np.minimum(rx, a - rx)
    ry = ((Y - margin) % a)
    ry = np.minimum(ry, a - ry)
    in_crystal_x = (X >= x0) & (X < x0 + npx * a)
    in_crystal_y = (Y >= margin) & (Y < margin + npy * a)
    rod = (rx ** 2 + ry ** 2 < r ** 2) & in_crystal_x & in_crystal_y
    eps[rod] = eps_rod
    return eps


eps_crystal = build_eps()
Cb = dt / (eps0 * eps_crystal)          # position-dependent (array)
CHx = dt / (mu0 * dy)
CHy = dt / (mu0 * dx)

src_col = margin // 2
trans_col = Nx - margin // 2
tau = 60 * dt
t0 = 3 * tau
mur = (c0 * dt - dx) / (c0 * dt + dx)


def run(use_crystal):
    cb = Cb if use_crystal else dt / (eps0 * np.ones((Nx + 1, Ny + 1)))
    Ez = np.zeros((Nx + 1, Ny + 1))
    Hx = np.zeros((Nx + 1, Ny))
    Hy = np.zeros((Nx, Ny + 1))
    trans = np.zeros(Nt)
    for n in range(Nt):
        Hx -= CHx * (Ez[:, 1:] - Ez[:, :-1])
        Hy += CHy * (Ez[1:, :] - Ez[:-1, :])
        Ez[1:-1, 1:-1] += cb[1:-1, 1:-1] * (
            (Hy[1:, 1:-1] - Hy[:-1, 1:-1]) / dx
            - (Hx[1:-1, 1:] - Hx[1:-1, :-1]) / dy)
        t = n * dt
        Ez[src_col, :] += np.exp(-((t - t0) / tau) ** 2)   # line source -> plane wave
        # Mur 1st-order ABC on the four edges
        Ez[0, :] = Ez[1, :] + mur * (Ez[1, :] - Ez[0, :])
        Ez[Nx, :] = Ez[Nx - 1, :] + mur * (Ez[Nx - 1, :] - Ez[Nx, :])
        Ez[:, 0] = Ez[:, 1] + mur * (Ez[:, 1] - Ez[:, 0])
        Ez[:, Ny] = Ez[:, Ny - 1] + mur * (Ez[:, Ny - 1] - Ez[:, Ny])
        trans[n] = Ez[trans_col, :].sum()
    return trans


trans_ref = run(False)
trans_cry = run(True)

freqs = np.fft.rfftfreq(Nt, dt)
ref_spec = np.abs(np.fft.rfft(trans_ref))
T = np.fft.rfft(trans_cry) / (ref_spec + 1e-30)
fa_c = freqs * a_phys / c0

fmax = 0.7
valid = ref_spec > 0.01 * ref_spec.max()      # keep only where the source has power
mask = valid & (fa_c > 0.01) & (fa_c < fmax)

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(fa_c[mask], np.abs(T[mask]) ** 2)
ax.set_xlabel("normalized frequency  f·a / c")
ax.set_ylabel("transmittance  |T|²")
ax.set_title("2D photonic crystal (square lattice, εr = 8.9, r/a = 0.2): transmission")
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1.05)

plt.suptitle('photonic_crystal_transmission')
plt.show()
print("05_photonic_crystal_transmission.py done")
