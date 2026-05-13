# -*- coding: utf-8 -*-
# 5.1 随机行走
# 一维/二维随机行走模拟

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

print("=== 一维随机行走 ===")
n_walkers = 1000
n_steps = 500

walks = np.random.choice([-1, 1], size=(n_walkers, n_steps))
positions = np.cumsum(walks, axis=1)
mean_pos = np.mean(positions, axis=0)
std_pos = np.std(positions, axis=0)

print(f"行走者数量: {n_walkers}")
print(f"步数: {n_steps}")
print(f"理论 RMS = √N: {np.sqrt(n_steps):.2f}")
print(f"实际 RMS: {std_pos[-1]:.2f}")

steps = np.arange(1, n_steps + 1)

print("\n=== 二维随机行走 ===")
n_steps_2d = 2000
angles = np.random.uniform(0, 2 * np.pi, size=(5, n_steps_2d))
dx = np.cos(angles)
dy = np.sin(angles)

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

ax = axes[0, 0]
for i in range(5):
    ax.plot(np.cumsum(dx[i]), np.cumsum(dy[i]), linewidth=0.5, alpha=0.7)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("二维随机行走 (5个粒子)")
ax.grid(True, alpha=0.3)
ax.set_aspect("equal")

ax = axes[0, 1]
for i in range(min(10, n_walkers)):
    ax.plot(steps, positions[i], linewidth=0.3, alpha=0.5)
ax.plot(steps, std_pos, "r-", linewidth=2, label="标准差 (σ)")
ax.plot(steps, -std_pos, "r-", linewidth=2)
ax.plot(steps, np.sqrt(steps), "k--", linewidth=1, label="√N 理论值")
ax.plot(steps, -np.sqrt(steps), "k--", linewidth=1)
ax.set_xlabel("步数 N")
ax.set_ylabel("位置")
ax.set_title("一维随机行走轨迹")
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1, 0]
final_pos = positions[:, -1]
ax.hist(final_pos, bins=40, density=True, alpha=0.7, color="steelblue", edgecolor="black")
x_gauss = np.linspace(-60, 60, 200)
sigma_theory = np.sqrt(n_steps)
ax.plot(x_gauss, np.exp(-x_gauss ** 2 / (2 * sigma_theory ** 2)) / (sigma_theory * np.sqrt(2 * np.pi)),
        "r-", linewidth=2, label=f"高斯分布 (σ=√{n_steps}={sigma_theory:.1f})")
ax.set_xlabel("最终位置")
ax.set_ylabel("概率密度")
ax.set_title(f"最终位置分布 (N={n_steps})")
ax.legend()
ax.grid(True, alpha=0.3)

ax = axes[1, 1]
ax.plot(steps, std_pos ** 2, "b-", linewidth=2, label="实际 <x²>")
ax.plot(steps, steps, "r--", linewidth=2, label="理论值 = N")
ax.set_xlabel("步数 N")
ax.set_ylabel("<x²>")
ax.set_title("均方位移 vs 步数")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
