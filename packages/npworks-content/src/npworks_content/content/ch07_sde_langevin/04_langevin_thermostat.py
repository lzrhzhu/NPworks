"""Langevin 恒温器：把确定性 MD 装上"阻尼+噪声"。

对一维谐振子施加 Langevin 恒温（BAOAB 思想的简化）：
  v <- v + (F/m)*dt/2 ;  v <- c1*v + c2*sqrt(kT/m)*N(0,1) ;  v <- v + (F/m)*dt/2
其中 c1=exp(-gamma*dt), c2=sqrt(1-c1^2)（精确的 OU 更新，保证 FDT）。
验证：体系从高/低温弛豫到目标温度 T0，位置分布趋于玻尔兹曼分布。
"""
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(3)

m = 1.0
k = 1.0           # 弹簧：U = k x^2 /2
T0 = 1.0          # 目标温度（k_B=1）
gamma = 1.0
dt = 0.01
N = 60000

n_p = 2000
x = np.zeros(n_p)
v = np.zeros(n_p)
v[:] = 3.0        # 初始"过热"

c1 = np.exp(-gamma * dt)
c2 = np.sqrt(1 - c1 ** 2)
sqrtT = np.sqrt(T0 / m)

KE_t = []
for i in range(N):
    F = -k * x
    v_half = v + 0.5 * (F / m) * dt          # B
    v_ou = c1 * v_half + c2 * sqrtT * np.random.randn(n_p)   # A（精确 OU）
    x = x + v_ou * dt                         # O (drift)
    F = -k * x
    v = v_ou + 0.5 * (F / m) * dt             # B
    if i % 20 == 0:
        KE = 0.5 * m * (v ** 2).mean()
        KE_t.append(2 * KE)                   # 瞬时温度 T=2<KE>/(自由度)

KE_t = np.array(KE_t)
t_ax = np.arange(len(KE_t)) * 20 * dt

# 平衡后位置分布
x_eq = x

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

axes[0].plot(t_ax, KE_t, 'b-', linewidth=1.3, label='瞬时温度 $T(t)$')
axes[0].axhline(T0, color='r', linestyle='--', linewidth=2, label=f'目标 $T_0={T0}$')
axes[0].set_xlabel('time $t$')
axes[0].set_ylabel('temperature $T$')
axes[0].set_title('Langevin 恒温器：弛豫到目标温度')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].hist(x_eq, bins=60, density=True, color='steelblue', alpha=0.7,
             label='平衡位置分布')
xg = np.linspace(-4, 4, 300)
boltz = np.exp(-0.5 * k * xg ** 2 / T0)
boltz /= np.trapz(boltz, xg)
axes[1].plot(xg, boltz, 'r-', linewidth=2.2, label=r'玻尔兹曼分布 $\propto e^{-U/k_BT}$')
axes[1].set_xlabel('$x$')
axes[1].set_ylabel('概率密度')
axes[1].set_title('平衡采样 = 正则系综')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('langevin_thermostat')
plt.show()
print("04_langevin_thermostat.py done")
