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

def pendulum_rhs(state, t_curr, FD):
    theta, omega = state
    dtheta = omega
    domega = -Omega2 * np.sin(theta) - q * omega + FD * np.sin(Omega_D * t_curr)
    return np.array([dtheta, domega])

def rk4_step(state, t_curr, dt_step, FD):
    k1 = pendulum_rhs(state, t_curr, FD)
    k2 = pendulum_rhs(state + 0.5 * dt_step * k1, t_curr + 0.5 * dt_step, FD)
    k3 = pendulum_rhs(state + 0.5 * dt_step * k2, t_curr + 0.5 * dt_step, FD)
    k4 = pendulum_rhs(state + dt_step * k3, t_curr + dt_step, FD)
    return state + (dt_step / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

for idx, FD in enumerate([0.5, 1.2]):
    state = np.array([0.2, 0.0])
    theta_arr = np.zeros(N); omega_arr = np.zeros(N)
    theta_arr[0] = state[0]; omega_arr[0] = state[1]
    for i in range(N - 1):
        state = rk4_step(state, t[i], dt, FD)
        theta_arr[i + 1] = state[0]; omega_arr[i + 1] = state[1]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(t, theta_arr, 'b-', linewidth=0.3)
    ax.set_ylabel(r'$\theta$ (rad)')
    ax.set_title(r'$\theta$-t for $F_D={}$'.format(FD))
    ax.set_xlabel('t (s)')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.suptitle('driven_pendulum' if FD == 0.5 else 'driven_pendulum_fd12')

print("01_driven_pendulum.py done")

plt.show()
