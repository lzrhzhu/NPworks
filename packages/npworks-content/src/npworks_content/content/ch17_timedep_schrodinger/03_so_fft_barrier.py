"""
Split-operator FFT (SO-FFT) method for the same barrier tunneling
problem as 02_cn_wave_packet.py (E = 4.5 < V0 = 6).

One Strang step:
    psi -> exp(-i V dt/2) * IFFT[ exp(-i k^2 dt/2) * FFT[ exp(-i V dt/2) psi ] ]
All substeps are unitary, so the norm is preserved exactly.
"""
import time
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300,
    'figure.figsize': (6.4, 4.0),
    'font.size': 11,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.top': True,
    'ytick.right': True,
    'axes.linewidth': 0.8,
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'axes.grid': False,
    'axes.unicode_minus': False,
})

x_min, x_max = -20.0, 20.0
N = 512
x = np.linspace(x_min, x_max, N, endpoint=False)
dx = x[1] - x[0]
dt = 0.01
Nt = 250                        # total time t = 2.5, same as the CN run

V_height = 6.0
V_width = 0.8
V = np.zeros(N)
V[np.abs(x) < V_width / 2] = V_height

x0, sigma, k0 = -5.0, 2.0, 3.0          # same as CN run: E = 4.5 < V0
psi = (2 * np.pi * sigma ** 2) ** (-0.25) \
      * np.exp(-(x - x0) ** 2 / (4 * sigma ** 2)) * np.exp(1j * k0 * x)
psi /= np.sqrt(np.sum(np.abs(psi) ** 2) * dx)

# wavenumber grid matched to FFT output ordering (hbar = m = 1)
k = 2 * np.pi * np.fft.fftfreq(N, d=dx)

P_V = np.exp(-1j * V * dt / 2)
P_T = np.exp(-1j * k ** 2 * dt / 2)

snap_steps = [0, 50, 100, 175, 250]
snapshots = [(0, np.abs(psi) ** 2)]

t_start = time.perf_counter()
for n in range(1, Nt + 1):
    psi = P_V * psi
    psi_k = np.fft.fft(psi)
    psi_k *= P_T
    psi = np.fft.ifft(psi_k)
    psi *= P_V
    if n in snap_steps:
        snapshots.append((n, np.abs(psi) ** 2))
elapsed = time.perf_counter() - t_start

norm = np.sum(np.abs(psi) ** 2) * dx
print(f"SO-FFT {Nt} steps (N = {N}): {elapsed:.3f} s, final norm = {norm:.12f}")

colors = plt.cm.viridis(np.linspace(0, 1, len(snapshots)))
styles = ['-', '--', '-.', ':', '-.']

fig, ax = plt.subplots(figsize=(7.2, 4.5))
peak0 = snapshots[0][1].max()
for idx, ((n, prob), color) in enumerate(zip(snapshots, colors)):
    ax.plot(x, prob, color=color, ls=styles[idx % len(styles)],
            label=f"t = {n * dt:.2f}")
ax.fill_between(x, 0, V / V_height * 0.5 * peak0, alpha=0.2,
                color='red', label='Barrier (scaled)')
ax.set_xlabel("x (a.u.)")
ax.set_ylabel(r"$|\psi|^2$ (a.u.$^{-1}$)")
ax.set_title("SO-FFT: tunneling through barrier (E=4.5 < V0=6)")
ax.legend(frameon=False, fontsize=8)
ax.set_xlim(-12, 12)

fig.suptitle('sofft_barrier')
plt.show()
