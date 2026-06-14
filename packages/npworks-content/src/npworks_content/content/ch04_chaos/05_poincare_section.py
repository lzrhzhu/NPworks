import numpy as np
import matplotlib.pyplot as plt

g = 9.8
l = 9.8
Omega2 = g / l
q = 0.5
Omega_D = 2.0 / 3.0
dt = 0.01
T_D = 2 * np.pi / Omega_D
steps_per_T = int(round(T_D / dt))
dt = T_D / steps_per_T

n_relay = 500
n_sample = 500

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for idx, FD in enumerate([0.5, 1.2]):
    state = np.array([0.2, 0.0])
    theta_poincare = []
    omega_poincare = []
    t = 0.0

    for n in range(n_relay + n_sample):
        for j in range(steps_per_T):
            k1 = np.array([state[1],
                           -Omega2 * np.sin(state[0]) - q * state[1]
                           + FD * np.sin(Omega_D * t)])
            s2 = state + 0.5 * dt * k1
            k2 = np.array([s2[1],
                           -Omega2 * np.sin(s2[0]) - q * s2[1]
                           + FD * np.sin(Omega_D * (t + 0.5 * dt))])
            s3 = state + 0.5 * dt * k2
            k3 = np.array([s3[1],
                           -Omega2 * np.sin(s3[0]) - q * s3[1]
                           + FD * np.sin(Omega_D * (t + 0.5 * dt))])
            s4 = state + dt * k3
            k4 = np.array([s4[1],
                           -Omega2 * np.sin(s4[0]) - q * s4[1]
                           + FD * np.sin(Omega_D * (t + dt))])
            state = state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            t += dt

        if n >= n_relay:
            theta_poincare.append(state[0])
            omega_poincare.append(state[1])

    axes[idx].plot(theta_poincare, omega_poincare, '.', markersize=1)
    axes[idx].set_xlabel(r'$\theta$ (rad)')
    axes[idx].set_ylabel(r'$\omega$ (rad/s)')
    axes[idx].set_title('Poincare Section ($F_D={}$)'.format(FD))
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('poincare_section')
plt.show()
print("05_poincare_section.py done")
