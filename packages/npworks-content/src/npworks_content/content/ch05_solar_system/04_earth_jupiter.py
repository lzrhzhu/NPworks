import numpy as np
import matplotlib.pyplot as plt

GM = 4.0 * np.pi ** 2
mass_ratio = 0.95e-3

dt = 0.001
T = 20.0
N = int(T / dt)

xE, yE = 1.0, 0.0
vxE, vyE = 0.0, 2.0 * np.pi

xJ, yJ = 5.2, 0.0
vxJ, vyJ = 0.0, 2.0 * np.pi / np.sqrt(5.2)

xEs = np.zeros(N + 1)
yEs = np.zeros(N + 1)
xJs = np.zeros(N + 1)
yJs = np.zeros(N + 1)

xEs[0] = xE
yEs[0] = yE
xJs[0] = xJ
yJs[0] = yJ


def compute_accelerations(xE, yE, xJ, yJ):
    rE = np.sqrt(xE**2 + yE**2)
    rJ = np.sqrt(xJ**2 + yJ**2)
    dx = xE - xJ
    dy = yE - yJ
    rEJ = np.sqrt(dx**2 + dy**2)
    axE = -GM * xE / rE**3 - GM * mass_ratio * dx / rEJ**3
    ayE = -GM * yE / rE**3 - GM * mass_ratio * dy / rEJ**3
    axJ = -GM * xJ / rJ**3
    ayJ = -GM * yJ / rJ**3
    return axE, ayE, axJ, ayJ


axE, ayE, axJ, ayJ = compute_accelerations(xE, yE, xJ, yJ)

for i in range(N):
    xE = xE + vxE * dt + 0.5 * axE * dt**2
    yE = yE + vyE * dt + 0.5 * ayE * dt**2
    xJ = xJ + vxJ * dt + 0.5 * axJ * dt**2
    yJ = yJ + vyJ * dt + 0.5 * ayJ * dt**2

    axE_new, ayE_new, axJ_new, ayJ_new = compute_accelerations(xE, yE, xJ, yJ)

    vxE = vxE + 0.5 * (axE + axE_new) * dt
    vyE = vyE + 0.5 * (ayE + ayE_new) * dt
    vxJ = vxJ + 0.5 * (axJ + axJ_new) * dt
    vyJ = vyJ + 0.5 * (ayJ + ayJ_new) * dt

    axE, ayE, axJ, ayJ = axE_new, ayE_new, axJ_new, ayJ_new

    xEs[i + 1] = xE
    yEs[i + 1] = yE
    xJs[i + 1] = xJ
    yJs[i + 1] = yJ

fig, ax = plt.subplots(figsize=(8, 8))
ax.plot(xEs, yEs, 'b-', linewidth=0.3, label='Earth')
ax.plot(xJs, yJs, 'r-', linewidth=0.3, label='Jupiter')
ax.plot(0, 0, 'yo', markersize=15, label='Sun')
ax.plot(xEs[0], yEs[0], 'b^', markersize=6)
ax.plot(xJs[0], yJs[0], 'r^', markersize=6)
ax.set_xlabel('x (AU)')
ax.set_ylabel('y (AU)')
ax.set_title('Earth-Jupiter Orbits ({}, velocity Verlet)'.format(int(T)))
ax.set_aspect('equal')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()

plt.suptitle('earth_jupiter')
plt.show()
print('ch05_earth_jupiter.png saved')
