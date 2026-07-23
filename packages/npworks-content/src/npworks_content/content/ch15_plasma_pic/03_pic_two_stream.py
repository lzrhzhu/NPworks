"""双流不稳定性（two-stream instability）—— 1D 静电 PIC。"""
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


IMG_DIR = _img_dir("ch15")

np.random.seed(7)
L = 2 * np.pi
NG = 128
dx = L / NG
NPP = 20000
v0 = 1.0
dt = 0.2
nsteps = 600
n0 = 1.0
w = n0 * L / (2 * NPP)
xg = np.arange(NG) * dx

x1 = np.linspace(0, L, NPP, endpoint=False) + (np.random.rand(NPP) - 0.5) * dx
x2 = np.linspace(0, L, NPP, endpoint=False) + (np.random.rand(NPP) - 0.5) * dx
x1 += 0.001 * np.cos(2 * np.pi * x1 / L)
x1 %= L; x2 %= L
x = np.concatenate([x1, x2])
v = np.concatenate([np.full(NPP, v0), np.full(NPP, -v0)])

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


field_energy = []
phase_snaps = {}
snap_times = [0, 120, 300, 599]

for n in range(nsteps):
    E = field(deposit(x))
    if n in snap_times:
        phase_snaps[n] = (x.copy(), v.copy())
    field_energy.append(0.5 * np.sum(E ** 2) * dx)
    v += -1.0 * gather(E, x) * dt
    x = (x + v * dt) % L

field_energy = np.array(field_energy)
t_ax = np.arange(nsteps) * dt

# --- 图1：场能增长 ---
fig, ax = plt.subplots(figsize=(9, 5))
ax.semilogy(t_ax, field_energy + 1e-12, 'b-', linewidth=1.5)
ax.set_xlabel('time $t$  ($\\omega_p^{-1}$)'); ax.set_ylabel(r'电场能 $\int E^2/2\,dx$')
ax.set_title('不稳定模指数增长（半对数）→ 饱和')
ax.grid(True, alpha=0.3, which='both')
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch15_two_stream_instability.png"), dpi=130)
plt.close(fig)

# --- 图2：相空间快照 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
colors = ['gray', 'steelblue', 'orange', 'crimson']
for c, n in zip(colors, snap_times):
    xs, vs = phase_snaps[n]
    ax.scatter(xs[::40], vs[::40], s=2, color=c, alpha=0.5, label=f'$t={n*dt:.0f}$')
ax.set_xlabel('$x$'); ax.set_ylabel('$v_x$')
ax.set_title('相空间：双束 → 猫眼涡旋')
ax.legend(markerscale=4, loc='upper right'); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, "ch15_two_stream_phasespace.png"), dpi=130)
plt.close(fig)

print("03_pic_two_stream.py done")
