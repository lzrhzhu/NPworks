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


def free_chain(N):
    diag = np.full(N, 2.0)
    diag[[0, -1]] = 1.0
    D = (np.diag(diag) + np.diag(-np.ones(N - 1), 1)
         + np.diag(-np.ones(N - 1), -1))
    omega2, modes = np.linalg.eigh(D)
    return np.sqrt(np.clip(omega2, 0.0, None)), modes


N = 32
omega, modes = free_chain(N)
n = np.arange(1, N + 1)
indices = [0, 1, 5, N - 1]

fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.3))
for panel, (ax, s) in enumerate(zip(axes.ravel(), indices)):
    vec = modes[:, s].copy()
    if vec[0] < 0:
        vec *= -1
    vec /= np.max(np.abs(vec))
    ax.plot(n, vec, 'o-', color='#0072B2', ms=3.0, lw=1.2)
    ax.axhline(0.0, color='0.7', lw=0.8)
    ax.set_xlabel('atom index $n$')
    ax.set_ylabel(r'$e_n^{(s)}$')
    ax.set_title(f'({chr(97 + panel)}) mode {s}, $\\omega={omega[s]:.3f}$')
    ax.set_xlim(0.5, N + 0.5)
    ax.set_ylim(-1.15, 1.15)

plt.suptitle('free_chain_modes')
print('orthogonality error:', np.max(np.abs(modes.T @ modes - np.eye(N))))
plt.show()
