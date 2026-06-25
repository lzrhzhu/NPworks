"""Arrhenius 律：越势垒的平均首达时间。

过阻尼朗之万粒子在双势阱中运动：
  dx = -U'(x) dt + sqrt(2*kT) dW
测量从一阱越过势垒到达另一阱的平均首达时间 tau(kT)。
验证 Arrhenius 律  tau ~ exp(dU / kT)（势垒越高/温度越低，等待越久）。
"""
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(2)


def dU(x):
    # U(x) = x^4/4 - x^2/2，势阱在 ±1，鞍点在 0，势垒 dU = 1/4
    return x ** 3 - x


dU_bar = 0.25
dt = 1e-3
n_steps = 200000
n_traj = 60

kT_list = np.linspace(0.05, 0.5, 10)
tau_list = []

for kT in kT_list:
    sigma = np.sqrt(2 * kT)
    fpt = []
    for _ in range(n_traj):
        x = -1.0
        crossed = False
        for i in range(n_steps):
            x += -dU(x) * dt + sigma * np.sqrt(dt) * np.random.randn()
            if not crossed and x > 0.6:        # 到达右阱底部附近
                fpt.append(i * dt)
                crossed = True
                break
        if not crossed:
            fpt.append(n_steps * dt)
    tau_list.append(np.mean(fpt))

tau_list = np.array(tau_list)

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

# 左：势能曲线 + 一条示意轨迹
xx = np.linspace(-1.8, 1.8, 400)
U = xx ** 4 / 4 - xx ** 2 / 2
ax = axes[0]
ax.plot(xx, U, 'k-', linewidth=2, label=r'$U(x)=x^4/4-x^2/2$')
ax.axhline(0, color='gray', linewidth=0.8)
ax.annotate('势垒 $\\Delta U=1/4$', xy=(0, -0.0), xytext=(0.5, 0.35),
            arrowprops=dict(arrowstyle='->'))
ax.set_xlabel('$x$')
ax.set_ylabel('$U(x)$')
ax.set_title('双势阱与越垒过程')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)

# 右：tau vs 1/kT（对数纵轴）→ 直线验证 Arrhenius
inv_kT = 1.0 / kT_list
axes[1].semilogy(inv_kT, tau_list, 'bo', markersize=7, label='模拟平均首达时间')
# 理论拟合 tau = A exp(dU/kT)
fit = np.polyfit(inv_kT, np.log(tau_list), 1)
inv_grid = np.linspace(inv_kT.min(), inv_kT.max(), 100)
axes[1].semilogy(inv_grid, np.exp(fit[0] * inv_grid + fit[1]), 'r--', linewidth=2,
                 label=fr'拟合 $\tau \propto e^{{\Delta U/k_BT}}$')
axes[1].set_xlabel(r'$1/k_BT$')
axes[1].set_ylabel(r'$\tau$（首达时间）')
axes[1].set_title('Arrhenius 律：半对数图为直线')
axes[1].legend()
axes[1].grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.suptitle('arrhenius')
plt.show()
print("03_arrhenius.py done")
