import numpy as np
import matplotlib.pyplot as plt

GM = 4.0 * np.pi ** 2

dt = 0.001
T = 1.0
N = int(T / dt)

x = 1.0
y = 0.0
vx = 0.0
vy = 2.0 * np.pi

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

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(xs, ys, 'b-', linewidth=0.5)
axes[0].plot(0, 0, 'yo', markersize=12)
axes[0].set_xlabel('x (AU)')
axes[0].set_ylabel('y (AU)')
axes[0].set_title('Circular Orbit (Euler-Cromer)')
axes[0].set_aspect('equal')
axes[0].grid(True, alpha=0.3)

axes[1].plot(ts, KE, 'r-', label='Kinetic Energy', linewidth=0.8)
axes[1].plot(ts, PE, 'b-', label='Potential Energy', linewidth=0.8)
axes[1].plot(ts, E, 'k--', label='Total Energy', linewidth=1.2)
axes[1].set_xlabel('Time (year)')
axes[1].set_ylabel('Energy')
axes[1].set_title('Energy Conservation')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('circular_orbit')
plt.show()
print('ch04_circular_orbit.png saved')
