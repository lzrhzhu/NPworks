# -*- coding: utf-8 -*-
# 5.2 分子动力学
# 二维气体分子模拟

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

N = 50
L = 10.0
dt = 0.005
n_steps = 3000
sigma = 0.5
epsilon = 1.0
r_cut = 2.5 * sigma
mass = 1.0

positions = np.random.uniform(sigma, L - sigma, (N, 2))
velocities = np.random.randn(N, 2) * 2.0
velocities -= np.mean(velocities, axis=0)

def compute_forces(pos, N, L, sigma, epsilon, r_cut):
    forces = np.zeros((N, 2))
    potential = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            dx = pos[j, 0] - pos[i, 0]
            dy = pos[j, 1] - pos[i, 1]
            if dx > L / 2: dx -= L
            elif dx < -L / 2: dx += L
            if dy > L / 2: dy -= L
            elif dy < -L / 2: dy += L

            r2 = dx ** 2 + dy ** 2
            if r2 < r_cut ** 2 and r2 > 0.01:
                r2i = sigma ** 2 / r2
                r6i = r2i ** 3
                r12i = r6i ** 2
                f_mag = 48 * epsilon * (r12i - 0.5 * r6i) / r2
                fx = f_mag * dx
                fy = f_mag * dy
                forces[i, 0] -= fx
                forces[i, 1] -= fy
                forces[j, 0] += fx
                forces[j, 1] += fy
                potential += 4 * epsilon * (r12i - r6i)
    return forces, potential

def apply_pbc(pos, L):
    pos[:, 0] = pos[:, 0] % L
    pos[:, 1] = pos[:, 1] % L

print("=== 二维分子动力学模拟 ===")
print(f"粒子数: {N}, 盒子大小: {L}x{L}")
print(f"模拟步数: {n_steps}")

KE_list = []
PE_list = []
T_list = []
frames = [0, n_steps // 3, 2 * n_steps // 3, n_steps - 1]

forces, _ = compute_forces(positions, N, L, sigma, epsilon, r_cut)

frame_data = []
for step in range(n_steps):
    velocities += 0.5 * dt * forces / mass
    positions += dt * velocities
    apply_pbc(positions, L)
    forces, PE = compute_forces(positions, N, L, sigma, epsilon, r_cut)
    velocities += 0.5 * dt * forces / mass

    KE = 0.5 * mass * np.sum(velocities ** 2)
    T = KE / N

    KE_list.append(KE)
    PE_list.append(PE)
    T_list.append(T)

    if step in frames:
        frame_data.append((step, positions.copy()))

    if (step + 1) % 1000 == 0:
        print(f"  步骤 {step+1}/{n_steps}, T={T:.3f}, KE={KE:.2f}, PE={PE:.2f}")

print(f"\n最终温度: {T_list[-1]:.3f}")
print(f"能量守恒: KE+PE变化率 = {abs((KE_list[-1]+PE_list[-1])-(KE_list[0]+PE_list[0]))/abs(KE_list[0]+PE_list[0]+1e-10)*100:.2f}%")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

for idx, (ax, (step_num, pos)) in enumerate(zip(axes.flat[:len(frame_data)], frame_data)):
    ax.scatter(pos[:, 0], pos[:, 1], s=50, c="steelblue", edgecolors="black", linewidth=0.5)
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_title(f"t = {step_num * dt:.2f}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal")

for ax in axes.flat[len(frame_data):]:
    ax.set_visible(False)

fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
t_arr = np.arange(n_steps) * dt
ax1.plot(t_arr, KE_list, "r-", label="动能", alpha=0.7)
ax1.plot(t_arr, PE_list, "b-", label="势能", alpha=0.7)
ax1.plot(t_arr, np.array(KE_list) + np.array(PE_list), "k--", label="总能量", linewidth=2)
ax1.set_xlabel("时间")
ax1.set_ylabel("能量")
ax1.set_title("能量随时间变化")
ax1.legend()
ax1.grid(True, alpha=0.3)

speeds = np.sqrt(velocities[:, 0] ** 2 + velocities[:, 1] ** 2)
ax2.hist(speeds, bins=15, density=True, alpha=0.7, color="steelblue", edgecolor="black")
v_range = np.linspace(0, max(speeds), 100)
T_final = T_list[-1]
a = mass / (T_final + 1e-10)
ax2.plot(v_range, a * v_range * np.exp(-0.5 * a * v_range ** 2), "r-", linewidth=2, label="Maxwell-Boltzmann")
ax2.set_xlabel("速率")
ax2.set_ylabel("概率密度")
ax2.set_title("速度分布")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
