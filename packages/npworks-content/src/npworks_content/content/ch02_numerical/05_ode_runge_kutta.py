# -*- coding: utf-8 -*-
# 2.5 龙格-库塔法
# 使用四阶 Runge-Kutta 方法求解 ODE

import numpy as np
import matplotlib.pyplot as plt

def rk4(f, y0, t_span, dt):
    t0, tf = t_span
    t = np.arange(t0, tf + dt, dt)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(len(t) - 1):
        k1 = dt * f(t[i], y[i])
        k2 = dt * f(t[i] + dt / 2, y[i] + k1 / 2)
        k3 = dt * f(t[i] + dt / 2, y[i] + k2 / 2)
        k4 = dt * f(t[i] + dt, y[i] + k3)
        y[i + 1] = y[i] + (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return t, y

def euler_method(f, y0, t_span, dt):
    t0, tf = t_span
    t = np.arange(t0, tf + dt, dt)
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(len(t) - 1):
        y[i + 1] = y[i] + dt * f(t[i], y[i])
    return t, y

def lorenz_deriv(t, state):
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0
    x, y, z = state
    return np.array([
        sigma * (y - x),
        x * (rho - z) - y,
        x * y - beta * z,
    ])

def rk4_system(f, y0, t_span, dt):
    t0, tf = t_span
    t = np.arange(t0, tf + dt, dt)
    y = np.zeros((len(t), len(y0)))
    y[0] = y0
    for i in range(len(t) - 1):
        k1 = dt * f(t[i], y[i])
        k2 = dt * f(t[i] + dt / 2, y[i] + k1 / 2)
        k3 = dt * f(t[i] + dt / 2, y[i] + k2 / 2)
        k4 = dt * f(t[i] + dt, y[i] + k3)
        y[i + 1] = y[i] + (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return t, y

print("=== RK4 vs 欧拉法: 谐振子 y'' + y = 0 ===")
def harmonic(t, y):
    return np.array([y[1], -y[0]])

dt = 0.5
t_e, y_e = euler_method(lambda t, s: harmonic(t, s)[0], 1.0, (0, 20), dt)
t_rk, y_rk = rk4(lambda t, s: harmonic(t, s)[0], 1.0, (0, 20), dt)

t_rk_sys, state_rk = rk4_system(harmonic, np.array([1.0, 0.0]), (0, 20), 0.01)
t_exact = np.linspace(0, 20, 1000)
y_exact = np.cos(t_exact)

print(f"  t=20时, 精确解={np.cos(20):.6f}")
print(f"  t=20时, RK4解={state_rk[-1, 0]:.6f} (dt=0.01)")

print("\n=== Lorenz 吸引子 (混沌系统) ===")
t_lorenz, state_lorenz = rk4_system(
    lorenz_deriv, np.array([1.0, 1.0, 1.0]), (0, 50), 0.01
)
print(f"  模拟步数: {len(t_lorenz)}")

fig = plt.figure(figsize=(14, 5))

ax1 = fig.add_subplot(131)
ax1.plot(t_exact, y_exact, "k--", label="精确解 cos(t)", linewidth=1)
ax1.plot(t_rk_sys, state_rk[:, 0], "b-", label="RK4", alpha=0.8)
ax1.set_xlabel("t")
ax1.set_ylabel("y")
ax1.set_title("RK4: 谐振子 y''+y=0")
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2 = fig.add_subplot(132)
ax2.plot(state_lorenz[:, 0], state_lorenz[:, 2], "b-", linewidth=0.3, alpha=0.7)
ax2.set_xlabel("x")
ax2.set_ylabel("z")
ax2.set_title("Lorenz 吸引子 (xz投影)")

ax3 = fig.add_subplot(133)
dts = [0.5, 0.2, 0.1, 0.05, 0.01]
rk4_errors = []
euler_errors = []
for d in dts:
    t_r, s_r = rk4_system(harmonic, np.array([1.0, 0.0]), (0, 10), d)
    rk4_errors.append(abs(s_r[-1, 0] - np.cos(10)))
    t_e2, y_e2 = euler_method(lambda t, s: harmonic(t, s)[0], 1.0, (0, 10), d)
    euler_errors.append(abs(y_e2[-1] - np.cos(10)))

ax3.loglog(dts, euler_errors, "ro-", label="欧拉法 O(h)")
ax3.loglog(dts, rk4_errors, "bs-", label="RK4 O(h⁴)")
ax3.set_xlabel("步长 dt")
ax3.set_ylabel("误差")
ax3.set_title("欧拉法 vs RK4 误差对比")
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
