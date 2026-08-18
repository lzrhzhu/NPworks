import numpy as np
import matplotlib.pyplot as plt


GM = 4.0 * np.pi ** 2
dt = 0.001
T = 2.0
N = int(T / dt)
v_factors = [1.0, 0.8, 0.6]
colors = ['b', 'r', 'g']

all_xy = []
all_Et = []
for vf in v_factors:
    x, y = 1.0, 0.0
    vx, vy = 0.0, vf * 2.0 * np.pi
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

fig, ax = plt.subplots(figsize=(7, 7))
for (xs, ys), vf, c in zip(all_xy, v_factors, colors):
    ax.plot(xs, ys, color=c, linewidth=0.5, label='v0 = {:.1f} * 2pi'.format(vf))
ax.plot(0, 0, 'yo', markersize=12)
ax.set_xlabel('x (AU)'); ax.set_ylabel('y (AU)')
ax.set_title('Elliptical Orbits (Euler-Cromer)'); ax.set_aspect('equal'); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.suptitle('elliptical_orbits')
fig, ax = plt.subplots(figsize=(8, 5))
for E, vf, c in zip(all_Et, v_factors, colors):
    ax.plot(ts, E, color=c, linewidth=0.8, label='v0 = {:.1f} * 2pi'.format(vf))
ax.set_xlabel('Time (year)'); ax.set_ylabel('Total Energy')
ax.set_title('Energy Conservation'); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.suptitle('elliptical_orbits_energy')
print('ch05_elliptical_orbits done')

plt.show()
