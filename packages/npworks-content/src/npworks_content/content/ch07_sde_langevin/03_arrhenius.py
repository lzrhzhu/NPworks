"""Arrhenius 律：越势垒的平均首达时间。

过阻尼朗之万粒子在双势阱中运动：
  dx = -U'(x) dt + sqrt(2*kT) dW
测量从一阱越过势垒到达另一阱的平均首达时间 tau(kT)。
验证 Arrhenius 律  tau ~ exp(dU / kT)。
"""
import numpy as np
import matplotlib.pyplot as plt


np.random.seed(2)


def dU(x):
    return x ** 3 - x


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
            if not crossed and x > 0.6:
                fpt.append(i * dt)
                crossed = True
                break
        if not crossed:
            fpt.append(n_steps * dt)
    tau_list.append(np.mean(fpt))

tau_list = np.array(tau_list)

# --- 图1：双势阱 ---
xx = np.linspace(-1.8, 1.8, 400)
U = xx ** 4 / 4 - xx ** 2 / 2
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(xx, U, 'k-', linewidth=2, label=r'$U(x)=x^4/4-x^2/2$')
ax.axhline(0, color='gray', linewidth=0.8)
ax.annotate('势垒 $\\Delta U=1/4$', xy=(0, -0.0), xytext=(0.5, 0.35),
            arrowprops=dict(arrowstyle='->'))
ax.set_xlabel('$x$')
ax.set_ylabel('$U(x)$')
ax.set_title('双势阱与越垒过程')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.suptitle('arrhenius_potential')

# --- 图2：Arrhenius 律 ---
inv_kT = 1.0 / kT_list
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(inv_kT, tau_list, 'bo', markersize=7, label='模拟平均首达时间')
fit = np.polyfit(inv_kT, np.log(tau_list), 1)
inv_grid = np.linspace(inv_kT.min(), inv_kT.max(), 100)
ax.semilogy(inv_grid, np.exp(fit[0] * inv_grid + fit[1]), 'r--', linewidth=2,
            label=fr'拟合 $\tau \propto e^{{\Delta U/k_BT}}$')
ax.set_xlabel(r'$1/k_BT$')
ax.set_ylabel(r'$\tau$（首达时间）')
ax.set_title('Arrhenius 律：半对数图为直线')
ax.legend()
ax.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.suptitle('arrhenius')

print("03_arrhenius.py done")

plt.show()
