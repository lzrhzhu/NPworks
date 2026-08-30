"""维纳过程（布朗运动的数学模型）。

模拟多条维纳过程轨迹 W(t)，验证其核心统计性质：
  - 增量独立、W(0)=0；
  - 均值 <W(t)>=0；
  - 方差 <W^2(t)>=t（扩散律：位移与时间的平方根成正比）。
"""
import numpy as np
import matplotlib.pyplot as plt


plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})


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

fig, ax = plt.subplots(figsize=(8, 5))
for i in range(20):
    ax.plot(t, W[i], color='steelblue', alpha=0.4, linewidth=1.2)
ax.plot(t, mean_W, 'r-', linewidth=2.2, label=r'$\langle W(t)\rangle=0$')
ax.plot(t, np.sqrt(t), 'k--', linewidth=1.5, label=r'$\pm\sqrt{t}$')
ax.plot(t, -np.sqrt(t), 'k--', linewidth=1.5)
ax.set_xlabel('time $t$ (reduced units)')
ax.set_ylabel('$W(t)$ (reduced units)')
ax.set_title('Wiener 过程轨迹（处处连续、处处不可导）')
ax.legend(loc='upper left', frameon=False)
plt.tight_layout()
plt.suptitle('wiener_process')

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(t, msd_W, 'b-', linewidth=2, label=r'模拟 $\langle W^2(t)\rangle$')
ax.plot(t, t, 'r--', linewidth=2, label=r'理论 $=t$')
ax.set_xlabel('time $t$ (reduced units)')
ax.set_ylabel(r'$\langle W^2(t)\rangle$')
ax.set_title('方差与时间成正比 → 扩散')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('wiener_msd')

print("01_wiener_process.py done")

plt.show()
