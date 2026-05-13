# -*- coding: utf-8 -*-
# 3.3 谐振子
# 简谐运动与相图

import numpy as np
import matplotlib.pyplot as plt

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

omega = 2 * np.pi
A = 1.0

def sho(t, state):
    return np.array([state[1], -omega ** 2 * state[0]])

t, state = rk4_system(sho, np.array([A, 0.0]), (0, 5), 0.001)

print("=== 简谐振子模拟 ===")
print(f"角频率 ω = {omega:.4f} rad/s")
print(f"周期 T = {2*np.pi/omega:.4f} s")
print(f"振幅 A = {A}")
print(f"最大速度 = {A*omega:.4f}")
print(f"总能量 = {0.5*omega**2*A**2:.4f}")

KE = 0.5 * state[:, 1] ** 2
PE = 0.5 * omega ** 2 * state[:, 0] ** 2
TE = KE + PE

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

ax = axes[0, 0]
ax.plot(t, state[:, 0], "b-", label="位移 x(t)")
ax.plot(t, state[:, 1] / omega, "r--", label="速度 v(t)/ω")
ax.set_xlabel("时间 t (s)")
ax.set_ylabel("x")
ax.set_title("简谐振子: 位移和速度")
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
ax.plot(state[:, 0], state[:, 1], "b-", linewidth=0.5)
ax.set_xlabel("位移 x")
ax.set_ylabel("速度 v")
ax.set_title("相图 (x vs v)")
ax.grid(True, alpha=0.3)
ax.set_aspect("equal")

ax = axes[1, 0]
ax.plot(t, KE, "r-", label="动能", alpha=0.7)
ax.plot(t, PE, "b-", label="势能", alpha=0.7)
ax.plot(t, TE, "k--", label="总能量", linewidth=2)
ax.set_xlabel("时间 t (s)")
ax.set_ylabel("能量")
ax.set_title("能量守恒")
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1, 1]
for amp in [0.5, 1.0, 1.5]:
    t_a, s_a = rk4_system(sho, np.array([amp, 0.0]), (0, 5), 0.001)
    ax.plot(s_a[:, 0], s_a[:, 1], label=f"A={amp}")
ax.set_xlabel("位移 x")
ax.set_ylabel("速度 v")
ax.set_title("不同振幅的相图")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_aspect("equal")

plt.tight_layout()
plt.show()
