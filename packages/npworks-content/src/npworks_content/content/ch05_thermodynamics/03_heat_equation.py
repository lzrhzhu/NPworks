# -*- coding: utf-8 -*-
# 5.3 热传导方程
# 有限差分法解热传导方程

import numpy as np
import matplotlib.pyplot as plt

L = 1.0
Nx = 50
dx = L / (Nx - 1)
alpha = 0.01
dt = 0.4 * dx ** 2 / alpha
Nt = 5000
x = np.linspace(0, L, Nx)

T = np.zeros(Nx)
T[0] = 100.0
T[-1] = 50.0
T[10:20] = 80.0

T_initial = T.copy()

print("=== 热传导方程求解 ===")
print(f"区域长度: {L}")
print(f"空间网格: {Nx} 点, dx={dx:.4f}")
print(f"热扩散系数: α={alpha}")
print(f"时间步长: dt={dt:.6f}")
print(f"稳定性条件: r = α·dt/dx² = {alpha*dt/dx**2:.4f} (< 0.5)")
print(f"总步数: {Nt}")

r = alpha * dt / dx ** 2
print(f"\n数值稳定性参数 r = {r:.4f} (需要 r < 0.5)")

frames = [0, 100, 500, 2000, Nt]
frame_data = [(0, T.copy())]

T_exact_steady = T[0] + (T[-1] - T[0]) * x / L

for step in range(1, Nt + 1):
    T_new = T.copy()
    for i in range(1, Nx - 1):
        T_new[i] = T[i] + r * (T[i + 1] - 2 * T[i] + T[i - 1])
    T = T_new

    if step in frames:
        frame_data.append((step, T.copy()))

    if step % 1000 == 0:
        print(f"  步骤 {step}/{Nt}, Tmax={T.max():.2f}, Tmin={T.min():.2f}")

print(f"\n最终状态: Tmax={T.max():.2f}, Tmin={T.min():.2f}")
print(f"稳态理论: T(x) = {T[0]:.0f} + ({T[-1]:.0f}-{T[0]:.0f})·x/L")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

colors = plt.cm.hot(np.linspace(0.2, 0.9, len(frame_data)))
for idx, (step_num, T_frame) in enumerate(frame_data):
    ax1.plot(x, T_frame, color=colors[idx], linewidth=1.5,
             label=f"t={step_num * dt:.3f}s" if step_num in [0, 100, 2000, Nt] else "")
ax1.plot(x, T_exact_steady, "k--", linewidth=2, label="稳态解析解")
ax1.set_xlabel("位置 x")
ax1.set_ylabel("温度 T")
ax1.set_title("热传导: 温度分布演化")
ax1.legend()
ax1.grid(True, alpha=0.3)

T_2d = np.zeros((50, Nx))
T_2d[0, :] = T_initial
T_temp = T_initial.copy()
save_steps = np.linspace(0, Nt, 50, dtype=int)
save_idx = 1
for step in range(1, Nt + 1):
    T_new = T_temp.copy()
    for i in range(1, Nx - 1):
        T_new[i] = T_temp[i] + r * (T_temp[i + 1] - 2 * T_temp[i] + T_temp[i - 1])
    T_temp = T_new
    if save_idx < len(save_steps) and step == save_steps[save_idx]:
        T_2d[save_idx, :] = T_temp.copy()
        save_idx += 1

im = ax2.imshow(T_2d, aspect="auto", origin="lower",
                extent=[0, L, 0, Nt * dt], cmap="hot")
ax2.set_xlabel("位置 x")
ax2.set_ylabel("时间 t")
ax2.set_title("热传导: 时空演化")
plt.colorbar(im, ax=ax2, label="温度")

plt.tight_layout()
plt.show()
