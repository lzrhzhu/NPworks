import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})

N = 2048
s = np.arange(N)
omega = 2.0 * np.sin(np.pi * s / (2.0 * N))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.9))

ax1.step(omega, (s + 1) / N, where='post', color='#0072B2', lw=1.2,
         label=f'finite chain, $N={N}$')
w = np.linspace(0.0, 1.9995, 800)
idos = 2.0 / np.pi * np.arcsin(w / 2.0)
ax1.plot(w, idos, '--', color='#D55E00', lw=1.4, label='continuum limit')
ax1.set_xlabel(r'$\omega$ (a.u.)')
ax1.set_ylabel(r'$F_N(\omega)$')
ax1.set_title('(a) Integrated density of states')
ax1.set_xlim(0.0, 2.02)
ax1.set_ylim(0.0, 1.03)
ax1.legend(frameon=False, loc='upper left')

bins = np.linspace(0.0, 2.0, 65)
ax2.hist(omega, bins=bins, density=True, histtype='step', lw=1.4,
         color='#0072B2', label='eigenvalue histogram')
w_dos = np.linspace(0.0, 1.985, 800)
dos = 2.0 / (np.pi * np.sqrt(4.0 - w_dos**2))
ax2.plot(w_dos, dos, '--', color='#D55E00', lw=1.4,
         label=r'$2/[\pi\sqrt{4-\omega^2}]$')
ax2.set_xlabel(r'$\omega$ (a.u.)')
ax2.set_ylabel(r'$g(\omega)$ (a.u.$^{-1}$)')
ax2.set_title('(b) Density grows at the band edge')
ax2.set_xlim(0.0, 2.02)
ax2.set_ylim(0.0, 3.6)
ax2.legend(frameon=False, loc='upper left')

plt.suptitle('density_of_states')
print('fraction of modes above omega=1.9:', np.mean(omega > 1.9))
plt.show()
