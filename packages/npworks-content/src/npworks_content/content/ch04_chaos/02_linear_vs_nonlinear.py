import numpy as np
import matplotlib.pyplot as plt

g = 9.81
l = 1.0
Omega2 = g / l
dt = 0.001
t_end = 10.0
t = np.arange(0, t_end, dt)
N = len(t)

theta0 = 0.2
omega0 = 0.0

theta_linear = np.zeros(N)
omega_linear = np.zeros(N)
theta_linear[0] = theta0
omega_linear[0] = omega0

for i in range(N - 1):
    omega_linear[i + 1] = omega_linear[i] - Omega2 * theta_linear[i] * dt
    theta_linear[i + 1] = theta_linear[i] + omega_linear[i + 1] * dt

theta_nonlinear = np.zeros(N)
omega_nonlinear = np.zeros(N)
theta_nonlinear[0] = theta0
omega_nonlinear[0] = omega0

for i in range(N - 1):
    omega_nonlinear[i + 1] = omega_nonlinear[i] - Omega2 * np.sin(theta_nonlinear[i]) * dt
    theta_nonlinear[i + 1] = theta_nonlinear[i] + omega_nonlinear[i + 1] * dt

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(t, theta_linear, 'b-', linewidth=1.0, label=r'Linear ($\sin\theta \approx \theta$)')
ax.plot(t, theta_nonlinear, 'r--', linewidth=1.0, label=r'Nonlinear ($\sin\theta$)')
ax.set_xlabel('t (s)')
ax.set_ylabel(r'$\theta$ (rad)')
ax.set_title('Linear vs Nonlinear Pendulum ($\\theta_0 = 0.2$ rad)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('linear_vs_nonlinear')
plt.show()
print("02_linear_vs_nonlinear.py done")
