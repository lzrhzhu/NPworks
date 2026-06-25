"""双流不稳定性（two-stream instability）—— 1D 静电 PIC。

两束反向电子流穿过静止离子背景。微小电荷涨落被指数放大：
一束的密度峰吸引另一束的电子使峰更高。源于波–粒子共振，
能量从束流动能转移到静电波。相空间形成"猫眼"涡旋。

方法：CIC 电荷分配 + 谱（FFT）Poisson 求解 + 蛙跳推进。
归一化单位：电子 q=-1, m=1, eps0=1, 离子背景 n0=1（固定）→ ωp=1。
"""
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(7)

# ---- 参数 ----
L = 2 * np.pi
NG = 128
dx = L / NG
NPP = 20000                 # 每束宏粒子数
v0 = 1.0                    # 束流速度（k*v0≈ωp=1 时增长最快）
dt = 0.2
nsteps = 600
n0 = 1.0
w = n0 * L / (2 * NPP)      # 每个宏粒子代表的真实粒子数
xg = np.arange(NG) * dx

# ---- 初始化：两束 + 小密度扰动激发不稳定模式 ----
x1 = np.linspace(0, L, NPP, endpoint=False) + (np.random.rand(NPP) - 0.5) * dx
x2 = np.linspace(0, L, NPP, endpoint=False) + (np.random.rand(NPP) - 0.5) * dx
pert = 0.001 * np.cos(2 * np.pi * x1 / L)   # k=1 扰动
x1 += pert
x1 %= L
x2 %= L
v1 = np.full(NPP, v0)
v2 = np.full(NPP, -v0)
x = np.concatenate([x1, x2])
v = np.concatenate([v1, v2]) - 0.0          # v 在半步（初始场≈0）


def deposit(xp):
    rho = np.zeros(NG)
    g = xp / dx
    i = np.floor(g).astype(int) % NG
    f = g - np.floor(g)
    np.add.at(rho, i, w * (1 - f) / dx)
    np.add.at(rho, (i + 1) % NG, w * f / dx)
    return rho                     # 电子电荷密度（已带 q=-1？未带，下步乘 -1）


k = 2 * np.pi * np.fft.fftfreq(NG, d=dx)
k2 = k ** 2
k2[0] = 1.0                        # 避免除零（k=0 模 neutrality 后为 0）


def field(rho_e_num):
    # rho_e_num: 电子数密度网格（正）。电荷密度 = -1*电子 + +1*离子背景
    rho = -1.0 * rho_e_num + n0
    rho_hat = np.fft.fft(rho)
    phi_hat = rho_hat / k2
    phi_hat[0] = 0.0
    E_hat = -1j * k * phi_hat
    E = np.fft.ifft(E_hat).real
    return E


def gather(E, xp):
    g = xp / dx
    i = np.floor(g).astype(int) % NG
    f = g - np.floor(g)
    return E[i] * (1 - f) + E[(i + 1) % NG] * f


field_energy = []
phase_snaps = {}
snap_times = [0, 120, 300, 599]

for n in range(nsteps):
    rho_e = deposit(x)
    E = field(rho_e)
    if n in snap_times:
        phase_snaps[n] = (x.copy(), v.copy())
    field_energy.append(0.5 * np.sum(E ** 2) * dx)
    Ep = gather(E, x)
    v += -1.0 * Ep * dt            # a = (q/m)E = -E（电子）
    x += v * dt
    x %= L

field_energy = np.array(field_energy)

# ---- 绘图 ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# 左：场能增长（线性增长期 → 指数；后饱和）
t_ax = np.arange(nsteps) * dt
axes[0].semilogy(t_ax, field_energy + 1e-12, 'b-', linewidth=1.5)
axes[0].set_xlabel('time $t$  ($\\omega_p^{-1}$)')
axes[0].set_ylabel('电场能 $\\int E^2/2\\,dx$')
axes[0].set_title('不稳定模指数增长（半对数）→ 饱和')
axes[0].grid(True, alpha=0.3, which='both')

# 右：相空间快照（猫眼涡旋）
colors = ['gray', 'steelblue', 'orange', 'crimson']
for c, n in zip(colors, snap_times):
    xs, vs = phase_snaps[n]
    axes[1].scatter(xs[::40], vs[::40], s=2, color=c, alpha=0.5,
                    label=f'$t={n*dt:.0f}$')
axes[1].set_xlabel('$x$')
axes[1].set_ylabel('$v_x$')
axes[1].set_title('相空间：双束 → 猫眼涡旋')
axes[1].legend(markerscale=4, loc='upper right')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.suptitle('two_stream_instability')
plt.show()
print("03_pic_two_stream.py done")
