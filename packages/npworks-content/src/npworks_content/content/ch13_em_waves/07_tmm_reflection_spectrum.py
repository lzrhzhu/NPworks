"""
Transfer matrix method (TMM): reflection / transmission spectrum of a
quarter-wave dielectric stack (high reflector) on a glass substrate. Each
layer is a 2x2 matrix; the product gives r and t exactly (no grid, O(N) per
wavelength). Verifies R + T = 1 and shows the high-reflection stop band.
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

n0 = 1.0          # incident medium (air)
ns = 1.5          # substrate (glass)
nL, nH = 1.46, 2.4     # low / high index layers
lam0 = 550.0      # design wavelength (nm)
Nperiod = 8

# quarter-wave optical thickness: n*d = lam0/4
dL = lam0 / (4 * nL)
dH = lam0 / (4 * nH)
n_stack = [nL, nH] * Nperiod
d_stack = [dL, dH] * Nperiod

lams = np.linspace(400.0, 800.0, 800)
R = np.zeros_like(lams)
T = np.zeros_like(lams)

for li, lam in enumerate(lams):
    M = np.eye(2, dtype=complex)
    for n, d in zip(n_stack, d_stack):
        delta = 2 * np.pi * n * d / lam
        Mj = np.array([[np.cos(delta), 1j / n * np.sin(delta)],
                       [1j * n * np.sin(delta), np.cos(delta)]], dtype=complex)
        M = Mj @ M
    m11, m12, m21, m22 = M[0, 0], M[0, 1], M[1, 0], M[1, 1]
    B = m11 + m12 * ns
    C = m21 + m22 * ns
    r = (n0 * B - C) / (n0 * B + C)
    t = 2 * n0 / (n0 * B + C)
    R[li] = np.abs(r) ** 2
    T[li] = (ns / n0) * np.abs(t) ** 2

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(lams, R, label="R  (reflectance)")
ax.plot(lams, T, label="T  (transmittance)")
ax.plot(lams, R + T, "k--", label="R + T  (≈ 1)")
ax.axvline(lam0, color="gray", ls=":", label=f"λ₀ = {lam0:g} nm")
ax.set_xlabel("Wavelength λ (nm)")
ax.set_ylabel("Reflectance / Transmittance")
ax.set_title(f"TMM: quarter-wave high reflector  ({Nperiod} (LH) pairs)")
ax.legend()
ax.set_ylim(0, 1.1)

plt.suptitle('tmm_reflection_spectrum')
plt.show()
print("07_tmm_reflection_spectrum.py done")
