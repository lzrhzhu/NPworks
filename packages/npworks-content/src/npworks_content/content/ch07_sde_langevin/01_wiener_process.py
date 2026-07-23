"""维纳过程（布朗运动的数学模型）。

模拟多条维纳过程轨迹 W(t)，验证其核心统计性质：
  - 增量独立、W(0)=0；
  - 均值 <W(t)>=0；
  - 方差 <W^2(t)>=t（扩散律：位移与时间的平方根成正比）。
"""
import numpy as np
import matplotlib.pyplot as plt
import os


def _img_dir(ch):
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):
        if os.path.isdir(os.path.join(d, "markdown")):
            return os.path.join(d, "markdown", "images", ch)
        d = os.path.dirname(d)
    out = os.path.join(os.path.expanduser("~"), "npworks_figures", ch)
    os.makedirs(out, exist_ok=True)
    return out


IMG_DIR = _img_dir("ch07")

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
    ax.plot(t, W[i], color='steelblue', alpha=0.4, linewidth=0.8)
ax.plot(t, mean_W, 'r-', linewidth=2.2, label=r'$\langle W(t)\rangle=0$')
ax.plot(t, np.sqrt(t), 'k--', linewidth=1.5, label=r'$\pm\sqrt{t}$')
ax.plot(t, -np.sqrt(t), 'k--', linewidth=1.5)
ax.set_xlabel('time $t$')
ax.set_ylabel('$W(t)$')
ax.set_title('Wiener 过程轨迹（处处连续、处处不可导）')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch07_wiener_process.png"), dpi=130)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(t, msd_W, 'b-', linewidth=2, label=r'模拟 $\langle W^2(t)\rangle$')
ax.plot(t, t, 'r--', linewidth=2, label=r'理论 $=t$')
ax.set_xlabel('time $t$')
ax.set_ylabel(r'$\langle W^2(t)\rangle$')
ax.set_title('方差与时间成正比 → 扩散')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch07_wiener_msd.png"), dpi=130)
plt.close(fig)

print("01_wiener_process.py done")
