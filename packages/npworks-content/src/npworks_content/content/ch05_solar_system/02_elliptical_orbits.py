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

GM = 1.0
dt = 0.002 * np.pi          # dimensionless step Δτ; 0.001 year
T = 4.0 * np.pi             # dimensionless end time τ; 2 years
N = int(T / dt)
v_factors = [1.0, 0.8, 0.6]
colors = ['#0072B2', '#D55E00', '#009E73']
linestyles = ['-', '--', '-.']

all_xy = []
all_Et = []
for vf in v_factors:
    x, y = 1.0, 0.0
    vx, vy = 0.0, vf
    xs = np.zeros(N + 1); ys = np.zeros(N + 1); E = np.zeros(N + 1)
    xs[0] = x; ys[0] = y
    r = np.sqrt(x ** 2 + y ** 2)
    E[0] = 0.5 * (vx ** 2 + vy ** 2) - GM / r
    for i in range(N):
        r = np.sqrt(x ** 2 + y ** 2)
        ax = -GM * x / r ** 3; ay = -GM * y / r ** 3
        vx = vx + ax * dt; vy = vy + ay * dt
        x = x + vx * dt; y = y + vy * dt
        xs[i + 1] = x; ys[i + 1] = y
        r = np.sqrt(x ** 2 + y ** 2)
        E[i + 1] = 0.5 * (vx ** 2 + vy ** 2) - GM / r
    all_xy.append((xs, ys)); all_Et.append(E)
ts = np.arange(N + 1) * dt

fig, ax = plt.subplots(figsize=(6.4, 6.0))
for (xs, ys), vf, c, ls in zip(all_xy, v_factors, colors, linestyles):
    ax.plot(xs, ys, color=c, linestyle=ls, label='v0 = {:.1f}'.format(vf))
ax.plot(0, 0, 'o', color='#E69F00', markersize=9)
ax.set_xlabel('x (AU)'); ax.set_ylabel('y (AU)')
ax.set_title('Elliptical Orbits (Euler-Cromer)'); ax.set_aspect('equal'); ax.legend(frameon=False)
plt.tight_layout(); plt.suptitle('elliptical_orbits')
fig, ax = plt.subplots()
for E, vf, c, ls in zip(all_Et, v_factors, colors, linestyles):
    ax.plot(ts, E, color=c, linestyle=ls, label='v0 = {:.1f}'.format(vf))
ax.set_xlabel(r'$\tau$ ( $T_0$ )'); ax.set_ylabel('Dimensionless total energy')
ax.set_title('Energy Conservation'); ax.legend(frameon=False)
plt.tight_layout(); plt.suptitle('elliptical_orbits_energy')
print('ch05_elliptical_orbits done')

plt.show()
