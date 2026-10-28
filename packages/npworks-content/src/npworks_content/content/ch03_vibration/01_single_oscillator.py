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

omega0 = 1.0
dt = 0.08
t_end = 80.0
t = np.arange(0.0, t_end + dt, dt)


def integrate(method):
    q = np.zeros_like(t)
    v = np.zeros_like(t)
    q[0] = 1.0
    for i in range(len(t) - 1):
        if method == 'explicit':
            q[i + 1] = q[i] + dt * v[i]
            v[i + 1] = v[i] - dt * omega0**2 * q[i]
        elif method == 'implicit':
            denominator = 1.0 + (omega0 * dt)**2
            q[i + 1] = (q[i] + dt * v[i]) / denominator
            v[i + 1] = (v[i] - dt * omega0**2 * q[i]) / denominator
        else:
            v[i + 1] = v[i] - dt * omega0**2 * q[i]
            q[i + 1] = q[i] + dt * v[i + 1]
    energy = 0.5 * (v**2 + omega0**2 * q**2)
    return q, v, energy


q_e, v_e, E_e = integrate('explicit')
q_i, v_i, E_i = integrate('implicit')
q_c, v_c, E_c = integrate('euler-cromer')

fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.0))
phase_data = [
    (q_e, v_e, '#D55E00', '(a) Explicit Euler: outward spiral'),
    (q_i, v_i, '#009E73', '(b) Implicit Euler: inward spiral'),
    (q_c, v_c, '#0072B2', '(c) Euler–Cromer: bounded orbit'),
]
for ax, (q, v, color, title) in zip(axes.ravel()[:3], phase_data):
    ax.plot(q, v, color=color, lw=1.1)
    ax.set_xlabel(r'$q$ (a.u.)')
    ax.set_ylabel(r'$\dot q$ (a.u.)')
    ax.set_title(title)
    ax.set_aspect('equal', adjustable='box')

ax = axes[1, 1]
ax.semilogy(t, E_e / E_e[0], color='#D55E00', lw=1.2,
            label='explicit Euler')
ax.semilogy(t, E_i / E_i[0], '--', color='#009E73', lw=1.2,
            label='implicit Euler')
ax.semilogy(t, E_c / E_c[0], '-.', color='#0072B2', lw=1.2,
            label='Euler–Cromer')
ax.set_xlabel(r'$t$ (a.u.)')
ax.set_ylabel(r'$E/E_0$')
ax.set_title('(d) Energy evolution')
ax.legend(frameon=False, loc='upper right')

plt.suptitle('single_oscillator')
print(f'explicit final E/E0 = {E_e[-1] / E_e[0]:.6g}')
print(f'implicit final E/E0 = {E_i[-1] / E_i[0]:.6g}')
print(f'Euler-Cromer max |E/E0-1| = {np.max(np.abs(E_c / E_c[0] - 1)):.6g}')
plt.show()
