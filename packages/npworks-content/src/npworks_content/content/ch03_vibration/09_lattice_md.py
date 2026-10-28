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

# 一维单原子链的多原子模拟：行波、波包色散、FFT 验证色散关系
# 自然单位 m = a = 1；K 为弹簧常数。周期性边界由 np.roll 实现。
N = 128                  # 原子数
K = 1.0                  # 弹簧常数
dt = 0.05                # Verlet 步长（稳定性上限 2/omega_max = 1）

n = np.arange(N)


def accel(u):
    # 周期边界：数组整体循环移位取近邻，边界自动首尾相接
    return K * (np.roll(u, -1) - 2.0 * u + np.roll(u, 1))


def verlet(u, v, n_steps):
    # 速度 Verlet：每步只做一次新的力计算；逐步记录位移与速度场
    n_rec = n_steps + 1
    U = np.zeros((n_rec, N))
    V = np.zeros((n_rec, N))
    U[0] = u
    V[0] = v
    a = accel(u)
    for step in range(1, n_steps + 1):
        u = u + v * dt + 0.5 * a * dt ** 2
        a_new = accel(u)
        v = v + 0.5 * (a + a_new) * dt
        a = a_new
        U[step] = u
        V[step] = v
    return U, V


def omega_of(k):
    # 解析色散关系 omega(k) = 2 sqrt(K/m) |sin(k a / 2)|，m = 1
    return 2.0 * np.sqrt(K) * np.abs(np.sin(k / 2.0))


# ---------- (a) 行波简正模：验证 Verlet 正确传播格波 ----------
k0 = np.pi / 2                                   # ka/pi = 0.5
w0 = omega_of(k0)
t1 = 16.0
Ua, _ = verlet(np.cos(k0 * n), w0 * np.sin(k0 * n), int(t1 / dt))
u1_md = Ua[-1]
u1_exact = np.cos(k0 * n - w0 * t1)

# ---------- (b) 局域波包：直观展示色散（相速度 vs 群速度） ----------
k0b = 2.0
w0b = omega_of(k0b)
xc, sigma = 32.0, 6.0
env = np.exp(-((n - xc) ** 2) / (2.0 * sigma ** 2))
T_b = 70.0
Ub, _ = verlet(env * np.cos(k0b * n), w0b * env * np.sin(k0b * n), int(T_b / dt))
vg = np.sqrt(K) * np.cos(k0b / 2.0)              # 群速度
vp = w0b / k0b                                   # 相速度

# ---------- (c) 随机激发：FFT 提取全部波矢的频率 ----------
rng = np.random.default_rng(42)
T_c = 2000.0
Uc, Vc = verlet(0.01 * rng.standard_normal(N), np.zeros(N), int(T_c / dt))

# 能量守恒检验（辛格式的误差应为有界振荡而非漂移）
E = (0.5 * np.sum(Vc ** 2, axis=1)
     + 0.5 * K * np.sum((np.roll(Uc, -1, axis=1) - Uc) ** 2, axis=1))
drift = np.max(np.abs(E - E[0])) / E[0]

# 空间 FFT 分解简正模 -> 逐模时间 FFT 取峰值频率（峰附近抛物线内插）
A_kt = np.fft.fft(Uc, axis=1)                    # (n_t, N)：各波矢复振幅
# 每个波矢的复振幅按 e^{-i omega t} 演化，实部即单一频率余弦，可直接作实输入
P = np.abs(np.fft.rfft(A_kt.real, axis=0)) ** 2  # (n_w, N)：功率谱
w_grid = 2.0 * np.pi * np.fft.rfftfreq(len(Uc), d=dt)
dw = w_grid[1] - w_grid[0]
omega_num = np.zeros(N)
for k in range(N):
    j = int(np.argmax(P[:, k]))
    if 0 < j < len(w_grid) - 1:
        y0, y1, y2 = np.log(P[j - 1:j + 2, k] + 1e-300)
        den = y0 - 2.0 * y1 + y2
        delta = 0.5 * (y0 - y2) / den if den != 0.0 else 0.0
        omega_num[k] = w_grid[j] + delta * dw
    else:
        omega_num[k] = w_grid[j]
k_axis = 2.0 * np.pi * np.fft.fftfreq(N, d=1.0)  # 第一布里渊区内的波矢
omega_exact = omega_of(k_axis)
mask = np.abs(k_axis) > 2.0 * np.pi / N          # 排除 k = 0 平移模
max_dev = np.max(np.abs(omega_num - omega_exact)[mask]) / (2.0 * np.sqrt(K))

print(f"09_lattice_md.py: max |omega_MD - omega_exact| / omega_max = {max_dev:.2e}")
print(f"09_lattice_md.py: max |E - E0| / E0 over T = {T_c:.0f}: {drift:.2e}")

# ---------- 绘图 ----------
fig = plt.figure(figsize=(10.5, 7.2), layout='constrained')
gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.2])
ax_a = fig.add_subplot(gs[0, 0])
ax_b = fig.add_subplot(gs[0, 1])
ax_c = fig.add_subplot(gs[1, :])

# (a) 行波快照：t=0 参考、t=16 数值点与解析行波重合
ax_a.plot(n, np.cos(k0 * n), color='0.65', lw=1.2, label=r'$t = 0$')
ax_a.plot(n, u1_md, 'o', color='#0072B2', ms=2.6, ls='none',
          label=r'MD, $t = %.0f$' % t1)
ax_a.plot(n, u1_exact, '--', color='#D55E00', lw=1.4, label='analytic')
ax_a.set_xlabel(r'$n$')
ax_a.set_ylabel(r'$u_n$ (a.u.)')
ax_a.set_title(r'(a) traveling mode, $k_0 a = \pi/2$')
ax_a.set_ylim(-1.45, 1.45)
ax_a.legend(frameon=False, loc='upper center', ncols=3)

# (b) 波包时空图：条纹斜率为相速度，包络以群速度推进并展宽
im = ax_b.imshow(Ub, aspect='auto', origin='lower', cmap='viridis',
                 interpolation='nearest', extent=(0, N, 0, T_b))
t_line = np.linspace(0.0, T_b, 50)
ax_b.plot(xc + vg * t_line, t_line, '--', color='white', lw=1.4,
          label=r'$v_g$ (envelope)')
ax_b.plot(xc + vp * t_line, t_line, ':', color='white', lw=1.4,
          label=r'$v_p$ (crests)')
ax_b.set_xlabel(r'$x/a$')
ax_b.set_ylabel(r'$t$ (a.u.)')
ax_b.set_title(r'(b) wave packet, $k_0 a = 2$')
ax_b.set_xlim(0, N)
ax_b.legend(frameon=False, loc='upper left')
cbar = fig.colorbar(im, ax=ax_b)
cbar.set_label(r'$u$ (a.u.)')

# (c) 色散验证：数值频率点落在解析曲线上
kk = np.linspace(-np.pi, np.pi, 400)
ax_c.plot(kk / np.pi, omega_of(kk), '-', color='#0072B2', lw=1.6,
          label='analytic dispersion')
ax_c.plot(k_axis / np.pi, omega_num, 'o', color='#D55E00', ms=3.2, ls='none',
          label='MD + FFT')
ax_c.set_xlabel(r'$ka/\pi$')
ax_c.set_ylabel(r'$\omega$ (a.u.)')
ax_c.set_title('(c) dispersion from MD + FFT')
ax_c.set_xlim(-1, 1)
ax_c.set_ylim(0.0, 2.1)
ax_c.legend(frameon=False, loc='upper center', ncols=2)

plt.suptitle('lattice_md_dispersion')

print("09_lattice_md.py done")

plt.show()
