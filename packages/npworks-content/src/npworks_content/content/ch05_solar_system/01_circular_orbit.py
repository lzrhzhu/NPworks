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

import os
_d = os.path.dirname(os.path.abspath(__file__))
for _ in range(10):
    if os.path.isdir(os.path.join(_d, "markdown")):
        IMG_DIR = os.path.join(_d, "markdown", "images", "ch05"); break
    _d = os.path.dirname(_d)
else:
    IMG_DIR = os.path.join(os.path.expanduser("~"), "npworks_figures", "ch05"); os.makedirs(IMG_DIR, exist_ok=True)

fig, ax = plt.subplots(figsize=(7, 7))
ax.plot(xs, ys, 'b-', linewidth=0.5)
ax.plot(0, 0, 'yo', markersize=12)
ax.set_xlabel('x (AU)'); ax.set_ylabel('y (AU)')
ax.set_title('Circular Orbit (Euler-Cromer)'); ax.set_aspect('equal'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "ch05_circular_orbit.png"), dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(ts, KE, 'r-', label='Kinetic Energy', linewidth=0.8)
ax.plot(ts, PE, 'b-', label='Potential Energy', linewidth=0.8)
ax.plot(ts, E, 'k--', label='Total Energy', linewidth=1.2)
ax.set_xlabel('Time (year)'); ax.set_ylabel('Energy')
ax.set_title('Energy Conservation'); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.savefig(os.path.join(IMG_DIR, "ch05_circular_orbit_energy.png"), dpi=130); plt.close(fig)
print('ch05_circular_orbit done')
