"""Arrhenius 律：越势垒的平均首达时间。

过阻尼朗之万粒子在双势阱中运动：
  dx = -U'(x) dt + sqrt(2*kT) dW
测量从一阱越过势垒到达另一阱的平均首达时间 tau(kT)。
验证 Arrhenius 律  tau ~ exp(dU / kT)。
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


np.random.seed(2)


def dU(x):
    return x ** 3 - x


dt = 1e-3
n_steps = 500000
n_traj = 60

kT_list = np.linspace(0.05, 0.5, 10)
tau_list = []
completion_list = []

for kT in kT_list:
    sigma = np.sqrt(2 * kT)
    fpt = []
    for _ in range(n_traj):
        x = -1.0
        crossed = False
        for i in range(n_steps):
            x += -dU(x) * dt + sigma * np.sqrt(dt) * np.random.randn()
            if not crossed and x > 0.0:
                fpt.append((i + 1) * dt)
                crossed = True
                break
    tau_list.append(np.mean(fpt) if fpt else np.nan)
    completion_list.append(len(fpt) / n_traj)
    print(f'kT={kT:.3f}: completed {len(fpt)}/{n_traj}')

tau_list = np.array(tau_list)
completion_list = np.array(completion_list)

# --- 图1：双势阱 ---
xx = np.linspace(-1.8, 1.8, 400)
U = xx ** 4 / 4 - xx ** 2 / 2
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(xx, U, 'k-', linewidth=2, label=r'$U(x)=x^4/4-x^2/2$')
ax.axhline(0, color='gray', linewidth=0.8)
ax.annotate('势垒 $\\Delta U=1/4$', xy=(0, -0.0), xytext=(0.5, 0.35),
            arrowprops=dict(arrowstyle='->'))
ax.set_xlabel('$x$ (reduced length)')
ax.set_ylabel('$U(x)$ (reduced energy)')
ax.set_title('双势阱与越垒过程')
ax.legend(loc='lower right', frameon=False)
plt.tight_layout()
plt.suptitle('arrhenius_potential')

# --- 图2：Arrhenius 律 ---
inv_kT = 1.0 / kT_list
valid = np.isfinite(tau_list) & (completion_list >= 0.9)
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(inv_kT[valid], tau_list[valid], 'bo', markersize=7, label='模拟平均首达时间')
ax.semilogy(inv_kT[~valid], tau_list[~valid], 'o', color='0.6', markerfacecolor='none',
            markersize=7, label='完成率不足 90%（不拟合）')
fit = np.polyfit(inv_kT[valid], np.log(tau_list[valid]), 1)
inv_grid = np.linspace(inv_kT.min(), inv_kT.max(), 100)
ax.semilogy(inv_grid, np.exp(fit[0] * inv_grid + fit[1]), 'r--', linewidth=2,
            label=fr'拟合斜率 $={fit[0]:.3f}$')
print(f'Arrhenius slope={fit[0]:.3f}; expected barrier=0.250')
ax.set_xlabel(r'$1/k_BT$ (reduced units)')
ax.set_ylabel(r'$\tau$ (reduced time)')
ax.set_title('Arrhenius 律：半对数图为直线')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('arrhenius')

print("03_arrhenius.py done")

plt.show()
