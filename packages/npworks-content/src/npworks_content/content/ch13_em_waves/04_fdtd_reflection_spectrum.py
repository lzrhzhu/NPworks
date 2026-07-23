"""
1D FDTD reflection / transmission spectrum of a dielectric slab (eps_r = 4).
A reference run (no slab) and a main run (with slab) are simulated; FFT of the
probe signals yields R(omega) and T(omega). Mur 1st-order ABC, Gaussian soft
source. Verifies |R|^2 + |T|^2 ~ 1 and shows Fabry-Perot fringes in the slab.
"""
import numpy as np
import matplotlib.pyplot as plt

c0 = 3e8
mu0 = 4e-7 * np.pi
eps0 = 1.0 / (mu0 * c0 ** 2)

Nx = 800
dx = 0.01
S = 0.5
dt = S * dx / c0
Nt = 8192

# dielectric slab eps_r = 4 in the middle third
eps_r = np.ones(Nx + 1)
eps_r[Nx // 3: 2 * Nx // 3] = 4.0

src = Nx // 6
ref_probe = Nx // 4          # left of slab: incident + reflected
trans_probe = 5 * Nx // 6    # right of slab: transmitted

tau = 40 * dt
t0 = 3 * tau
mur = (c0 * dt - dx) / (c0 * dt + dx)


def run(eps):
    cb = dt / (eps * eps0 * dx)
    Ez = np.zeros(Nx + 1)
    Hy = np.zeros(Nx)
    rec_ref = np.zeros(Nt)
    rec_trans = np.zeros(Nt)
    for n in range(Nt):
        Hy += (dt / (mu0 * dx)) * (Ez[1:] - Ez[:-1])
        Ez[1:-1] += cb[1:-1] * (Hy[1:] - Hy[:-1])
        Ez[src] += np.exp(-((n * dt - t0) / tau) ** 2)
        # Mur 1st-order ABC at both ends
        Ez[0] = Ez[1] + mur * (Ez[1] - Ez[0])
        Ez[Nx] = Ez[Nx - 1] + mur * (Ez[Nx - 1] - Ez[Nx])
        rec_ref[n] = Ez[ref_probe]
        rec_trans[n] = Ez[trans_probe]
    return rec_ref, rec_trans


ref_inc, trans_inc = run(np.ones(Nx + 1))      # reference (no slab)
ref_tot, trans_tot = run(eps_r)                # with slab

freqs = np.fft.rfftfreq(Nt, dt)
Einc = np.fft.rfft(ref_inc)
R = np.fft.rfft(ref_tot - ref_inc) / (Einc + 1e-30)
T = np.fft.rfft(trans_tot) / (np.fft.rfft(trans_inc) + 1e-30)

fmax = 2.0e9
mask = (freqs > 1e7) & (freqs < fmax)

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(freqs[mask] / 1e9, np.abs(R[mask]) ** 2, label="|R|² (reflectance)")
ax.plot(freqs[mask] / 1e9, np.abs(T[mask]) ** 2, label="|T|² (transmittance)")
ax.plot(freqs[mask] / 1e9, np.abs(R[mask]) ** 2 + np.abs(T[mask]) ** 2,
        "k--", label="|R|² + |T|² (≈ 1)")
ax.set_xlabel("Frequency (GHz)")
ax.set_ylabel("Reflectance / Transmittance")
ax.set_title("1D FDTD: reflection/transmission spectrum of a dielectric slab (εr = 4)")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1.1)

plt.suptitle('fdtd_reflection_spectrum')
plt.show()
print("04_fdtd_reflection_spectrum.py done")
