"""朗道阻尼（Landau damping）—— 1D 静电 PIC。"""
import numpy as np
from scipy.special import erfinv
import matplotlib.pyplot as plt

plt.rcParams.update({
    'savefig.dpi': 300, 'figure.figsize': (6.4, 4.0), 'font.size': 11,
    'axes.titlesize': 12, 'axes.labelsize': 11, 'xtick.labelsize': 10,
    'ytick.labelsize': 10, 'legend.fontsize': 10, 'xtick.direction': 'in',
    'ytick.direction': 'in', 'xtick.top': True, 'ytick.right': True,
    'axes.linewidth': 0.8, 'lines.linewidth': 1.5, 'lines.markersize': 5,
    'axes.grid': False, 'axes.unicode_minus': False,
})


np.random.seed(11)
L = 2 * np.pi
NG = 256
dx = L / NG
NP = 100000
v_th = 0.5
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
    phi_hat = np.fft.fft(rho) / k2
    phi_hat[0] = 0.0
    return np.fft.ifft(-1j * k * phi_hat).real


def gather(E, xp):
    g = xp / dx
    i = np.floor(g).astype(int) % NG
    f = g - np.floor(g)
    return E[i] * (1 - f) + E[(i + 1) % NG] * f


u = (np.arange(NP) + 0.5) / NP
v = v_th * np.sqrt(2) * erfinv(2 * u - 1)
x = np.arange(NP) * (L / NP)
eps = 0.02
x = (x + eps * np.sin(2 * np.pi * x / L)) % L

# 把给定的整数时刻速度初始化到蛙跳格式的 n=-1/2 时刻。
E0 = field(deposit(x))
v += 0.5 * gather(E0, x) * dt

E_mode = []
for n in range(nsteps):
    E = field(deposit(x))
    E_mode.append(np.fft.fft(E)[1])
    v += -1.0 * gather(E, x) * dt
    x = (x + v * dt) % L

E_mode = np.array(E_mode)
amp = np.abs(E_mode)
t = np.arange(nsteps) * dt
amp_n = amp / amp.max()
gamma_theory = -0.153

# 用局部极大值表示振荡包络，只拟合最初的线性阻尼阶段。
peak_idx = np.where((amp[1:-1] > amp[:-2]) & (amp[1:-1] >= amp[2:]))[0] + 1
fit_peaks = peak_idx[(t[peak_idx] >= 1.0) & (t[peak_idx] <= 12.0)]
gamma_fit, fit_intercept = np.polyfit(t[fit_peaks], np.log(amp[fit_peaks]), 1)
envelope_scale = np.exp(fit_intercept) / amp.max()
env_fit = envelope_scale * np.exp(gamma_fit * t)
env_theory = envelope_scale * np.exp(gamma_theory * t)

# --- 图1：k=1 电场实部 + 衰减包络 ---
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(t, E_mode.real / np.abs(E_mode).max(), 'b-', linewidth=1, label=r'Re$[E_{k=1}(t)]$')
ax.plot(t, env_fit, 'r--', linewidth=1.8, label=fr'fit envelope: $\gamma={gamma_fit:.3f}$')
ax.plot(t, -env_fit, 'r--', linewidth=1.8)
ax.set_xlabel('time $t$  ($\\omega_p^{-1}$)'); ax.set_ylabel(r'$E_{k=1}$（归一化）')
ax.set_title('Langmuir 波振幅指数衰减'); ax.set_xlim(0, t[-1])
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('landau_damping')

# --- 图2：振幅半对数 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(t, amp_n + 1e-8, color='0.7', linewidth=1.0, label=r'PIC $|E_{k=1}|$')
ax.semilogy(t[peak_idx], amp_n[peak_idx], 'bo', markersize=3, label='local maxima')
ax.semilogy(t, env_fit, 'r-', linewidth=1.8, label=fr'fit: $\gamma={gamma_fit:.3f}$')
ax.semilogy(t, env_theory, 'k--', linewidth=1.5, label=r'theory: $\gamma=-0.153$')
ax.set_xlabel('time $t$'); ax.set_ylabel(r'$|E_{k=1}|$（对数）')
ax.set_title('半对数图：直线 → 指数阻尼')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('landau_damping_log')

print(f"04_landau_damping.py done; fitted damping rate = {gamma_fit:.4f}")

plt.show()
