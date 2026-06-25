"""朗道阻尼（Landau damping）—— 1D 静电 PIC。

无碰撞等离子体中，即使没有耗散性碰撞，静电波（Langmuir 波）也会衰减：
能量从波转移给与波共振（速度接近相速度）的粒子。
本例用单 Maxwellian 电子 + 小密度扰动激发 k=1 的 Langmuir 波，
追踪该模式电场振幅，可见 ~exp(-gamma t) 的衰减。

参数取 k*λD ≈ 0.5，理论朗道阻尼率 γ ≈ -0.15 ωp。
"""
import numpy as np
from scipy.special import erfinv
import matplotlib.pyplot as plt

np.random.seed(11)

# ---- 参数 ----
L = 2 * np.pi
NG = 256
dx = L / NG
NP = 100000
v_th = 0.5                     # λD = v_th/ωp = 0.5 → kλD = 0.5
dt = 0.05
nsteps = 600
n0 = 1.0
w = n0 * L / NP
k = 2 * np.pi * np.fft.fftfreq(NG, d=dx)
k2 = k ** 2
k2[0] = 1.0


def deposit(xp):
    rho = np.zeros(NG)
    g = xp / dx
    i = np.floor(g).astype(int) % NG
    f = g - np.floor(g)
    np.add.at(rho, i, w * (1 - f) / dx)
    np.add.at(rho, (i + 1) % NG, w * f / dx)
    return rho


def field(rho_e_num):
    rho = -1.0 * rho_e_num + n0
    rho_hat = np.fft.fft(rho)
    phi_hat = rho_hat / k2
    phi_hat[0] = 0.0
    E = np.fft.ifft(-1j * k * phi_hat).real
    return E


def gather(E, xp):
    g = xp / dx
    i = np.floor(g).astype(int) % NG
    f = g - np.floor(g)
    return E[i] * (1 - f) + E[(i + 1) % NG] * f


# ---- 静启动（quiet start）：低噪声 Maxwellian ----
u = (np.arange(NP) + 0.5) / NP
v = v_th * np.sqrt(2) * erfinv(2 * u - 1)        # Maxwellian，低噪声
x = np.arange(NP) * (L / NP)
# 激发 k=1 Langmuir 波：小幅位置 + 速度扰动
eps = 0.02
x = (x + eps * np.sin(2 * np.pi * x / L)) % L
v = v - eps * 1.0 * np.cos(2 * np.pi * x / L)     # 速度扰动驱动波

E_mode = []
for n in range(nsteps):
    rho_e = deposit(x)
    E = field(rho_e)
    E_mode.append(np.fft.fft(E)[1])              # k=1 复振幅
    Ep = gather(E, x)
    v += -1.0 * Ep * dt
    x += v * dt
    x %= L

E_mode = np.array(E_mode)
amp = np.abs(E_mode)
t = np.arange(nsteps) * dt

# 归一化振幅 + 理论衰减包络
amp_n = amp / amp.max()
gamma_theory = -0.15
env = np.exp(gamma_theory * t)

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

# 左：k=1 电场实部（振荡）+ 衰减包络
axes[0].plot(t, E_mode.real / np.abs(E_mode).max(), 'b-', linewidth=1,
             label=r'Re$[E_{k=1}(t)]$（Langmuir 振荡）')
axes[0].plot(t, env, 'r--', linewidth=2, label=r'$e^{-0.15\,t}$（朗道阻尼包络）')
axes[0].plot(t, -env, 'r--', linewidth=2)
axes[0].set_xlabel('time $t$  ($\\omega_p^{-1}$)')
axes[0].set_ylabel(r'$E_{k=1}$（归一化）')
axes[0].set_title('Langmuir 波振幅指数衰减')
axes[0].set_xlim(0, t[-1])
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# 右：振幅（半对数）
axes[1].semilogy(t, amp_n + 1e-6, 'b-', linewidth=1.5, label='模拟 |E_{k=1}|')
axes[1].semilogy(t, env, 'r--', linewidth=2, label=r'$e^{-0.15\,t}$')
axes[1].set_xlabel('time $t$')
axes[1].set_ylabel(r'$|E_{k=1}|$（对数）')
axes[1].set_title('半对数图：直线 → 指数阻尼')
axes[1].legend()
axes[1].grid(True, alpha=0.3, which='both')

plt.tight_layout()
plt.suptitle('landau_damping')
plt.show()
print("04_landau_damping.py done")
