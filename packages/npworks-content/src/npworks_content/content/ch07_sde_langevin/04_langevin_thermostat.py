"""Langevin 恒温器：把确定性 MD 装上"阻尼+噪声"。

对一维谐振子施加 Langevin 恒温：
  v <- v + (F/m)*dt/2 ;  v <- c1*v + c2*sqrt(kT/m)*N(0,1) ;  v <- v + (F/m)*dt/2
其中 c1=exp(-gamma*dt), c2=sqrt(1-c1^2)（精确的 OU 更新，保证 FDT）。
验证：体系从高/低温弛豫到目标温度 T0，位置分布趋于玻尔兹曼分布。
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
ax.set_xlabel('time $t$')
ax.set_ylabel('temperature $T$')
ax.set_title('Langevin 恒温器：弛豫到目标温度')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch07_langevin_thermostat.png"), dpi=130)
plt.close(fig)

# --- 图2：平衡位置分布 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(x_eq, bins=60, density=True, color='steelblue', alpha=0.7, label='平衡位置分布')
xg = np.linspace(-4, 4, 300)
boltz = np.exp(-0.5 * k * xg ** 2 / T0)
boltz /= np.trapz(boltz, xg)
ax.plot(xg, boltz, 'r-', linewidth=2.2, label=r'玻尔兹曼分布 $\propto e^{-U/k_BT}$')
ax.set_xlabel('$x$')
ax.set_ylabel('概率密度')
ax.set_title('平衡采样 = 正则系综')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch07_langevin_distribution.png"), dpi=130)
plt.close(fig)

print("04_langevin_thermostat.py done")
