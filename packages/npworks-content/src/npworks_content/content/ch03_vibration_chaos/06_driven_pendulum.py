import numpy as np
import matplotlib.pyplot as plt

g = 9.8
l = 9.8
Omega2 = g / l
q = 0.5
Omega_D = 2.0 / 3.0
dt = 0.01
t_end = 200.0
t = np.arange(0, t_end, dt)
N = len(t)

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

for idx, FD in enumerate([0.5, 1.2]):
    theta = np.zeros(N)
    omega_arr = np.zeros(N)
    theta[0] = 0.2
    omega_arr[0] = 0.0

    for i in range(N - 1):
        omega_arr[i + 1] = omega_arr[i] + (-Omega2 * np.sin(theta[i]) - q * omega_arr[i] + FD * np.sin(Omega_D * t[i])) * dt
        theta[i + 1] = theta[i] + omega_arr[i + 1] * dt

    axes[idx, 0].plot(t, theta, 'b-', linewidth=0.3)
    axes[idx, 0].set_ylabel(r'$\theta$ (rad)')
    axes[idx, 0].set_title(r'$\theta$-t for $F_D={}$'.format(FD))
    axes[idx, 0].grid(True, alpha=0.3)

    axes[idx, 1].plot(t, omega_arr, 'r-', linewidth=0.3)
    axes[idx, 1].set_ylabel(r'$\omega$ (rad/s)')
    axes[idx, 1].set_title(r'$\omega$-t for $F_D={}$'.format(FD))
    axes[idx, 1].grid(True, alpha=0.3)

axes[1, 0].set_xlabel('t (s)')
axes[1, 1].set_xlabel('t (s)')

plt.tight_layout()
plt.suptitle('driven_pendulum')
plt.show()
print("06_driven_pendulum.py done")
