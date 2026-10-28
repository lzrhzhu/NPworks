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


def dynamical_matrix(N, boundary):
    D = (np.diag(np.full(N, 2.0)) + np.diag(-np.ones(N - 1), 1)
         + np.diag(-np.ones(N - 1), -1))
    if boundary == 'free':
        D[0, 0] = D[-1, -1] = 1.0
    elif boundary == 'periodic':
        D[0, -1] = D[-1, 0] = -1.0
    return D


N = 24
fig, ax = plt.subplots(figsize=(7.8, 4.6))

w_free = np.sqrt(np.clip(np.linalg.eigvalsh(dynamical_matrix(N, 'free')), 0.0, None))
k_free = np.arange(N) * np.pi / N
ax.plot(k_free / np.pi, w_free, 'o', ms=4.2, color='#0072B2', label='free ends')

w_fixed = np.sqrt(np.linalg.eigvalsh(dynamical_matrix(N, 'fixed')))
k_fixed = np.arange(1, N + 1) * np.pi / (N + 1)
ax.plot(k_fixed / np.pi, w_fixed, 's', ms=3.8, mfc='none', color='#E69F00',
        label='fixed ends')

k_periodic = 2.0 * np.pi * np.fft.fftfreq(N)
w_periodic = np.sqrt(np.clip(np.linalg.eigvalsh(dynamical_matrix(N, 'periodic')), 0.0, None))
w_periodic_by_k = 2.0 * np.abs(np.sin(k_periodic / 2.0))
ax.plot(np.abs(k_periodic) / np.pi, w_periodic_by_k, '+', ms=6.0,
        color='#009E73', label='periodic')

k = np.linspace(0.0, np.pi, 600)
ax.plot(k / np.pi, 2.0 * np.sin(k / 2.0), '-', color='0.3', lw=1.4,
        label='bulk dispersion')
ax.set_xlabel(r'$|k|a/\pi$')
ax.set_ylabel(r'$\omega$ (a.u.)')
ax.set_title('Finite boundaries sample the same bulk curve')
ax.set_xlim(0.0, 1.0)
ax.set_ylim(0.0, 2.08)
ax.legend(frameon=False, loc='lower right', ncols=2)

plt.suptitle('boundary_spectra')
print('periodic matrix/analytic spectrum mismatch:',
      np.max(np.abs(np.sort(w_periodic_by_k) - w_periodic)))
plt.show()
