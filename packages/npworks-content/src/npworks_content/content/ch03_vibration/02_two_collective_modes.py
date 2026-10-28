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

omega0_sq = 1.0
kappa = 0.18
D = np.array([[omega0_sq + kappa, -kappa],
              [-kappa, omega0_sq + kappa]])
omega2, eigenvectors = np.linalg.eigh(D)
omega = np.sqrt(omega2)

# 局域初态 q(0)=(1,0) 是两个集体模的等权叠加。
q0 = np.array([1.0, 0.0])
Q0 = eigenvectors.T @ q0
t = np.linspace(0.0, 180.0, 4000)
Q = Q0[:, None] * np.cos(omega[:, None] * t)
Qdot = -Q0[:, None] * omega[:, None] * np.sin(omega[:, None] * t)
q = eigenvectors @ Q
mode_energy = 0.5 * (Qdot**2 + omega2[:, None] * Q**2)

fig, axes = plt.subplots(1, 3, figsize=(11.0, 3.7))
n = np.array([1, 2])
for s, (color, label) in enumerate([('#0072B2', 'in-phase'),
                                    ('#D55E00', 'out-of-phase')]):
    vec = eigenvectors[:, s].copy()
    if vec[0] < 0:
        vec *= -1
    axes[0].plot(n, vec / np.max(np.abs(vec)), 'o-', color=color,
                 label=rf'{label}, $\omega={omega[s]:.3f}$')
axes[0].axhline(0.0, color='0.65', lw=0.8)
axes[0].set_xticks([1, 2])
axes[0].set_xlabel('oscillator index')
axes[0].set_ylabel('relative amplitude')
axes[0].set_title('(a) Collective eigenvectors')
axes[0].legend(frameon=False, loc='lower left')

axes[1].plot(t, q[0], color='#0072B2', lw=1.0, label=r'$q_1$')
axes[1].plot(t, q[1], '--', color='#D55E00', lw=1.0, label=r'$q_2$')
axes[1].set_xlabel(r'$t$ (a.u.)')
axes[1].set_ylabel(r'$q_i$ (a.u.)')
axes[1].set_title('(b) Local coordinates show beats')
axes[1].legend(frameon=False, loc='upper right')

for s, (color, label) in enumerate([('#0072B2', r'$E_+$'),
                                    ('#D55E00', r'$E_-$')]):
    axes[2].plot(t, mode_energy[s], color=color, lw=1.2, label=label)
axes[2].set_xlabel(r'$t$ (a.u.)')
axes[2].set_ylabel('mode energy (a.u.)')
axes[2].set_title('(c) Mode energies are constant')
axes[2].set_ylim(0.0, 0.35)
axes[2].legend(frameon=False, loc='upper right')

plt.suptitle('two_collective_modes')
print('frequencies:', omega)
print('maximum modal-energy variation:', np.ptp(mode_energy, axis=1))
plt.show()
