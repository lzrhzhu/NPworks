import numpy as np
import matplotlib.pyplot as plt

g = 9.8
l = 9.8
Omega2 = g / l
q = 0.5
Omega_D = 2.0 / 3.0
T_D = 2 * np.pi / Omega_D
dt = 0.05
steps_per_T = int(round(T_D / dt))
dt = T_D / steps_per_T

n_relay = 200
n_sample = 100

fig = plt.figure(figsize=(14, 10))

ax_ts = fig.add_subplot(2, 1, 1)
colors_ts = ['b', 'g', 'r']
FD_ts_list = [1.35, 1.44, 1.465]

for FD, color in zip(FD_ts_list, colors_ts):
    n_total_steps = int(80.0 / dt)
    theta_arr = np.zeros(n_total_steps + 1)
    t_arr = np.zeros(n_total_steps + 1)
    th = 0.2
    om = 0.0
    theta_arr[0] = th
    t_now = 0.0

    for i in range(n_total_steps):
        k1_th = om
        k1_om = -Omega2 * np.sin(th) - q * om + FD * np.sin(Omega_D * t_now)
        th2 = th + 0.5 * dt * k1_th
        om2 = om + 0.5 * dt * k1_om
        k2_th = om2
        k2_om = -Omega2 * np.sin(th2) - q * om2 + FD * np.sin(Omega_D * (t_now + 0.5 * dt))
        th3 = th + 0.5 * dt * k2_th
        om3 = om + 0.5 * dt * k2_om
        k3_th = om3
        k3_om = -Omega2 * np.sin(th3) - q * om3 + FD * np.sin(Omega_D * (t_now + 0.5 * dt))
        th4 = th + dt * k3_th
        om4 = om + dt * k3_om
        k4_th = om4
        k4_om = -Omega2 * np.sin(th4) - q * om4 + FD * np.sin(Omega_D * (t_now + dt))
        th = th + (dt / 6.0) * (k1_th + 2 * k2_th + 2 * k3_th + k4_th)
        om = om + (dt / 6.0) * (k1_om + 2 * k2_om + 2 * k3_om + k4_om)
        t_now += dt
        theta_arr[i + 1] = th
        t_arr[i + 1] = t_now

    ax_ts.plot(t_arr, theta_arr, color=color, linewidth=0.5, label=r'$F_D={}$'.format(FD))

ax_ts.set_xlabel('t (s)')
ax_ts.set_ylabel(r'$\theta$ (rad)')
ax_ts.set_title(r'$\theta$-t for $F_D=1.35, 1.44, 1.465$')
ax_ts.legend()
ax_ts.grid(True, alpha=0.3)

ax_bif = fig.add_subplot(2, 1, 2)

FD_values = np.linspace(1.35, 1.5, 200)
all_FD = []
all_theta = []

for FD in FD_values:
    th = 0.2
    om = 0.0
    t = 0.0

    for n in range(n_relay):
        for j in range(steps_per_T):
            k1_th = om
            k1_om = -Omega2 * np.sin(th) - q * om + FD * np.sin(Omega_D * t)
            th2 = th + 0.5 * dt * k1_th
            om2 = om + 0.5 * dt * k1_om
            k2_th = om2
            k2_om = -Omega2 * np.sin(th2) - q * om2 + FD * np.sin(Omega_D * (t + 0.5 * dt))
            th3 = th + 0.5 * dt * k2_th
            om3 = om + 0.5 * dt * k2_om
            k3_th = om3
            k3_om = -Omega2 * np.sin(th3) - q * om3 + FD * np.sin(Omega_D * (t + 0.5 * dt))
            th4 = th + dt * k3_th
            om4 = om + dt * k3_om
            k4_th = om4
            k4_om = -Omega2 * np.sin(th4) - q * om4 + FD * np.sin(Omega_D * (t + dt))
            th = th + (dt / 6.0) * (k1_th + 2 * k2_th + 2 * k3_th + k4_th)
            om = om + (dt / 6.0) * (k1_om + 2 * k2_om + 2 * k3_om + k4_om)
            t += dt

    for n in range(n_sample):
        for j in range(steps_per_T):
            k1_th = om
            k1_om = -Omega2 * np.sin(th) - q * om + FD * np.sin(Omega_D * t)
            th2 = th + 0.5 * dt * k1_th
            om2 = om + 0.5 * dt * k1_om
            k2_th = om2
            k2_om = -Omega2 * np.sin(th2) - q * om2 + FD * np.sin(Omega_D * (t + 0.5 * dt))
            th3 = th + 0.5 * dt * k2_th
            om3 = om + 0.5 * dt * k2_om
            k3_th = om3
            k3_om = -Omega2 * np.sin(th3) - q * om3 + FD * np.sin(Omega_D * (t + 0.5 * dt))
            th4 = th + dt * k3_th
            om4 = om + dt * k3_om
            k4_th = om4
            k4_om = -Omega2 * np.sin(th4) - q * om4 + FD * np.sin(Omega_D * (t + dt))
            th = th + (dt / 6.0) * (k1_th + 2 * k2_th + 2 * k3_th + k4_th)
            om = om + (dt / 6.0) * (k1_om + 2 * k2_om + 2 * k3_om + k4_om)
            t += dt
        all_FD.append(FD)
        all_theta.append(th)

ax_bif.plot(all_FD, all_theta, 'k.', markersize=0.3)
ax_bif.set_xlabel(r'$F_D$')
ax_bif.set_ylabel(r'$\theta$ (rad)')
ax_bif.set_title('Bifurcation Diagram')
ax_bif.grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('bifurcation')
plt.show()
print("11_bifurcation.py done")
