"""双流不稳定性（two-stream instability）—— 1D 静电 PIC。"""
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


np.random.seed(7)
L = 2 * np.pi
NG = 128
dx = L / NG
NPP = 20000
v0 = 0.5
dt = 0.2
nsteps = 600
n0 = 1.0
w = n0 * L / (2 * NPP)
xg = np.arange(NG) * dx

x1 = np.linspace(0, L, NPP, endpoint=False) + (np.random.rand(NPP) - 0.5) * dx
x2 = np.linspace(0, L, NPP, endpoint=False) + (np.random.rand(NPP) - 0.5) * dx
x1 += 0.01 * L * np.cos(2 * np.pi * x1 / L)
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

# 把给定的整数时刻速度初始化到蛙跳格式的 n=-1/2 时刻。
E0 = field(deposit(x))
v += 0.5 * gather(E0, x) * dt

for n in range(nsteps):
    E = field(deposit(x))
    if n in snap_times:
        phase_snaps[n] = (x.copy(), v.copy())
    field_energy.append(0.5 * np.sum(E ** 2) * dx)
    v += -1.0 * gather(E, x) * dt
    x = (x + v * dt) % L

field_energy = np.array(field_energy)
t_ax = np.arange(nsteps) * dt

# 在线性增长区拟合 ln(W_E)，能量增长率是振幅增长率的两倍。
fit_mask = (t_ax >= 6.0) & (t_ax <= 12.0)
gamma_energy, fit_intercept = np.polyfit(t_ax[fit_mask], np.log(field_energy[fit_mask]), 1)
gamma_amplitude = 0.5 * gamma_energy
fit_line = np.exp(fit_intercept + gamma_energy * t_ax[fit_mask])

# --- 图1：场能增长 ---
fig, ax = plt.subplots(figsize=(9, 5))
ax.semilogy(t_ax, field_energy + 1e-12, 'b-', linewidth=1.5, label='PIC')
ax.semilogy(t_ax[fit_mask], fit_line, 'r--', linewidth=1.8,
            label=fr'linear fit: $\gamma_A={gamma_amplitude:.3f}$')
ax.set_xlabel(r'time $t$ ($\omega_p^{-1}$)'); ax.set_ylabel(r'$W_E=\int E^2/2\,dx$')
ax.set_title('不稳定模指数增长（半对数）→ 饱和')
ax.legend(frameon=False)
plt.tight_layout()
plt.suptitle('two_stream_instability')

# --- 图2：相空间快照 ---
fig, ax = plt.subplots(figsize=(8, 5.5))
colors = ['0.25', 'tab:blue', 'tab:orange', 'tab:red']
styles = ['-', '--', '-.', ':']
for c, ls, n in zip(colors, styles, snap_times):
    xs, vs = phase_snaps[n]
    ax.scatter(xs[::40], vs[::40], s=3, color=c, alpha=0.45, marker='o', label=f'$t={n*dt:.0f}$')
ax.set_xlabel('$x$'); ax.set_ylabel('$v_x$')
ax.set_title('相空间：双束 → 猫眼涡旋')
ax.legend(markerscale=4, loc='upper right', frameon=False)
plt.tight_layout()
plt.suptitle('two_stream_phasespace')

print(f"03_pic_two_stream.py done; fitted amplitude growth rate = {gamma_amplitude:.4f}")

plt.show()
