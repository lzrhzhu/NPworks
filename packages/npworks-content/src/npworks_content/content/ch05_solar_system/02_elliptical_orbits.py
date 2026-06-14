import numpy as np
import matplotlib.pyplot as plt

GM = 4.0 * np.pi ** 2

dt = 0.001
T = 2.0
N = int(T / dt)
v_factors = [1.0, 0.8, 0.6]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

colors = ['b', 'r', 'g']
for idx, vf in enumerate(v_factors):
    x = 1.0
    y = 0.0
    vx = 0.0
    vy = vf * 2.0 * np.pi

    xs = np.zeros(N + 1)
    ys = np.zeros(N + 1)
    E = np.zeros(N + 1)
    ts = np.zeros(N + 1)

    xs[0] = x
    ys[0] = y
    r = np.sqrt(x ** 2 + y ** 2)
    E[0] = 0.5 * (vx ** 2 + vy ** 2) - GM / r

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
        E[i + 1] = 0.5 * (vx ** 2 + vy ** 2) - GM / r
        ts[i + 1] = (i + 1) * dt

    label = 'v0 = {:.1f} * 2pi'.format(vf)
    axes[0].plot(xs, ys, color=colors[idx], linewidth=0.5, label=label)
    axes[1].plot(ts, E, color=colors[idx], linewidth=0.8, label=label)

axes[0].plot(0, 0, 'yo', markersize=12)
axes[0].set_xlabel('x (AU)')
axes[0].set_ylabel('y (AU)')
axes[0].set_title('Elliptical Orbits (Euler-Cromer)')
axes[0].set_aspect('equal')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].set_xlabel('Time (year)')
axes[1].set_ylabel('Total Energy')
axes[1].set_title('Energy Conservation')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('elliptical_orbits')
plt.show()
print('ch05_elliptical_orbits.png saved')
