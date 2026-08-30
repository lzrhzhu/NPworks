"""
Plane-wave expansion (PWE) band structure of a 2D square lattice of
dielectric rods (eps_r = 8.9, r/a = 0.2), H-polarization (H out of plane).
The 1/eps Fourier coefficients are obtained by FFT of the unit cell; the
Hermitian matrix M(k) with elements (k+G_i).(k+G_j) * eta_{G_i-G_j} is
diagonalized along the Gamma-X-M-Gamma path. Eigenvalues give
(omega*a / 2*pi*c)^2, i.e. the photonic bands.
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

a = 1.0
r = 0.2 * a
eps_rod = 8.9
eps_bg = 1.0

Ncell = 64                                 # unit-cell sampling for FFT of 1/eps
xa = np.linspace(0, a, Ncell, endpoint=False)
X, Y = np.meshgrid(xa, xa, indexing="ij")
inv_eps = np.where((X - a / 2) ** 2 + (Y - a / 2) ** 2 <= r ** 2,
                   1.0 / eps_rod, 1.0 / eps_bg)
eta = np.fft.fftn(inv_eps) / (Ncell * Ncell)   # eta[m, n]


def eta_G(p, q):
    return eta[int(p) % Ncell, int(q) % Ncell]


Npw = 7                                    # plane waves per axis: -3 .. 3
offs = np.arange(-(Npw // 2), Npw // 2 + 1)
G = np.array([(m, n) for m in offs for n in offs])   # (Npw^2, 2)
ng = G.shape[0]

# high-symmetry path, k in units of 2*pi/a: Gamma -> X -> M -> Gamma
corners = [np.array([0.0, 0.0]), np.array([0.5, 0.0]),
           np.array([0.5, 0.5]), np.array([0.0, 0.0])]
names = ["Γ", "X", "M", "Γ"]
nk_seg = 25
ks = []
kx_axis = []
corner_x = []
d = 0.0
for seg in range(len(corners) - 1):
    a0, a1 = corners[seg], corners[seg + 1]
    seglen = np.linalg.norm(a1 - a0)
    s_vals = np.linspace(0, 1, nk_seg)
    if seg == 0:
        ks.append(a0.copy())
        kx_axis.append(0.0)
        s_vals = s_vals[1:]
    for s in s_vals:
        d += seglen / nk_seg
        ks.append(a0 + s * (a1 - a0))
        kx_axis.append(d)
    corner_x.append(d)

nbands = 8
bands = np.zeros((len(ks), nbands))
for ki, k in enumerate(ks):
    M = np.zeros((ng, ng), dtype=complex)
    for i in range(ng):
        kGi = k + G[i]
        for j in range(ng):
            M[i, j] = np.dot(kGi, k + G[j]) * eta_G(G[i, 0] - G[j, 0],
                                                    G[i, 1] - G[j, 1])
    w2 = np.linalg.eigvalsh(M)            # ascending = (omega*a/2*pi*c)^2
    bands[ki, :] = np.sqrt(np.clip(w2[:nbands], 0, None))

fig, ax = plt.subplots(figsize=(8, 6))
for b in range(nbands):
    ax.plot(kx_axis, bands[:, b], color="C0")
for cx in corner_x:
    ax.axvline(cx, color="gray", ls="--", lw=0.8)
ax.set_xticks([0] + corner_x)
ax.set_xticklabels(names)
ax.set_ylabel("frequency  ω·a / (2πc)")
ax.set_title("PWE band structure: square lattice of rods (εr = 8.9, r/a = 0.2)")
ax.set_ylim(0, max(0.8, bands[:, nbands - 1].max() * 1.05))

plt.suptitle('plane_wave_expansion_bands')
plt.show()
print("06_plane_wave_expansion_bands.py done")
