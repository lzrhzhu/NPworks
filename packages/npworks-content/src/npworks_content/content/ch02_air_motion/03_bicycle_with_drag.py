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

P = 400
dt = 0.1
N = 1001
m = 70
C_D = 1.0
A = 0.33
rho = 1.29

t = np.zeros(N)
vd = np.zeros(N)
vf = np.zeros(N)

v_0 = 4
vd[0] = v_0
vf[0] = v_0
t[0] = 0

for i in range(N - 1):
    if vd[i] > 0:
        vd[i + 1] = vd[i] + (P / (m * vd[i]) - 0.5 * C_D * rho * A * vd[i]**2 / m) * dt
    if vf[i] > 0:
        vf[i + 1] = vf[i] + (P / (m * vf[i])) * dt
    t[i + 1] = t[i] + dt

plt.figure(figsize=(10, 6))
plt.plot(t, vf, label='No Air Resistance', linestyle='--')
plt.plot(t, vd, label='With Air Resistance', color='red')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.legend(frameon=False)
plt.suptitle('bicycle_with_drag')
plt.show()
