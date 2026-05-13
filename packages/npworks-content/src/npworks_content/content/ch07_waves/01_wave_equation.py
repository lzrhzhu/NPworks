# -*- coding: utf-8 -*-
# 7.1 波动方程
# 一维波动模拟

import numpy as np
import matplotlib.pyplot as plt

c = 1.0
L = 10.0
Nx = 200
dx = L / (Nx - 1)
dt = 0.5 * dx / c
Nt = 1000
x = np.linspace(0, L, Nx)

r = c * dt / dx
print("=== 一维波动方程模拟 ===")
print(f"波速 c = {c}")
print(f"区域长度 L = {L}")
print(f"空间网格 N = {Nx}, dx = {dx:.4f}")
print(f"时间步长 dt = {dt:.6f}")
print(f"CFL数 r = {r:.4f} (需要 r ≤ 1)")
print(f"总步数: {Nt}")

u_prev = np.zeros(Nx)
u_curr = np.zeros(Nx)
u_next = np.zeros(Nx)

x0 = 2.0
sigma = 0.3
u_prev = np.exp(-((x - x0) ** 2) / (2 * sigma ** 2))
u_curr = np.exp(-((x - (x0 + c * dt)) ** 2) / (2 * sigma ** 2))

u_prev[0] = 0
u_curr[0] = 0
u_prev[-1] = 0
u_curr[-1] = 0

frames = [0, 100, 250, 500, 750, Nt]
frame_data = [(0, u_curr.copy())]

for step in range(1, Nt + 1):
    for i in range(1, Nx - 1):
        u_next[i] = 2 * u_curr[i] - u_prev[i] + r ** 2 * (u_curr[i + 1] - 2 * u_curr[i] + u_curr[i - 1])

    u_next[0] = 0
    u_next[-1] = 0

    u_prev[:] = u_curr
    u_curr[:] = u_next

    if step in frames:
        frame_data.append((step, u_curr.copy()))

    if step % 200 == 0:
        energy = np.sum(u_curr ** 2) * dx
        print(f"  步骤 {step}/{Nt}, 能量={energy:.6f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

colors = plt.cm.viridis(np.linspace(0, 1, len(frame_data)))
for idx, (step_num, u_frame) in enumerate(frame_data):
    ax1.plot(x, u_frame, color=colors[idx], linewidth=1.2,
             label=f"t={step_num*dt:.2f}")
ax1.set_xlabel("x")
ax1.set_ylabel("u(x,t)")
ax1.set_title("波动方程: 固定边界条件 (u=0)")
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

n_time = 100
u_spacetime = np.zeros((n_time, Nx))
u_prev2 = np.zeros(Nx)
u_curr2 = np.zeros(Nx)
u_next2 = np.zeros(Nx)

u_prev2 = np.exp(-((x - x0) ** 2) / (2 * sigma ** 2))
u_curr2 = np.exp(-((x - (x0 + c * dt)) ** 2) / (2 * sigma ** 2))
u_prev2[0] = u_curr2[0] = u_prev2[-1] = u_curr2[-1] = 0

total_steps = Nt
save_interval = max(1, total_steps // n_time)
u_spacetime[0] = u_curr2.copy()

step_count = 1
for step in range(1, total_steps + 1):
    for i in range(1, Nx - 1):
        u_next2[i] = 2 * u_curr2[i] - u_prev2[i] + r ** 2 * (u_curr2[i + 1] - 2 * u_curr2[i] + u_curr2[i - 1])
    u_next2[0] = 0
    u_next2[-1] = 0
    u_prev2[:] = u_curr2
    u_curr2[:] = u_next2

    if step % save_interval == 0 and step_count < n_time:
        u_spacetime[step_count] = u_curr2.copy()
        step_count += 1

im = ax2.imshow(u_spacetime[:step_count], aspect="auto", origin="lower",
                extent=[0, L, 0, total_steps * dt], cmap="seismic",
                vmin=-1, vmax=1)
ax2.set_xlabel("x")
ax2.set_ylabel("时间 t")
ax2.set_title("波动方程: 时空图")
plt.colorbar(im, ax=ax2, label="u")

plt.tight_layout()
plt.show()
