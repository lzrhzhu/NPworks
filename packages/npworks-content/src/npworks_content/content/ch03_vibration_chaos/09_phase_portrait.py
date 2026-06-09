import numpy as np
import matplotlib.pyplot as plt

g = 9.8
l = 9.8
Omega2 = g / l
q = 0.5
Omega_D = 2.0 / 3.0
dt = 0.01
t_end = 500.0
n_trans = int(200.0 / dt)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for idx, FD in enumerate([0.5, 1.2]):
    n_total = int(t_end / dt)
    theta_arr = np.zeros(n_total)
    omega_arr = np.zeros(n_total)
    theta_arr[0] = 0.2
    omega_arr[0] = 0.0

    for i in range(n_total - 1):
        omega_arr[i + 1] = omega_arr[i] + (-Omega2 * np.sin(theta_arr[i]) - q * omega_arr[i] + FD * np.sin(Omega_D * (i * dt))) * dt
        theta_arr[i + 1] = theta_arr[i] + omega_arr[i + 1] * dt

    theta_plot = theta_arr[n_trans:]
    omega_plot = omega_arr[n_trans:]

    axes[idx].plot(theta_plot, omega_plot, ',', markersize=0.3, alpha=0.5)
    axes[idx].set_xlabel(r'$\theta$ (rad)')
    axes[idx].set_ylabel(r'$\omega$ (rad/s)')
    if FD == 0.5:
        axes[idx].set_title(r'$F_D=0.5$: Limit Cycle (Phase Portrait)')
    else:
        axes[idx].set_title(r'$F_D=1.2$: Strange Attractor (Phase Portrait)')
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('phase_portrait')
plt.show()
print("09_phase_portrait.py done")
