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

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(t, theta, 'b-', linewidth=0.8)
ax.set_xlabel('t (s)'); ax.set_ylabel(r'$\theta$ (rad)')
ax.set_title('Explicit Euler: Amplitude Growing (Simple Pendulum)'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.suptitle('euler_explicit')
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(t, omega, 'r-', linewidth=0.8)
ax.set_xlabel('t (s)'); ax.set_ylabel(r'$\omega$ (rad/s)'); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.suptitle('euler_explicit_omega')
print("01_euler_explicit.py done")

plt.show()
