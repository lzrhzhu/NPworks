"""Ornstein–Uhlenbeck 过程（带阻尼的朗之万速度过程）。

数值求解速度朗之万方程（Euler–Maruyama）：
  dv = -gamma * v * dt + sqrt(2*gamma*kT/m) * dW
验证涨落-耗散定理：稳态 <v^2> = kT/m，速度分布趋于高斯（一维 Maxwell）。
"""
import numpy as np
import matplotlib.pyplot as plt


np.random.seed(1)

kT_m = 1.0
gamma = 2.0
sigma = np.sqrt(2 * gamma * kT_m)

T = 5.0
N = 50000
dt = T / N
t = np.linspace(0, T, N + 1)
n_traj = 300

v = np.zeros(n_traj)
v_traj = np.zeros((n_traj, N + 1))
v_traj[:, 0] = 5.0

for i in range(N):
    dW = np.sqrt(dt) * np.random.randn(n_traj)
    v += -gamma * v * dt + sigma * dW
    v_traj[:, i + 1] = v

v_eq = v_traj[:, N // 2:].reshape(-1)
v2_mean = (v_traj ** 2).mean(axis=0)

# --- 图1：速度弛豫 ---
fig, ax = plt.subplots(figsize=(9, 5))
for i in range(8):
    ax.plot(t, v_traj[i], alpha=0.5, linewidth=0.7)
ax.plot(t, v2_mean, 'r-', linewidth=2.2, label=r'$\langle v^2(t)\rangle$')
ax.axhline(kT_m, color='k', linestyle='--', linewidth=1.5,
           label=r'$k_BT/m=1$（FDT 预言）')
ax.set_xlabel('time $t$')
ax.set_ylabel('$v(t)$')
ax.set_title('OU 过程：速度弛豫到热平衡')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('ou_process')

# --- 图2：稳态速度分布 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(v_eq, bins=60, density=True, color='steelblue', alpha=0.7, label='模拟稳态分布')
v_grid = np.linspace(-4, 4, 200)
gauss = np.exp(-v_grid ** 2 / (2 * kT_m)) / np.sqrt(2 * np.pi * kT_m)
ax.plot(v_grid, gauss, 'r-', linewidth=2.2, label='Maxwell 分布')
ax.set_xlabel('$v$')
ax.set_ylabel('概率密度')
ax.set_title('稳态速度分布 = Maxwell 分布')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('ou_distribution')

print("02_ou_process.py done")

plt.show()
