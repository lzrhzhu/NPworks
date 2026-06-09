import numpy as np
import matplotlib.pyplot as plt

omega0 = 2 * np.pi
dt = 0.001
t_end = 5.0
t = np.arange(0, t_end, dt)
N = len(t)

gamma_list = [0.1, 0.5, np.pi, 5.0]
labels = [r'$\gamma=0.1$ (underdamped)', r'$\gamma=0.5$ (underdamped)',
          r'$\gamma=\pi$ (critical)', r'$\gamma=5.0$ (overdamped)']
colors = ['b', 'g', 'r', 'm']

fig, ax = plt.subplots(figsize=(10, 5))

for gamma, label, color in zip(gamma_list, labels, colors):
    theta = np.zeros(N)
    theta[0] = 0.2
    omega = np.zeros(N)
    omega[0] = 0.0

    for i in range(N - 1):
        omega[i + 1] = omega[i] + (-omega0**2 * theta[i] - gamma * omega[i]) * dt
        theta[i + 1] = theta[i] + omega[i + 1] * dt

    ax.plot(t, theta, color=color, linewidth=0.8, label=label)

ax.set_xlabel('t (s)')
ax.set_ylabel(r'$\theta$ (rad)')
ax.set_title('Damped Pendulum: Three Damping Regimes')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('damped_pendulum')
plt.show()
print("05_damped_pendulum.py done")
