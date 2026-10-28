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

K = 1.0
a = 1.0
k = np.linspace(0.0, np.pi / a, 600)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.0))

omega_mono = 2.0 * np.sqrt(K) * np.sin(k * a / 2.0)
group_velocity = np.sqrt(K) * a * np.cos(k * a / 2.0)
ax1.plot(k * a / np.pi, omega_mono, color='#0072B2', lw=1.8, label=r'$\omega(k)$')
ax1.plot(k * a / np.pi, group_velocity, '--', color='#D55E00', lw=1.4,
         label=r'$v_g=d\omega/dk$')
ax1.set_xlabel(r'$ka/\pi$')
ax1.set_ylabel('frequency or velocity (a.u.)')
ax1.set_title('(a) Monatomic chain')
ax1.set_xlim(0.0, 1.0)
ax1.set_ylim(0.0, 2.08)
ax1.legend(frameon=False, loc='center left')

m1, m2 = 1.0, 2.0
base = K * (1.0 / m1 + 1.0 / m2)
disc = K * np.sqrt((1.0 / m1 + 1.0 / m2)**2
                   - 4.0 * np.sin(k * a / 2.0)**2 / (m1 * m2))
omega_acoustic = np.sqrt(base - disc)
omega_optical = np.sqrt(base + disc)
ax2.plot(k * a / np.pi, omega_acoustic, color='#0072B2', lw=1.8,
         label='acoustic branch')
ax2.plot(k * a / np.pi, omega_optical, '--', color='#D55E00', lw=1.8,
         label='optical branch')
ax2.axhspan(np.sqrt(2.0 * K / m2), np.sqrt(2.0 * K / m1),
            color='0.7', alpha=0.25, label='gap')
ax2.set_xlabel(r'$ka/\pi$')
ax2.set_ylabel(r'$\omega$ (a.u.)')
ax2.set_title(r'(b) Diatomic chain, $m_2=2m_1$')
ax2.set_xlim(0.0, 1.0)
ax2.legend(frameon=False, loc='center left')

plt.suptitle('lattice_dispersion')
print('monatomic band edge:', omega_mono[-1])
print('diatomic gap:', np.sqrt(2.0 * K / m1) - np.sqrt(2.0 * K / m2))
plt.show()
