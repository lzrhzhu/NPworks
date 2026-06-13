import numpy as np
import matplotlib.pyplot as plt

g = 9.8
l = 9.8
Omega2 = g / l
q = 0.5
Omega_D = 2.0 / 3.0
dt = 0.01
t_end = 120.0
t = np.arange(0, t_end, dt)
N = len(t)

delta_theta0 = 0.001

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for idx, FD in enumerate([0.5, 1.2]):
    theta1 = np.zeros(N)
    omega1 = np.zeros(N)
    theta2 = np.zeros(N)
    omega2 = np.zeros(N)

    theta1[0] = 0.2
    omega1[0] = 0.0
    theta2[0] = 0.2 + delta_theta0
    omega2[0] = 0.0

    for i in range(N - 1):
        omega1[i + 1] = omega1[i] + (-Omega2 * np.sin(theta1[i]) - q * omega1[i] + FD * np.sin(Omega_D * t[i])) * dt
        theta1[i + 1] = theta1[i] + omega1[i + 1] * dt

        omega2[i + 1] = omega2[i] + (-Omega2 * np.sin(theta2[i]) - q * omega2[i] + FD * np.sin(Omega_D * t[i])) * dt
        theta2[i + 1] = theta2[i] + omega2[i + 1] * dt

    delta = np.abs(theta2 - theta1)
    delta[delta < 1e-15] = 1e-15

    axes[idx].semilogy(t, delta, 'b-', linewidth=0.5)
    axes[idx].set_xlabel('t (s)')
    axes[idx].set_ylabel(r'$|\Delta\theta|$ (rad)')
    axes[idx].set_title(r'$F_D={}$: Sensitivity to Initial Conditions'.format(FD))
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('chaos_sensitivity')
plt.show()
print("08_chaos_sensitivity.py done")
