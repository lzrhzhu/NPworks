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


def free_frequencies(N):
    diag = np.full(N, 2.0)
    diag[[0, -1]] = 1.0
    D = (np.diag(diag) + np.diag(-np.ones(N - 1), 1)
         + np.diag(-np.ones(N - 1), -1))
    return np.sqrt(np.clip(np.linalg.eigvalsh(D), 0.0, None))


fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.8))

x_curve = np.linspace(0.0, 1.0, 600)
axes[0].plot(x_curve, 2.0 * np.sin(np.pi * x_curve / 2.0),
             color='0.35', lw=1.5, label='limiting curve')
styles = [('o', '#0072B2'), ('s', '#E69F00'), ('^', '#009E73'), ('+', '#D55E00')]
for N, (marker, color) in zip([4, 8, 32, 128], styles):
    omega = free_frequencies(N)
    x = np.arange(N) / N
    axes[0].plot(x, omega, marker=marker, ls='none', ms=4.0,
                 color=color, label=f'$N={N}$')
axes[0].set_xlabel(r'normalized mode index $s/N$')
axes[0].set_ylabel(r'$\omega$ (a.u.)')
axes[0].set_title('(a) Discrete spectra fill a band')
axes[0].set_xlim(0.0, 1.0)
axes[0].set_ylim(0.0, 2.08)
axes[0].legend(frameon=False, loc='lower right', ncols=2)

Ns = 2 ** np.arange(3, 10)
edge_gap = np.array([2.0 - free_frequencies(int(N))[-1] for N in Ns])
axes[1].loglog(Ns, edge_gap, 'o', color='#0072B2', label='matrix eigenvalues')
axes[1].loglog(Ns, np.pi**2 / (4.0 * Ns**2), '--', color='#D55E00',
               label=r'$\pi^2/(4N^2)$')
axes[1].set_xlabel(r'$N$')
axes[1].set_ylabel(r'$\omega_{\rm edge}-\omega_{N-1}$')
axes[1].set_title('(b) Highest mode approaches the edge')
axes[1].legend(frameon=False, loc='lower left')

N = 128
omega = free_frequencies(N)
spacing = np.diff(omega)
axes[2].semilogy(np.arange(N - 1) / N, spacing, '-', color='#0072B2', lw=1.3)
axes[2].axhline(np.pi / N, color='0.45', ls='--', lw=1.0,
                label=r'bulk scale $N^{-1}$')
axes[2].axhline(3.0 * np.pi**2 / (4.0 * N**2), color='#D55E00', ls=':', lw=1.2,
                label=r'top spacing $N^{-2}$')
axes[2].set_xlabel(r'normalized mode index $s/N$')
axes[2].set_ylabel(r'$\omega_{s+1}-\omega_s$')
axes[2].set_title('(c) Levels crowd near the upper edge')
axes[2].legend(frameon=False, loc='lower left')

plt.suptitle('band_formation')
coefficient = np.polyfit(np.log(Ns), np.log(edge_gap), 1)[0]
print(f'band-edge convergence exponent = {coefficient:.6f}')
plt.show()
