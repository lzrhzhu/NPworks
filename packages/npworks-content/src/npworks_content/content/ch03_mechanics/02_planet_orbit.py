# -*- coding: utf-8 -*-
# 3.2 行星轨道
# 万有引力 + 轨道模拟

import numpy as np
import matplotlib.pyplot as plt

GM = 4 * np.pi ** 2

def simulate_orbit(x0, y0, vx0, vy0, dt, n_steps):
    x = np.zeros(n_steps)
    y = np.zeros(n_steps)
    vx_arr = np.zeros(n_steps)
    vy_arr = np.zeros(n_steps)
    x[0], y[0] = x0, y0
    vx_arr[0], vy_arr[0] = vx0, vy0

    for i in range(n_steps - 1):
        r = np.sqrt(x[i] ** 2 + y[i] ** 2)
        ax = -GM * x[i] / r ** 3
        ay = -GM * y[i] / r ** 3

        vx_half = vx_arr[i] + 0.5 * dt * ax
        vy_half = vy_arr[i] + 0.5 * dt * ay

        x[i + 1] = x[i] + dt * vx_half
        y[i + 1] = y[i] + dt * vy_half

        r_new = np.sqrt(x[i + 1] ** 2 + y[i + 1] ** 2)
        ax_new = -GM * x[i + 1] / r_new ** 3
        ay_new = -GM * y[i + 1] / r_new ** 3

        vx_arr[i + 1] = vx_half + 0.5 * dt * ax_new
        vy_arr[i + 1] = vy_half + 0.5 * dt * ay_new

    return x, y, vx_arr, vy_arr

def compute_energy(x, y, vx, vy):
    r = np.sqrt(x ** 2 + y ** 2)
    KE = 0.5 * (vx ** 2 + vy ** 2)
    PE = -GM / r
    return KE, PE, KE + PE

print("=== 行星轨道模拟 ===")

orbits = [
    {"label": "圆形轨道 (e≈0)", "r0": 1.0, "v_factor": 1.0, "color": "blue"},
    {"label": "椭圆轨道 (e≈0.5)", "r0": 1.0, "v_factor": 0.8, "color": "green"},
    {"label": "高椭圆轨道", "r0": 1.0, "v_factor": 0.6, "color": "red"},
]

dt = 0.001
n_steps = 10000

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

theta = np.linspace(0, 2 * np.pi, 200)
ax1.plot(0, 0, "yo", markersize=15, label="太阳")

for orb in orbits:
    r0 = orb["r0"]
    v0 = 2 * np.pi / np.sqrt(r0) * orb["v_factor"]
    x, y, vx, vy = simulate_orbit(r0, 0, 0, v0, dt, n_steps)
    ax1.plot(x, y, color=orb["color"], label=orb["label"], linewidth=1)

    KE, PE, TE = compute_energy(x[0], y[0], vx[0], vy[0])
    print(f"\n{orb['label']}:")
    print(f"  初始位置: ({x[0]:.2f}, {y[0]:.2f}), 速度: ({vx[0]:.4f}, {vy[0]:.4f})")
    print(f"  总能量: {TE:.6f}")

ax1.set_xlabel("x (AU)")
ax1.set_ylabel("y (AU)")
ax1.set_title("行星轨道模拟")
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)
ax1.set_aspect("equal")

r0_circ = 1.0
v0_circ = 2 * np.pi
x_c, y_c, vx_c, vy_c = simulate_orbit(r0_circ, 0, 0, v0_circ, dt, n_steps)
KE, PE, TE = compute_energy(x_c, y_c, vx_c, vy_c)
t = np.arange(n_steps) * dt

ax2.plot(t, KE, "b-", label="动能", alpha=0.7)
ax2.plot(t, PE, "r-", label="势能", alpha=0.7)
ax2.plot(t, TE, "k--", label="总能量", linewidth=2)
ax2.set_xlabel("时间 (年)")
ax2.set_ylabel("能量 (AU单位)")
ax2.set_title("圆形轨道能量守恒")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
