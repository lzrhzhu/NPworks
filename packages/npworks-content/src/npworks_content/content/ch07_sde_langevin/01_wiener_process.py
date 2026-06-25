"""维纳过程（布朗运动的数学模型）。

模拟多条维纳过程轨迹 W(t)，验证其核心统计性质：
  - 增量独立、W(0)=0；
  - 均值 <W(t)>=0；
  - 方差 <W^2(t)>=t（扩散律：位移与时间的平方根成正比）。
"""
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)

T = 1.0      # 总时间
N = 1000     # 步数
dt = T / N
n_traj = 500  # 轨迹数（用于统计平均）

t = np.linspace(0, T, N + 1)
dW = np.sqrt(dt) * np.random.randn(n_traj, N)      # 独立增量 ~ N(0, dt)
W = np.zeros((n_traj, N + 1))
W[:, 1:] = np.cumsum(dW, axis=1)                    # 累加得 W(t)

mean_W = W.mean(axis=0)          # <W(t)>
msd_W = (W ** 2).mean(axis=0)    # <W^2(t)>

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

# 左：若干条轨迹 + 均值
for i in range(20):
    axes[0].plot(t, W[i], color='steelblue', alpha=0.4, linewidth=0.8)
axes[0].plot(t, mean_W, 'r-', linewidth=2.2, label=r'$\langle W(t)\rangle=0$')
axes[0].plot(t, np.sqrt(t), 'k--', linewidth=1.5, label=r'$\pm\sqrt{t}$')
axes[0].plot(t, -np.sqrt(t), 'k--', linewidth=1.5)
axes[0].set_xlabel('time $t$')
axes[0].set_ylabel('$W(t)$')
axes[0].set_title('Wiener 过程轨迹（处处连续、处处不可导）')
axes[0].legend(loc='upper left')
axes[0].grid(True, alpha=0.3)

# 右：方差 <W^2> vs t
axes[1].plot(t, msd_W, 'b-', linewidth=2, label=r'模拟 $\langle W^2(t)\rangle$')
axes[1].plot(t, t, 'r--', linewidth=2, label=r'理论 $=t$')
axes[1].set_xlabel('time $t$')
axes[1].set_ylabel(r'$\langle W^2(t)\rangle$')
axes[1].set_title('方差与时间成正比 → 扩散')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('wiener_process')
plt.show()
print("01_wiener_process.py done")
