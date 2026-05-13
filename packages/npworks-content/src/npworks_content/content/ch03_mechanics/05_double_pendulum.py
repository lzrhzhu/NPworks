# -*- coding: utf-8 -*-
# 3.5 双摆
# 混沌系统 — 双摆模拟

import numpy as np
import matplotlib.pyplot as plt

g = 9.8
L1, L2 = 1.0, 1.0
m1, m2 = 1.0, 1.0

def double_pendulum_deriv(t, state):
    theta1, omega1, theta2, omega2 = state
    delta = theta2 - theta1

    den1 = (2 * m1 + m2 - m2 * np.cos(2 * delta))
    den2 = den1

    dtheta1 = omega1
    dtheta2 = omega2

    domega1 = (
        -g * (2 * m1 + m2) * np.sin(theta1)
        - m2 * g * np.sin(theta1 - 2 * theta2)
        - 2 * np.sin(delta) * m2 * (omega2 ** 2 * L2 + omega1 ** 2 * L1 * np.cos(delta))
    ) / (L1 * den1)

    domega2 = (
        2 * np.sin(delta) * (
            omega1 ** 2 * L1 * (m1 + m2)
            + g * (m1 + m2) * np.cos(theta1)
            + omega2 ** 2 * L2 * m2 * np.cos(delta)
        )
    ) / (L2 * den2)

    return np.array([dtheta1, domega1, dtheta2, domega2])

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

print("=== 双摆模拟 (混沌系统) ===")

theta1_0 = np.radians(120)
theta2_0 = np.radians(-10)
omega1_0 = 0.0
omega2_0 = 0.0
y0 = np.array([theta1_0, omega1_0, theta2_0, omega2_0])

t, state = rk4_system(double_pendulum_deriv, y0, (0, 30), 0.005)

x1 = L1 * np.sin(state[:, 0])
y1_pos = -L1 * np.cos(state[:, 0])
x2 = x1 + L2 * np.sin(state[:, 2])
y2_pos = y1_pos - L2 * np.cos(state[:, 2])

eps = np.radians(0.01)
y0_pert = np.array([theta1_0 + eps, omega1_0, theta2_0, omega2_0])
t2, state2 = rk4_system(double_pendulum_deriv, y0_pert, (0, 30), 0.005)
x2_pert = x1 + L2 * np.sin(state2[:, 2])
y2_pert = y1_pos - L2 * np.cos(state2[:, 2])

divergence = np.sqrt((state[:, 0] - state2[:, 0]) ** 2 + (state[:, 2] - state2[:, 2]) ** 2)

print(f"初始条件: θ₁={np.degrees(theta1_0):.1f}°, θ₂={np.degrees(theta2_0):.1f}°")
print(f"扰动: Δθ = {np.degrees(eps):.4f}°")
print(f"模拟时间: 30s, 步数: {len(t)}")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

ax = axes[0, 0]
skip = 5
ax.plot(x2[::skip], y2[::skip], "b-", linewidth=0.2, alpha=0.5)
ax.plot([0], [0], "ko", markersize=8)
ax.plot(x2[0], y2[0], "go", markersize=8, label="起点")
ax.plot(x2[-1], y2[-1], "ro", markersize=8, label="终点")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("双摆末端轨迹")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_aspect("equal")

ax = axes[0, 1]
n_frames = 8
indices = np.linspace(0, len(t) - 1, n_frames, dtype=int)
for idx in indices:
    c = plt.cm.viridis(idx / len(t))
    ax.plot([0, x1[idx]], [0, y1_pos[idx]], "o-", color=c, markersize=4, linewidth=1.5)
    ax.plot([x1[idx], x2[idx]], [y1_pos[idx], y2_pos[idx]], "o-", color=c, markersize=4, linewidth=1.5)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("双摆不同时刻姿态")
ax.grid(True, alpha=0.3)
ax.set_aspect("equal")

ax = axes[1, 0]
ax.plot(t, np.degrees(state[:, 0]), "b-", label="θ₁", linewidth=0.5)
ax.plot(t, np.degrees(state[:, 2]), "r-", label="θ₂", linewidth=0.5)
ax.set_xlabel("时间 t (s)")
ax.set_ylabel("角度 (°)")
ax.set_title("双摆角度随时间变化")
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1, 1]
ax.semilogy(t, divergence + 1e-15, "b-", linewidth=0.5)
ax.set_xlabel("时间 t (s)")
ax.set_ylabel("|Δθ| (rad)")
ax.set_title(f"混沌: 对初始条件的敏感性 (Δθ₀={np.degrees(eps):.4f}°)")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
