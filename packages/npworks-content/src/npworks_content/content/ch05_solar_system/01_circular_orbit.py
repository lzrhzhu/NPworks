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
T = 2.0 * np.pi             # dimensionless end time τ; 1 year
N = int(T / dt)

x = 1.0
y = 0.0
vx = 0.0
vy = 1.0

xs = np.zeros(N + 1)
ys = np.zeros(N + 1)
KE = np.zeros(N + 1)
PE = np.zeros(N + 1)
ts = np.zeros(N + 1)

xs[0] = x
ys[0] = y
r = np.sqrt(x ** 2 + y ** 2)
KE[0] = 0.5 * (vx ** 2 + vy ** 2)
PE[0] = -GM / r
ts[0] = 0.0

for i in range(N):
    r = np.sqrt(x ** 2 + y ** 2)
    ax = -GM * x / r ** 3
    ay = -GM * y / r ** 3
    vx = vx + ax * dt
    vy = vy + ay * dt
    x = x + vx * dt
    y = y + vy * dt
    xs[i + 1] = x
    ys[i + 1] = y
    r = np.sqrt(x ** 2 + y ** 2)
    KE[i + 1] = 0.5 * (vx ** 2 + vy ** 2)
    PE[i + 1] = -GM / r
    ts[i + 1] = (i + 1) * dt

E = KE + PE

fig, ax = plt.subplots(figsize=(6.4, 6.0))
ax.plot(xs, ys, color='#0072B2', linestyle='-', linewidth=1.5)
ax.plot(0, 0, 'o', color='#E69F00', markersize=9)
ax.set_xlabel('x (AU)'); ax.set_ylabel('y (AU)')
ax.set_title('Circular Orbit (Euler-Cromer)'); ax.set_aspect('equal')
plt.tight_layout(); plt.suptitle('circular_orbit')
fig, ax = plt.subplots()
ax.plot(ts, KE, color='#D55E00', linestyle='-', label='Kinetic energy')
ax.plot(ts, PE, color='#0072B2', linestyle='--', label='Potential energy')
ax.plot(ts, E, color='black', linestyle='-.', label='Total energy')
ax.set_xlabel(r'$\tau$ ( $T_0$ )'); ax.set_ylabel('Dimensionless energy')
ax.set_title('Energy Conservation'); ax.legend(frameon=False)
plt.tight_layout(); plt.suptitle('circular_orbit_energy')
print('ch05_circular_orbit done')

plt.show()
