import numpy as np
import matplotlib.pyplot as plt

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
plt.title('Bicycle V-t Curve With and Without Air Resistance')
plt.grid(True)
plt.legend()
plt.suptitle('bicycle_with_drag')
plt.show()
