"""朗道阻尼（Landau damping）—— 1D 静电 PIC。"""
import numpy as np
from scipy.special import erfinv
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


IMG_DIR = _img_dir("ch15")

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
v = v - eps * 1.0 * np.cos(2 * np.pi * x / L)

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
gamma_theory = -0.15
env = np.exp(gamma_theory * t)

# --- 图1：k=1 电场实部 + 衰减包络 ---
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(t, E_mode.real / np.abs(E_mode).max(), 'b-', linewidth=1, label=r'Re$[E_{k=1}(t)]$')
ax.plot(t, env, 'r--', linewidth=2, label=r'$e^{-0.15\,t}$（朗道阻尼包络）')
ax.plot(t, -env, 'r--', linewidth=2)
ax.set_xlabel('time $t$  ($\\omega_p^{-1}$)'); ax.set_ylabel(r'$E_{k=1}$（归一化）')
ax.set_title('Langmuir 波振幅指数衰减'); ax.set_xlim(0, t[-1])
ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch15_landau_damping.png"), dpi=130)
plt.close(fig)

# --- 图2：振幅半对数 ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(t, amp_n + 1e-6, 'b-', linewidth=1.5, label='模拟 |E_{k=1}|')
ax.semilogy(t, env, 'r--', linewidth=2, label=r'$e^{-0.15\,t}$')
ax.set_xlabel('time $t$'); ax.set_ylabel(r'$|E_{k=1}|$（对数）')
ax.set_title('半对数图：直线 → 指数阻尼')
ax.legend(); ax.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch15_landau_damping_log.png"), dpi=130)
plt.close(fig)

print("04_landau_damping.py done")
