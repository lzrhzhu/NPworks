# -*- coding: utf-8 -*-
# 3.4 阻尼振动
# 阻尼振动模拟

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

omega0 = 2 * np.pi
A = 1.0

def damped_oscillator(gamma, omega0):
    def f(t, state):
        return np.array([state[1], -2 * gamma * state[1] - omega0 ** 2 * state[0]])
    return f

print("=== 阻尼振动模拟 ===")
print(f"固有频率 ω₀ = {omega0:.4f} rad/s")
print(f"振幅 A = {A}\n")

damping_cases = [
    {"gamma": 0.1, "label": "欠阻尼 (γ=0.1)", "color": "blue"},
    {"gamma": 0.5, "label": "欠阻尼 (γ=0.5)", "color": "green"},
    {"gamma": omega0 / 2, "label": "临界阻尼 (γ=π)", "color": "red"},
    {"gamma": 5.0, "label": "过阻尼 (γ=5.0)", "color": "purple"},
]

t_end = 8
dt = 0.001

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

for case in damping_cases:
    gamma = case["gamma"]
    f = damped_oscillator(gamma, omega0)
    t, state = rk4_system(f, np.array([A, 0.0]), (0, t_end), dt)

    omega_d = np.sqrt(max(omega0 ** 2 - gamma ** 2, 0))
    if gamma < omega0:
        regime = "欠阻尼"
        envelope = A * np.exp(-gamma * t)
    elif gamma == omega0 / 2:
        regime = "临界阻尼"
        envelope = None
    else:
        regime = "过阻尼"
        envelope = None

    print(f"{case['label']}: {regime}, ωd={omega_d:.4f}")

    ax1.plot(t, state[:, 0], color=case["color"], label=case["label"], linewidth=1)
    if envelope is not None:
        ax1.plot(t, envelope, "--", color=case["color"], alpha=0.4)
        ax1.plot(t, -envelope, "--", color=case["color"], alpha=0.4)

    ax2.plot(state[:, 0], state[:, 1], color=case["color"], label=case["label"], linewidth=0.5)

ax1.set_xlabel("时间 t (s)")
ax1.set_ylabel("位移 x(t)")
ax1.set_title("阻尼振动: 位移随时间变化")
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.set_xlabel("位移 x")
ax2.set_ylabel("速度 v")
ax2.set_title("阻尼振动相图")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
