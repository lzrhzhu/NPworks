import numpy as np
import matplotlib.pyplot as plt

g = 9.81
l = 1.0
Omega2 = g / l
dt = 0.01
t = np.arange(0, 30, dt)

def pendulum_rhs(state, t):
    theta, omega = state
    return np.array([omega, -Omega2 * theta])

def rk4_step(state, t, dt, f):
    k1 = f(state, t)
    k2 = f(state + 0.5 * dt * k1, t + 0.5 * dt)
    k3 = f(state + 0.5 * dt * k2, t + 0.5 * dt)
    k4 = f(state + dt * k3, t + dt)
    return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

N = len(t)
theta_rk4 = np.zeros(N)
omega_rk4 = np.zeros(N)
state = np.array([0.2, 0.0])

for i in range(N):
    theta_rk4[i] = state[0]
    omega_rk4[i] = state[1]
    state = rk4_step(state, t[i], dt, pendulum_rhs)

E_rk4 = 0.5 * l**2 * omega_rk4**2 + 0.5 * g * l * theta_rk4**2
E0 = E_rk4[0]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(t, (E_rk4 - E0) / E0, 'b-', linewidth=0.5)
ax.set_xlabel('t (s)')
ax.set_ylabel(r'$\Delta E / E_0$')
ax.set_title('RK4: Relative Energy Error for Simple Pendulum')
ax.grid(True, alpha=0.3)
ax.ticklabel_format(style='sci', axis='y', scilimits=(-2, 2))

plt.tight_layout()
plt.suptitle('rk4_pendulum')
plt.show()
print("04_rk4_pendulum.py done")
