import numpy as np
import matplotlib.pyplot as plt

g = 9.81
l = 1.0
Omega2 = g / l
dt = 0.01
t_end = 10.0
num_steps = int(t_end / dt)

t = np.zeros(num_steps + 1)
theta = np.zeros(num_steps + 1)
omega = np.zeros(num_steps + 1)

theta[0] = 0.2
omega[0] = 0.0

for i in range(num_steps):
    t[i + 1] = t[i] + dt
    omega[i + 1] = omega[i] - Omega2 * theta[i] * dt
    theta[i + 1] = theta[i] + omega[i] * dt

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
ax1.plot(t, theta, 'b-', linewidth=0.8)
ax1.set_ylabel(r'$\theta$ (rad)')
ax1.set_title('Explicit Euler: Amplitude Growing (Simple Pendulum)')
ax1.grid(True, alpha=0.3)

ax2.plot(t, omega, 'r-', linewidth=0.8)
ax2.set_xlabel('t (s)')
ax2.set_ylabel(r'$\omega$ (rad/s)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('euler_explicit')
plt.show()
print("01_euler_explicit.py done")
