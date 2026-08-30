"""Langevin 恒温器：把确定性 MD 装上"阻尼+噪声"。

对一维谐振子施加 Langevin 恒温：
  v <- v + (F/m)*dt/2 ;  v <- c1*v + c2*sqrt(kT/m)*N(0,1) ;  v <- v + (F/m)*dt/2
其中 c1=exp(-gamma*dt), c2=sqrt(1-c1^2)（精确的 OU 更新，保证 FDT）。
验证：体系从高/低温弛豫到目标温度 T0，位置分布趋于玻尔兹曼分布。
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


np.random.seed(3)

m = 1.0
k = 1.0
T0 = 1.0
gamma = 1.0
dt = 0.01
N = 60000

n_p = 2000
x = np.zeros(n_p)
v = np.zeros(n_p)
v[:] = 3.0

c1 = np.exp(-gamma * dt)
c2 = np.sqrt(1 - c1 ** 2)
sqrtT = np.sqrt(T0 / m)

KE_t = []
for i in range(N):
    F = -k * x
    v_half = v + 0.5 * (F / m) * dt
    v_ou = c1 * v_half + c2 * sqrtT * np.random.randn(n_p)
    x = x + v_ou * dt
    F = -k * x
    v = v_ou + 0.5 * (F / m) * dt
    if i % 20 == 0:
        KE = 0.5 * m * (v ** 2).mean()
        KE_t.append(2 * KE)

KE_t = np.array(KE_t)
t_ax = np.arange(len(KE_t)) * 20 * dt
x_eq = x

# --- 图1：温度弛豫 ---
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(t_ax, KE_t, 'b-', linewidth=1.3, label='瞬时温度 $T(t)$')
ax.axhline(T0, color='r', linestyle='--', linewidth=2, label=f'目标 $T_0={T0}$')
ax.set_xlabel('time $t$ (reduced units)')
ax.set_ylabel('temperature $T$ (reduced units)')
ax.set_title('Langevin 恒温器：弛豫到目标温度')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('langevin_thermostat')

# --- 图2：平衡位置分布 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(x_eq, bins=60, density=True, color='steelblue', alpha=0.7, label='平衡位置分布')
xg = np.linspace(-4, 4, 300)
boltz = np.exp(-0.5 * k * xg ** 2 / T0)
boltz /= np.trapz(boltz, xg)
ax.plot(xg, boltz, 'r-', linewidth=2.2, label=r'玻尔兹曼分布 $\propto e^{-U/k_BT}$')
ax.set_xlabel('$x$ (reduced units)')
ax.set_ylabel('概率密度')
ax.set_title('平衡采样 = 正则系综')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('langevin_distribution')

print("04_langevin_thermostat.py done")

plt.show()
