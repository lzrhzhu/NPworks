import numpy as np
import matplotlib.pyplot as plt

g = 9.8
l = 9.8
Omega2 = g / l
q = 0.5
Omega_D = 2.0 / 3.0
dt = 0.01
t_end = 120.0
t = np.arange(0, t_end, dt)
N = len(t)

delta_theta0 = 0.001

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

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for idx, FD in enumerate([0.5, 1.2]):
    state1 = np.array([0.2, 0.0])
    state2 = np.array([0.2 + delta_theta0, 0.0])
    theta1 = np.zeros(N)
    theta2 = np.zeros(N)
    theta1[0] = state1[0]
    theta2[0] = state2[0]

    for i in range(N - 1):
        state1 = rk4_step(state1, t[i], dt, FD)
        state2 = rk4_step(state2, t[i], dt, FD)
        theta1[i + 1] = state1[0]
        theta2[i + 1] = state2[0]

    delta = np.abs(theta2 - theta1)
    delta[delta < 1e-15] = 1e-15

    axes[idx].semilogy(t, delta, 'b-', linewidth=0.5)
    axes[idx].set_xlabel('t (s)')
    axes[idx].set_ylabel(r'$|\Delta\theta|$ (rad)')
    axes[idx].set_title(r'$F_D={}$: Sensitivity to Initial Conditions'.format(FD))
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('chaos_sensitivity')
plt.show()
print("03_chaos_sensitivity.py done")
