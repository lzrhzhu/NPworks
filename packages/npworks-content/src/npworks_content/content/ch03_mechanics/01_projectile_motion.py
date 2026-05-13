# -*- coding: utf-8 -*-
# 3.1 抛体运动
# 二维抛体轨迹模拟

import numpy as np
import matplotlib.pyplot as plt

g = 9.8

def projectile(v0, angle_deg, dt=0.01):
    angle = np.radians(angle_deg)
    vx = v0 * np.cos(angle)
    vy = v0 * np.sin(angle)
    t_flight = 2 * vy / g

    t = np.arange(0, t_flight + dt, dt)
    x = vx * t
    y = vy * t - 0.5 * g * t ** 2
    y = np.maximum(y, 0)

    max_h = vy ** 2 / (2 * g)
    range_x = v0 ** 2 * np.sin(2 * angle) / g

    return x, y, t, max_h, range_x

print("=== 抛体运动模拟 ===")
v0 = 50
print(f"初速度: {v0} m/s\n")
print(f"{'角度(°)':>8} {'最大高度(m)':>14} {'射程(m)':>10} {'飞行时间(s)':>14}")
print("-" * 50)

angles = [15, 30, 45, 60, 75]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

for angle in angles:
    x, y, t, max_h, range_x = projectile(v0, angle)
    tf = 2 * v0 * np.sin(np.radians(angle)) / g
    print(f"{angle:>8} {max_h:>14.2f} {range_x:>10.2f} {tf:>14.2f}")
    ax1.plot(x, y, label=f"θ={angle}°")

ax1.set_xlabel("水平距离 x (m)")
ax1.set_ylabel("高度 y (m)")
ax1.set_title(f"抛体运动轨迹 (v₀={v0} m/s)")
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_ylim(bottom=0)

angles_cont = np.linspace(1, 89, 200)
ranges = [v0 ** 2 * np.sin(2 * np.radians(a)) / g for a in angles_cont]
max_heights = [(v0 * np.sin(np.radians(a))) ** 2 / (2 * g) for a in angles_cont]

ax2_twin = ax2.twinx()
ax2.plot(angles_cont, ranges, "b-", label="射程")
ax2_twin.plot(angles_cont, max_heights, "r--", label="最大高度")
ax2.set_xlabel("发射角度 θ (°)")
ax2.set_ylabel("射程 (m)", color="b")
ax2_twin.set_ylabel("最大高度 (m)", color="r")
ax2.set_title("射程和最大高度 vs 发射角度")
ax2.grid(True, alpha=0.3)

lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax2_twin.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
plt.show()
