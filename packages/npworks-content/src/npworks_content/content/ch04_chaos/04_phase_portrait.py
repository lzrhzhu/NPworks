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
    n_total = int(t_end / dt)
    theta_arr = np.zeros(n_total)
    omega_arr = np.zeros(n_total)
    state = np.array([0.2, 0.0])
    theta_arr[0] = state[0]; omega_arr[0] = state[1]
    for i in range(n_total - 1):
        state = rk4_step(state, i * dt, dt, FD)
        theta_arr[i + 1] = state[0]; omega_arr[i + 1] = state[1]
    # 摆角以 2π 为周期，绘制前折回 [-π, π]
    theta_plot = (theta_arr[n_trans:] + np.pi) % (2 * np.pi) - np.pi
    omega_plot = omega_arr[n_trans:]

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(theta_plot, omega_plot, ',', markersize=0.3, alpha=0.5)
    ax.set_xlabel(r'$\theta$ (rad)'); ax.set_ylabel(r'$\omega$ (rad/s)')
    ax.set_title(r'$F_D={}$: {}'.format(FD, 'Limit Cycle' if FD == 0.5 else 'Strange Attractor'))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.suptitle('phase_portrait' if FD == 0.5 else 'phase_portrait_fd12')
print("04_phase_portrait.py done")

plt.show()
